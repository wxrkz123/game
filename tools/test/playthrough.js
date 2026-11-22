// Full automated playthrough of 《余音》 in headless Chromium.
//   node tools/test/playthrough.js [--shots] [--alt]
//   --alt takes the other answer at the two choices that change later scenes
const fs = require('fs');
const path = require('path');
const { serve, launch } = require('./harness');

const OUT = path.join(__dirname, 'out');
const SHOTS = process.argv.includes('--shots');
const ALT = process.argv.includes('--alt');
const PORT = 8765;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// the route, switch and variable ids live in steps.js so the desktop test can share them
const { steps } = require('./steps');
const STEPS = steps(ALT);

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  const server = await serve(PORT);
  const { browser, page, errors } = await launch(PORT);
  const bot = fs.readFileSync(path.join(__dirname, 'bot.js'), 'utf8');
  const st = () => page.evaluate(() => Bot.state());
  let ok = true;

  // boot to title
  for (let i = 0; i < 300; i++) {
    const s = await page.evaluate(() => SceneManager._scene && SceneManager._scene.constructor.name).catch(() => null);
    if (s === 'Scene_Title') break;
    await sleep(100);
  }
  await sleep(1500);
  await page.screenshot({ path: path.join(OUT, '00_title.png') });
  await page.addScriptTag({ content: bot });

  const seen = {};
  async function watch(s) {
    if (!SHOTS) return;
    let key = null;
    if (s.scene === 'Scene_LifeSong') key = 'mg_' + s.minigames;
    if (s.scene === 'Scene_LSChapter') key = 'card_' + s.cards;
    if (s.busy && s.text.startsWith('【') && !seen.msg) key = 'msg';
    if (key && !seen[key]) {
      seen[key] = true;
      await sleep(key.startsWith('mg') ? 900 : 700);
      await page.screenshot({ path: path.join(OUT, key + '.png') });
    }
  }
  async function waitIdle(limitSec = 240) {
    let streak = 0;
    for (let i = 0; i < limitSec * 10; i++) {
      const s = await st();
      await watch(s);
      if (s.scene === 'Scene_Title') return s;
      if (s.idle) { streak++; if (streak >= 4) return s; } else streak = 0;
      await sleep(100);
    }
    throw new Error('timeout waiting for idle: ' + JSON.stringify(await st()));
  }

  for (const step of STEPS) {
    const [op, arg] = step;
    try {
      if (op === 'newgame') {
        await page.evaluate(() => { DataManager.setupNewGame(); SceneManager.goto(Scene_Map); });
        for (let i = 0; i < 100; i++) {
          if ((await st()).scene === 'Scene_Map') break;
          await sleep(100);
        }
      } else if (op === 'idle') {
        await waitIdle();
      } else if (op === 'go') {
        const r = await page.evaluate((n) => Bot.goTo(n), arg);
        if (r !== 'ok') throw new Error(r);
        let started = false;
        let still = 0;
        let last = null;
        for (let i = 0; i < 600; i++) {
          const s = await st();
          if (s.running || s.scene !== 'Scene_Map' || s.busy || s.started.length) { started = true; break; }
          const pos = s.x + ',' + s.y + ',' + s.map;
          if (pos === last && !s.dest) still++; else still = 0;
          last = pos;
          if (still > 15) break;
          await sleep(100);
        }
        if (!started) throw new Error('interaction did not start: ' + arg + ' ' + JSON.stringify(await st()));
      } else if (op === 'expectMap') {
        const s = await st();
        if (s.map !== arg) throw new Error('expected map ' + arg + ' got ' + s.map);
      } else if (op === 'expectSwitch') {
        const [v] = await page.evaluate((i) => Bot.switches([i]), arg);
        if (!v) throw new Error('switch ' + arg + ' is off');
      } else if (op === 'expectVar') {
        const [id, want] = arg;
        const got = await page.evaluate((i) => $gameVariables.value(i), id);
        if (got !== want) throw new Error('variable ' + id + ' is ' + JSON.stringify(got) + ', expected ' + JSON.stringify(want));
      } else if (op === 'expectLog') {
        // arg: text, or a list of texts that must all be in the same message
        const parts = [].concat(arg);
        const log = await page.evaluate(() => Bot.log);
        if (!log.some((l) => parts.every((p) => l.includes(p)))) throw new Error('never shown: ' + parts.join(' … '));
      } else if (op === 'choices') {
        await page.evaluate((c) => { Bot.choices = c.slice(); }, arg);
      } else if (op === 'mistakes') {
        await page.evaluate((n) => { Bot.mistakes = n; }, arg);
      } else if (op === 'shot') {
        if (SHOTS) {
          await sleep(400);
          await page.screenshot({ path: path.join(OUT, arg + '.png') });
        }
      } else if (op === 'menu') {
        await page.evaluate(() => SceneManager.push(Scene_Menu));
        await sleep(1500);
        if (SHOTS) await page.screenshot({ path: path.join(OUT, '01b_menu.png') });
        await page.evaluate(() => SceneManager.push(Scene_Item));
        await sleep(1200);
        if (SHOTS) await page.screenshot({ path: path.join(OUT, '01c_items.png') });
        await page.evaluate(() => { SceneManager.goto(Scene_Map); });
        await waitIdle();
      } else if (op === 'title') {
        let creditShots = 0;
        for (let i = 0; i < 6000; i++) {
          const s = await st();
          if (s.scene === 'Scene_Title') break;
          if (SHOTS && s.credits && creditShots < 8 && i % 10 === 0) {
            await page.screenshot({ path: path.join(OUT, 'credits_' + creditShots++ + '.png') });
          }
          if (i % 50 === 0) console.log('  ...', JSON.stringify(s));
          await sleep(100);
        }
        const s = await st();
        if (s.scene !== 'Scene_Title') throw new Error('did not return to title');
      } else if (op === 'save') {
        const saved = await page.evaluate(() => { $gameSystem.onBeforeSave(); return DataManager.saveGame(1); });
        if (!saved) throw new Error('saveGame(1) failed');
      } else if (op === 'load') {
        // what Scene_Load does after picking a slot
        const loaded = await page.evaluate(() => {
          if (!DataManager.loadGame(1)) return false;
          $gameSystem.onAfterLoad();
          SceneManager.goto(Scene_Map);
          return true;
        });
        if (!loaded) throw new Error('loadGame(1) failed');
        for (let i = 0; i < 100 && (await st()).scene !== 'Scene_Map'; i++) await sleep(100);
        const s = await waitIdle();
        if (s.scene !== 'Scene_Map' || s.map !== arg) throw new Error('after loading: ' + JSON.stringify(s));
      }
      console.log('ok  ', op, arg !== undefined ? JSON.stringify(arg) : '');
    } catch (e) {
      ok = false;
      console.log('FAIL', op, arg, '\n     ', e.message);
      await page.screenshot({ path: path.join(OUT, 'fail.png') });
      break;
    }
  }
  const log = await page.evaluate(() => Bot.log).catch(() => []);
  console.log('\nbot log:\n  ' + log.filter((l) => !l.startsWith('text ')).join('\n  '));
  console.log('\nerrors (' + errors.length + '):\n  ' + errors.slice(0, 30).join('\n  '));
  await browser.close();
  server.close();
  process.exit(ok && errors.length === 0 ? 0 : 1);
}

main();
