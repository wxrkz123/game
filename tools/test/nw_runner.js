// The playthrough of playthrough.js, run from inside the game page itself, so it can test the
// desktop build (NW.js) where there is no Playwright. tools/windows/assemble.js --test adds this
// file, steps.js and bot.js to the page (--test=alt plays the other story branch). The report
// goes to test-result.json next to the .exe (or to window.YY_RESULT in a normal browser), then
// the game quits.  Keep this file ES2017: the desktop runtime is Chromium 65.
(function () {
  var isNw = typeof require === 'function' && typeof process === 'object';
  var result = { ok: false, done: false, alt: !!window.YY_ALT, step: '', steps: 0, errors: [], env: {} };

  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function st() { return Bot.state(); }
  function sceneName() { return SceneManager._scene ? SceneManager._scene.constructor.name : null; }
  function report(e) { result.errors.push(String(e)); }

  function write() {
    if (isNw) {
      var fs = require('fs');
      var path = require('path');
      fs.writeFileSync(path.join(path.dirname(process.execPath), 'test-result.json'), JSON.stringify(result, null, 2));
    } else {
      window.YY_RESULT = result;
    }
  }

  // collect every error the game would otherwise show on screen or in the console
  window.addEventListener('error', function (e) {
    if (e.target && e.target !== window) report('load failed: ' + (e.target.src || e.target.href));
    else report('error: ' + e.message + ' @ ' + e.filename + ':' + e.lineno);
  }, true);
  var _catch = SceneManager.catchException;
  SceneManager.catchException = function (e) {
    report('exception: ' + (e && e.stack ? e.stack : e));
    _catch.call(this, e);
  };
  var _consoleError = console.error;
  console.error = function () {
    report('console: ' + Array.prototype.join.call(arguments, ' '));
    return _consoleError.apply(console, arguments);
  };

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = src;
      s.onload = resolve;
      s.onerror = function () { reject(new Error('cannot load ' + src)); };
      document.body.appendChild(s);
    });
  }

  async function waitIdle(limitSec) {
    var streak = 0;
    for (var i = 0; i < (limitSec || 240) * 10; i++) {
      var s = st();
      if (s.scene === 'Scene_Title') return s;
      if (s.idle) { streak++; if (streak >= 4) return s; } else streak = 0;
      await sleep(100);
    }
    throw new Error('timeout waiting for idle: ' + JSON.stringify(st()));
  }

  async function waitScene(name, limitSec) {
    for (var i = 0; i < limitSec * 10 && sceneName() !== name; i++) await sleep(100);
    if (sceneName() !== name) throw new Error('expected ' + name + ', got ' + sceneName());
  }

  async function runStep(op, arg) {
    var s;
    if (op === 'newgame') {
      DataManager.setupNewGame();
      SceneManager.goto(Scene_Map);
      await waitScene('Scene_Map', 10);
    } else if (op === 'idle') {
      await waitIdle();
    } else if (op === 'go') {
      var r = Bot.goTo(arg);
      if (r !== 'ok') throw new Error(r);
      var started = false, still = 0, last = null;
      for (var i = 0; i < 600; i++) {
        s = st();
        if (s.running || s.scene !== 'Scene_Map' || s.busy || s.started.length) { started = true; break; }
        var pos = s.x + ',' + s.y + ',' + s.map;
        if (pos === last && !s.dest) still++; else still = 0;
        last = pos;
        if (still > 15) break;
        await sleep(100);
      }
      if (!started) throw new Error('interaction did not start: ' + arg + ' ' + JSON.stringify(st()));
    } else if (op === 'expectMap') {
      if (st().map !== arg) throw new Error('expected map ' + arg + ' got ' + st().map);
    } else if (op === 'expectSwitch') {
      if (!Bot.switches([arg])[0]) throw new Error('switch ' + arg + ' is off');
    } else if (op === 'expectVar') {
      var got = $gameVariables.value(arg[0]);
      if (got !== arg[1]) throw new Error('variable ' + arg[0] + ' is ' + JSON.stringify(got) + ', expected ' + JSON.stringify(arg[1]));
    } else if (op === 'expectLog') {
      var parts = [].concat(arg);
      var seen = Bot.log.some(function (l) { return parts.every(function (p) { return l.indexOf(p) >= 0; }); });
      if (!seen) throw new Error('never shown: ' + parts.join(' … '));
    } else if (op === 'choices') {
      Bot.choices = arg.slice();
    } else if (op === 'mistakes') {
      Bot.mistakes = arg;
    } else if (op === 'menu') {
      SceneManager.push(Scene_Menu);
      await sleep(1500);
      SceneManager.push(Scene_Item);
      await sleep(1200);
      SceneManager.goto(Scene_Map);
      await waitIdle();
    } else if (op === 'title') {
      await waitScene('Scene_Title', 600);
    } else if (op === 'save') {
      $gameSystem.onBeforeSave();
      if (!DataManager.saveGame(1)) throw new Error('saveGame(1) failed');
      if (isNw) {
        // the desktop build must save real files (www/save/file1.rpgsave), not browser storage
        var file = require('path').join(StorageManager.localFileDirectoryPath(), 'file1.rpgsave');
        if (!require('fs').existsSync(file)) throw new Error('no save file at ' + file);
        result.saveFile = file;
      }
    } else if (op === 'load') {
      if (!DataManager.loadGame(1)) throw new Error('loadGame(1) failed');
      $gameSystem.onAfterLoad();
      SceneManager.goto(Scene_Map);
      await waitScene('Scene_Map', 10);
      s = await waitIdle();
      if (s.map !== arg) throw new Error('after loading: ' + JSON.stringify(s));
    }
    // 'shot' (screenshots) only exists in the Playwright version
  }

  async function main() {
    await waitScene('Scene_Title', 120);
    await sleep(1500);
    result.env = {
      nw: isNw ? process.versions.nw : null,
      chromium: isNw ? process.versions.chromium : navigator.userAgent,
      webgl: Graphics.isWebGL(),
      gameFont: Graphics.isFontLoaded('GameFont'),
      audio: !!WebAudio._context,
      audioExt: AudioManager.audioFileExt(),
      localSave: StorageManager.isLocalMode(),
    };
    await loadScript('test/bot.js');
    var steps = window.YY_TEST.steps(!!window.YY_ALT);
    for (var i = 0; i < steps.length; i++) {
      result.step = JSON.stringify(steps[i]);
      await runStep(steps[i][0], steps[i][1]);
      result.steps = i + 1;
      write();
    }
    result.ok = result.errors.length === 0;
  }

  main().catch(function (e) {
    report('FAIL at ' + result.step + ': ' + (e && e.message ? e.message : e));
  }).then(function () {
    result.done = true;
    if (window.Bot) result.log = Bot.log.filter(function (l) { return l.indexOf('text ') !== 0; });
    write();
    if (isNw) setTimeout(function () { nw.App.quit(); }, 300);
  });
})();
