"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),vm=require("node:vm");
const js=fs.readFileSync("../../docs/video_tour.js","utf8");
const html=fs.readFileSync("index.html","utf8");
assert(html.includes('data-page="tour"'));
assert(html.includes('data-catalog-url="/video-tour/catalog.json"'));
class El {
  constructor(tag=""){this.tag=tag;this.children=[];this.dataset={};this.handlers={};this.textContent="";this.attrs={};this.href="";}
  append(...x){this.children.push(...x);}
  replaceChildren(...x){this.children=[...x];}
  addEventListener(event,fn){this.handlers[event]=fn;}
  setAttribute(k,v){this.attrs[k]=v;}
  click(){this.handlers.click?.();}
}
const root=new El("root");root.dataset={catalogUrl:"/video-tour/catalog.json",autoload:"false"};
const status=new El("status"),button=new El("button");
const doc={
  querySelector(s){return s==="#video-tour-list"?root:s==="#video-tour-status"?status:
    s==='button[data-page="tour"]'?button:null;},
  createElement(type){return new El(type);},
  createDocumentFragment(){return new El("fragment");}
};
const tag="conflux-portal-tour-v0.1",prefix="https://github.com/MedioCritasVT/CrystalCove/releases/download/"+tag+"/";
const clips=["01-threshold-welcome.mp4","02-ledger-workspace.mp4","03-game-first-launch.mp4","04-node-companions.mp4"];
let requests=0;
const fetch=async url=>{
 requests++;
 if(url==="/video-tour/catalog.json")return {ok:true,json:async()=>({
   schema:"conflux.portal.video-tour.v0.1",release_tag:tag,
   items:clips.map((filename,i)=>({id:String(i),title:"Clip "+(i+1),description:"Preview "+i,filename,seconds:13}))
 })};
 if(url.includes("/releases/tags/"))return {ok:true,json:async()=>({
   tag_name:tag,draft:false,
   assets:[
    {name:clips[0],size:240663,browser_download_url:prefix+clips[0]},
    {name:clips[1],size:300000,browser_download_url:"https://untrusted.invalid/"+clips[1]},
    {name:clips[2],size:0,browser_download_url:prefix+clips[2]}
   ]
 })};
 throw Error("unexpected URL "+url);
};
vm.runInNewContext(js,{document:doc,fetch});
const tick=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
 assert.equal(requests,0,"No remote request until Video Tour is opened");
 button.click();
 await tick();await tick();await tick();
 assert.equal(root.children.length,1,"Replace with document fragment");
 const cards=root.children[0].children;
 assert.equal(cards.length,4);
 const links=cards.flatMap(c=>c.children.filter(e=>e.tag==="a"));
 assert.equal(links.length,1,"only actually published official MP4 is linkable");
 assert.equal(links[0].href,prefix+clips[0]);
 assert.equal(links[0].target,"_blank");
 assert.equal(links[0].rel,"noopener noreferrer");
 assert(status.textContent.includes("1 of 4"),"status must not claim all videos published");
 console.log("Video Tour: deferred source checking, 4 cards, only official release asset links OK");
})().catch(e=>{console.error(e);process.exitCode=1;});
