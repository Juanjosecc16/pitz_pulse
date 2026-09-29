# Pitz Pulse

Triage inteligente de solicitudes internas. Recibe mensajes libres (en español o portugués) que las áreas de Pitz le escriben a Product & Tech y devuelve, para cada uno, una clasificación estructurada con **categoría, prioridad, equipo sugerido, idioma, resumen en español** y, si falta información, **la pregunta que habría que hacerle al solicitante**.

- **Parte 1 · Clasificación con IA:** Claude (`claude-haiku-4-5`, `temperature = 0`) con salida JSON validada. Resultado de los 12 mensajes del Anexo A en `[resultados.json](resultados.json)`.
- **Parte 2 · Servicio:** API HTTP con `POST /solicitudes` y `GET /solicitudes` (filtros por categoría y prioridad), persistencia en SQLite y una web sencilla.
- **Parte 3 · Reflexión:** `[DECISIONES.md](DECISIONES.md)` y registro de uso de IA en `[AI_LOG.md](AI_LOG.md)`.

---



## Instalación y ejecución (< 5 minutos)

Requisito: **Python 3.11 o superior**.

```bash
git clone https://github.com/Juanjosecc16/pitz_pulse.git
cd pitz_pulse
python -m venv .venv
```

Activar el entorno e instalar dependencias:


| Windows (PowerShell)              | Linux / macOS                     |
| --------------------------------- | --------------------------------- |
| `.venv\Scripts\activate`          | `source .venv/bin/activate`       |
| `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| `copy .env.example .env`          | `cp .env.example .env`            |


Levantar el servidor:

```bash
uvicorn app.main:app --reload
```

- **Web:** [http://localhost:8000](http://localhost:8000)
- **Documentación interactiva de la API:** [http://localhost:8000/docs](http://localhost:8000/docs)

> Sin tocar el `.env`, el proyecto arranca en **modo mock** (sin IA, sin costo). Para usar el modelo real, ver la siguiente sección.



## Enlace compartido de conversación para el Case

**Web:** [Click aquí😁](https://claude.ai/artifact/F9WjY15jWwV3q8MVGr1cBG)

## Configuración (`.env`)


| Variable              | Valor por defecto  | Descripción                                                                     |
| --------------------- | ------------------ | ------------------------------------------------------------------------------- |
| `LLM_PROVIDER`        | `mock`             | `anthropic` usa el modelo real; `mock` clasifica con reglas por palabras clave. |
| `ANTHROPIC_API_KEY`   | *(vacío)*          | Obligatoria si `LLM_PROVIDER=anthropic`. La app no arranca sin ella.            |
| `LLM_MODEL`           | `claude-haiku-4-5` | Debe aceptar `temperature` y salida estructurada.                               |
| `LLM_TIMEOUT_SECONDS` | `30`               | Tiempo máximo por intento.                                                      |
| `LLM_MAX_RETRIES`     | `2`                | Reintentos ante timeout, error del proveedor o respuesta inválida.              |
| `MASK_SENSITIVE_DATA` | `true`             | Enmascara CNPJ, CPF, RFC, emails y tarjetas antes de enviar el mensaje al LLM.  |
| `DATABASE_PATH`       | `pitz_pulse.db`    | Archivo SQLite (relativo a la raíz del proyecto).                               |


Para usar Claude:

```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```



### Modo mock

Pensado para correr el proyecto sin API key. Clasifica con reglas simples (`[app/classifier/mock_rules.py](app/classifier/mock_rules.py)`): detecta el idioma contando palabras y letras típicas (`ã`, `ç` vs. `ñ`, `¿`), la categoría y la prioridad por palabras clave, y pide más información si el mensaje es muy corto. Devuelve el mismo JSON que el modelo real, así que pasa por la misma validación. **No resume ni traduce**: el resumen indica "modo mock, sin IA".

## Uso



### Web

Tres pestañas: **Nueva solicitud** (formulario → resultado legible), **Consultar solicitudes** (lista con filtros por tipo y prioridad) y **Conectar con Slack** (próximamente).

### API

`POST /solicitudes` — clasifica y guarda un mensaje.

```json
{ "message": "Oi, o botão de exportar pedidos não funciona desde hoje cedo.", "source_area": "Operações BR" }
```

Respuesta `201`:

```json
{
  "id": "REQ-356B58B8",
  "categoria": "bug",
  "prioridad": "media",
  "area_sugerida": "frontend",
  "idioma": "pt",
  "resumen": "El botón de exportar pedidos no funciona desde hoy en la mañana; probado en dos navegadores.",
  "requiere_info": true,
  "pregunta_seguimiento": "Qual é a mensagem de erro que aparece, ou o botão simplesmente não responde quando clicam?",
  "message": "Oi, o botão de exportar pedidos não funciona desde hoje cedo.",
  "source_area": "Operações BR",
  "created_at": "2026-09-29T01:48:51.733369Z"
}
```

`GET /solicitudes?categoria=bug&prioridad=alta` — lista las solicitudes (más recientes primero). Ambos filtros son opcionales y aceptan los mismos valores que el JSON.


| Código | Cuándo                                                                                                          |
| ------ | --------------------------------------------------------------------------------------------------------------- |
| `422`  | Mensaje vacío, demasiado largo o filtro con un valor no permitido.                                              |
| `503`  | El proveedor de IA no respondió a tiempo o está saturado (reintentar más tarde).                                |
| `502`  | El modelo devolvió una respuesta inválida tras los reintentos, o rechazó la petición (p. ej. API key inválida). |


Si la IA falla, **no se guarda nada**. La forma más simple de probar la API es `/docs` (en Windows, `curl` con acentos escritos en la consola puede no enviarlos en UTF-8).

### Regenerar `resultados.json`

```bash
python -m scripts.process_annex
```

Lee `[data/mensajes.json](data/mensajes.json)` (los 12 mensajes del Anexo A) y escribe `resultados.json`. Si un mensaje falla, sigue con el resto y termina con código `1`. El archivo incluido fue generado con `claude-haiku-4-5`.

### Tests

```bash
python -m pytest            # 121 tests, sin llamadas a la API
python -m pytest -m live    # 3 tests contra el modelo real (requiere API key, < USD 0,01)
```



## Stack y por qué


| Pieza        | Elección                               | Por qué                                                                                                                                                      |
| ------------ | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Lenguaje     | Python 3.11                            | Ecosistema maduro para trabajar con LLMs (SDK oficial de Anthropic) y validar datos; permite un prototipo completo con muy poco código.                      |
| API          | FastAPI + Uvicorn                      | Endpoints en pocas líneas, validación automática de entrada y documentación interactiva en `/docs` sin trabajo extra.                                        |
| Validación   | Pydantic v2                            | Un solo modelo valida la entrada de la API y la salida del LLM. Los valores permitidos viven en enums: agregar una categoría es cambiar una línea.           |
| LLM          | Anthropic SDK + `claude-haiku-4-5`     | Acepta `temperature = 0` (los modelos más grandes actuales la rechazan) y salida con JSON schema; es el más barato y rápido para una tarea de clasificación. |
| Persistencia | SQLite (`sqlite3` estándar)            | Cero instalación, un archivo, suficiente para un prototipo. Está detrás de una interfaz: migrar a Postgres es escribir otra implementación.                  |
| Web          | HTML + CSS + JavaScript sin frameworks | Una página, sin build ni dependencias; se sirve desde el mismo FastAPI.                                                                                      |
| Tests        | pytest + `TestClient`                  | Unitarios sin red (cliente LLM falso) y tests `live` opcionales contra el modelo real.                                                                       |




## Estructura

```
app/
├── core/config.py          # configuración desde .env
├── domain/                 # enums (valores permitidos) y modelos con validación
├── classifier/             # prompt, esquema, clientes LLM (Anthropic / mock), parser, reintentos, enmascarado
├── repository/             # interfaz de almacenamiento + implementación SQLite
├── services/               # caso de uso: clasificar + guardar + listar
├── api/                    # endpoints, dependencias y mapeo de errores a HTTP
├── static/                 # web (index.html, styles.css, js/)
├── batch.py                # clasificación en lote
└── main.py                 # app FastAPI
scripts/process_annex.py    # genera resultados.json
tests/                      # unitarios por capa + tests live
```

El flujo es `endpoint → RequestService → ClassifierService → LLMClient` y `RequestService → RequestRepository`. Cada capa depende de interfaces, no de implementaciones concretas, lo que permite cambiar el proveedor de IA o la base de datos sin tocar el resto (y probar todo sin red).

## Suposiciones

- **Nombres:** el código usa nombres en inglés; el JSON de salida mantiene las claves y valores en español que exige el enunciado (`categoria`, `requiere_info`, `alta`…), mediante alias de Pydantic. Los campos que agrega la API (`message`, `source_area`, `created_at`) van en inglés.
- `pregunta_seguimiento` se escribe en el idioma del solicitante (a quien va dirigida); el **resumen** siempre en español, para el equipo.
- Si el modelo devuelve `requiere_info = false` con una pregunta, la pregunta se descarta (no se rechaza la respuesta).
- `area_sugerida` es el equipo técnico que debería atender el pedido, no el área que lo escribió.
- El **id** lo genera el servicio (`REQ-XXXXXXXX`), nunca el modelo.
- Un plazo explícito cercano ("para el viernes") puede subir la prioridad un nivel.



## Qué quedó pendiente

- **Integración con Slack:** la pestaña existe pero la integración no. El siguiente paso sería un endpoint que reciba el webhook / slash command de Slack y responda en el hilo con la clasificación.
- **Extras opcionales no hechos:** Dockerfile y detección de solicitudes duplicadas (ver próximos pasos en `[DECISIONES.md](DECISIONES.md)`).
- **Autenticación:** la web y la API no tienen login; es un prototipo para uso interno.

