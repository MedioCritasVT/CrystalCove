"use strict";
// An opt-in fork between a new tab and a separate window for Portal links.
// Only ordinary left-clicks on explicit target=_blank links are intercepted.
// Native middle-click, Ctrl/Meta-click and context menus remain untouched.
(() => {
  const dialog = document.querySelector("#open-choice-dialog");
  if (!dialog || typeof dialog.showModal !== "function") return;
  const destination = document.querySelector("#open-choice-destination");
  const tab = document.querySelector("#open-choice-tab");
  const windowButton = document.querySelector("#open-choice-window");
  const cancel = document.querySelector("#open-choice-cancel");
  let pending = null;

  document.addEventListener("click", (event) => {
    if (event.defaultPrevented || event.button !== 0 ||
        event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest?.('a[target="_blank"]');
    if (!link || link.hasAttribute("download")) return;
    // Links are authored inside Portal; don't add a way to navigate to
    // arbitrary unsupported protocols through this modal.
    let url;
    try {
      url = new URL(link.href, window.location.href);
    } catch { return; }
    if (url.protocol !== "https:" && url.protocol !== "http:") return;
    event.preventDefault();
    pending = url.href;
    const label = link.textContent.trim() || "Selected page";
    destination.textContent = label + " — " + url.host;
    if (!dialog.open) dialog.showModal();
  });

  function openChoice(asWindow) {
    if (!pending) return;
    const url = pending;
    pending = null;
    dialog.close();
    // The browser makes the final tab/window decision. This is called from
    // the user's button click, not an effect or delayed callback.
    const features = asWindow ?
      "noopener,noreferrer,popup=yes,width=1180,height=820" :
      "noopener,noreferrer";
    window.open(url, "_blank", features);
  }
  tab.addEventListener("click", () => openChoice(false));
  windowButton.addEventListener("click", () => openChoice(true));
  cancel.addEventListener("click", () => {
    pending = null;
    dialog.close();
  });
  dialog.addEventListener("close", () => { pending = null; });
})();
