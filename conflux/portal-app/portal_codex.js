"use strict";
/*
 * Genuine Codex app-server client. All RPCs stay behind the local Portal.
 * No model runs until Start; all output is rendered via textContent.
 */
(() => {
  const $ = id => document.getElementById(id);
  const panel = $("assistant-dock"), toggle = $("assistant-dock-toggle");
  const nav = $("assistant-open-nav"), log = $("codex-transcript");
  if (!panel || !toggle || !nav || !log) return;

  const KEY = "conflux-codex-thread-v1";
  let token = "", ready = false, connected = false, busy = false;
  let editing = false, installed = false, seq = 0, polling = false;
  let thread = null, currentApproval = null, authenticated = false;
  const bubbles = new Map();
  const approvalQueue = [];
  const send = $("codex-send"), message = $("codex-message");

  function notice(text) { $("codex-status").textContent = text; }
  function badge(text) { $("codex-indicator").textContent = text; }
  function addMessage(role, content) {
    const node = document.createElement("div");
    node.className = "codex-message " + role;
    node.textContent = content;
    log.append(node);
    log.scrollTop = log.scrollHeight;
    return node;
  }
  function updateControls() {
    message.disabled = !ready || !authenticated || busy;
    send.disabled = message.disabled;
    $("codex-start").hidden = ready;
    $("codex-login").hidden = !ready || authenticated;
    $("codex-new").hidden = !ready || !authenticated;
    $("codex-new").disabled = busy;
    $("codex-edits").hidden = !ready || !authenticated;
    $("codex-edits").disabled = busy;
    $("codex-edits").textContent = editing ? "Disable edits" : "Enable edits";
    $("codex-interrupt").hidden = !busy;
    badge(!installed ? "Codex CLI not installed" :
      !ready ? "Codex is not running" :
      !authenticated ? "Sign in to Codex" :
      busy ? "Codex working…" : "Codex ready" + (editing ? " · edits enabled" : " · read-only"));
  }
  async function post(path, data={}) {
    if (!token) throw Error("Local Portal session not available.");
    const response = await fetch(path, {
      method: "POST",
      headers: {"Content-Type":"application/json","X-Conflux-Token":token},
      body: JSON.stringify(data)
    });
    const result = await response.json();
    if (!response.ok) throw Error(result.error || "Codex request was rejected.");
    return result;
  }
  async function get(path) {
    const res = await fetch(path, {cache:"no-store"});
    const data = await res.json();
    if (!res.ok) throw Error(data.error || "Could not reach local Codex.");
    return data;
  }
  function approvalNext() {
    if (currentApproval || !approvalQueue.length) return;
    currentApproval = approvalQueue.shift();
    $("codex-approval").hidden = false;
    const a = currentApproval;
    $("codex-approval-message").textContent = [a.description || "Codex wants to perform an operation.",
      a.reason || "", a.cwd ? "Working directory: " + a.cwd : ""].filter(Boolean).join("\n");
  }
  function resolveApproval(id) {
    if (currentApproval && currentApproval.request_id === id) {
      currentApproval = null;
      $("codex-approval").hidden = true;
      approvalNext();
    }
    for (let n=approvalQueue.length-1;n>=0;n--) {
      if (approvalQueue[n].request_id === id) approvalQueue.splice(n,1);
    }
  }
  async function approve(decision) {
    if (!currentApproval) return;
    const id = currentApproval.request_id;
    $("codex-approve").disabled = true;
    $("codex-decline").disabled = true;
    try {
      await post("/api/codex/approval", {request_id:id, decision});
      resolveApproval(id);
      addMessage("event","Permission " + (decision === "accept" ? "approved once." : "declined."));
    } catch(error) { notice(error.message); }
    finally {
      $("codex-approve").disabled = false;
      $("codex-decline").disabled = false;
    }
  }
  function processEvent(e) {
    if (e.kind === "delta") {
      const id = e.item_id || "current";
      let node = bubbles.get(id);
      if (!node) {node = addMessage("agent","");bubbles.set(id,node);}
      node.textContent = (node.textContent + (e.text || "")).slice(0,18000);
      log.scrollTop = log.scrollHeight;
    } else if(e.kind === "answer") {
      const id = e.item_id || "current";
      let node = bubbles.get(id);
      if (!node) node = addMessage("agent",e.text||"");
      else node.textContent = e.text || node.textContent;
      bubbles.set(id,node);
    } else if(e.kind === "approval") {
      approvalQueue.push(e);
      approvalNext();
    } else if(e.kind === "approval_resolved") {
      resolveApproval(e.request_id);
    } else if(e.kind === "turn_started") {
      busy = true;
      updateControls();
    } else if(e.kind === "turn_finished") {
      busy = false;
      updateControls();
      if (e.status !== "completed") addMessage("event","Codex turn " + e.status + (e.error? ": "+e.error:""));
      bubbles.clear();
      currentApproval = null; approvalQueue.length = 0;
      $("codex-approval").hidden = true;
      message.focus();
    } else if(e.kind === "new_thread") {
      thread = e.thread;
      try {localStorage.setItem(KEY,thread);} catch {}
    } else if(e.kind === "account_updated" || e.kind === "login_finished") {
      if (e.kind === "login_finished" && e.success === false) {
        addMessage("event","ChatGPT sign-in did not finish.");
      } else refreshAuth();
    } else if(e.kind === "activity" || e.kind === "notice") {
      addMessage("event",e.message || "Codex update");
    }
  }
  async function refreshAuth() {
    if (!ready) return;
    try {
      const result = await post("/api/codex/start");
      authenticated = !!result.authenticated;
      connected = !!result.running;
      if(result.thread) thread = result.thread;
      installed = !!result.installed;
      updateControls();
      if(authenticated) notice("Signed in to Codex. Conversation remains in this panel.");
    } catch(error) {notice(error.message);}
  }
  async function poll() {
    if (polling || panel.hidden || !ready) return;
    polling = true;
    try {
      const state = await get("/api/codex/events?since=" + seq);
      if (state.latest < seq) seq = 0;
      for(const event of state.events || []) {
        if (event.seq <= seq) continue;
        processEvent(event);
        seq = event.seq;
      }
      if (state.latest > seq) seq = state.latest;
      if(state.thread && state.thread !== thread) {
        thread = state.thread;
        try {localStorage.setItem(KEY,thread);} catch {}
      }
      ready = !!state.running;
      busy = !!state.busy;
      editing = !!state.editing;
      updateControls();
    } catch(error){notice(error.message);}
    finally{polling = false;}
  }
  async function startCodex() {
    $("codex-start").disabled = true;
    notice("Connecting to the locally installed Codex app-server…");
    try {
      let previous=null;
      try {previous=localStorage.getItem(KEY);}catch{}
      const state=await post("/api/codex/start",{resume: previous || undefined});
      ready=!!state.running;
      installed=!!state.installed;
      authenticated=!!state.authenticated;
      editing=!!state.editing;
      busy=!!state.busy;
      thread=state.thread || null;
      updateControls();
      if(!authenticated) notice("Sign in with ChatGPT once; the conversation will remain here.");
      else notice("Codex connected to this local checkout. Read-only until you explicitly enable edits.");
      poll();
    }catch(error){notice(error.message);addMessage("event",error.message);}
    finally{$("codex-start").disabled=false;updateControls();}
  }
  async function login() {
    // Open a blank tab in the trusted click, then navigate to Codex's own
    // provider authorization URL. No provider session is embedded here.
    const tab=window.open("about:blank","_blank");
    try {
      const result=await post("/api/codex/login");
      if(tab)tab.location.href=result.auth_url;
      else {
        const link=document.createElement("a");
        link.href=result.auth_url;link.target="_blank";link.rel="noopener noreferrer";
        link.textContent="Open ChatGPT authorization";
        addMessage("event","Your browser blocked the sign-in tab.");
        log.append(link);
      }
      notice("Complete the one-time sign-in on ChatGPT. Return here to keep coding inside the panel.");
    }catch(error){
      if(tab && !tab.closed)tab.close();
      notice(error.message);
    }
  }
  async function newConversation() {
    if(busy || !window.confirm("Start a fresh Codex conversation? Your existing Codex history remains in Codex."))return;
    try {
      const result=await post("/api/codex/new");
      thread=result.thread;
      try {localStorage.setItem(KEY,thread);}catch{}
      log.replaceChildren();
      bubbles.clear();
      notice("New Codex conversation ready. This is not the original ChatGPT Limen thread.");
    }catch(error){notice(error.message);}
  }
  async function edits() {
    if(busy)return;
    const allow=!editing;
    if(allow && !window.confirm("Let Codex modify files in the Portal's current checkout? Review changes before committing or pushing."))return;
    try {
      const result=await post("/api/codex/edits",{enabled:allow});
      editing=result.editing;updateControls();
      notice(editing?"Codex may modify files in this checkout. Review and approve requested escalations.":"Codex returned to read-only mode.");
    }catch(error){notice(error.message);}
  }
  async function submit(event) {
    event.preventDefault();
    if(!ready || !authenticated || busy)return;
    const text=message.value.trim();
    if(!text || text.length>2000)return;
    message.value="";
    addMessage("user",text);
    busy=true;updateControls();
    try {
      const result=await post("/api/codex/message",{message:text});
      if(result.thread) {
        thread=result.thread;
        try {localStorage.setItem(KEY,thread);}catch{}
      }
      notice(editing?"Codex is working with workspace edits enabled.":"Codex is working in read-only mode.");
    } catch(error){
      busy=false;updateControls();addMessage("event",error.message);
      notice(error.message);
    }
  }
  function open(visible) {
    panel.hidden=!visible;
    toggle.setAttribute("aria-expanded",String(visible));
    nav.setAttribute("aria-expanded",String(visible));
    if(visible) {
      poll();
      if(ready)message.focus();else $("codex-start").focus();
    } else toggle.focus();
  }
  toggle.addEventListener("click",()=>open(panel.hidden));
  nav.addEventListener("click",()=>open(true));
  $("assistant-close").addEventListener("click",()=>open(false));
  document.addEventListener("keydown",event=>{
    if(event.key==="Escape" && !panel.hidden)open(false);
  });
  $("codex-start").addEventListener("click",startCodex);
  $("codex-login").addEventListener("click",login);
  $("codex-new").addEventListener("click",newConversation);
  $("codex-edits").addEventListener("click",edits);
  $("codex-approve").addEventListener("click",()=>approve("accept"));
  $("codex-decline").addEventListener("click",()=>approve("decline"));
  $("codex-interrupt").addEventListener("click",async()=>{
    try{await post("/api/codex/interrupt");notice("Requested interruption.");}
    catch(error){notice(error.message);}
  });
  $("codex-form").addEventListener("submit",submit);
  message.addEventListener("keydown",event=>{
    if(event.key==="Enter"&&!event.shiftKey){
      event.preventDefault();$("codex-form").requestSubmit();
    }
  });
  (async()=>{
    try{
      token=(await get("/api/status")).launch_token || "";
      const s=await get("/api/codex/status");
      installed=!!s.installed;ready=!!s.running;busy=!!s.busy;
      editing=!!s.editing;thread=s.thread;
      updateControls();
      if(!installed)notice("Codex CLI is not installed. Updates & Setup links to the official installation guide; no installation is automatic.");
      if(ready)await refreshAuth();
    }catch(error){notice(error.message);}
    setInterval(()=>{if(!panel.hidden)poll();},900);
  })();
})();
