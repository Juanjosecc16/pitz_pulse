"use strict";

// Human-readable labels for the API values. Unknown values fall back to the raw value,
// so a new category added in the backend still displays without changing this file.
const LABELS = {
  categoria: {
    bug: "Error / Bug",
    datos: "Pedido de datos",
    acceso: "Pedido de acceso",
    automatizacion: "Automatización",
    consulta: "Consulta",
    otro: "Otro",
  },
  prioridad: { alta: "Alta", media: "Media", baja: "Baja" },
  area_sugerida: {
    backend: "Backend",
    frontend: "Frontend",
    data: "Data",
    devops: "DevOps",
    producto: "Producto",
    digital_transformation: "Digital Transformation",
  },
  idioma: { es: "Español", pt: "Portugués" },
};

const elements = {
  formView: document.getElementById("form-view"),
  form: document.getElementById("request-form"),
  sourceArea: document.getElementById("source-area"),
  message: document.getElementById("message"),
  charCount: document.getElementById("char-count"),
  submitButton: document.getElementById("submit-button"),
  loadingHint: document.getElementById("loading-hint"),
  formError: document.getElementById("form-error"),
  resultView: document.getElementById("result-view"),
  newRequestButton: document.getElementById("new-request-button"),
};

function label(field, value) {
  return LABELS[field]?.[value] ?? value;
}

function setText(id, text) {
  document.getElementById(id).textContent = text; // textContent: user text is never parsed as HTML
}

function showError(text) {
  elements.formError.textContent = text;
  elements.formError.hidden = !text;
}

function setLoading(isLoading) {
  elements.submitButton.disabled = isLoading;
  elements.submitButton.textContent = isLoading ? "Clasificando…" : "Enviar solicitud";
  elements.loadingHint.hidden = !isLoading;
}

function describeError(response) {
  if (response.status === 422) return "Revisa el mensaje: no puede estar vacío ni superar 4000 caracteres.";
  if (response.status === 503) return "El servicio está ocupado en este momento. Intenta de nuevo en unos segundos.";
  return "No pudimos procesar tu solicitud. Intenta de nuevo más tarde.";
}

function renderResult(request) {
  setText("result-id", request.id);
  setText("result-summary", request.resumen);
  setText("result-category", label("categoria", request.categoria));
  setText("result-area", label("area_sugerida", request.area_sugerida));
  setText("result-language", label("idioma", request.idioma));
  setText("result-message", request.message);

  const priorityBadge = document.getElementById("result-priority");
  priorityBadge.textContent = label("prioridad", request.prioridad);
  priorityBadge.className = `badge priority-${request.prioridad}`;

  document.getElementById("follow-up").hidden = !request.requiere_info;
  document.getElementById("ready-note").hidden = request.requiere_info;
  setText("follow-up-question", request.pregunta_seguimiento ?? "");

  elements.formView.hidden = true;
  elements.resultView.hidden = false;
  elements.resultView.focus();
}

async function submitRequest(event) {
  event.preventDefault();
  const message = elements.message.value.trim();
  if (!message) {
    showError("Escribe tu solicitud antes de enviarla.");
    elements.message.focus();
    return;
  }

  showError("");
  setLoading(true);
  try {
    const response = await fetch("/solicitudes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, source_area: elements.sourceArea.value.trim() || null }),
    });
    if (!response.ok) {
      showError(describeError(response));
      return;
    }
    renderResult(await response.json());
  } catch {
    showError("No hay conexión con el servidor. Verifica que esté corriendo e intenta de nuevo.");
  } finally {
    setLoading(false);
  }
}

function startNewRequest() {
  elements.form.reset();
  updateCharCount();
  elements.resultView.hidden = true;
  elements.formView.hidden = false;
  elements.message.focus();
}

function updateCharCount() {
  elements.charCount.textContent = `${elements.message.value.length} / ${elements.message.maxLength}`;
}

elements.form.addEventListener("submit", submitRequest);
elements.newRequestButton.addEventListener("click", startNewRequest);
elements.message.addEventListener("input", updateCharCount);
elements.message.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) elements.form.requestSubmit();
});
