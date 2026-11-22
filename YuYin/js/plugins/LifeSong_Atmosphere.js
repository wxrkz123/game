//=============================================================================
// LifeSong_Atmosphere.js  —  《余音》氛围插件
//=============================================================================
/*:
 * @plugindesc 《余音》氛围：灯光、窗口照进来的光柱、飘落的树叶和花瓣、萤火虫、云影、画面暗角。
 * @author 《余音》制作组
 *
 * @param Vignette
 * @desc 画面四周变暗的程度（0 = 不变暗，1 = 很暗）。可以在地图备注里用 <暗角: 0.5> 单独设置。
 * @default 0.3
 *
 * @help
 * ============================================================================
 *  用法：在“地图属性 → 备注”里写下面这些标签（中文、英文都可以）
 * ============================================================================
 *
 *  <氛围: 落叶 云影>            这张地图一直有这些效果
 *  <氛围@3: 落叶>               只在 3 号开关打开时才有（比如“第二章”开关）
 *
 *      可用的效果：
 *        花粉 (pollen)       夏天空气里飘着的细小光点
 *        萤火虫 (fireflies)  画面越暗越亮的萤火虫
 *        落叶 (leaves)       秋天飘落的树叶
 *        花瓣 (petals)       春天飘落的花瓣
 *        灰尘 (dust)         屋子里慢慢浮动的灰尘
 *        光点 (motes)        黄昏时金色的小光点
 *        云影 (clouds)       地面上慢慢移过的云的影子（白天才看得见）
 *
 *  <灯光: 4.5 6.2 3 #ffd27a>   在第 4.5 列、第 6.2 行（可以写小数）放一盏
 *                              半径 3 格、颜色 #ffd27a 的灯。
 *  <灯光: 4.5 6.2 3 #ffd27a 0.8 闪>
 *                              第 5 个数是亮度（默认 1），写“闪”会轻轻闪烁（烛火、灯笼）。
 *  <灯光@55: ...>              只在 55 号开关打开时亮。
 *
 *      灯光会随着画面色调自动变化：白天只有淡淡一圈，
 *      用“更改画面色调”把画面调暗（黄昏、夜晚），灯就会亮起来。
 *
 *  <光柱: 5 2>                 第 5 列、第 2 行的窗户照进一道斜斜的阳光，
 *  <光柱: 5 2 4>               第 3 个数是光柱的长度（格），默认 4。
 *                              天越暗光柱越淡，晚上会消失。
 *
 *  <暗角: 0.5>                 这张地图的暗角强度。
 *
 *  事件也能发光：在事件的“备注”里写 <灯光: 2 #ffcf6b>（半径、颜色、[亮度]、[闪]），
 *  灯光会跟着这个事件走，比如提着灯笼的人。
 *
 *  本游戏的地图是用 tools/build 自动生成的，放路灯、窗户、灯笼时会自动写好这些标签。
 */

(function() {
    'use strict';

    var params = PluginManager.parameters('LifeSong_Atmosphere');
    var DEFAULT_VIGNETTE = Number(params['Vignette'] || 0.3);

    var NAMES = {
        '花粉': 'pollen', '萤火虫': 'fireflies', '落叶': 'leaves', '花瓣': 'petals',
        '灰尘': 'dust', '光点': 'motes', '云影': 'clouds'
    };
    var TAGS = {
        '氛围': 'atmos', '灯光': 'light', '光柱': 'beam', '暗角': 'vignette',
        'atmos': 'atmos', 'light': 'light', 'beam': 'beam', 'vignette': 'vignette'
    };

    // ------------------------------------------------------------------------
    // reading the notes
    // ------------------------------------------------------------------------
    function parseNote(note) {
        var out = { effects: [], lights: [], beams: [], vignette: null };
        var re = /<\s*([^\s@:：>]+)\s*(?:@\s*(\d+))?\s*[:：]\s*([^>]*)>/g;
        var m;
        while ((m = re.exec(note || ''))) {
            var tag = TAGS[m[1].toLowerCase()] || TAGS[m[1]];
            if (!tag) continue;
            var sw = Number(m[2] || 0);
            var args = m[3].split(/[\s,，]+/).filter(function(s) { return s; });
            if (tag === 'atmos') {
                args.forEach(function(a) {
                    out.effects.push({ name: NAMES[a] || a.toLowerCase(), sw: sw });
                });
            } else if (tag === 'light') {
                out.lights.push(parseLight(args, sw, false));
            } else if (tag === 'beam') {
                out.beams.push({ x: Number(args[0]), y: Number(args[1]), len: Number(args[2] || 4), sw: sw });
            } else if (tag === 'vignette') {
                out.vignette = Number(args[0]);
            }
        }
        return out;
    }

    // map lights: x y radius color [strength] [闪]; event lights: radius color [strength] [闪]
    function parseLight(args, sw, onEvent) {
        var nums = [], color = '#ffd27a', flicker = false;
        args.forEach(function(a) {
            if (a.charAt(0) === '#') color = a;
            else if (a === '闪' || a.toLowerCase() === 'flicker') flicker = true;
            else nums.push(Number(a));
        });
        if (onEvent) nums.unshift(0, 0);
        return { x: nums[0], y: nums[1], r: nums[2] || 2, color: color,
                 strength: nums.length > 3 ? nums[3] : 1, flicker: flicker, sw: sw };
    }

    function switchOn(sw) {
        return !sw || $gameSwitches.value(sw);
    }

    // how dark / how grey the screen tint currently is (0..1)
    function toneDarkness() {
        var t = $gameScreen.tone();
        return Math.max(0, Math.min(1, -(t[0] + t[1] + t[2]) / 3 / 85 + t[3] / 255 * 0.15));
    }
    function toneGrey() {
        return $gameScreen.tone()[3] / 255;
    }

    // ------------------------------------------------------------------------
    // textures (made once, from tiny pixel drawings or soft gradients)
    // ------------------------------------------------------------------------
    var TEX = {};

    function pixelBitmap(rows, palette) {
        var bmp = new Bitmap(rows[0].length, rows.length);
        rows.forEach(function(row, y) {
            for (var x = 0; x < row.length; x++) {
                var c = palette[row.charAt(x)];
                if (c) bmp.fillRect(x, y, 1, 1, c);
            }
        });
        return bmp;
    }

    function glowBitmap(size, color, core) {
        var bmp = new Bitmap(size, size);
        var ctx = bmp.context;
        var r = size / 2;
        var g = ctx.createRadialGradient(r, r, 0, r, r, r);
        g.addColorStop(0, color);
        if (core) g.addColorStop(core, color);
        g.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = g;
        ctx.globalAlpha = 1;
        ctx.fillRect(0, 0, size, size);
        bmp.smooth = true;
        bmp._setDirty();
        return bmp;
    }

    function texture(name) {
        if (TEX[name]) return TEX[name];
        var bmp;
        switch (name) {
        case 'pollen': bmp = pixelBitmap(['ab', 'bb'], { a: '#fffbe6', b: '#f6e7a8' }); break;
        case 'dust': bmp = pixelBitmap(['a'], { a: '#f3e6cc' }); break;
        case 'leaf0': bmp = pixelBitmap(['.ab', 'abb', 'bc.'], { a: '#f3b24c', b: '#e0843a', c: '#9a5a2a' }); break;
        case 'leaf1': bmp = pixelBitmap(['ab.', 'bbc', '.c.'], { a: '#e8a23e', b: '#c8562e', c: '#7a3a22' }); break;
        case 'leaf2': bmp = pixelBitmap(['.a', 'ab', 'b.'], { a: '#f7d55c', b: '#d9a33a' }); break;
        case 'petal0': bmp = pixelBitmap(['ab', 'bb'], { a: '#fff0f4', b: '#f6b8c8' }); break;
        case 'petal1': bmp = pixelBitmap(['ab.', '.bb'], { a: '#fde3ea', b: '#efa0b8' }); break;
        case 'firefly': bmp = glowBitmap(24, 'rgba(214,255,140,1)', 0.12); break;
        case 'mote': bmp = glowBitmap(12, 'rgba(255,220,140,1)', 0.2); break;
        case 'cloud':
            bmp = new Bitmap(320, 180);
            (function(ctx) {
                ctx.save();
                ctx.scale(1, 180 / 320);
                var g = ctx.createRadialGradient(160, 160, 10, 160, 160, 160);
                g.addColorStop(0, 'rgba(20,30,40,0.9)');
                g.addColorStop(0.55, 'rgba(20,30,40,0.55)');
                g.addColorStop(1, 'rgba(20,30,40,0)');
                ctx.fillStyle = g;
                ctx.fillRect(0, 0, 320, 320);
                ctx.restore();
            })(bmp.context);
            bmp.smooth = true;
            bmp._setDirty();
            break;
        default:
            if (name.indexOf('light:') === 0) bmp = glowBitmap(128, name.slice(6), 0.05);
        }
        TEX[name] = bmp;
        return bmp;
    }

    function hexToRgba(hex, a) {
        var h = hex.replace('#', '');
        if (h.length === 3) h = h.replace(/(.)/g, '$1$1');
        var n = parseInt(h, 16);
        return 'rgba(' + ((n >> 16) & 255) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + a + ')';
    }

    // a sun shaft falling from a window towards the lower right
    function beamBitmap(len) {
        var tw = 48, w = Math.round(tw * (1.2 + len * 0.55)), h = Math.round(tw * (len + 0.5));
        var bmp = new Bitmap(w, h);
        var ctx = bmp.context;
        var g = ctx.createLinearGradient(0, 0, w * 0.35, h);
        g.addColorStop(0, 'rgba(255,240,200,0.55)');
        g.addColorStop(0.6, 'rgba(255,236,190,0.22)');
        g.addColorStop(1, 'rgba(255,236,190,0)');
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.moveTo(4, 0);
        ctx.lineTo(tw - 4, 0);
        ctx.lineTo(w, h);
        ctx.lineTo(w - tw * 1.6, h);
        ctx.closePath();
        ctx.fill();
        bmp.smooth = true;
        bmp._setDirty();
        return bmp;
    }

    function vignetteBitmap(w, h) {
        var bmp = new Bitmap(w, h);
        var ctx = bmp.context;
        ctx.save();
        ctx.translate(w / 2, h / 2);
        ctx.scale(1, h / w);
        var g = ctx.createRadialGradient(0, 0, w * 0.28, 0, 0, w * 0.72);
        g.addColorStop(0, 'rgba(10,6,20,0)');
        g.addColorStop(0.6, 'rgba(10,6,20,0.45)');
        g.addColorStop(1, 'rgba(10,6,20,1)');
        ctx.fillStyle = g;
        ctx.fillRect(-w, -w, w * 2, w * 2);
        ctx.restore();
        bmp.smooth = true;
        bmp._setDirty();
        return bmp;
    }

    // ------------------------------------------------------------------------
    // particles
    // ------------------------------------------------------------------------
    var KINDS = {
        pollen:    { count: 28, tex: ['pollen'], scale: 2, vx: [-0.25, 0.25], vy: [-0.3, -0.05], sway: 0.25, alpha: [0.35, 0.8], twinkle: true },
        dust:      { count: 34, tex: ['dust'], scale: 2, vx: [-0.08, 0.08], vy: [-0.12, 0.06], sway: 0.12, alpha: [0.2, 0.5], twinkle: true },
        leaves:    { count: 22, tex: ['leaf0', 'leaf1', 'leaf2'], scale: 2, vx: [0.35, 0.9], vy: [0.55, 1.1], sway: 1.1, alpha: [0.9, 1], spin: true },
        petals:    { count: 26, tex: ['petal0', 'petal1'], scale: 2, vx: [0.25, 0.7], vy: [0.4, 0.8], sway: 0.9, alpha: [0.85, 1], spin: true },
        fireflies: { count: 18, tex: ['firefly'], scale: 1, vx: [-0.3, 0.3], vy: [-0.3, 0.3], sway: 0.6, alpha: [0.6, 1], glow: true, pulse: true, night: true },
        motes:     { count: 22, tex: ['mote'], scale: 1, vx: [-0.12, 0.12], vy: [-0.25, -0.06], sway: 0.3, alpha: [0.4, 0.85], glow: true, pulse: true }
    };

    function rand(range) {
        return range[0] + Math.random() * (range[1] - range[0]);
    }

    function ParticleSystem(kind, parent) {
        this.kind = kind;
        this.cfg = KINDS[kind];
        this.sprites = [];
        this.margin = 32;
        var W = Graphics.width, H = Graphics.height;
        for (var i = 0; i < this.cfg.count; i++) {
            var s = new Sprite(texture(this.cfg.tex[i % this.cfg.tex.length]));
            s.anchor.x = s.anchor.y = 0.5;
            s.scale.x = s.scale.y = this.cfg.scale;
            if (this.cfg.glow) s.blendMode = Graphics.BLEND_ADD;
            s.wx = Math.random() * (W + this.margin * 2);
            s.wy = Math.random() * (H + this.margin * 2);
            s.vx = rand(this.cfg.vx);
            s.vy = rand(this.cfg.vy);
            s.phase = Math.random() * Math.PI * 2;
            s.freq = 0.01 + Math.random() * 0.03;
            s.baseAlpha = rand(this.cfg.alpha);
            s.spin = this.cfg.spin ? (Math.random() - 0.5) * 0.1 : 0;
            parent.addChild(s);
            this.sprites.push(s);
        }
    }

    ParticleSystem.prototype.update = function(t, ox, oy, dark) {
        var cfg = this.cfg, m = this.margin;
        var W = Graphics.width + m * 2, H = Graphics.height + m * 2;
        var shown = cfg.night ? Math.min(1, dark * 1.8) : 1;
        this.sprites.forEach(function(s) {
            s.wx += s.vx + Math.sin(t * s.freq + s.phase) * cfg.sway;
            s.wy += s.vy + (cfg.glow ? Math.cos(t * s.freq * 0.7 + s.phase) * cfg.sway * 0.6 : 0);
            var x = ((s.wx - ox) % W + W) % W - m;
            var y = ((s.wy - oy) % H + H) % H - m;
            s.x = Math.round(x / 2) * 2;
            s.y = Math.round(y / 2) * 2;
            if (cfg.spin) {
                s.rotation += s.spin;
                s.scale.x = cfg.scale * Math.cos(t * s.freq * 2 + s.phase);
            }
            var a = s.baseAlpha;
            if (cfg.pulse) a *= 0.55 + 0.45 * Math.sin(t * s.freq * 3 + s.phase);
            else if (cfg.twinkle) a *= 0.75 + 0.25 * Math.sin(t * s.freq * 4 + s.phase);
            s.opacity = Math.round(255 * a * shown);
        });
    };

    ParticleSystem.prototype.setVisible = function(v) {
        this.sprites.forEach(function(s) { s.visible = v; });
    };

    // big soft shadows that drift over the ground on sunny maps
    function CloudShadows(parent) {
        this.sprites = [];
        this.area = Graphics.width + 640;
        for (var i = 0; i < 4; i++) {
            var s = new Sprite(texture('cloud'));
            s.scale.x = s.scale.y = 1.4 + Math.random() * 0.8;
            s.wx = i * this.area / 4 + Math.random() * 120;
            s.wy = Math.random() * (Graphics.height + 300) - 150;
            s.vx = 0.18 + Math.random() * 0.12;
            parent.addChild(s);
            this.sprites.push(s);
        }
    }

    CloudShadows.prototype.update = function(t, ox, oy, dark) {
        var A = this.area, H = Graphics.height + 400;
        this.sprites.forEach(function(s) {
            s.wx += s.vx;
            s.x = ((s.wx - ox) % A + A) % A - 480;
            s.y = ((s.wy - oy) % H + H) % H - 200;
            s.opacity = Math.round(255 * 0.13 * Math.max(0, 1 - dark * 2.5));
        });
    };

    CloudShadows.prototype.setVisible = function(v) {
        this.sprites.forEach(function(s) { s.visible = v; });
    };

    // ------------------------------------------------------------------------
    // the atmosphere of one map
    // ------------------------------------------------------------------------
    function Atmosphere(spriteset) {
        this._spriteset = spriteset;
        this._config = parseNote($dataMap ? $dataMap.note : '');
        this._t = 0;
        this._low = new Sprite();       // tinted together with the map: clouds, leaves, dust...
        this._glow = new Sprite();      // above the tint: lamps, sun shafts, fireflies
        this._systems = {};
        this._lights = [];
        this._beams = [];
        spriteset._baseSprite.addChild(this._low);
        this.createBeams();
        this.createLights();
        this.createParticles();
        this.createVignette();
    }

    Atmosphere.prototype.tileW = function() { return $gameMap.tileWidth(); };
    Atmosphere.prototype.tileH = function() { return $gameMap.tileHeight(); };

    Atmosphere.prototype.createParticles = function() {
        var self = this;
        this._config.effects.forEach(function(e) {
            if (self._systems[e.name]) {
                self._systems[e.name].sws.push(e.sw);
                return;
            }
            var sys;
            if (e.name === 'clouds') sys = new CloudShadows(self._low);
            else if (KINDS[e.name]) sys = new ParticleSystem(e.name, KINDS[e.name].glow ? self._glow : self._low);
            if (sys) {
                sys.sws = [e.sw];
                self._systems[e.name] = sys;
            }
        });
    };

    Atmosphere.prototype.createLights = function() {
        var self = this;
        this._config.lights.forEach(function(l) {
            self._lights.push(self.makeLight(l, null));
        });
        $gameMap.events().forEach(function(ev) {
            var note = ev.event().note;
            var m = /<\s*(?:灯光|light)\s*[:：]\s*([^>]*)>/i.exec(note || '');
            if (m) {
                var args = m[1].split(/[\s,，]+/).filter(function(s) { return s; });
                self._lights.push(self.makeLight(parseLight(args, 0, true), ev));
            }
        });
    };

    Atmosphere.prototype.makeLight = function(l, ev) {
        var s = new Sprite(texture('light:' + hexToRgba(l.color, 1)));
        s.anchor.x = s.anchor.y = 0.5;
        s.blendMode = Graphics.BLEND_ADD;
        var size = l.r * this.tileW() * 2 / 128;
        s.scale.x = s.scale.y = size;
        s.cfg = l;
        s.event = ev;
        s.seed = Math.random() * 100;
        this._glow.addChild(s);
        return s;
    };

    Atmosphere.prototype.createBeams = function() {
        var self = this;
        this._config.beams.forEach(function(b) {
            var s = new Sprite(beamBitmap(b.len));
            s.blendMode = Graphics.BLEND_ADD;
            s.cfg = b;
            self._glow.addChild(s);
            self._beams.push(s);
        });
    };

    Atmosphere.prototype.createVignette = function() {
        var v = this._config.vignette != null ? this._config.vignette : DEFAULT_VIGNETTE;
        if (v <= 0) return;
        this._vignette = new Sprite(vignetteBitmap(Graphics.width, Graphics.height));
        this._vignette.opacity = Math.round(255 * Math.min(1, v));
        this._glow.addChild(this._vignette);
    };

    Atmosphere.prototype.update = function() {
        this._t++;
        var t = this._t;
        var tw = this.tileW(), th = this.tileH();
        var ox = $gameMap.displayX() * tw, oy = $gameMap.displayY() * th;
        var dark = toneDarkness(), grey = toneGrey();
        var key;
        for (key in this._systems) {
            var sys = this._systems[key];
            var on = sys.sws.some(switchOn);
            sys.setVisible(on);
            if (on) sys.update(t, ox, oy, dark);
        }
        // lamps: a faint halo by day, bright at dusk and night, almost colourless in a grey world
        var lampLevel = (0.22 + dark * 1.1) * (1 - grey * 0.85);
        this._lights.forEach(function(s) {
            var c = s.cfg;
            var visible = switchOn(c.sw);
            if (s.event) {
                // only while the event's current page shows a graphic (e.g. lanterns hung in chapter 5)
                visible = visible && !s.event._erased && !!s.event.page() && !s.event.isTransparent() &&
                    !!(s.event.characterName() || s.event.tileId());
                s.x = s.event.screenX();
                s.y = s.event.screenY() - th / 2;
            } else {
                s.x = Math.round($gameMap.adjustX(c.x) * tw);
                s.y = Math.round($gameMap.adjustY(c.y) * th);
            }
            s.visible = visible;
            var a = Math.min(1, lampLevel * c.strength);
            if (c.flicker) a *= 0.88 + 0.08 * Math.sin(t * 0.21 + s.seed) + 0.04 * Math.sin(t * 0.53 + s.seed * 2);
            s.opacity = Math.round(255 * a * 0.85);
        });
        // sun shafts fade out as the light outside goes
        var sun = Math.max(0, 1 - dark * 2.2) * (1 - grey * 0.9);
        this._beams.forEach(function(s) {
            var c = s.cfg;
            s.visible = switchOn(c.sw);
            s.x = Math.round($gameMap.adjustX(c.x) * tw);
            s.y = Math.round($gameMap.adjustY(c.y + 0.5) * th);
            s.opacity = Math.round(255 * sun * (0.8 + 0.2 * Math.sin(t * 0.01)));
        });
    };

    // ------------------------------------------------------------------------
    // hooks
    // ------------------------------------------------------------------------
    var _createToneChanger = Spriteset_Map.prototype.createToneChanger;
    Spriteset_Map.prototype.createToneChanger = function() {
        _createToneChanger.call(this);
        // after the tone changer, so lamps keep their colour in dark scenes (WebGL and canvas)
        this._lsAtmos = new Atmosphere(this);
        this.addChild(this._lsAtmos._glow);
    };

    var _update = Spriteset_Map.prototype.update;
    Spriteset_Map.prototype.update = function() {
        _update.call(this);
        if (this._lsAtmos) this._lsAtmos.update();
    };

    // for tests
    window.LSAtmosphere = { parseNote: parseNote };
})();
