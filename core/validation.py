from .loader import components_loader, id_sort_key

def _join(ids):
    return ", ".join(sorted(ids, key=id_sort_key))

def check_circuit(circuit: dict) -> list[str]:
    #Return a list of readable problems that stop the circuit from being calculated.

    try:
        load = components_loader(circuit)
    except (ValueError, KeyError) as err:
        return[f"The circuit data is invalid: {err}"]
    if not load.components:
        return ["The circuit is empty. Add a source and at least one component"]

    problems = []
    nodes = load.nodes
    ground = circuit.get("ground")

    #At least one source:
    if not circuit.get("source"):
        problems.append("There is no voltage source. Add a source.")
    #Ground node is set, and it is a part of the circuit
    if not ground:
        problems.append("No ground node is set. Pick a node and press Set ground.")
    elif ground not in nodes:
        problems.append(f"The ground node {ground} is not connected to any component.")
        ground = None

    #No open ends. Every node must touch at least 2 components ends.
    for node_id in sorted(nodes, key=id_sort_key):
        connected = nodes[node_id].connected_components
        if len(connected) < 2:
            problems.append(f"Node {node_id} is an open end: only {connected[0].id} is connected to it. Connect another component to {node_id}.")

    #Every node can reach ground by following components.
    if ground:
        reached = {ground}
        todo = [ground]
        while todo:
            for comp in nodes[todo.pop()].connected_components:
                for other in (comp.from_node, comp.to_node):
                    if other not in reached:
                        reached.add(other)
                        todo.append(other)
        cut_off = set(nodes) - reached
        if cut_off:
            problems.append(f"These nodes are not connected to ground ({ground}): {_join(cut_off)}. "
                            "Connect that part of the circuit to the rest.")

    return problems