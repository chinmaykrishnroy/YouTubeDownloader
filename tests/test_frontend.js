const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const html = fs.readFileSync('static/index.html', 'utf8');
const script = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].at(-1)[1];
const elements = new Map();
const timers = [];
const players = [];
function element(id) {
  if (!elements.has(id)) elements.set(id, {
    innerHTML: '', style: {}, className: '',
    classList: {add() {}, remove() {}, contains() {return false;}},
    addEventListener() {}, querySelector() {return this.innerHTML.includes('ytIframePlayer') ? {} : null;},
  });
  return elements.get(id);
}
const context = vm.createContext({
  console, Set, JSON, Object, Math, AbortSignal,
  document: {getElementById: element, body: {style: {}}, addEventListener() {}},
  location: {protocol: 'https:', host: 'example.com', origin: 'https://example.com'},
  setInterval(callback) {timers.push(callback); return timers.length;}, clearInterval() {},
  setTimeout(callback) {return 1;}, clearTimeout() {},
  fetch: async () => ({ok: true, json: async () => ({jobs: []})}),
});
context.window = context;
context.addEventListener = () => {};
context.YT = {Player: function (id, options) {
  this.options = options;
  this.loads = [];
  this.loadVideoById = value => this.loads.push(value);
  this.playVideo = () => {};
  this.destroy = () => {this.destroyed = true;};
  players.push(this);
}};
context.WebSocket = class {
  static OPEN = 1;
  readyState = 1;
  addEventListener() {}
  send(value) {this.lastMessage = value;}
};
// Load the real application handlers without starting its page initialization.
vm.runInContext(script.split('/* ── Init Application ── */')[0], context);
vm.runInContext("updateMiniPlayState = () => {}; watchState = 'full'; activeVideo = {id: 'first'}; mountYouTubePlayer('first');", context);
players[0].options.events.onReady({target: players[0]});
vm.runInContext("mountYouTubePlayer('second')", context);
assert.deepEqual(players[0].loads, ['second']);

vm.runInContext("closeWatch(); watchState = 'full'; activeVideo = {id: 'third'}; mountYouTubePlayer('third');", context);
assert.equal(players[0].destroyed, true);
assert.equal(players.length, 2, 'reopening must create a connected player');
players[0].options.events.onReady({target: players[0]});
assert.equal(vm.runInContext('playerReady', context), false, 'late events from a destroyed iframe must be ignored');

// A second selection before ready must not send commands to an unready iframe.
vm.runInContext("activeVideo = {id: 'fourth'}; mountYouTubePlayer('fourth');", context);
assert.equal(players[1].destroyed, true);
assert.equal(players.length, 3);
assert.equal(players[2].options.videoId, 'fourth');
assert.equal(players[2].options.playerVars.playsinline, 1);

// A click before the API arrives is promoted from its fallback iframe on readiness.
vm.runInContext("destroyYouTubePlayer(); YT = undefined; activeVideo = {id: 'early'}; mountYouTubePlayer('early');", context);
assert.ok(element('ytPlayerContainer').innerHTML.includes('/embed/early'));
context.YT = {Player: function (id, options) {players.push({options});}};
context.onYouTubeIframeAPIReady();
assert.equal(players.at(-1).options.videoId, 'early');

(async () => {
  await vm.runInContext('connectWebSocket()', context);
  assert.ok(timers.length > 0, 'the connection must schedule a heartbeat without a ReferenceError');
  timers.at(-1)();
  assert.equal(vm.runInContext('ws.lastMessage', context), 'ping');

  const pending = [];
  context.fetch = async () => await new Promise(resolve => pending.push(resolve));
  vm.runInContext('showSkeleton = () => {}; renderResults = (query) => { window.renderedQuery = query; };', context);
  const firstSearch = vm.runInContext("doSearch('old query')", context);
  const secondSearch = vm.runInContext("doSearch('new query')", context);
  pending[1]({ok: true, json: async () => ({results: [{id: 'new'}]})});
  await secondSearch;
  pending[0]({ok: true, json: async () => ({results: [{id: 'old'}]})});
  await firstSearch;
  assert.equal(context.renderedQuery, 'new query', 'a slow old search must not replace the latest results');

  vm.runInContext("activeVideo = {id: 'new'}; upcomingQueue = [];", context);
  const related = vm.runInContext("fetchRelatedVideos({id: 'old'})", context);
  pending[2]({ok: true, json: async () => ({results: [{id: 'stale', title: 'Stale suggestion'}]})});
  await related;
  assert.equal(vm.runInContext('upcomingQueue.length', context), 0, 'stale recommendations must not leak into a different song queue');
  assert.equal(vm.runInContext("getSafeDownloadName({title: 'Song', format: 'audio', filename: 'id.m4a'})", context), 'Song.m4a');
  console.log('Player lifecycle and WebSocket heartbeat regressions passed');
})().catch(error => {console.error(error); process.exitCode = 1;});
