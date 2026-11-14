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

/* Existing service media storage updater. Independent of the new installer:
 * a Git update never touches user Quadlets, and this section requires its own
 * explicit preview, checkbox and native confirmation. */
(() => {
  const get = id => document.getElementById(id);
  const service = get("mirror-storage-service"), target = get("mirror-storage-target");
  const folder = get("mirror-storage-folder"), browse = get("mirror-storage-browse");
  const preview = get("mirror-storage-preview"), review = get("mirror-storage-plan");
  const approve = get("mirror-storage-approve"), apply = get("mirror-storage-apply");
  const status = get("mirror-storage-status");
  if (![service,target,folder,browse,preview,review,approve,apply,status].every(Boolean)) return;
  const local = window.location.hostname === "127.0.0.1";
  const choices = {
    jellyfin: [["/media","/media · videos"]],
    kavita: [["/books","/books · books"],["/comics","/comics · comics"],
             ["/manga","/manga · manga"]],
    navidrome: [["/music","/music · music"]]
  };
  let planToken = "";
  const say = message => { status.textContent = message; };
  const row = (parent, tag, message) => {
    const el = document.createElement(tag);
    el.textContent = String(message);
    parent.append(el);
    return el;
  };
  const reset = () => {
    planToken = "";
    approve.checked = false;
    apply.disabled = true;
    preview.replaceChildren();
  };
  const updateDestinations = () => {
    target.replaceChildren();
    for (const [value,label] of choices[service.value] || []) {
      const opt = document.createElement("option");
      opt.value = value;
      opt.textContent = label;
      target.append(opt);
    }
    reset();
  };
  async function request(route, payload) {
    const r = await fetch("/api/status", {cache:"no-store"});
    if (!r.ok) throw Error("Portal session unavailable");
    const token = (await r.json()).launch_token;
    const result = await fetch(route, {
      method:"POST",
      headers:{"Content-Type":"application/json","X-Conflux-Token":token},
      body:JSON.stringify(payload)
    });
    const data = await result.json();
    if (!result.ok) throw Error(data.error || "Storage action declined");
    return data;
  }
  service.addEventListener("change", updateDestinations);
  target.addEventListener("change", reset);
  folder.addEventListener("input", reset);
  updateDestinations();
  if (!local) {
    for (const control of [service,target,folder,browse,review,approve,apply]) {
      control.disabled = true;
    }
    say("Storage changes are available only at http://127.0.0.1:8765 on the Bazzite desktop.");
    return;
  }
  browse.addEventListener("click", async () => {
    reset();
    browse.disabled = true;
    say("Choose a directory in the native Bazzite folder picker...");
    try {
      const data = await request("/api/services/storage/browse", {});
      if (!data.cancelled && data.folder) {
        folder.value = data.folder;
        say("Folder selected. Preview it to verify that the external drive is mounted.");
      } else {
        say(data.detail || "No folder selected. You can paste its absolute path from Dolphin.");
      }
    } catch (err) {
      say("Folder selection failed: " + err.message);
    } finally { browse.disabled = false; }
  });
  review.addEventListener("click", async () => {
    reset();
    if (!folder.value.trim()) { say("Choose or enter a mounted media folder first."); return; }
    review.disabled = true;
    say("Inspecting the existing Quadlet, source filesystem, and proposed mount line...");
    try {
      const data = await request("/api/services/storage/plan", {
        service:service.value, destination:target.value, host_folder:folder.value.trim()
      });
      row(preview, "h3", "Proposed update for " + data.service);
      row(preview, "p", "Current media source: " + data.current_host_folder);
      row(preview, "p", "New media source: " + data.new_host_folder);
      row(preview, "p", "Mounted at: " + data.mount.mount_point +
          " (" + data.mount.filesystem + ")");
      row(preview, "p", "Will write: " + data.preview);
      row(preview, "p", "Existing account, cache, databases, and other Quadlet settings stay in place.");
      row(preview, "p", "A backup of the old Quadlet is saved before updating. If running, only this service is restarted.");
      planToken = data.will_change ? (data.plan_token || "") : "";
      say(data.will_change ? "Review the proposal, then approve the selected-service change below." :
          "This media source is already configured. Nothing needs changing.");
    } catch (err) { say("Preview blocked: " + err.message); }
    finally { review.disabled = false; }
  });
  approve.addEventListener("change", () => {
    apply.disabled = !planToken || !approve.checked;
  });
  apply.addEventListener("click", async () => {
    if (!planToken || !approve.checked) return;
    const selected = planToken;
    reset();
    review.disabled = true;
    say("Confirm this exact mount change in the native Bazzite desktop dialog.");
    try {
      const result = await request("/api/services/storage/apply", {
        plan_token:selected, explicit_confirmation:"APPLY READ-ONLY MEDIA MOUNT"
      });
      row(preview, "h3", "Mount update applied");
      row(preview, "p", result.service + ": " + result.host_folder +
          " → " + result.destination);
      row(preview, "p", "Original Quadlet backup: " + result.unit_backup);
      row(preview, "p", result.restarted ?
          "The selected service was restarted; check the library in its browser UI." :
          "The service was stopped and remains stopped. Its updated mount will be used at next start.");
      say("Configuration updated without reinstalling the app or moving media. Test a sample file.");
    } catch (err) {
      say("Update stopped: " + err.message + " Check logs and try a fresh preview.");
    } finally { review.disabled = false; }
  });
})();
