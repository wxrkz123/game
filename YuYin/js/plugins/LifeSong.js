//=============================================================================
// LifeSong.js  —  《余音》核心插件
//=============================================================================
/*:
 * @plugindesc 《余音》核心插件：旋律小游戏、章节标题卡、对话名字框、像素字体与菜单美化。
 * @author 《余音》制作组
 *
 * @param Font Size
 * @desc 对话和菜单的字号。像素字体请用 12 的倍数（24 最清晰）。
 * @default 24
 *
 * @param Text Wait
 * @desc 对话每个字之间多等几帧（0 = 最快，1 = 舒缓，2 = 很慢）。
 * @default 1
 *
 * @param Chapter Variable
 * @desc 保存“当前章节标题”的变量编号（菜单里会显示这个变量的内容）。
 * @default 1
 *
 * @param Fragment Variable
 * @desc 保存“旋律碎片数量”的变量编号。
 * @default 2
 *
 * @param Fragment Max
 * @desc 旋律碎片的总数。
 * @default 5
 *
 * @help
 * ============================================================================
 *  一、对话名字框
 * ============================================================================
 *  在“显示文字”的第一行开头写【名字】，就会在对话框上方显示一个名字框：
 *
 *      【爷爷】小音，你听——
 *
 *  名字里可以用 \N[1] 显示主角名字：【\N[1]】
 *
 * ============================================================================
 *  二、插件指令（事件指令 → 第3页 → 插件指令）
 * ============================================================================
 *  乐器代号：Harm(口琴)  Gtr(吉他)  Pno(钢琴)  Box(八音盒)  Rec(竖笛)
 *            也可以直接写中文：口琴 / 吉他 / 钢琴 / 八音盒 / 竖笛
 *  音符写法：1 2 3 4 5 6 7 是简谱的 do re mi fa sol la si，8 = 高音 do。
 *            用逗号隔开，例如 3,5,6,5,3,2,1
 *
 *  LifeSong Chapter 第一章 蝉鸣 八岁·夏
 *      显示章节标题卡（黑屏 + 大标题），播放完才继续往下执行。
 *
 *  LifeSong Echo 乐器 音符 [结果变量] [提示文字]
 *      “跟着弹”小游戏：先听一遍，再用数字键 1~8（或鼠标点击琴键）弹出来。
 *      弹错了会重新示范；错两次以后会显示简谱提示。
 *      结果变量 = 弹错的次数（0 表示一次就成功）。不需要就写 0。
 *      例：LifeSong Echo Harm 3,5,6,5,3,2,1 11 跟着爷爷吹一遍
 *
 *  LifeSong Feel 乐器 音符 [结果变量] [提示文字]
 *      和 Echo 一样，但示范时几乎听不见声音，只能“看”琴键的震动来跟随。
 *
 *  LifeSong Free 乐器 [最多几个音] [保存变量] [提示文字]
 *      自由演奏。玩家弹完按“完成”。如果填了保存变量，
 *      弹出的旋律会以文字形式（如 "5,6,8"）存进这个变量。
 *      最多几个音写 0 表示不限（从道具菜单吹口琴时用）。
 *
 *  LifeSong Play 乐器 音符 [每拍帧数]
 *      在地图上直接播放一段旋律（事件会等它播完）。
 *      音符可以带拍子：3:1.5,5:0.5,6,5   （冒号后是拍数，默认 1 拍）
 *      音符也可以写 v:20，表示播放变量 20 里保存的旋律。
 *
 *  LifeSong SetText 变量编号 文字
 *      把一段文字存进变量（例如菜单里显示的章节标题）。
 *
 *  LifeSong Song 乐器 [每拍帧数]
 *      播放整首《余音》主旋律 + 变量里保存的玩家结尾（终章用）。
 * ============================================================================
 */

var LifeSong = LifeSong || {};

(function() {
    'use strict';

    var params = PluginManager.parameters('LifeSong');
    var FONT_SIZE = Number(params['Font Size'] || 24);
    var TEXT_WAIT = Number(params['Text Wait'] || 1);
    var CHAPTER_VAR = Number(params['Chapter Variable'] || 1);
    var FRAGMENT_VAR = Number(params['Fragment Variable'] || 2);
    var FRAGMENT_MAX = Number(params['Fragment Max'] || 5);

    LifeSong.INSTRUMENTS = {
        harm: 'Harm', '口琴': 'Harm', gtr: 'Gtr', guitar: 'Gtr', '吉他': 'Gtr',
        pno: 'Pno', piano: 'Pno', '钢琴': 'Pno', box: 'Box', '八音盒': 'Box',
        rec: 'Rec', '竖笛': 'Rec'
    };
    LifeSong.INSTRUMENT_NAMES = { Harm: '口琴', Gtr: '吉他', Pno: '钢琴', Box: '八音盒', Rec: '竖笛' };
    LifeSong.SOLFEGE = ['do', 're', 'mi', 'fa', 'sol', 'la', 'si', 'do'];
    LifeSong.PAD_COLORS = ['#e8705f', '#f09a4f', '#f2c855', '#8fcf6a', '#5fbfb0', '#6a9be0', '#9a7ad8', '#e07ab0'];
    // the whole leitmotif, for "LifeSong Song"
    LifeSong.THEME = '3:1.5,5:.5,6,5,3,2,1:2,2:1.5,3:.5,5,6,5,3,2:2,6:1.5,8:.5,6,5,3,5,6:2,5:1.5,3:.5,2,1,2,3,1:2';

    LifeSong.instrument = function(code) {
        var key = String(code || 'Harm');
        return LifeSong.INSTRUMENTS[key.toLowerCase()] || LifeSong.INSTRUMENTS[key] || 'Harm';
    };

    LifeSong.parseNotes = function(text) {
        text = String(text || '');
        var m = /^v:(\d+)$/i.exec(text);
        if (m) {
            text = String($gameVariables.value(Number(m[1])) || '');
        }
        var out = [];
        text.split(/[,，\s]+/).forEach(function(tok) {
            if (!tok) return;
            var parts = tok.split(':');
            var n = parts[0].replace(/[i']/g, function() { return '8'; });
            n = Number(n);
            if (n >= 1 && n <= 8) {
                out.push({ note: n, beats: parts.length > 1 ? Number(parts[1]) || 1 : 1 });
            }
        });
        return out;
    };

    LifeSong.playNote = function(inst, n, volume) {
        AudioManager.playSe({ name: 'YY_' + inst + '_' + n, volume: volume === undefined ? 90 : volume,
                              pitch: 100, pan: 0 });
    };

    // ------------------------------------------------------------------------
    // a tiny scheduler so melodies can play on any scene
    // ------------------------------------------------------------------------
    LifeSong._queue = [];
    LifeSong.schedule = function(inst, notes, framesPerBeat, volume) {
        var t = 0;
        notes.forEach(function(n) {
            LifeSong._queue.push({ at: Graphics.frameCount + t, inst: inst, note: n.note, volume: volume });
            t += Math.round(n.beats * framesPerBeat);
        });
        return t;
    };
    LifeSong.updateQueue = function() {
        var now = Graphics.frameCount;
        var rest = [];
        LifeSong._queue.forEach(function(q) {
            if (q.at <= now) {
                LifeSong.playNote(q.inst, q.note, q.volume);
            } else {
                rest.push(q);
            }
        });
        LifeSong._queue = rest;
    };
    var _Scene_Base_update = Scene_Base.prototype.update;
    Scene_Base.prototype.update = function() {
        _Scene_Base_update.call(this);
        LifeSong.updateQueue();
    };

    // ------------------------------------------------------------------------
    // number keys 1-8 for the mini-game
    // ------------------------------------------------------------------------
    for (var k = 1; k <= 8; k++) {
        Input.keyMapper[48 + k] = 'ls' + k;
    }

    // ------------------------------------------------------------------------
    // font: crisp pixel text
    // ------------------------------------------------------------------------
    Window_Base.prototype.standardFontFace = function() {
        return 'GameFont, sans-serif';
    };
    Window_Base.prototype.standardFontSize = function() {
        return FONT_SIZE;
    };
    var _drawTextOutline = Bitmap.prototype._drawTextOutline;
    Bitmap.prototype._drawTextOutline = function(text, tx, ty, maxWidth) {
        _drawTextOutline.call(this, text, Math.round(tx), Math.round(ty), maxWidth);
    };
    var _drawTextBody = Bitmap.prototype._drawTextBody;
    Bitmap.prototype._drawTextBody = function(text, tx, ty, maxWidth) {
        _drawTextBody.call(this, text, Math.round(tx), Math.round(ty), maxWidth);
    };

    // ------------------------------------------------------------------------
    // message: typewriter speed + 【名字】 name box
    // ------------------------------------------------------------------------
    function Window_LSName() {
        this.initialize.apply(this, arguments);
    }
    Window_LSName.prototype = Object.create(Window_Base.prototype);
    Window_LSName.prototype.constructor = Window_LSName;
    Window_LSName.prototype.initialize = function() {
        Window_Base.prototype.initialize.call(this, 0, 0, 240, this.fittingHeight(1));
        this._name = '';
        this.openness = 0;
    };
    Window_LSName.prototype.standardPadding = function() {
        return 12;
    };
    Window_LSName.prototype.setName = function(name) {
        if (this._name === name) return;
        this._name = name;
        if (name) {
            var w = this.textWidth(name) + this.standardPadding() * 2 + this.textPadding() * 2 + 8;
            this.width = Math.max(120, w);
            this.createContents();
            this.changeTextColor(this.textColor(6));
            this.drawText(name, 0, 0, this.contentsWidth(), 'center');
        }
    };
    Window_LSName.prototype.follow = function(msg) {
        if (!this._name) {
            this.openness = 0;
            return;
        }
        this.x = msg.x + 16;
        if (msg.y > 0) {
            this.y = msg.y - this.height + 6;
        } else {
            this.y = msg.y + msg.height - 6;
        }
        this.openness = msg.openness;
    };

    var _WM_createSubWindows = Window_Message.prototype.createSubWindows;
    Window_Message.prototype.createSubWindows = function() {
        _WM_createSubWindows.call(this);
        this._lsNameBox = new Window_LSName();
    };
    var _WM_subWindows = Window_Message.prototype.subWindows;
    Window_Message.prototype.subWindows = function() {
        return _WM_subWindows.call(this).concat([this._lsNameBox]);
    };
    var _WM_startMessage = Window_Message.prototype.startMessage;
    Window_Message.prototype.startMessage = function() {
        _WM_startMessage.call(this);
        var text = this._textState.text;
        var m = /^【([^】]{1,16})】\n?/.exec(text);
        if (m) {
            this._textState.text = text.slice(m[0].length);
            this._lsNameBox.setName(m[1]);
        } else {
            this._lsNameBox.setName('');
        }
        this._textSpeed = TEXT_WAIT;
        this._textSpeedCount = 0;
    };
    var _WM_terminateMessage = Window_Message.prototype.terminateMessage;
    Window_Message.prototype.terminateMessage = function() {
        _WM_terminateMessage.call(this);
        if (this._lsNameBox) this._lsNameBox.setName('');
    };
    var _WM_update = Window_Message.prototype.update;
    Window_Message.prototype.update = function() {
        _WM_update.call(this);
        if (this._lsNameBox) {
            this._lsNameBox.follow(this);
        }
    };

    // ------------------------------------------------------------------------
    // plugin commands
    // ------------------------------------------------------------------------
    var _pluginCommand = Game_Interpreter.prototype.pluginCommand;
    Game_Interpreter.prototype.pluginCommand = function(command, args) {
        _pluginCommand.call(this, command, args);
        if (String(command).toLowerCase() !== 'lifesong') return;
        var sub = String(args[0] || '').toLowerCase();
        if (sub === 'chapter') {
            SceneManager.push(Scene_LSChapter);
            SceneManager.prepareNextScene(args[1] || '', args[2] || '', args.slice(3).join(' '));
        } else if (sub === 'echo' || sub === 'feel') {
            SceneManager.push(Scene_LifeSong);
            SceneManager.prepareNextScene({
                mode: sub, inst: LifeSong.instrument(args[1]), notes: LifeSong.parseNotes(args[2]),
                variable: Number(args[3] || 0), prompt: args.slice(4).join(' ')
            });
        } else if (sub === 'free') {
            SceneManager.push(Scene_LifeSong);
            SceneManager.prepareNextScene({
                mode: 'free', inst: LifeSong.instrument(args[1]), max: Number(args[2] || 0),
                variable: Number(args[3] || 0), prompt: args.slice(4).join(' ')
            });
        } else if (sub === 'settext') {
            $gameVariables.setValue(Number(args[1]), args.slice(2).join(' '));
        } else if (sub === 'play') {
            var fpb = Number(args[3] || 24);
            var t = LifeSong.schedule(LifeSong.instrument(args[1]), LifeSong.parseNotes(args[2]), fpb);
            this.wait(t + 20);
        } else if (sub === 'song') {
            var fpb2 = Number(args[2] || 22);
            var notes = LifeSong.parseNotes(LifeSong.THEME);
            var extra = LifeSong.parseNotes('v:' + (args[3] || 0));
            if (extra.length) {
                notes.push({ note: 0, beats: 1 });
                extra.forEach(function(n) { n.beats = 1; });
                notes = notes.concat(extra);
                notes[notes.length - 1].beats = 2;
            }
            var t2 = 0;
            var inst = LifeSong.instrument(args[1]);
            notes.forEach(function(n) {
                if (n.note > 0) {
                    LifeSong._queue.push({ at: Graphics.frameCount + t2, inst: inst, note: n.note });
                }
                t2 += Math.round(n.beats * fpb2);
            });
            this.wait(t2 + 30);
        }
    };

    // ------------------------------------------------------------------------
    // Chapter title card
    // ------------------------------------------------------------------------
    function Scene_LSChapter() {
        this.initialize.apply(this, arguments);
    }
    Scene_LSChapter.prototype = Object.create(Scene_Base.prototype);
    Scene_LSChapter.prototype.constructor = Scene_LSChapter;
    Scene_LSChapter.prototype.prepare = function(label, title, sub) {
        this._label = label;
        this._title = title;
        this._sub = sub;
    };
    Scene_LSChapter.prototype.create = function() {
        Scene_Base.prototype.create.call(this);
        var bmp = new Bitmap(Graphics.width, Graphics.height);
        bmp.fillAll('#14121e');
        this._back = new Sprite(bmp);
        this.addChild(this._back);
        var t = new Bitmap(Graphics.width, Graphics.height);
        t.fontFace = 'GameFont, sans-serif';
        t.outlineWidth = 0;
        t.fontSize = 24;
        t.textColor = '#d9b26a';
        t.drawText(this._label, 0, 200, Graphics.width, 36, 'center');
        t.fontSize = 72;
        t.textColor = '#fff6e4';
        t.drawText(this._title, 0, 246, Graphics.width, 90, 'center');
        t.fontSize = 24;
        t.textColor = '#b8b0c8';
        t.drawText(this._sub, 0, 352, Graphics.width, 36, 'center');
        t.fillRect(Graphics.width / 2 - 60, 342, 120, 2, '#5a5070');
        this._text = new Sprite(t);
        this._text.opacity = 0;
        this.addChild(this._text);
        this._count = 0;
    };
    Scene_LSChapter.prototype.start = function() {
        Scene_Base.prototype.start.call(this);
        AudioManager.playMe({ name: 'YY_Chapter', volume: 90, pitch: 100, pan: 0 });
    };
    Scene_LSChapter.prototype.update = function() {
        Scene_Base.prototype.update.call(this);
        this._count++;
        var c = this._count;
        if (c < 50) {
            this._text.opacity = c * 255 / 50;
        } else if (c < 210) {
            this._text.opacity = 255;
            if (c > 80 && (Input.isTriggered('ok') || TouchInput.isTriggered())) {
                this._count = 210;
            }
        } else if (c < 250) {
            this._text.opacity = (250 - c) * 255 / 40;
        } else if (!this._done) {
            this._done = true;
            this.popScene();
        }
    };
    window.Scene_LSChapter = Scene_LSChapter;

    // ------------------------------------------------------------------------
    // The melody mini-game
    // ------------------------------------------------------------------------
    function Scene_LifeSong() {
        this.initialize.apply(this, arguments);
    }
    Scene_LifeSong.prototype = Object.create(Scene_MenuBase.prototype);
    Scene_LifeSong.prototype.constructor = Scene_LifeSong;

    var PAD_W = 84, PAD_H = 132, PAD_GAP = 10, PAD_Y = 420;

    Scene_LifeSong.prototype.prepare = function(opts) {
        this._opts = opts;
    };
    Scene_LifeSong.prototype.create = function() {
        Scene_MenuBase.prototype.create.call(this);
        var o = this._opts || { mode: 'free', inst: 'Harm', notes: [] };
        this._mode = o.mode;
        this._inst = o.inst;
        this._target = (o.notes || []).map(function(n) { return n.note; });
        this._max = this._mode === 'free' ? (o.max || 0) : this._target.length;
        this._variable = o.variable || 0;
        this._prompt = o.prompt || '';
        this._played = [];
        this._mistakes = 0;
        this._cursor = 0;
        this._padFlash = [0, 0, 0, 0, 0, 0, 0, 0, 0];
        this._ripples = [];
        this._floaters = [];
        this._phase = 'intro';
        this._timer = 40;
        this._shake = 0;
        this._status = '';
        this._color = this._mode === 'feel' ? 0 : 1;
        var dim = new Bitmap(Graphics.width, Graphics.height);
        dim.fillAll('rgba(14,12,26,0.78)');
        this.addChild(new Sprite(dim));
        this._fx = new Sprite(new Bitmap(Graphics.width, Graphics.height));
        this.addChild(this._fx);
        this._board = new Sprite(new Bitmap(Graphics.width, Graphics.height));
        this.addChild(this._board);
        this._dirty = true;
    };
    Scene_LifeSong.prototype.start = function() {
        Scene_MenuBase.prototype.start.call(this);
        this._savedBgm = AudioManager.saveBgm();
        this._savedBgs = AudioManager.saveBgs();
        AudioManager.fadeOutBgm(1);
        AudioManager.fadeOutBgs(1);
    };
    Scene_LifeSong.prototype.terminate = function() {
        Scene_MenuBase.prototype.terminate.call(this);
        if (this._savedBgm && this._savedBgm.name) AudioManager.replayBgm(this._savedBgm);
        if (this._savedBgs && this._savedBgs.name) AudioManager.replayBgs(this._savedBgs);
    };

    Scene_LifeSong.prototype.padCount = function() {
        return this._mode === 'free' ? 9 : 8;
    };
    Scene_LifeSong.prototype.padRect = function(i) {
        var n = this.padCount();
        var w = n === 9 ? 76 : PAD_W;
        var total = n * w + (n - 1) * PAD_GAP;
        var x0 = Math.floor((Graphics.width - total) / 2);
        return new Rectangle(x0 + i * (w + PAD_GAP), PAD_Y, w, PAD_H);
    };

    Scene_LifeSong.prototype.noteVolume = function(listening) {
        if (this._mode === 'feel') {
            return listening ? 12 : (this._color >= 1 ? 90 : 35 + 55 * this._color);
        }
        return 90;
    };

    Scene_LifeSong.prototype.sound = function(n, listening) {
        LifeSong.playNote(this._inst, n, this.noteVolume(listening));
        this._padFlash[n - 1] = 18;
        var r = this.padRect(n - 1);
        this._ripples.push({ x: r.x + r.width / 2, y: r.y + r.height / 2, t: 0, n: n });
        this._floaters.push({ x: r.x + r.width / 2, y: r.y - 6, t: 0, n: n });
        if (this._mode === 'feel' && listening) this._shake = 8;
        this._dirty = true;
    };

    Scene_LifeSong.prototype.update = function() {
        Scene_MenuBase.prototype.update.call(this);
        this.updatePhase();
        this.updateEffects();
        if (this._dirty) {
            this.redraw();
            this._dirty = false;
        }
    };

    Scene_LifeSong.prototype.setStatus = function(text) {
        this._status = text;
        this._dirty = true;
    };

    Scene_LifeSong.prototype.updatePhase = function() {
        if (this._timer > 0) {
            this._timer--;
        }
        switch (this._phase) {
        case 'intro':
            if (this._timer === 0) {
                if (this._mode === 'free') {
                    this._phase = 'play';
                    this.setStatus(this._max ? '弹出你心里的旋律（' + this._max + '个音以内），然后点「完成」' :
                                               '随意地弹吧。按 Esc 结束');
                } else {
                    this.startListen();
                }
            }
            break;
        case 'listen':
            if (this._timer === 0) {
                if (this._listenIndex < this._target.length) {
                    this.sound(this._target[this._listenIndex], true);
                    this._listenIndex++;
                    this._timer = 34;
                } else {
                    this._phase = 'play';
                    this._played = [];
                    this.setStatus(this._mistakes >= 2 ? '轮到你了（已显示简谱提示）' : '轮到你了！');
                }
            }
            break;
        case 'play':
            this.updateInput();
            break;
        case 'wrong':
            if (this._timer === 0) this.startListen();
            break;
        case 'success':
            if (this._timer === 0) {
                if (this._replayIndex < this._played.length) {
                    this.sound(this._played[this._replayIndex], false);
                    this._replayIndex++;
                    this._timer = 26;
                } else {
                    this._phase = 'done';
                    this.setStatus(this._mode === 'free' ? '这是只属于你的旋律。（按确定键继续）' :
                                                           '完成了！（按确定键继续）');
                    AudioManager.playSe({ name: 'YY_Sparkle', volume: 80, pitch: 100, pan: 0 });
                }
            }
            break;
        case 'done':
            if (Input.isTriggered('ok') || Input.isTriggered('cancel') || TouchInput.isTriggered()) {
                this.finish();
            }
            break;
        }
        if (this._mode === 'feel' && this._phase === 'success' && this._color < 1) {
            this._color = Math.min(1, this._color + 0.02);
            this._dirty = true;
        }
    };

    Scene_LifeSong.prototype.startListen = function() {
        this._phase = 'listen';
        this._listenIndex = 0;
        this._played = [];
        this._timer = 30;
        this.setStatus(this._mode === 'feel' ? '听不清……试着用眼睛和心去“听”' : '仔细听……');
    };

    Scene_LifeSong.prototype.updateInput = function() {
        var n = this.padCount();
        if (Input.isRepeated('left')) {
            this._cursor = (this._cursor + n - 1) % n;
            SoundManager.playCursor();
            this._dirty = true;
        }
        if (Input.isRepeated('right')) {
            this._cursor = (this._cursor + 1) % n;
            SoundManager.playCursor();
            this._dirty = true;
        }
        var pressed = 0;
        for (var i = 1; i <= 8; i++) {
            if (Input.isTriggered('ls' + i)) pressed = i;
        }
        if (!pressed && Input.isTriggered('ok')) {
            pressed = this._cursor + 1;
        }
        if (!pressed && TouchInput.isTriggered()) {
            for (var j = 0; j < n; j++) {
                var r = this.padRect(j);
                if (TouchInput.x >= r.x && TouchInput.x < r.x + r.width &&
                    TouchInput.y >= r.y && TouchInput.y < r.y + r.height) {
                    pressed = j + 1;
                    this._cursor = j;
                }
            }
        }
        if (pressed === 9) {
            this.finishFree();
            return;
        }
        if (Input.isTriggered('cancel')) {
            if (this._mode === 'free' && !this._max) {
                this.finish();
            } else if (this._mode === 'free' && this._played.length) {
                this._played.pop();
                SoundManager.playCancel();
                this._dirty = true;
            }
            return;
        }
        if (pressed) {
            this.onPlay(pressed);
        }
    };

    Scene_LifeSong.prototype.onPlay = function(n) {
        this.sound(n, false);
        if (this._mode === 'free') {
            if (!this._max) return;
            this._played.push(n);
            if (this._played.length >= this._max) this.finishFree();
            return;
        }
        var expected = this._target[this._played.length];
        if (n === expected) {
            this._played.push(n);
            if (this._played.length === this._target.length) {
                this._phase = 'success';
                this._replayIndex = 0;
                this._timer = 40;
                this.setStatus('♪');
            }
        } else {
            this._mistakes++;
            this._shake = 14;
            this._phase = 'wrong';
            this._timer = 60;
            AudioManager.playSe({ name: 'YY_Cancel', volume: 60, pitch: 100, pan: 0 });
            this.setStatus(this._mistakes >= 2 ? '没关系，看着简谱再来一次' : '差一点……再听一遍');
        }
    };

    Scene_LifeSong.prototype.finishFree = function() {
        if (this._max && this._played.length < 3) {
            SoundManager.playBuzzer();
            this.setStatus('再多弹几个音吧（至少 3 个）');
            return;
        }
        if (!this._max) {
            this.finish();
            return;
        }
        this._phase = 'success';
        this._replayIndex = 0;
        this._timer = 30;
        this.setStatus('♪');
    };

    Scene_LifeSong.prototype.finish = function() {
        if (this._finished) return;
        this._finished = true;
        if (this._variable > 0) {
            if (this._mode === 'free') {
                $gameVariables.setValue(this._variable, this._played.join(','));
            } else {
                $gameVariables.setValue(this._variable, this._mistakes);
            }
        }
        this.popScene();
    };

    Scene_LifeSong.prototype.updateEffects = function() {
        var i;
        var changed = false;
        for (i = 0; i < this._padFlash.length; i++) {
            if (this._padFlash[i] > 0) {
                this._padFlash[i]--;
                changed = true;
            }
        }
        this._ripples = this._ripples.filter(function(r) { r.t++; return r.t < 40; });
        this._floaters = this._floaters.filter(function(f) { f.t++; return f.t < 50; });
        if (this._ripples.length || this._floaters.length) changed = true;
        if (this._shake > 0) {
            this._shake--;
            this._board.x = (this._shake % 4 < 2 ? 1 : -1) * Math.min(this._shake, 6);
        } else {
            this._board.x = 0;
        }
        if (changed) {
            this._dirty = true;
            this.drawEffects();
        }
    };

    Scene_LifeSong.prototype.padColor = function(i, bright) {
        var hex = LifeSong.PAD_COLORS[i];
        var r = parseInt(hex.substr(1, 2), 16), g = parseInt(hex.substr(3, 2), 16), b = parseInt(hex.substr(5, 2), 16);
        // desaturate in 'feel' mode until the colour comes back
        var gray = (r * 0.3 + g * 0.59 + b * 0.11);
        var c = this._color;
        r = gray + (r - gray) * c; g = gray + (g - gray) * c; b = gray + (b - gray) * c;
        var k = bright ? 1.25 : 1;
        r = Math.min(255, Math.round(r * k)); g = Math.min(255, Math.round(g * k)); b = Math.min(255, Math.round(b * k));
        return 'rgb(' + r + ',' + g + ',' + b + ')';
    };

    Scene_LifeSong.prototype.drawPixelBox = function(bmp, x, y, w, h, fill, border) {
        bmp.fillRect(x + 2, y, w - 4, h, border);
        bmp.fillRect(x, y + 2, w, h - 4, border);
        bmp.fillRect(x + 2, y + 2, w - 4, h - 4, fill);
    };

    Scene_LifeSong.prototype.drawEffects = function() {
        var bmp = this._fx.bitmap;
        bmp.clear();
        var self = this;
        this._ripples.forEach(function(r) {
            var s = r.t * (self._mode === 'feel' ? 3 : 2);
            var a = (1 - r.t / 40) * (self._mode === 'feel' ? 0.9 : 0.5);
            var col = self.padColor(r.n - 1, true);
            bmp.paintOpacity = Math.round(a * 255);
            var x = Math.round(r.x - 40 - s), y = Math.round(r.y - 64 - s);
            var w = 80 + s * 2, h = 128 + s * 2;
            bmp.fillRect(x, y, w, 2, col);
            bmp.fillRect(x, y + h - 2, w, 2, col);
            bmp.fillRect(x, y, 2, h, col);
            bmp.fillRect(x + w - 2, y, 2, h, col);
        });
        bmp.paintOpacity = 255;
        bmp.fontFace = 'GameFont, sans-serif';
        bmp.fontSize = 24;
        bmp.outlineWidth = 0;
        this._floaters.forEach(function(f) {
            bmp.paintOpacity = Math.round(255 * (1 - f.t / 50));
            bmp.textColor = self.padColor(f.n - 1, true);
            bmp.drawText('♪', Math.round(f.x - 20 + Math.sin(f.t / 6) * 6), Math.round(f.y - f.t * 2.2 - 30), 40, 36,
                         'center');
        });
        bmp.paintOpacity = 255;
    };

    Scene_LifeSong.prototype.redraw = function() {
        var bmp = this._board.bitmap;
        bmp.clear();
        bmp.fontFace = 'GameFont, sans-serif';
        bmp.outlineWidth = 3;
        bmp.outlineColor = 'rgba(0,0,0,0.6)';
        var W = Graphics.width;
        // header
        var title = this._prompt || (this._mode === 'free' ? '自由演奏' : '跟着弹一遍');
        bmp.fontSize = 24;
        bmp.textColor = '#ffd98a';
        bmp.drawText('♪ ' + title + ' ♪', 0, 40, W, 36, 'center');
        bmp.fontSize = 24;
        bmp.textColor = '#b8b0c8';
        bmp.drawText('乐器：' + (LifeSong.INSTRUMENT_NAMES[this._inst] || ''), 0, 78, W, 36, 'center');
        // score row
        var count = this._mode === 'free' ? Math.max(this._max || 0, this._played.length) : this._target.length;
        if (this._mode === 'free' && !this._max) count = 0;
        var bw = 64, gap = 10;
        var total = count * bw + Math.max(0, count - 1) * gap;
        var x0 = Math.floor((W - total) / 2);
        var hint = this._mistakes >= 2;
        for (var i = 0; i < count; i++) {
            var x = x0 + i * (bw + gap), y = 150;
            var done = i < this._played.length;
            var isCur = this._phase === 'play' && i === this._played.length;
            var listenNow = this._phase === 'listen' && i === this._listenIndex - 1;
            var fill = done ? '#3a3350' : '#26223a';
            var border = isCur ? '#ffd98a' : (done ? '#8a7aa8' : '#4a4466');
            if (listenNow) border = '#ffffff';
            this.drawPixelBox(bmp, x, y, bw, 76, fill, border);
            var label = '·';
            var n = 0;
            if (done) n = this._played[i];
            else if (this._mode !== 'free' && (hint || this._phase === 'success' || this._phase === 'done')) n = this._target[i];
            else if (listenNow) n = this._target[i];
            if (n) label = n === 8 ? '1' : String(n);
            bmp.fontSize = 36;
            bmp.textColor = n ? (done ? '#ffd98a' : '#d8d0e8') : '#6a6488';
            bmp.drawText(label, x, y + 18, bw, 40, 'center');
            if (n === 8) bmp.fillRect(x + bw / 2 - 2, y + 12, 4, 4, bmp.textColor);
        }
        // status
        bmp.fontSize = 24;
        bmp.textColor = '#fff6e4';
        bmp.drawText(this._status, 0, 260, W, 36, 'center');
        // pads
        var pads = this.padCount();
        for (var p = 0; p < pads; p++) {
            var r = this.padRect(p);
            var lift = (p < 8 && this._padFlash[p] > 0) ? 6 : 0;
            if (p === 8) {
                var sel9 = this._cursor === 8;
                this.drawPixelBox(bmp, r.x, r.y, r.width, r.height, sel9 ? '#5a5080' : '#3a3456',
                                  sel9 ? '#ffffff' : '#8a7aa8');
                bmp.fontSize = 24;
                bmp.textColor = '#ffd98a';
                bmp.drawText('完成', r.x, r.y + 46, r.width, 36, 'center');
                continue;
            }
            var sel = this._cursor === p && this._phase === 'play';
            var flash = this._padFlash[p] > 0;
            var col = this.padColor(p, flash);
            this.drawPixelBox(bmp, r.x, r.y - lift, r.width, r.height, col, sel ? '#ffffff' : '#1c1828');
            bmp.fillRect(r.x + 6, r.y - lift + 6, r.width - 12, 4, 'rgba(255,255,255,0.35)');
            bmp.fontSize = 48;
            bmp.textColor = '#fffaf0';
            bmp.drawText(p === 7 ? '1' : String(p + 1), r.x, r.y - lift + 24, r.width, 52, 'center');
            if (p === 7) bmp.fillRect(r.x + r.width / 2 - 3, r.y - lift + 18, 6, 6, '#fffaf0');
            bmp.fontSize = 24;
            bmp.textColor = '#2a2238';
            bmp.outlineWidth = 0;
            bmp.drawText(LifeSong.SOLFEGE[p], r.x, r.y - lift + 84, r.width, 36, 'center');
            bmp.outlineWidth = 3;
        }
        // footer help
        bmp.fontSize = 24;
        bmp.textColor = '#8a84a0';
        var help = this._mode === 'free' ? (this._max ? '数字键 1~8 / 方向键+确定 / 鼠标点击　　Esc：删掉上一个音' :
                                                         '数字键 1~8 / 方向键+确定 / 鼠标点击　　Esc：结束')
                                         : '数字键 1~8 弹奏　也可用 ←→ 选择再按确定，或用鼠标点击';
        bmp.drawText(help, 0, 572, W, 36, 'center');
    };
    window.Scene_LifeSong = Scene_LifeSong;

    // ------------------------------------------------------------------------
    // Menu: show the heroine's life instead of RPG stats
    // ------------------------------------------------------------------------
    Window_MenuStatus.prototype.numVisibleRows = function() {
        return 1;
    };
    Window_MenuStatus.prototype.drawItem = function(index) {
        var actor = $gameParty.members()[index];
        if (!actor) return;
        var rect = this.itemRect(index);
        this.drawItemBackground(index);
        var bitmap = ImageManager.loadCharacter(actor.characterName());
        var self = this;
        var draw = function() {
            var big = ImageManager.isBigCharacter(actor.characterName());
            var pw = bitmap.width / (big ? 3 : 12);
            var ph = bitmap.height / (big ? 4 : 8);
            var n = actor.characterIndex();
            var sx = (big ? 0 : (n % 4 * 3)) * pw + pw;
            var sy = (big ? 0 : Math.floor(n / 4) * 4) * ph;
            self.contents.blt(bitmap, sx, sy, pw, ph, rect.x + 24, rect.y + 24, pw * 2, ph * 2);
        };
        if (bitmap.isReady()) draw(); else bitmap.addLoadListener(draw);
        var x = rect.x + 160;
        this.resetFontSettings();
        this.changeTextColor(this.textColor(6));
        this.drawText(actor.name(), x, rect.y + 20, 300);
        this.resetTextColor();
        var chapter = $gameVariables.value(CHAPTER_VAR);
        this.drawText(chapter ? String(chapter) : '', x, rect.y + 64, rect.width - 180);
        this.changeTextColor(this.systemColor());
        this.drawText('旋律碎片', x, rect.y + 120, 200);
        var got = Number($gameVariables.value(FRAGMENT_VAR)) || 0;
        for (var i = 0; i < FRAGMENT_MAX; i++) {
            this.contents.paintOpacity = i < got ? 255 : 50;
            this.drawIcon(16 + i, x + 130 + i * 40, rect.y + 122);
        }
        this.contents.paintOpacity = 255;
        this.resetTextColor();
        var nick = actor.nickname();
        if (nick) {
            this.changeTextColor(this.textColor(8));
            this.drawText(nick, x, rect.y + 176, rect.width - 180);
            this.resetTextColor();
        }
    };
    Window_Gold.prototype.refresh = function() {
        this.contents.clear();
        var got = Number($gameVariables.value(FRAGMENT_VAR)) || 0;
        this.drawIcon(4, 0, 2);
        this.drawText('碎片 ' + got + '/' + FRAGMENT_MAX, 36, 0, this.contentsWidth() - 36, 'right');
    };
})();
