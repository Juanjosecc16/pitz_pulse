// "Consultar solicitudes" tab: filters → GET /solicitudes → list of readable items.
import { listRequests } from "./api.js";
import { LABELS } from "./labels.js";
import { renderRequest } from "./render.js";

export function initListView() {
  const filterSelects = document.querySelectorAll("[data-filter]");
  const list = document.getElementById("request-list");
  const status = document.getElementById("list-status");
  const itemTemplate = document.getElementById("request-item-template");

  // Filter options come from the same labels used everywhere else.
  filterSelects.forEach((select) => {
    select.add(new Option("Todas", ""));
    Object.entries(LABELS[select.dataset.filter]).forEach(([value, text]) => select.add(new Option(text, value)));
    select.addEventListener("change", refresh);
  });

  function currentFilters() {
    return Object.fromEntries([...filterSelects].map((select) => [select.dataset.filter, select.value]));
  }

  function renderItems(requests) {
    list.replaceChildren(
      ...requests.map((request) => {
        const item = itemTemplate.content.firstElementChild.cloneNode(true);
        renderRequest(item, request);
        return item;
      }),
    );
    status.textContent = requests.length
      ? `${requests.length} solicitud${requests.length === 1 ? "" : "es"}`
      : "No hay solicitudes con estos filtros.";
  }

  async function refresh() {
    status.textContent = "Cargando…";
    try {
      renderItems(await listRequests(currentFilters()));
    } catch (error) {
      list.replaceChildren();
      status.textContent = error.message;
    }
  }

  return { refresh };
}
