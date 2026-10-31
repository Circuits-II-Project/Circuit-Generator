# Fórmulas por terminal y almacenamiento JSON

Este flujo calcula una fórmula seleccionada en la terminal y, después de un
resultado correcto, permite guardar sus entradas y resultados en JSON. Guarda
cálculos de fórmulas aisladas; no guarda un circuito completo.

## Ejecutar desde la raíz del repositorio

En PowerShell, desde la raíz de Circuit Generator:

```powershell
.\.venv\Scripts\python.exe formula_input_test.py
```

El programa muestra las 18 opciones disponibles. Tras mostrar un resultado
correcto, pregunta `¿Deseas guardar este cálculo? (s/n):`.

- Escribe `s` para guardar el cálculo.
- Escribe `n` para no guardar; no se crea ni modifica un archivo.
- Cualquier otra respuesta repite la pregunta.
- Si la entrada termina en esa pregunta (por ejemplo, una ejecución canalizada
  antigua), se interpreta como `n`.

## Ejemplos

### DC: voltaje de un resistor

Selecciona la opción `1`, que pide `current` y `resistance`:

```text
Elige una fórmula: 1
current: 0.005
resistance: 100
...
resistor_voltage: 0.5
¿Deseas guardar este cálculo? (s/n): s
Cálculo guardado correctamente.
```

El resultado usa la fórmula existente de voltaje de resistor y se guarda solo
después de que el cálculo finaliza correctamente.

### AC: reactancia capacitiva

Selecciona la opción `17`, que pide `capacitance` y `source_frequency`:

```text
Elige una fórmula: 17
capacitance: 0.1
source_frequency: 10
...
capacitive_reactance: 0.15915494309189535
¿Deseas guardar este cálculo? (s/n): n
```

En este ejemplo se conserva el resultado en pantalla, pero no se guarda ningún
registro.

## Ubicación del almacenamiento

La ruta predeterminada es `storage.json`, relativa al directorio de trabajo
actual del proceso. Por ello, al ejecutar el comando desde la raíz del
repositorio, el archivo objetivo es `storage.json` en esa raíz. Ejecutar el
programa desde otra carpeta cambia la ubicación relativa usada por el CLI.

## Formato JSON

Un archivo creado por el almacenamiento usa este formato:

```json
{
  "schema_version": 1,
  "calculations": [
    {
      "formula_option": "1",
      "formula_name": "DC / Basic - Resistor voltage",
      "inputs": {
        "current": 0.005,
        "resistance": 100.0
      },
      "results": {
        "resistor_voltage": 0.5
      },
      "diagram_path": null
    }
  ]
}
```

Campos de cada registro:

- `formula_option`: opción seleccionada en el menú.
- `formula_name`: nombre asociado a esa opción.
- `inputs`: valores validados que recibió la fórmula.
- `results`: diccionario devuelto por la fórmula existente.
- `diagram_path`: referencia opcional a un diagrama. El CLI actual guarda
  `null`.

El módulo de almacenamiento no agrega unidades, conversiones ni formatos de
resultados nuevos: conserva las claves y valores producidos por el servicio de
fórmulas.

## Archivos y errores de almacenamiento

- Un archivo inexistente o vacío se interpreta como una colección vacía. Solo
  se escribe un documento JSON si se acepta guardar un cálculo.
- Si el JSON está corrupto o no cumple el esquema esperado, el guardado falla
  con un mensaje en la terminal y el contenido anterior se conserva.
- Las escrituras se realizan en un archivo temporal de la misma carpeta y se
  reemplazan atómicamente al finalizar. Si ocurre un error de escritura o de
  reemplazo, el archivo anterior se conserva y el CLI no anuncia éxito.
- El almacenamiento rechaza valores no compatibles con JSON y números no
  finitos; el cálculo ya mostrado no se elimina si el guardado falla.

## Estado de diagramas

El almacenamiento admite `diagram_path` como una referencia relativa y rechaza
rutas absolutas. Sin embargo, todavía no define desde qué carpeta se resuelve
esa ruta.

Actualmente el CLI siempre guarda `diagram_path` como `null`. La asociación de
un diagrama con un cálculo y la base de resolución de la ruta deben acordarse
con el flujo de diagramas de Nancy. No se debe asociar una imagen de ejemplo a
un cálculo sin evidencia de que representa el mismo circuito.

## Limitación actual

Las opciones de fórmulas trabajan con valores aislados, como corriente,
resistencia, capacitancia o frecuencia. Este flujo no guarda un circuito
completo, componentes, nodos, fuente ni una integración real con diagramas.

## Ejecutar pruebas

Desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -v
```
