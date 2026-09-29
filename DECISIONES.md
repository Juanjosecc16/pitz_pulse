# Decisiones para el proyecto

**Diseño del prompt:** El prompt (`[prompt.py](app/classifier/prompt.py)`) explica qué es Pitz y qué significa cada categoría, prioridad y área, usando el criterio de prioridad del enunciado. Esas listas salen del mismo código que valida las respuestas, así que no se desalinean. Trae dos ejemplos resueltos (el del Anexo B y uno en portugués). Si la respuesta no cumple las reglas, se vuelve a pedir **diciéndole al modelo qué estuvo mal**.

**Un error que encontré con el test live:** Con el modelo real, el resumen de MSG-02 salió a medio traducir: *"planilha de vendas de agosto… con totales y comisiones"*. La regla "resumen en español" no bastaba, el modelo copiaba palabras del portugués. Lo solucioné con (1) una regla más clara ("tradúcelo por completo") y (2) un ejemplo en portugués con su resumen bien traducido. Ese ejemplo es inventado, para no darle al modelo las respuestas del Anexo A. Después, el test pasó y los 12 resúmenes salieron en español.

**Dónde puede equivocarse:**

- MSG-05 (HubSpot) salió como consulta; yo lo veo como un error de integración, aunque el mensaje es ambiguo.
- MSG-12 mezcla una pregunta ("¿cómo proceso el reembolso?") con un posible error de pagos; eligió bug de prioridad alta, y estoy de acuerdo.
- La prioridad de MSG-02 y MSG-04 es discutible.
- Pide más información en 9 de 12 mensajes (pregunta de más) y a veces hace varias preguntas en una.
- MSG-01 salió perfecto, pero no cuenta: es el ejemplo que está dentro del prompt.

**Cómo mediría si funciona.** Con un set de mensajes etiquetados a mano, midiendo aciertos por campo en cada cambio del prompt. En producción, lo más útil es contar **cuántas clasificaciones corrige el equipo** y usar esas correcciones para mejorar el set.

**Costo:** Medido con los 12 mensajes: unos 1.870 tokens de entrada y 105 de salida Aprox. Con Claude Haiku 4.5 es **≈ USD 0,0024 por mensaje, unos USD 1,2 al mes con 500 solicitudes** (menos de USD 4 aun con reintentos).

**Datos sensibles:** Antes de enviar el mensaje a la IA, la app oculta CNPJ, CPF, RFC, emails y tarjetas. Faltaría ocultar nombres y teléfonos, revisar con Legal cómo guarda los datos el proveedor (LGPD, LFPDPPP), agregar login y evitar que la pregunta de seguimiento pida datos sensibles (en MSG-08 pidió CNPJs).

**Con dos semanas más.** (1) Conectar Slack, que es donde llegan las solicitudes. (2) Permitir corregir la clasificación desde la web y usar esas correcciones para medir y mejorar. (3) Avisar al equipo asignado y detectar solicitudes repetidas. (4) Establecer más idiomas de traducción para los nuevos países donde pitz va a crecer.