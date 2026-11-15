"use strict";
(() => {
  const $=id=>document.getElementById(id);
  const rooms=new Set(["home","apps","downloads","vos","library","nodes","tour","soundtrack","philosophy","about-arch","guide","service-setup","studio","updates"]);
  const log=$("assistant-log"),provider=$("assistant-provider"),agent=$("assistant-agent");
  let token="",room="home",history=[],busy=false;
  function note(msg){$("assistant-connection").textContent=msg}
  function notify(msg){$("connection-help").textContent=msg}
  function bubble(role,content){
    const e=document.createElement("div");
    e.className="bubble "+role;
    e.textContent=content;
    log.append(e);
    log.scrollTop=log.scrollHeight;
  }
  function clear(){
    history=[];
    log.replaceChildren();
    bubble("system","Read-only. The model cannot inspect your files or change your project.");
  }
  async function post(path,body){
    if(!token)throw Error("Portal session not available.");
    const r=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json","X-Conflux-Token":token},body:JSON.stringify(body)});
    const data=await r.json();
    if(!r.ok)throw Error(data.error||"Request failed.");
    return data;
  }
  async function refresh(){
    try {
      const [c,a]=await Promise.all([
        fetch("/api/connections/status",{cache:"no-store"}).then(r=>r.json()),
        fetch("/api/assistant/status",{cache:"no-store"}).then(r=>r.json())
      ]);
      const chat=c.chatgpt||{},git=c.github||{};
      $("chatgpt-state").textContent=chat.connected?"Connected":"Not connected";
      $("chatgpt-state").classList.toggle("connected",!!chat.connected);
      $("disconnect-chatgpt").hidden=!chat.connected;
      $("chatgpt-details").textContent=chat.connected?(chat.email||"ChatGPT account")+" · Plan authorized":
        chat.ready?"Continue in a new tab; no API key required.":
        "Optional PyJWT[crypto] dependency required on the Portal host.";
      $("github-state").textContent=git.connected?"Connected":"Not connected";
      $("github-state").classList.toggle("connected",!!git.connected);
      $("disconnect-github").hidden=!git.connected;
      $("github-details").textContent=git.connected?(git.login||"GitHub account")+" · Chat cannot change repositories":
        git.configured?"Authorize the registered GitHub App in a new tab.":
        "GitHub App client ID/secret must be configured locally first.";
      $("connect-github").disabled=!git.configured;
      if(provider.value==="chatgpt")
        note(chat.connected?"Connected to your ChatGPT plan.":"Connect ChatGPT above to chat without an API key.");
      else if(provider.value==="openai")
        note(a.openai?.configured?"OpenAI API key available. Separate charges may apply.":"No API key configured. Use ChatGPT account or Ollama.");
      else note("Local Ollama requires a running model server.");
      return c;
    }catch {note("Could not inspect local provider status.");return {};}
  }
  async function connect(kind){
    const tab=window.open("about:blank","_blank");
    notify("Preparing "+kind+" authorization…");
    try {
      const result=await post("/api/connections/start",{provider:kind});
      if(!/^https:\/\/(auth\.openai\.com|github\.com)\//.test(result.url||""))
        throw Error("Unexpected authorization destination.");
      if(tab)tab.location.href=result.url;
      else{
        const link=document.createElement("a");
        link.href=result.url;link.target="_blank";link.rel="noopener noreferrer";
        link.textContent="Open "+kind+" authorization";
        $("connection-help").replaceChildren(link);
      }
      notify("Complete authorization in the new tab, then return here.");
      for(let n=0;n<90;n++){
        await new Promise(resolve=>setTimeout(resolve,1600));
        const state=await refresh();
        if(state[kind]?.connected){notify(kind+" connected successfully.");return;}
        if(tab?.closed && n>2)break;
      }
      notify("Connection not confirmed; try again if needed.");
    }catch(e){if(tab&&!tab.closed)tab.close();notify(e.message);}
  }
  $("connect-chatgpt").addEventListener("click",()=>connect("chatgpt"));
  $("connect-github").addEventListener("click",()=>connect("github"));
  for(const kind of ["chatgpt","github"]){
    $("disconnect-"+kind).addEventListener("click",async()=>{
      if(!confirm("Disconnect "+kind+" locally?"))return;
      try {
        const result=await post("/api/connections/sign-out",{provider:kind});
        notify(result.note);clear();await refresh();
      }catch(e){notify(e.message);}
    });
  }
  $("connections-toggle").addEventListener("click",()=>{
    const box=$("connection-list");box.hidden=!box.hidden;
    $("connections-toggle").textContent=box.hidden?"Show":"Hide";
    $("connections-toggle").setAttribute("aria-expanded",String(!box.hidden));
  });
  $("assistant-clear").addEventListener("click",clear);
  provider.addEventListener("change",()=>{clear();refresh();});
  agent.addEventListener("change",clear);
  $("assistant-form").addEventListener("submit",async event=>{
    event.preventDefault();
    if(busy)return;
    const message=$("assistant-message").value.trim();
    if(!message||message.length>1500)return;
    const before=history.slice(-4);
    bubble("user",message);$("assistant-message").value="";
    busy=true;$("assistant-send").disabled=true;
    note("Contacting selected model…");
    try{
      const response=await post("/api/assistant/chat",{provider:provider.value,agent:agent.value,room,message,history:before});
      bubble("assistant",response.reply);
      history.push({role:"user",content:message},{role:"assistant",content:response.reply.slice(0,900)});
      history=history.slice(-4);
      note("Read-only reply from "+provider.value+".");
    }catch(e){bubble("system",e.message);await refresh();}
    finally{busy=false;$("assistant-send").disabled=false;$("assistant-message").focus();}
  });
  $("assistant-message").addEventListener("keydown",event=>{
    if(event.key==="Enter"&&!event.shiftKey){event.preventDefault();$("assistant-form").requestSubmit();}
  });
  // The only editing action available to a model is a *proposal*.
  // A human sees the complete bounded CSS diff and separately authorizes Git.
  let pendingChange=null,editing=false;
  const editStatus=$("change-status");
  function editNote(text){editStatus.textContent=text}
  function clearProposal(){
    pendingChange=null;
    $("change-review").hidden=true;
    $("change-publish").disabled=true;
    $("change-review-link").hidden=true;
  }
  $("change-file").addEventListener("change",clearProposal);
  provider.addEventListener("change",clearProposal);
  agent.addEventListener("change",clearProposal);
  $("change-share").addEventListener("change",clearProposal);
  $("change-propose").addEventListener("click",async()=>{
    if(busy||editing)return;
    const instruction=$("assistant-message").value.trim();
    if(instruction.length<5){
      editNote("Describe the change in the message field first.");
      return;
    }
    if(!$("change-share").checked){
      editNote("Explicitly approve sharing the chosen CSS source before proceeding.");
      return;
    }
    const selected=$("change-file").value;
    if(!selected){editNote("Select a supported CSS file.");return;}
    editing=true;clearProposal();
    $("change-propose").disabled=true;
    editNote("Asking "+provider.value+" to propose one bounded CSS replacement…");
    try{
      const result=await post("/api/changes/propose",{
        instruction,file:selected,provider:provider.value,agent:agent.value,
        approve_share:true
      });
      pendingChange=result;
      $("change-target").textContent=result.repository+" · "+result.file+
        " · HEAD "+result.base+" · proposed by "+result.agent;
      $("change-diff").textContent=result.diff;
      $("change-review").hidden=false;
      $("change-publish").disabled=false;
      editNote("Diff prepared in chat. No files changed or pushed. Read it before approval.");
      bubble("system","Proposed a CSS edit for "+result.file+
        ". Open the edit section to inspect the diff before any Git operation.");
    }catch(e){editNote("No change prepared: "+e.message);}
    finally{editing=false;$("change-propose").disabled=false;}
  });
  $("change-publish").addEventListener("click",async()=>{
    if(!pendingChange||editing)return;
    const expected="PUSH REVIEW TO "+pendingChange.repository;
    const confirmText=window.prompt("After reviewing the diff, type the EXACT text below to push a new Git review branch (not merge):\n"+expected,"");
    if(confirmText!==expected){editNote("Publication cancelled. No Git changes made.");return;}
    editing=true;$("change-publish").disabled=true;
    editNote("Creating an isolated Git review branch and pushing the approved edit…");
    try{
      const result=await post("/api/changes/publish",{
        ticket:pendingChange.ticket,confirmation:confirmText
      });
      pendingChange=null;
      const url=result.pr_url||result.compare_url;
      const link=$("change-review-link");
      link.href=url;
      link.textContent=result.pr_created?"Open draft pull request":"Open Git compare and create PR";
      link.hidden=false;
      editNote(result.pr_created?
        "A draft PR was created. Review its tests and merge via Updates & Setup when ready.":
        "A review branch was pushed; open the compare link to create a PR. "+
        (result.pr_note||""));
      bubble("system","Git review branch pushed: "+result.repository+" / "+result.branch+
        ". No merge or update performed.");
    }catch(e){editNote("Git publication stopped: "+e.message);}
    finally{editing=false;}
  });
  async function loadEditableFiles(){
    try{
      const res=await fetch("/api/changes/files",{cache:"no-store"});
      if(!res.ok)throw Error("File list unavailable.");
      const data=await res.json();
      const select=$("change-file");
      select.replaceChildren();
      for(const f of data.files){
        const option=document.createElement("option");
        option.value=f.path;
        option.textContent=f.label+" · "+f.path.split("/").pop();
        select.append(option);
      }
      editNote("CSS-only pilot. Other Portal code changes require a later sandboxed editor.");
    }catch(e){editNote(e.message);}
  }
  window.addEventListener("message",event=>{
    if(event.origin!==location.origin)return;
    if(event.data?.type==="conflux-room"&&rooms.has(event.data.room)){
      room=event.data.room;$("room-label").textContent=room.replaceAll("-"," ");
    }
  });
  (async()=>{
    try{
      const r=await fetch("/api/status",{cache:"no-store"});
      token=(await r.json()).launch_token||"";
    }catch{notify("Local Portal session unavailable.");}
    clear();await refresh();await loadEditableFiles();
    if(window.parent!==window)window.parent.postMessage({type:"conflux-assistant-ready"},location.origin);
  })();
})();
