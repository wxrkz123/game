// Lays the game out the way RPG Maker MV's "File → Deployment → Windows" does:
//   <out>/package.json   tells NW.js (YuYin.exe) to open www/index.html
//   <out>/www/           the game: YuYin/ without the editor's project file
//   <out>/README.txt     how to play (Chinese, CRLF + BOM so every Notepad shows it)
// The NW.js runtime files are copied next to these by .github/workflows/windows.yml.
//   node tools/windows/assemble.js <out> [--test | --test=alt]
// --test also puts the automated playthrough (tools/test/nw_runner.js) into the page;
// --test=alt plays the other answer at the story's two choices.
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const GAME = path.join(ROOT, 'YuYin');
const out = path.resolve(process.argv[2] || path.join(ROOT, 'build', 'YuYin'));
const testArg = process.argv.find((a) => a.startsWith('--test'));
const www = path.join(out, 'www');

fs.rmSync(www, { recursive: true, force: true });
fs.mkdirSync(out, { recursive: true });
const skip = new Set(['Game.rpgproject', 'package.json', 'save']);
fs.cpSync(GAME, www, { recursive: true, filter: (src) => src === GAME || !skip.has(path.basename(src)) });

const pkg = JSON.parse(fs.readFileSync(path.join(GAME, 'package.json'), 'utf8'));
pkg.main = 'www/index.html';
pkg.window.icon = 'www/' + pkg.window.icon;
fs.writeFileSync(path.join(out, 'package.json'), JSON.stringify(pkg, null, 4) + '\n');

const readme = fs.readFileSync(path.join(__dirname, 'README.txt'), 'utf8').replace(/\r?\n/g, '\r\n');
fs.writeFileSync(path.join(out, 'README.txt'), '\ufeff' + readme);

if (testArg) {
  fs.mkdirSync(path.join(www, 'test'));
  for (const f of ['steps.js', 'bot.js', 'nw_runner.js']) {
    fs.copyFileSync(path.join(ROOT, 'tools', 'test', f), path.join(www, 'test', f));
  }
  fs.writeFileSync(path.join(www, 'test', 'config.js'), 'window.YY_ALT = ' + (testArg === '--test=alt') + ';\n');
  const index = path.join(www, 'index.html');
  const html = fs.readFileSync(index, 'utf8');
  if (!html.includes('</body>')) throw new Error('index.html has no </body>');
  const tags = ['config.js', 'steps.js', 'nw_runner.js']
    .map((f) => '<script type="text/javascript" src="test/' + f + '"></script>').join('\n        ');
  fs.writeFileSync(index, html.replace('</body>', '    ' + tags + '\n    </body>'));
}
console.log('assembled', out, testArg ? '(with automated playthrough' + (testArg === '--test=alt' ? ', other branch)' : ')') : '');
