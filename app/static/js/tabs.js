// Switches between tab panels. onActivate callbacks run each time their tab is opened.
export function initTabs(onActivate = {}) {
  const tabs = document.querySelectorAll(".tab[aria-controls]");

  function activate(selectedTab) {
    tabs.forEach((tab) => {
      const isSelected = tab === selectedTab;
      tab.setAttribute("aria-selected", String(isSelected));
      document.getElementById(tab.getAttribute("aria-controls")).hidden = !isSelected;
    });
    onActivate[selectedTab.id]?.();
  }

  tabs.forEach((tab) => tab.addEventListener("click", () => activate(tab)));
}
