"use strict";
// Browser-free soundtrack regression checks. Real audio is never played in CI.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const html = fs.readFileSync("index.html", "utf8");
const script = fs.readFileSync("music.js", "utf8");
for (const id of ["music-toggle","music-zip","music-install-status",
                  "music-recheck","music-audio","soundtrack-downloads"]) {
  assert(html.includes('id="' + id + '"'), "missing UI element: " + id);
}
class Element {
  constructor(id = "") {
    this.id = id;
    this.handlers = {};
    this.children = [];
    this.textContent = "";
    this.value = "";
    this.disabled = false;
    this.paused = true;
    this.files = [];
    this.dataset = {};
    this.attrs = {};
    this.src = "";
    this.volume = 0;
    this.playCount = 0;
  }
  append(...items) {this.children.push(...items);}
  replaceChildren(...items) {this.children = [...items];}
  setAttribute(key, value) {this.attrs[key] = value;}
  removeAttribute(key) {delete this[key];}
  addEventListener(key, listener) {this.handlers[key] = listener;}
  click() {return this.handlers.click?.();}
  load() {}
  pause() {this.paused = true;this.handlers.pause?.();}
  async play() {this.playCount++;this.paused = false;this.handlers.play?.();}
}
const ids = [
  "music-audio","music-toggle","music-files","music-select","music-version",
  "music-prev","music-play","music-next","music-volume","music-status",
  "soundtrack-versions","music-library-status","music-catalog",
  "music-zip","music-recheck","music-install-status","soundtrack-downloads"
];
const nodes = Object.fromEntries(ids.map(id => [id, new Element(id)]));
nodes["music-volume"].value = "45";
const document = {
  querySelector(selector) {
    const result = nodes[selector.slice(1)];
    if (!result) throw Error("Missing music element " + selector);
    return result;
  },
  createElement(type) {return new Element(type);}
};
const calls = [];
const urls = [];
const revoked = [];
const remote = "https://github.com/MedioCritasVT/CrystalCove/releases/download/conflux-soundtrack-v0.1/";
let installed = false;
function library() {
  const sound = {
    tracks: [
      {id:"ritual",title:"Ritual in the Circuit",variants:[
        {id:"provided",filename:"Conflux-Ritual-in-the-Circuit.mp3",url: installed ?
          "/music/audio/Conflux-Ritual-in-the-Circuit.mp3" :
          remote+"Conflux-Ritual-in-the-Circuit.mp3",source:installed?"local":"published",
           download_url:remote+"Conflux-Ritual-in-the-Circuit.mp3"}]},
      {id:"sacrament",title:"Sacrament of Oath",variants:[
        {id:"take-1",filename:"Conflux-Sacrament-of-Oath-Take-1.mp3",
         url:remote+"Conflux-Sacrament-of-Oath-Take-1.mp3",source:"published"},
        {id:"take-2",filename:"Conflux-Sacrament-of-Oath-Take-2.mp3",
         url:remote+"Conflux-Sacrament-of-Oath-Take-2.mp3",source:"published"}]}
    ], available:3, local: installed ? 1:0, published: installed ? 2:3
  };
  return sound;
}
const fakeFetch = async (url, options) => {
  calls.push({url, options});
  if (url === "/api/music/library")
    return {ok:true,json:async()=>library()};
  if (url === "/api/status")
    return {ok:true,json:async()=>({launch_token:"local-test-token"})};
  if (url === "/api/music/install") {
    assert.equal(options.method, "POST");
    assert.equal(options.headers["X-Conflux-Token"], "local-test-token");
    assert(options.body, "upload body must be chosen by the user");
    installed = true;
    return {ok:true,json:async()=>({installed:7})};
  }
  if (url === "/soundtrack/catalog.json")
    return {ok:true,json:async()=>({tracks:[
      {title:"Ritual in the Circuit",variants:[{id:"provided"}]},
      {title:"Sacrament of Oath",variants:[{id:"take-1"},{id:"take-2"}]}
    ]})};
  throw Error("Unexpected network request "+url);
};
const fakeURL = {
  createObjectURL(file) {const url="blob:local-"+(urls.length+1);urls.push({file,url});return url;},
  revokeObjectURL(url) {revoked.push(url);}
};
const window = {addEventListener(){}};
vm.runInNewContext(script, {document,window,URL:fakeURL,fetch:fakeFetch});
const tick = () => new Promise(resolve=>setTimeout(resolve,0));
(async()=>{
  await tick();
  await tick();
  const toggle=nodes["music-toggle"],audio=nodes["music-audio"];
  assert.equal(toggle.textContent,"Music Off");
  assert.equal(toggle.attrs["aria-pressed"],"false");
  assert.equal(audio.playCount,0,"must not autoplay on page load");
  assert.equal(nodes["music-select"].children.length,2,
               "published tracks must be loaded automatically");
  assert.equal(nodes["music-version"].children.length,1);
  assert(audio.src.includes("Conflux-Ritual-in-the-Circuit.mp3"),
         "published audio URL must be preselected");
  assert(nodes["music-install-status"].textContent.includes("ready automatically"));
  assert.equal(nodes["music-catalog"].children.length,2);
  assert.equal(nodes["soundtrack-downloads"].children.length,2);
  const firstDownload = nodes["soundtrack-downloads"].children[0].children[1].children[1];
  assert.equal(firstDownload.textContent, "Download MP3");
  assert(firstDownload.href.startsWith(remote));
  assert.equal(calls.filter(c=>c.url==="/api/music/library").length,1);
  assert(!calls.some(c=>c.url==="/api/music/install"),"no implicit upload or install");

  await toggle.click();
  await tick();
  assert.equal(toggle.textContent,"Music On");
  assert.equal(audio.paused,false);
  nodes["music-select"].value="Sacrament of Oath";
  nodes["music-select"].handlers.change();
  await tick();
  assert.equal(nodes["music-version"].children.length,2);
  const first=audio.src;
  nodes["music-version"].value="1";
  nodes["music-version"].handlers.change();
  await tick();
  assert.notEqual(audio.src,first,"both Sacrament takes must remain selectable");
  toggle.click();
  assert.equal(toggle.textContent,"Music Off");
  assert.equal(audio.paused,true);

  // A ZIP is chosen only once. After installation the automatic library refreshes.
  nodes["music-zip"].files=[{name:"Conflux_Soundtrack_Release_v0_1.zip",size:30000000,\n    arrayBuffer:async()=>new ArrayBuffer(16)}];
  await nodes["music-zip"].handlers.change();
  await tick();
  assert(installed);
  assert(nodes["music-install-status"].textContent.includes("Installed and verified 7"));
  assert.equal(audio.playCount>=1,true);
  assert.equal(toggle.textContent,"Music Off");
  assert(calls.some(c=>c.url==="/api/music/install"));
  assert(calls.filter(c=>c.url==="/api/music/library").length>=2);
  // A restored/unreadable file fails before upload, with usable instructions.
  const uploadsBefore = calls.filter(c=>c.url==="/api/music/install").length;
  nodes["music-zip"].files=[{name:"restored.zip",size:30000000,
    arrayBuffer:async()=>{throw Error("NotReadableError");}}];
  await nodes["music-zip"].handlers.change();
  assert.equal(calls.filter(c=>c.url==="/api/music/install").length,uploadsBefore);
  assert(nodes["music-install-status"].textContent.includes("Downloads folder"));
  assert.equal(nodes["music-zip"].disabled,false);


  // Old manual file selection still works as an optional fallback.
  const files=nodes["music-files"];
  files.files=[
    {name:"Sacrament of Oath(1).mp3",size:300,lastModified:1},
    {name:"Sacrament of Oath (1)(1).mp3",size:312,lastModified:2}
  ];
  files.handlers.change();
  assert.equal(nodes["music-select"].children.length,1);
  assert.equal(nodes["music-version"].children.length,2);
  assert.equal(audio.playCount>=1,true);
  assert.equal(urls.length,2);
  console.log("Soundtrack UI: automatic release loading, no autoplay, two variants, one-time ZIP import, and local fallback OK");
})().catch(e=>{console.error(e);process.exitCode=1;});
