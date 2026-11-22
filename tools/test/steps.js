// The playthrough route, shared by playthrough.js (headless Chromium) and nw_runner.js
// (inside the real desktop build). Works both as a Node module and as a plain <script>.
(function (root) {
  // switch ids (see tools/build/story_core.py)
  var S = { PRO: 1, CH1: 2, CH2: 3, CH3: 4, CH4: 5, CH5: 6, SOUND_QUEST: 11, SOUNDS_DONE: 12, LESSON_DONE: 13,
    GOT_GUITAR: 21, MOM_TALK: 22, JOINED_BAND: 23, SONG_WRITTEN: 24, FESTIVAL: 26, HOME_NIGHT: 27, PHONE: 31,
    OWNER: 32, DEMO: 33, JIE_BYE: 34, NOTEBOOK: 45, COLOR_BACK: 46, MET_XIAOHE: 47, TEACH: 48, C5_READY: 56,
    CONCERT: 55, C5_GRAVE: 54 };
  // variables: the two story choices, and the player's last phrase as shown in the credits
  var V = { CH2_CHOICE: 12, CH3_CHOICE: 13, FINAL_TEXT: 21 };

  // ALT takes the other answer at the two choices that change later scenes.
  // ['save'] saves to slot 1 mid-game; ['load', map] loads it back after the ending.
  function steps(ALT) {
    return [
      ['newgame'],
      ['idle'], ['expectMap', 1], ['shot', '01_prologue_home'],
      ['menu'],
      ['go', '照片1'], ['idle'],
      ['go', '钢琴'], ['idle'], ['expectMap', 3], ['expectSwitch', S.CH1], ['shot', '02_ch1_grandpa_house'], ['save'],
      ['go', '门'], ['idle'], ['expectMap', 2], ['shot', '03_ch1_village'],
      ['go', '爷爷'], ['idle'], ['expectSwitch', S.SOUND_QUEST],
      ['go', '知了'], ['idle'],
      ['go', '小河'], ['idle'],
      ['go', '风铃'], ['idle'],
      ['go', '卖冰棍的'], ['idle'], ['expectSwitch', S.SOUNDS_DONE],
      ['mistakes', 1],
      ['go', '爷爷'], ['idle'], ['expectSwitch', S.CH2], ['expectMap', 4], ['shot', '04_ch2_home'],
      ['go', '包裹'], ['idle'], ['expectSwitch', S.GOT_GUITAR],
      ['choices', [ALT ? 1 : 0]],
      ['go', '妈妈'], ['idle'], ['expectSwitch', S.MOM_TALK], ['expectVar', [V.CH2_CHOICE, ALT ? 2 : 1]],
      ['go', '家门'], ['idle'], ['expectMap', 5], ['shot', '05_ch2_school'],
      ['go', '阿杰'], ['idle'], ['expectSwitch', S.JOINED_BAND],
      ['choices', [1]],
      ['go', '教学楼大门'], ['idle'], ['expectSwitch', S.HOME_NIGHT], ['expectMap', 4], ['shot', '06_ch2_night'],
      ['go', '包裹'], ['idle'], ['expectSwitch', S.CH3], ['expectMap', 9], ['shot', '07_ch3_basement'],
      ['expectLog', ALT ? '你说你真的很喜欢' : '不用再藏在床底下'],
      ['go', '电话'], ['idle'], ['expectSwitch', S.PHONE],
      ['go', '门'], ['idle'], ['expectMap', 8], ['shot', '08_ch3_city'],
      ['choices', [ALT ? 0 : 1]],
      ['go', '老板娘'], ['idle'], ['expectSwitch', S.OWNER], ['expectVar', [V.CH3_CHOICE, ALT ? 1 : 2]],
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
      ['expectLog', ALT ? '你看，我吃了一辈子呢' : '其实你早就知道了吧'],
      ['go', '钢琴'], ['idle'],
      ['go', '小禾（大人）'], ['idle'],
      ['go', '阿杰（老年）'], ['idle'],
      ['expectLog', ALT ? '原来音音也会累啊' : '傻的是我'],
      ['go', '小雨（大人）'], ['idle'], ['expectSwitch', S.C5_READY],
      ['go', '钢琴'], ['title'],
      ['expectVar', [V.FINAL_TEXT, '5 6 1 6 5']],
      ['expectLog', ['credits ', '作曲　你', '\\V[' + V.FINAL_TEXT + ']']],
      ['load', 3],
    ];
  }

  var api = { S: S, V: V, steps: steps };
  root.YY_TEST = api;
  if (typeof module === 'object' && module && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : this);
