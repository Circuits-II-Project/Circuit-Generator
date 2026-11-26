# API de circuitos guardados para la GUI

Las rutas usan el mismo servidor de Circuit Generator. Las rutas relativas de
`diagram_path` se resuelven desde la carpeta de `web/saved_circuits.json`; la
GUI no debe convertirlas en rutas absolutas ni leer el JSON directamente.

Los nombres repetidos están permitidos. `record_id` identifica el documento y
no cambia al editarlo; `circuit_id` es el hash de la instantánea y cambia si
el contenido eléctrico cambia. Un circuito que se acaba de cargar deja su ID
en `state.loaded_record_id`.

| Método y URL | Cuerpo | Éxito | Errores |
|---|---|---|---|
| `GET /circuits` | ninguno | `200 {"circuits":[{"record_id","circuit_name","circuit_id","diagram_path","image_available"}]}` | `400` si la colección está dañada. |
| `POST /circuits` | `{"circuit_name":"Amplificador"}` | `201 {"record":...,"image_available":true,"state":...}`. Siempre crea otro documento, incluso si el nombre se repite. | `400` si el nombre está vacío, el circuito no está listo o no hay PNG actual. |
| `GET /circuits/<record_id>` | ninguno | `200 {"record":...,"image_available":bool}` | `404` si no existe; `400` si la colección está dañada. |
| `POST /circuits/<record_id>/load` | ninguno | `200 {"record":...,"image_available":bool,"state":...}`. Restaura el estado editable y vuelve a dibujar desde datos. | `404` si no existe; `400` si está dañado. Si falta la imagen archivada responde además `warning`, pero carga el circuito. |
| `PUT /circuits/<record_id>` | Opcionalmente `{"circuit_name":"Nombre nuevo"}` | `200 {"record":...,"image_available":true,"state":...}`. Actualiza solo el documento actualmente cargado y no añade otro. | `400` si no es el documento cargado, el nombre es vacío, el circuito no está listo o falla el guardado. |

`record` incluye `record_id`, `circuit_name`, `circuit_id`, `circuit`,
`results`, `editor_state` y `diagram_path`. `editor_state` conserva
`next_node` y `last_node` para que, después de cargar, se pueda añadir una
parte sin reutilizar nodos.

## Acciones que Nancy debe conectar

1. Solicitar `GET /circuits` al abrir/refrescar el selector y mostrar
   `circuit_name`; puede usar `image_available` como indicador.
2. En “Guardar como nuevo”, pedir un nombre no vacío y llamar
   `POST /circuits`. Guardar `state.loaded_record_id` recibido.
3. En “Cargar”, llamar `POST /circuits/<record_id>/load`, reemplazar el estado
   visual con `state`, refrescar la imagen de trabajo y mostrar `warning` si
   viene presente.
4. En “Actualizar”, llamar `PUT /circuits/<state.loaded_record_id>`.
   Si el usuario cambió el nombre, enviar `circuit_name`; si no, enviar `{}`.
5. Para “Guardar como nuevo” después de editar un circuito cargado, usar
   siempre `POST /circuits`, no `PUT`.

La imagen archivada no se usa para cargar el modelo. Cada guardado o
actualización copia una imagen nueva; una actualización reemplaza el registro
solo después de crear la copia y escribir JSON. La imagen previamente
referenciada se conserva como archivo para protegerla ante fallos.
