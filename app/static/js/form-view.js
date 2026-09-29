// "Nueva solicitud" tab: form → POST /solicitudes → result card.
import { createRequest } from "./api.js";
import { renderRequest } from "./render.js";

export function initFormView() {
  const form = document.getElementById("request-form");
  const formView = document.getElementById("form-view");
  const resultView = document.getElementById("result-view");
  const sourceArea = document.getElementById("source-area");
  const message = document.getElementById("message");
  const charCount = document.getElementById("char-count");
  const submitButton = document.getElementById("submit-button");
  const loadingHint = document.getElementById("loading-hint");
  const formError = document.getElementById("form-error");

  function showError(text) {
    formError.textContent = text;
    formError.hidden = !text;
  }

  function setLoading(isLoading) {
    submitButton.disabled = isLoading;
    submitButton.textContent = isLoading ? "Clasificando…" : "Enviar solicitud";
    loadingHint.hidden = !isLoading;
  }

  function updateCharCount() {
    charCount.textContent = `${message.value.length} / ${message.maxLength}`;
  }

  async function submit(event) {
    event.preventDefault();
    const text = message.value.trim();
    if (!text) {
      showError("Escribe tu solicitud antes de enviarla.");
      message.focus();
      return;
    }

    showError("");
    setLoading(true);
    try {
      renderRequest(resultView, await createRequest(text, sourceArea.value.trim()));
      formView.hidden = true;
      resultView.hidden = false;
      resultView.focus();
    } catch (error) {
      showError(error.message);
    } finally {
      setLoading(false);
    }
  }

  function startNewRequest() {
    form.reset();
    updateCharCount();
    resultView.hidden = true;
    formView.hidden = false;
    message.focus();
  }

  form.addEventListener("submit", submit);
  message.addEventListener("input", updateCharCount);
  message.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) form.requestSubmit();
  });
  document.getElementById("new-request-button").addEventListener("click", startNewRequest);
}
