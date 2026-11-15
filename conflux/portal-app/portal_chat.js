"use strict";
// The Portal owns only the open/close surface; chat and OAuth live in /assistant.
(() => {
  const dock=document.getElementById("assistant-dock");
  const toggle=document.getElementById("assistant-dock-toggle");
  const nav=document.getElementById("assistant-open-nav");
  const iframe=document.getElementById("assistant-iframe");
  if(!dock||!toggle||!nav||!iframe)return;
  function sendRoom(){
    const room=document.body.dataset.view||"home";
    iframe.contentWindow?.postMessage({type:"conflux-room",room},location.origin);
  }
  function show(open){
    dock.hidden=!open;
    toggle.setAttribute("aria-expanded",String(open));
    nav.setAttribute("aria-expanded",String(open));
    if(open){sendRoom();document.getElementById("assistant-close").focus();}
  }
  toggle.addEventListener("click",()=>show(dock.hidden));
  nav.addEventListener("click",()=>show(true));
  document.getElementById("assistant-close").addEventListener("click",()=>show(false));
  window.addEventListener("message",event=>{
    if(event.origin===location.origin&&event.data?.type==="conflux-assistant-ready")sendRoom();
  });
  document.querySelectorAll("[data-page],[data-go]").forEach(b=>b.addEventListener("click",()=>{
    if(!dock.hidden)sendRoom();
  }));
  document.addEventListener("keydown",event=>{if(event.key==="Escape"&&!dock.hidden)show(false);});
})();