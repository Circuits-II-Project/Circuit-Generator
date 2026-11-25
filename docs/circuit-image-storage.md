# Guardado de circuitos e imágenes

La GUI permite guardar un circuito completo mediante **Save circuit and image**.
La acción solo se habilita cuando el circuito puede calcularse: conserva los
componentes, sus valores y nodos, la fuente, tierra, resultados del cálculo y
una copia PNG del diagrama que ya generó la GUI.

## Ubicación y rutas

Por defecto la GUI crea estos archivos locales, que no se versionan:

- `web/saved_circuits.json`
- `web/saved_circuit_images/`

Cada `diagram_path` en el JSON es relativo a la carpeta que contiene
`saved_circuits.json` (por ejemplo,
`saved_circuit_images/circuit-<id>-<uuid>.png`). Para abrirlo desde un lector,
se resuelve como `Path(storage_json).parent / diagram_path`. Mover el JSON y
esa carpeta de imágenes juntos conserva las referencias.

## Integridad y límites

- La imagen de trabajo de la GUI, `web/static/MyCirc_2.png`, se sobrescribe al
  editar. Al guardar se hace una copia PNG con un UUID, por lo que un diagrama
  guardado no cambia cuando se genera otro circuito.
- El registro contiene un `circuit_id`: SHA-256 de la instantánea canónica del
  circuito. La GUI solo guarda si la imagen de trabajo fue generada con esa
  misma instantánea; así no se enlaza una imagen antigua a datos nuevos.
- Si no existe una imagen actual, agrega o modifica una parte del circuito para
  que la GUI la genere y vuelve a guardar. Actualmente el flujo de dibujo
  admite PNG.
- La copia de imagen se crea antes de actualizar JSON. La colección se escribe
  con reemplazo atómico; si falla la copia o el JSON, los registros previos se
  conservan y se borra únicamente la imagen nueva de ese intento.
- El almacenamiento anterior de fórmulas (`core/formula_storage.py`) permanece
  separado y compatible. Sus registros pueden seguir teniendo
  `diagram_path: null`; no se reinterpretan como circuitos completos.
