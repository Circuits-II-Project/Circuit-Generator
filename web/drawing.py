#Draw the circuit from its node connections

import math 
import schemdraw
import schemdraw.elements as elm 

from core.loader import COMPONENT_TYPES, id_sort_key

ELEMENT = {"resistor": elm.Resistor, "capacitor": elm.Capacitor, "inductor": elm.Inductor}
UNIT = {"resistor": "Ω", "capacitor": "F", "inductor": "H", "source": "V"}

PART_LEN = 3.0
ROW_GAP = 2.0
BUS = 0.75
NODE_STYLE = {"fontsize": 10, "color": "gray"}

#Helpers
# 1000 -> "1 kΩ", 1e-6 -> "1 µF"
def si (value, unit):
    for scale, prefix in ((1e9, "G"), (1e6, "M"), (1e3, "k"), (1, ""), (1e-3, "m"),
                          (1e-6, "µ"), (1e-9, "n"), (1e-12, "p")):
        if abs(value) >= scale * 0.9995:
            return f"{value / scale:.4g} {prefix}{unit}"
    return f"{value:.3g} {unit}"

# Plain list of every part, source included: dicts with id, type, a, b, value.
def parts_of(circuit):
    parts = []
    for c in circuit.get("components", []):
        field = COMPONENT_TYPES[c["component_type"]][1]
        parts.append({"id": c["component_id"], "type": c["component_type"],
                      "a": c["from_node"], "b": c["to_node"], "value": c[field]})
    src = circuit.get("source")
    if src:
        parts.append({"id": src["source_id"], "type": "source",
                      "a": src["from_node"], "b": src["to_node"], "value": src["source_voltage"]})
    return parts

def label_of(part):
    return f"{part['id']}\n{si(part['value'], UNIT[part['type']])}"

#series parallel reduction
def flip(tree):
    # Same block seen from the other end
    if tree[0] == "ser":
        return ("ser", [flip(c) for c in reversed(tree[1])], list(reversed(tree[2])))
    if tree[0] == "par":
        return ("par", [flip(c) for c in tree[1]])
    return tree

def join_series(t1, node, t2):
    kids1, joints1 = (t1[1], t1[2]) if t1[0] == "ser" else ([t1], [])
    kids2, joints2 = (t2[1], t2[2]) if t2[0] == "ser" else ([t2], [])
    return ("ser", kids1 + kids2, joints1 + [node] + joints2)


def join_parallel(trees):
    kids = []
    for t in trees:
        kids.extend(t[1] if t[0] == "par" else [t])
    return ("par", kids)

#Return the series-parallel tree going from plus to minus
def reduce_sp(parts, plus, minus):
    edges = [{"a": p["a"], "b": p["b"], "tree": ("part", p)} for p in parts]
    if not edges:
        return None

    while True:
        # Parallel: two edges on the same pair of nodes become one
        merged = False
        groups = {}
        for e in edges:
            groups.setdefault(frozenset((e["a"], e["b"])), []).append(e)
        for group in groups.values():
            if len(group) > 1:
                first = group[0]
                trees = [g["tree"] if g["a"] == first["a"] else flip(g["tree"]) for g in group]
                edges = [e for e in edges if all(e is not g for g in group)]
                edges.append({"a": first["a"], "b": first["b"], "tree": join_parallel(trees)})
                merged = True
                break
        if merged:
            continue

        # Series: an inside node touched by exactly two edges disappears
        touching = {}
        for e in edges:
            touching.setdefault(e["a"], []).append(e)
            touching.setdefault(e["b"], []).append(e)
        for node in sorted(touching, key=id_sort_key):
            pair = touching[node]
            if node in (plus, minus) or len(pair) != 2:
                continue
            e1, e2 = pair
            start = e1["a"] if e1["b"] == node else e1["b"]
            end = e2["b"] if e2["a"] == node else e2["a"]
            t1 = e1["tree"] if e1["b"] == node else flip(e1["tree"])
            t2 = e2["tree"] if e2["a"] == node else flip(e2["tree"])
            edges = [e for e in edges if e is not e1 and e is not e2]
            edges.append({"a": start, "b": end, "tree": join_series(t1, node, t2)})
            merged = True
            break
        if not merged:
            break

    if len(edges) == 1 and {edges[0]["a"], edges[0]["b"]} == {plus, minus}:
        e = edges[0]
        return e["tree"] if e["a"] == plus else flip(e["tree"])
    return None

#R1 + (R2 ∥ R3)
def expression(tree):
    kind = tree[0]
    if kind == "part":
        return tree[1]["id"]
    if kind == "ser":
        return " + ".join(f"({expression(c)})" if c[0] == "par" else expression(c) for c in tree[1])
    return " ∥ ".join(f"({expression(c)})" if c[0] == "ser" else expression(c) for c in tree[1])

#Readable series/parallel structure of the circuit seen from the source
def structure(circuit):
    src = circuit.get("source")
    if not src:
        return None
    loads = [p for p in parts_of(circuit) if p["type"] != "source"]
    tree = reduce_sp(loads, src["from_node"], src["to_node"])
    return expression(tree) if tree else None

#Series parallel layout

def size(tree):
    kind = tree[0]
    if kind == "part":
        return PART_LEN, 0.0
    sizes = [size(c) for c in tree[1]]
    if kind == "ser":
        return sum(w for w, _ in sizes), max(h for _, h in sizes)
    width = max(w for w, _ in sizes) + 2 * BUS
    depth = sum(h for _, h in sizes) + ROW_GAP * (len(sizes) - 1)
    return width, depth

def place(d, tree, x, y, where):
    #Draw tree with its left end at (x, y)
    kind = tree[0]
    width, _ = size(tree)
    if kind == "part":
        part = tree[1]
        d += ELEMENT[part["type"]]().endpoints((x, y), (x + width, y)).label(label_of(part))
        return
    if kind == "ser":
        cx = x
        for i, child in enumerate(tree[1]):
            place(d, child, cx, y, where)
            cx += size(child)[0]
            if i < len(tree[2]):
                where[tree[2][i]] = (cx, y)
                d += elm.Dot().at((cx, y))
        return
    # Parallel: left bus at x, right bus at x + width, branches stacked downward
    right = x + width
    cy = y
    for i, child in enumerate(tree[1]):
        cw, ch = size(child)
        if i > 0:
            d += elm.Line().endpoints((x, prev_y), (x, cy))
            d += elm.Line().endpoints((right, prev_y), (right, cy))
            d += elm.Dot().at((x, prev_y))
            d += elm.Dot().at((right, prev_y))
        d += elm.Line().endpoints((x, cy), (x + BUS, cy))
        place(d, child, x + BUS, cy, where)
        d += elm.Line().endpoints((x + BUS + cw, cy), (right, cy))
        prev_y = cy
        cy -= ch + ROW_GAP

def draw_series_parallel(d, tree, circuit):
    src = circuit["source"]
    width, depth = size(tree)
    bottom = -(depth + ROW_GAP)
    where = {src["from_node"]: (0.0, 0.0), src["to_node"]: (0.0, bottom)}

    # Short lead first, so a parallel blocks left bus doesnt sit on the source wire
    d += elm.Line().endpoints((0.0, 0.0), (BUS, 0.0))
    place(d, tree, BUS, 0.0, where)
    right = BUS + width
    # Return wire on the right and bottom, source on the left (+ at the top)
    d += elm.Line().endpoints((right, 0.0), (right, bottom))
    d += elm.Line().endpoints((right, bottom), (0.0, bottom))
    source_part = [p for p in parts_of(circuit) if p["type"] == "source"][0]
    d += elm.SourceV().endpoints((0.0, bottom), (0.0, 0.0)).label(label_of(source_part))
    return where

#fallback right layout

def draw_ring(d, circuit):
    parts = parts_of(circuit)
    nodes = sorted({p["a"] for p in parts} | {p["b"] for p in parts}, key=id_sort_key)
    src = circuit.get("source")
    if src:
        # + node at the top, - node opposite it, the rest split over both sides
        others = [n for n in nodes if n not in (src["from_node"], src["to_node"])]
        half = (len(others) + 1) // 2
        nodes = [src["from_node"], *others[:half], src["to_node"], *others[half:]]

    radius = max(PART_LEN, len(nodes) * PART_LEN / (2 * math.pi)) * 1.3
    where = {}
    for k, node in enumerate(nodes):
        angle = math.pi / 2 - 2 * math.pi * k / len(nodes)
        where[node] = (radius * math.cos(angle), radius * math.sin(angle))

    groups = {}
    for p in parts:
        if p["type"] != "source":
            groups.setdefault(frozenset((p["a"], p["b"])), []).append(p)
    for group in groups.values():
        for k, p in enumerate(group):
            (ax, ay), (bx, by) = where[p["a"]], where[p["b"]]
            length = math.hypot(bx - ax, by - ay)
            #Parts on the same two nodes are pushed sideways so they sit side by side
            shift = (k - (len(group) - 1) / 2) * 1.5
            ox, oy = -(by - ay) / length * shift, (bx - ax) / length * shift
            start, end = (ax + ox, ay + oy), (bx + ox, by + oy)
            if shift:
                d += elm.Line().endpoints((ax, ay), start)
                d += elm.Line().endpoints(end, (bx, by))
            d += ELEMENT[p["type"]]().endpoints(start, end).label(label_of(p))

    if src:
        #Source goes around the outside on the left instead of through the middle
        (px, py), (qx, qy) = where[src["from_node"]], where[src["to_node"]]
        left = min(x for x, _ in where.values()) - PART_LEN / 2
        d += elm.Line().endpoints((px, py), (left, py))
        d += elm.SourceV().endpoints((left, qy), (left, py)).label(
            label_of([p for p in parts if p["type"] == "source"][0]))
        d += elm.Line().endpoints((left, qy), (qx, qy))

    for node in nodes:
        d += elm.Dot().at(where[node])
    return where

#Entry point

#Save a drawing of circuit to path.
def draw_circuit(circuit, path):
    with schemdraw.Drawing(file=path,show=False) as d:
        src = circuit.get("source")
        tree = None
        if src:
            loads = [p for p in parts_of(circuit) if p["type"] != "source"]
            tree = reduce_sp(loads, src["from_node"], src["to_node"])
        if tree:
            where = draw_series_parallel(d,tree,circuit)
            layout = "series-parallel"
        else:
            where = draw_ring(d, circuit)
            layout = "ring"

        #node names
        for node, point in where.items():
            d += elm.Label().at(point).label(node, loc="bottom", **NODE_STYLE)
        ground = circuit.get("ground")
        if ground in where:
            d+= elm.Ground().at(where[ground])
    return layout