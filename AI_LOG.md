# Registro de uso de IA

Herramienta: **Claude Code** (modelo Claude Opus 5.5) durante todo el case. Trabajé por fases (plan con checklist → dominio → clasificador → lote → API → web → docs), revisando y probando cada fase antes del commit. Cinco ejemplos concretos:

## 1. Mi regla de "todo en inglés" chocaba con el enunciado

- **Qué pedí:** que todos los nombres de variables y campos estuvieran en inglés.
- **Qué devolvió:** antes de escribir código, me advirtió que el enunciado exige un JSON con claves en español (`categoria`, `requiere_info`…) y valores como `alta` o `datos`; cumplir mi regla al pie de la letra habría roto el formato pedido. Propuso atributos en inglés con **alias de Pydantic** en español.
- **Qué decidí:** lo acepté. Los campos que agrega la API (`message`, `created_at`) quedaron en inglés y lo documenté como suposición en el README.



## 2. `temperature = 0` rompió al usar la API real

- **Qué pedí:** integrar Claude con `temperature = 0`, como pide el case.
- **Qué devolvió:** eligió `claude-haiku-4-5` porque verificó que los modelos más grandes rechazan `temperature`. El código pasaba todos los tests, pero al correrlo con mi API key falló: `TypeError: Messages.create() got an unexpected keyword argument 'temperature'`. Había verificado el *modelo*, no la *librería*: el SDK 1.x eliminó ese argumento.
- **Qué cambié:** se envía con `extra_body={"temperature": 0}` (la vía documentada por el SDK). Lo más importante: el test no lo detectó porque el *mock* aceptaba cualquier argumento; ahora valida la llamada contra la firma real del SDK. Aprendí que un mock demasiado permisivo esconde errores de integración, y por eso agregamos tests `live` opcionales (`pytest -m live`).



## 3. Resúmenes a medio traducir

- **Qué pedí:** resumen siempre en español, aunque el mensaje venga en portugués.
- **Qué devolvió:** la instrucción en el prompt. Al correr los tests contra el modelo real, uno falló con el resumen *"planilha de vendas de agosto… con totales y comisiones"*: mezcla de portugués y español.
- **Qué cambié:** una regla explícita ("tradúcelo por completo") y un segundo ejemplo en portugués. Pedí que fuera **inventado** y no un mensaje del Anexo A, para no contaminar la evaluación con las respuestas. También agregamos un test que exige que los ejemplos del prompt pasen nuestra propia validación.



## 4. No confiar en el "listo" de la IA

- **Qué pasó:** en la fase del clasificador, la IA hizo el commit aunque un test fallaba. El comando encadenado (`pytest | tail && git commit`) tomaba el código de salida de `tail`, no el de pytest. En ese commit también se coló `.env copy.example`, una copia que yo había hecho del ejemplo.
- **Qué hice:** verificamos que la copia no tuviera ninguna clave, la sacamos del repo y corregimos el bug que había detectado el test (la regex de emails se "comía" el punto final de la oración). Desde ahí, cada commit se hace solo si el resultado de pytest no contiene fallos.



## 5. La web: de "panel de control" a algo simple

- **Qué pedí:** una web sencilla. El plan inicial incluía tabla y filtros.
- **Qué pasó:** cuando revisé, vi una página técnica que parecía un panel; la IA me aclaró que era `/docs` (la documentación automática de FastAPI) y que la web todavía no existía. Le pedí un formulario con un botón y el resultado mostrado de forma amigable, sin JSON.
- **Qué cambié yo:** después de probarlo, pedí tres pestañas (manual, consulta y Slack "próximamente"), reubiqué Slack a la derecha y pedí que fuera clickeable como las demás. También le pedí que me explicara cómo el modo mock detecta el idioma antes de aceptarlo (cuenta palabras y letras típicas de cada idioma; ante empate, español).

