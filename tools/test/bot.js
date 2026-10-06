// Injected into the game page: a tiny auto-player used by the playthrough test.
(function () {
  var Bot = (window.Bot = {
    choices: [],          // queue of choice indexes to pick (default 0)
    mistakes: 0,          // how many wrong notes to play in the next mini-games (tests the retry path)
    freeNotes: [5, 6, 8, 6, 5],
    log: [],
    pressing: 0,
    frame: 0,
    minigames: 0,
    cards: 0,
    lastMap: 0,
  });

  // run the game faster in tests
  SceneManager._deltaTime = 1.0 / 240;
  Game_Character.prototype.searchLimit = function () { return 300; };

  function press(name) {
    Input._currentState[name] = true;
    Bot.pressing = 2;
  }

  var _updateInputData = SceneManager.updateInputData;
  SceneManager.updateInputData = function () {
    if (Bot.pressing > 0) {
      Bot.pressing--;
      if (Bot.pressing === 0) {
        Input._currentState.ok = false;
        Input._currentState.cancel = false;
      }
    }
    _updateInputData.call(this);
    Bot.tick();
  };

  Bot.scene = function () { return SceneManager._scene; };

  Bot.tick = function () {
    Bot.frame++;
    var scene = SceneManager._scene;
    if (!scene) return;
    if (scene instanceof Scene_Map && $gameMap && $gameMap.mapId() !== Bot.lastMap) {
      Bot.lastMap = $gameMap.mapId();
      Bot.log.push('map ' + Bot.lastMap);
    }
    if (scene.constructor.name === 'Scene_LifeSong' || (window.Scene_LifeSong && scene instanceof window.Scene_LifeSong)) {
      Bot.playMinigame(scene);
      return;
    }
    if (window.Scene_LSChapter && scene instanceof window.Scene_LSChapter) {
      if (!scene._botSeen) { scene._botSeen = true; Bot.cards++; Bot.log.push('card ' + scene._title); }
      if (scene._count > 90 && Bot.frame % 8 === 0) press('ok');
      return;
    }
    if (scene instanceof Scene_Map) {
      var mw = scene._messageWindow;
      if (!mw) return;
      var cw = mw._choiceWindow;
      if (cw && cw.active && cw.isOpen()) {
        if (!cw._botChosen) {
          var idx = Bot.choices.length ? Bot.choices.shift() : 0;
          cw._botChosen = true;
          cw.select(idx);
          Bot.log.push('choice ' + idx + ' of ' + $gameMessage.choices().join('/'));
          press('ok');
        }
        return;
      }
      if (cw) cw._botChosen = false;
      if ($gameMessage.isBusy() && Bot.frame % 4 === 0) {
        press('ok');
      }
      // scrolling text (credits) — let it run, pressing ok speeds it up
      if (scene._scrollTextWindow && scene._scrollTextWindow.visible && Bot.frame % 30 === 0) press('ok');
    }
  };

  Bot.playMinigame = function (scene) {
    if (!scene._botSeen) {
      scene._botSeen = true;
      Bot.minigames++;
      Bot.log.push('minigame ' + scene._mode + ' ' + scene._inst + ' [' + scene._target.join(',') + ']');
    }
    if (Bot.frame % 6 !== 0) return;
    if (scene._phase === 'play') {
      if (scene._mode === 'free') {
        if (!scene._max) { scene.finish(); return; }
        if (scene._played.length < Bot.freeNotes.length && scene._played.length < scene._max) {
          scene.onPlay(Bot.freeNotes[scene._played.length]);
        } else {
          scene.finishFree();
        }
        return;
      }
      var want = scene._target[scene._played.length];
      if (Bot.mistakes > 0 && scene._played.length === 2) {
        Bot.mistakes--;
        Bot.log.push('deliberate mistake');
        scene.onPlay(want === 1 ? 2 : 1);
        return;
      }
      scene.onPlay(want);
    } else if (scene._phase === 'done') {
      press('ok');
    }
  };

  Bot.idle = function () {
    var scene = SceneManager._scene;
    return scene instanceof Scene_Map && !SceneManager.isSceneChanging() && scene.isActive() &&
      !$gameMap.isEventRunning() && !$gameMessage.isBusy() && !$gamePlayer.isMoving() &&
      !$gamePlayer.isTransferring() && !scene._messageWindow.isOpening() && !scene._messageWindow.isClosing() &&
      $gameScreen.brightness() > 0;
  };

  Bot.findEvent = function (name) {
    var evs = $gameMap.events().filter(function (e) {
      return e.event().name === name && e.page() && !e._erased;
    });
    return evs[0] || null;
  };

  // walk to an event (or onto it for touch events) using the engine's pathfinding
  Bot.goTo = function (name) {
    var ev = Bot.findEvent(name);
    if (!ev) return 'no-event:' + name;
    $gameTemp.setDestination(ev.x, ev.y);
    Bot.target = ev;
    return 'ok';
  };

  Bot.state = function () {
    var s = SceneManager._scene;
    return {
      scene: s ? s.constructor.name : null,
      map: $gameMap ? $gameMap.mapId() : 0,
      x: $gamePlayer ? $gamePlayer.x : 0,
      y: $gamePlayer ? $gamePlayer.y : 0,
      idle: Bot.idle(),
      busy: $gameMessage ? $gameMessage.isBusy() : false,
      running: $gameMap ? $gameMap.isEventRunning() : false,
      text: $gameMessage ? $gameMessage.allText().slice(0, 60) : '',
      dest: $gameTemp ? $gameTemp.isDestinationValid() : false,
      minigames: Bot.minigames,
      cards: Bot.cards,
    };
  };

  Bot.switches = function (ids) {
    return ids.map(function (i) { return $gameSwitches.value(i); });
  };
})();
