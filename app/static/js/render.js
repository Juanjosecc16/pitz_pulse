// Fills any element marked with data-field / data-show-if from a stored request.
// Shared by the result card and the list items, so both always show the same data the same way.
import { label } from "./labels.js";

const DATE_FORMAT = new Intl.DateTimeFormat("es", { dateStyle: "medium", timeStyle: "short" });

const FORMATTERS = {
  categoria: (value) => label("categoria", value),
  prioridad: (value) => label("prioridad", value),
  area_sugerida: (value) => label("area_sugerida", value),
  idioma: (value) => label("idioma", value),
  source_area: (value) => value || "Sin área",
  created_at: (value) => DATE_FORMAT.format(new Date(value)),
};

export function renderRequest(root, request) {
  root.querySelectorAll("[data-field]").forEach((element) => {
    const field = element.dataset.field;
    const format = FORMATTERS[field] ?? ((value) => value ?? "");
    element.textContent = format(request[field]); // textContent: never parsed as HTML
    if (field === "prioridad") element.className = `badge priority-${request.prioridad}`;
  });

  const visibility = { "needs-info": request.requiere_info, ready: !request.requiere_info };
  root.querySelectorAll("[data-show-if]").forEach((element) => {
    element.hidden = !visibility[element.dataset.showIf];
  });
}
