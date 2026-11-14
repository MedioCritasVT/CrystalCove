"use strict";
// Installation controls are only available from the desktop's loopback Portal.
(() => {
  const byId = id => document.getElementById(id);
  const check = byId("mirror-check"), install = byId("mirror-install");
  const approve = byId("mirror-approve"), status = byId("mirror-status");
  const output = byId("mirror-report");
  if (!check || !install || !approve || !status || !output) return;
  let token = "";
  const local = window.location.hostname === "127.0.0.1";
  const message = txt => { status.textContent = txt; };
  function reset() { token = ""; approve.checked = false; install.disabled = true; }
  function add(node, tag, value) {
    const el = document.createElement(tag);
    el.textContent = String(value);
    node.append(el);
    return el;
  }
  async function call(route, body) {
    const response = await fetch("/api/status", {cache:"no-store"});
    if (!response.ok) throw Error("Portal session unavailable");
    const session = await response.json();
    const result = await fetch(route, {
      method:"POST",
      headers:{"Content-Type":"application/json", "X-Conflux-Token":session.launch_token},
      body:JSON.stringify(body)
    });
    const payload = await result.json();
    if (!result.ok) throw Error(payload.error || "Request declined");
    return payload;
  }
  function render(data) {
    output.replaceChildren();
    add(output, "h3", "Bazzite system inspection");
    add(output, "p", "Host: " + data.host);
    const checks = add(output, "ul", "");
    for (const [key,value] of Object.entries(data.checks || {}))
      add(checks, "li", key.replaceAll("_", " ") + ": " + (value ? "ready" : "needs attention"));
    const ports = add(output, "ul", "");
    for (const [name,service] of Object.entries(data.services || {}))
      add(ports, "li", name + ": " + service.local_url +
          " (optional Tailscale HTTPS port " + service.optional_tailscale_https_port + ")" +
          (!service.port_free ? " — port occupied" : "") +
          (service.unit_conflict || service.state_conflict ? " — files already exist" : ""));
    add(output, "p", data.ready ? "New installation is available for approval." :
        "Installation is blocked. No packages or services have been changed.");
  }
  if (!local) {
    check.disabled = true; reset();
    message("View-only over Tailscale. Open http://127.0.0.1:8765 on the Bazzite desktop to install.");
    return;
  }
  check.addEventListener("click", async () => {
    reset(); check.disabled = true;
    message("Checking prerequisites and local ports without making changes…");
    try {
      const data = await call("/api/services/check", {});
      render(data);
      token = data.ready ? (data.plan_token || "") : "";
      message(token ? "Review the proposed installation, then tick the approval box." :
              "Check blocked installation; see the report above.");
    } catch (error) { message("Check failed: " + error.message); }
    finally { check.disabled = false; }
  });
  approve.addEventListener("change", () => {
    install.disabled = !token || !approve.checked;
  });
  install.addEventListener("click", async () => {
    if (!token || !approve.checked || !local) return;
    const selected = token; reset(); check.disabled = true;
    message("A second confirmation will appear on the Bazzite desktop. Approve it only if you are ready to download and start NEW services.");
    try {
      const result = await call("/api/services/install", {
        plan_token:selected, explicit_confirmation:"INSTALL NEW BAZZITE MIRROR"
      });
      output.replaceChildren();
      add(output, "h3", "Installation result");
      for (const [name,state] of Object.entries(result.services || {}))
        add(output, "p", name + ": " + (state.started ? "started" : "needs review") + " — " + state.url);
      message(result.all_started ? "New empty services started. Complete each app's local first-run setup; backups and Tailscale routes are separate." :
              "Some services need manual review. Existing libraries were not imported or replaced.");
    } catch (error) { message("Stopped: " + error.message + " Run a fresh check before trying again."); }
    finally { check.disabled = false; }
  });
})();
