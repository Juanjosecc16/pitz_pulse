import { initFormView } from "./form-view.js";
import { initListView } from "./list-view.js";
import { initTabs } from "./tabs.js";

initFormView();
const listView = initListView();
initTabs({ "tab-list": listView.refresh }); // reload the list every time the tab is opened
