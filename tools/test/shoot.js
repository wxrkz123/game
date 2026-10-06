// Screenshot specific game states.   node tools/test/shoot.js <name> '<js setup>' [waitMs]
// The setup code runs right after DataManager.setupNewGame(), before the first map loads.
const path = require('path');
const fs = require('fs');
const { serve, launch } = require('./harness');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const [name, setup, wait] = process.argv.slice(2);
  const out = path.join(__dirname, 'out');
  fs.mkdirSync(out, { recursive: true });
  const port = 8800 + Math.floor(Math.random() * 100);
  const server = await serve(port);
  const { browser, page, errors } = await launch(port);
  for (let i = 0; i < 300; i++) {
    const s = await page.evaluate(() => SceneManager._scene && SceneManager._scene.constructor.name).catch(() => null);
    if (s === 'Scene_Title') break;
    await sleep(100);
  }
  await page.evaluate((code) => {
    DataManager.setupNewGame();
    $gamePlayer.setTransparent(false);
    eval(code);
    SceneManager.goto(Scene_Map);
  }, setup);
  await sleep(Number(wait || 2500));
  await page.screenshot({ path: path.join(out, name + '.png') });
  console.log(errors.length ? errors.join('\n') : 'no errors');
  await browser.close();
  server.close();
}
main();
