"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const catalog = JSON.parse(fs.readFileSync("../video-tour/catalog.json", "utf8"));
const readme = fs.readFileSync("../../README.md", "utf8");
const portal = fs.readFileSync("index.html", "utf8");
const website = fs.readFileSync("../../docs/index.html", "utf8");
const prefix = "https://github.com/MedioCritasVT/CrystalCove/releases/download/conflux-portal-tour-v0.1/";
assert.equal(catalog.status,"four_short_clips_published_github_release");
assert.equal(catalog.items.length,4);
for (const entry of catalog.items) {
  const url = prefix + entry.filename;
  assert.equal(entry.publication_status,"published");
  assert.equal(entry.published_url,url);
  assert(Number.isSafeInteger(entry.bytes) && entry.bytes>0);
  for(const [label,page] of [["README",readme],["Portal",portal],["website",website]]) {
    assert(page.includes(url),label+" is missing direct "+entry.filename+" link");
  }
}
for (const asset of ["01-threshold-preview.gif","02-creative-workspace-preview.gif",
                     "03-gameplay-preview.gif","04-library-music-preview.gif",
                     "05-node-companions.png"]) {
  const file="../../docs/previews/"+asset;
  const bytes=fs.readFileSync(file);
  assert(bytes.length>8000 && bytes.length<1000000,asset+" must be a lightweight real image");
  assert(readme.includes("docs/previews/"+asset),"README does not embed "+asset);
  if (asset.endsWith(".gif")) assert.equal(bytes.toString("ascii",0,3),"GIF",asset+" not a GIF");
  else assert.equal(bytes.subarray(1,4).toString("ascii"),"PNG",asset+" not PNG");
}

class El {
  constructor(tag=""){this.tag=tag;this.children=[];this.dataset={};this.handlers={};this.textContent="";}
  append(...elements){this.children.push(...elements);}
  replaceChildren(...elements){this.children=elements;}
  addEventListener(name,fn){this.handlers[name]=fn;}
  setAttribute(key,value){this[key]=value;}
}
const root=new El("root");root.dataset={catalogUrl:"/video-tour/catalog.json",autoload:"false"};
const status=new El("status"),button=new El("button");
const document={
  querySelector(s){return s==="#video-tour-list"?root:s==="#video-tour-status"?status:
    s==='button[data-page="tour"]'?button:null;},
  createElement:t=>new El(t),
  createDocumentFragment:()=>new El("fragment")
};
let apiCalls=0;
const fetch=async url=>{
  if(url==="/video-tour/catalog.json")return {ok:true,json:async()=>catalog};
  if(url.includes("/releases/tags/")){apiCalls++;throw Error("Simulated GitHub API outage");}
  throw Error("Unexpected URL "+url);
};
vm.runInNewContext(fs.readFileSync("../../docs/video_tour.js","utf8"),{document,fetch});
const tick=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
  assert.equal(apiCalls,0,"No Release API call before visiting Video Tour");
  button.handlers.click();
  await tick();await tick();await tick();
  assert.equal(root.children.length,1,"Tour should render a fragment");
  const cards=root.children[0].children;
  assert.equal(cards.length,4);
  const links=cards.flatMap(card=>card.children.filter(child=>child.tag==="a"));
  assert.equal(links.length,4,"Published links must remain usable during API outage");
  assert(links.every(link=>link.href.startsWith(prefix)));
  assert(links.every(link=>link.target==="_blank"));
  assert(status.textContent.includes("All four"),"Must recognize four published videos");
  console.log("Five README visuals and four resilient GitHub Video Tour links OK");
})().catch(e=>{console.error(e);process.exitCode=1;});
