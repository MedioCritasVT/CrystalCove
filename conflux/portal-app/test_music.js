"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const script = fs.readFileSync("music.js", "utf8");
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
  "soundtrack-versions","music-library-status","music-catalog"
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
const fakeFetch = async (url, options) => {
  calls.push({url, options});
  if (url !== "/soundtrack/catalog.json") throw Error("Unexpected network request");
  return {ok:true,json:async()=>({tracks:[
    {title:"Ritual in the Circuit",variants:[{id:"provided"}]},
    {title:"Sacrament of Oath",status:"source_files_not_received",
     variants:[{id:"v1",status:"missing"},{id:"v2",status:"missing"}]}
  ]})};
};
const fakeURL = {
  createObjectURL(file) {const url = "blob:local-" + (urls.length+1);urls.push({file,url});return url;},
  revokeObjectURL(url) {revoked.push(url);}
};
const window = {addEventListener(){}};
vm.runInNewContext(script, {document,window,URL:fakeURL,fetch:fakeFetch});
const tick = () => new Promise(resolve=>setTimeout(resolve,0));
(async()=>{
  await tick();
  const toggle = nodes["music-toggle"];
  const files = nodes["music-files"];
  const audio = nodes["music-audio"];
  assert.equal(toggle.textContent,"Music Off");
  assert.equal(toggle.attrs["aria-pressed"],"false");
  assert.equal(audio.playCount,0,"never autoplay when page opens");
  assert.equal(nodes["music-catalog"].children.length,2);
  assert.equal(calls.length,1);
  // User-selected files stay local and versions are grouped by title.
  files.files = [
    {name:"Sacrament of Oath.mp3",size:300,lastModified:1},
    {name:"Sacrament of Oath (2).mp3",size:312,lastModified:2},
    {name:"Ritual in the Circuit.mp3",size:300,lastModified:3},
  ];
  files.handlers.change();
  assert.equal(nodes["music-select"].children.length,2,"versions must share a composition");
  assert.equal(nodes["soundtrack-versions"].children.length,2);
  assert.equal(nodes["music-version"].children.length,2);
  assert.equal(audio.playCount,0,"selecting files must not start music");
  assert.equal(toggle.textContent,"Music Off");
  await toggle.click();
  await tick();
  assert.equal(toggle.textContent,"Music On");
  assert.equal(audio.paused,false);
  const prior = audio.src;
  nodes["music-version"].value = "1";
  nodes["music-version"].handlers.change();
  await tick();
  assert.notEqual(audio.src,prior,"different variants must be independently playable");
  assert.equal(nodes["music-version"].children.length,2);
  toggle.click();
  assert.equal(toggle.textContent,"Music Off");
  assert.equal(audio.paused,true);
  assert.equal(calls.length,1,"local music must never upload to a server");
  assert.equal(urls.length,3);
  console.log("Soundtrack UI smoke: silent startup, local files, variants, toggle and no uploads OK");
})().catch(e=>{console.error(e);process.exitCode=1;});
