// Thin wrapper over the backend endpoints. Errors carry a message ready to show the user.

export class ApiError extends Error {}

const ERROR_MESSAGES = {
  422: "Revisa los datos: el mensaje no puede estar vacío ni superar 4000 caracteres.",
  503: "El servicio está ocupado en este momento. Intenta de nuevo en unos segundos.",
};
const DEFAULT_ERROR = "No pudimos procesar tu solicitud. Intenta de nuevo más tarde.";
const CONNECTION_ERROR = "No hay conexión con el servidor. Verifica que esté corriendo e intenta de nuevo.";
const TIMEOUT_ERROR =
  "El servidor tardó demasiado en responder. Revisa en «Consultar solicitudes» si tu solicitud quedó registrada.";

// Classification may retry the LLM several times, so the limit is generous.
const REQUEST_TIMEOUT_MS = 60_000;

async function request(url, options = {}) {
  let response;
  try {
    response = await fetch(url, { ...options, signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS) });
  } catch (error) {
    throw new ApiError(error.name === "TimeoutError" ? TIMEOUT_ERROR : CONNECTION_ERROR);
  }
  if (!response.ok) throw new ApiError(ERROR_MESSAGES[response.status] ?? DEFAULT_ERROR);
  return response.json();
}

export function createRequest(message, sourceArea) {
  return request("/solicitudes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, source_area: sourceArea || null }),
  });
}

export function listRequests(filters) {
  const query = new URLSearchParams(Object.entries(filters).filter(([, value]) => value));
  return request(`/solicitudes${query.size ? `?${query}` : ""}`);
}
