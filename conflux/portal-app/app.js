"use strict";
const pages=[...document.querySelectorAll(".panel")];
function show(id){pages.forEach(p=>p.hidden=p.id!==id);document.querySelectorAll("nav button").forEach(b=>{if(b.dataset.page===id)b.setAttribute("aria-current","page");else b.removeAttribute("aria-current")});}
document.querySelectorAll("[data-page]").forEach(b=>b.addEventListener("click",()=>show(b.dataset.page)));
document.querySelectorAll("[data-go]").forEach(b=>b.addEventListener("click",()=>show(b.dataset.go)));
const nodes=[["Medio","Balance & welcome","#e5c4a5"],["Ratio","Precision & craft","#b9c4e5"],["Nexus","Continuity & community","#e4b3ce"],["Specula","Observation & evidence","#c5c7d9"],["Limen","Thresholds & interpretation","#9ed6c7"]];
for(const [name,role,color] of nodes){const card=document.createElement("article");card.className="card";const wrap=document.createElement("div");wrap.className="node";const orb=document.createElement("div");orb.className="orb";orb.style.background=color;orb.setAttribute("aria-hidden","true");const words=document.createElement("div");const title=document.createElement("strong");title.textContent=name;const small=document.createElement("small");small.textContent=role+" · chibi pending";words.append(title,small);wrap.append(orb,words);card.append(wrap);document.querySelector("#node-list").append(card);}

let token="";
async function refresh(){
  const target=document.querySelector("#app-list");
  try{
    const response=await fetch("/api/status",{cache:"no-store"});
    if(!response.ok)throw Error("status");
    const data=await response.json();
    token=data.launch_token;
    target.replaceChildren();
    for(const app of data.apps){
      const card=document.createElement("article");card.className="card";
      const title=document.createElement("h3");title.textContent=app.name;
      const status=document.createElement("p");
      status.textContent=app.action==="launch"?"Installed and ready to launch":app.action==="download"?"Available to download · not registered locally":app.action==="open"?"Included with this Portal · opens in a browser tab":"Coming soon · no published download";
      const button=document.createElement("button");button.className="action";
      button.textContent=app.action==="launch"?"Launch":app.action==="download"?"Download":app.action==="open"?"Open":"Coming Soon";
      button.disabled=app.action==="coming-soon";
      button.addEventListener("click",async()=>{
        if(app.action==="open"){
          if(app.open_url)window.open(app.open_url,"_blank","noopener,noreferrer");
          return;
        }
        if(app.action==="download"){
          // Fixed, verified project release URLs only; no arbitrary user-supplied links.
          if(app.download_url)window.open(app.download_url,"_blank","noopener,noreferrer");
          return;
        }
        if(app.action!=="launch")return;
        button.disabled=true;
        try{
          const r=await fetch("/api/launch",{method:"POST",headers:{"Content-Type":"application/json","X-Conflux-Token":token},body:JSON.stringify({id:app.id})});
          const out=await r.json();
          status.textContent=r.ok?"Launch requested. Check the application window.":"Launch failed: "+out.error;
        }catch{status.textContent="Launch request failed."}
        finally{button.disabled=false;}
      });
      card.append(title,status,button);target.append(card);
    }
  }catch{target.textContent="Local portal service unavailable.";}
}
refresh();
