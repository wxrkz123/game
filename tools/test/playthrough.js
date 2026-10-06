// Full automated playthrough of 《余音》 in headless Chromium.
//   node tools/test/playthrough.js [--shots]
const fs = require('fs');
const path = require('path');
const { serve, launch } = require('./harness');

const OUT = path.join(__dirname, 'out');
const SHOTS = process.argv.includes('--shots');
const PORT = 8765;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// switch ids (see tools/build/story_core.py)
const S = { PRO: 1, CH1: 2, CH2: 3, CH3: 4, CH4: 5, CH5: 6, SOUND_QUEST: 11, SOUNDS_DONE: 12, LESSON_DONE: 13,
  GOT_GUITAR: 21, MOM_TALK: 22, JOINED_BAND: 23, SONG_WRITTEN: 24, FESTIVAL: 26, HOME_NIGHT: 27, PHONE: 31,
  OWNER: 32, DEMO: 33, JIE_BYE: 34, NOTEBOOK: 45, COLOR_BACK: 46, MET_XIAOHE: 47, TEACH: 48, C5_READY: 56,
  CONCERT: 55, C5_GRAVE: 54 };

const STEPS = [
  ['newgame'],
  ['idle'], ['expectMap', 1], ['shot', '01_prologue_home'],
  ['menu'],
  ['go', '照片1'], ['idle'],
  ['go', '钢琴'], ['idle'], ['expectMap', 3], ['expectSwitch', S.CH1], ['shot', '02_ch1_grandpa_house'],
  ['go', '门'], ['idle'], ['expectMap', 2], ['shot', '03_ch1_village'],
  ['go', '爷爷'], ['idle'], ['expectSwitch', S.SOUND_QUEST],
  ['go', '知了'], ['idle'],
  ['go', '小河'], ['idle'],
  ['go', '风铃'], ['idle'],
  ['go', '卖冰棍的'], ['idle'], ['expectSwitch', S.SOUNDS_DONE],
  ['mistakes', 1],
  ['go', '爷爷'], ['idle'], ['expectSwitch', S.CH2], ['expectMap', 4], ['shot', '04_ch2_home'],
  ['go', '包裹'], ['idle'], ['expectSwitch', S.GOT_GUITAR],
  ['go', '妈妈'], ['idle'], ['expectSwitch', S.MOM_TALK],
  ['go', '家门'], ['idle'], ['expectMap', 5], ['shot', '05_ch2_school'],
  ['go', '阿杰'], ['idle'], ['expectSwitch', S.JOINED_BAND],
  ['choices', [1]],
  ['go', '教学楼大门'], ['idle'], ['expectSwitch', S.HOME_NIGHT], ['expectMap', 4], ['shot', '06_ch2_night'],
  ['go', '包裹'], ['idle'], ['expectSwitch', S.CH3], ['expectMap', 9], ['shot', '07_ch3_basement'],
  ['go', '电话'], ['idle'], ['expectSwitch', S.PHONE],
  ['go', '门'], ['idle'], ['expectMap', 8], ['shot', '08_ch3_city'],
  ['choices', [1]],
  ['go', '老板娘'], ['idle'], ['expectSwitch', S.OWNER],
  ['go', '唱片公司'], ['idle'], ['expectSwitch', S.DEMO],
  ['go', '阿杰'], ['idle'], ['expectSwitch', S.JIE_BYE],
  ['go', '卖唱的地方'], ['idle'], ['expectSwitch', S.CH4], ['expectMap', 2], ['shot', '09_ch4_village_gray'],
  ['go', '小禾'], ['idle'],
  ['go', '爷爷家的门'], ['idle'], ['expectMap', 3],
  ['go', '爷爷的床'], ['idle'], ['expectSwitch', S.COLOR_BACK], ['shot', '10_ch4_color_back'],
  ['go', '门'], ['idle'], ['expectMap', 2],
  ['go', '小禾'], ['idle'], ['expectSwitch', S.MET_XIAOHE], ['shot', '11_ch4_village'],
  ['go', '校长'], ['idle'], ['expectSwitch', S.CH5], ['expectMap', 1], ['shot', '12_ch5_home'],
  ['go', '门'], ['idle'], ['expectMap', 2], ['shot', '13_ch5_village_evening'],
  ['go', '爷爷的墓'], ['idle'], ['expectSwitch', S.C5_GRAVE],
  ['go', '钢琴'], ['idle'],
  ['go', '小禾（大人）'], ['idle'],
  ['go', '阿杰（老年）'], ['idle'],
  ['go', '小雨（大人）'], ['idle'], ['expectSwitch', S.C5_READY],
  ['go', '钢琴'], ['title'],
];

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
          if (s.running || s.scene !== 'Scene_Map' || s.busy) { started = true; break; }
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
        for (let i = 0; i < 6000; i++) {
          const s = await st();
          if (s.scene === 'Scene_Title') break;
          if (i % 50 === 0) console.log('  ...', JSON.stringify(s));
          await sleep(100);
        }
        const s = await st();
        if (s.scene !== 'Scene_Title') throw new Error('did not return to title');
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
  console.log('\nbot log:\n  ' + log.join('\n  '));
  console.log('\nerrors (' + errors.length + '):\n  ' + errors.slice(0, 30).join('\n  '));
  await browser.close();
  server.close();
  process.exit(ok && errors.length === 0 ? 0 : 1);
}

main();
