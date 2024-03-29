const CELL_SIZE = 30;
const BACKGROUND_COLOR = "#444";

class Game {
  constructor(canvasId, cellSize) {
    this.canvas = document.getElementById("myCanvas").getContext("2d");
    document.onkeydown = this.handleKeyboardEvent.bind(this);

    this.cellSize = cellSize;
    this.width = document.getElementById("myCanvas").width;
    this.height = document.getElementById("myCanvas").height;

    this.lightCycles = [];
    this.recordedPositions = [];
    this.opponent_position = 0;
    this.my_position = 0;
  }

  addLightCycle(lightCycle) {
    this.lightCycles.push(Object.assign({}, lightCycle));
  }

  handleKeyboardEvent(e) {
    for (let i = 0; i < this.lightCycles.length; i++) {
      const lightCycle = this.lightCycles[i];

      if (!lightCycle.active) {
        continue;
      }

      let newDirection;
      if (e.keyCode === lightCycle.keyBindings.up) {
        newDirection = { x: 0, y: -1 };
      } else if (e.keyCode === lightCycle.keyBindings.down) {
        newDirection = { x: 0, y: 1 };
      } else if (e.keyCode === lightCycle.keyBindings.left) {
        newDirection = { x: -1, y: 0 };
      } else if (e.keyCode === lightCycle.keyBindings.right) {
        newDirection = { x: 1, y: 0 };
      } else {
        continue;
      }

      // If we want to go on the direction we come from, do nothing.
      if (
        (newDirection.x === lightCycle.direction.x &&
          newDirection.y !== lightCycle.direction.y) ||
        (newDirection.y === lightCycle.direction.y &&
          newDirection.x !== lightCycle.direction.x)
      ) {
        continue;
      }

      lightCycle.direction = newDirection;
    }
  }

  playerShouldDie(lightCycle) {
    if (
      lightCycle.position.x < 0 ||
      lightCycle.position.y < 0 ||
      lightCycle.position.x >= this.width ||
      lightCycle.position.y >= this.height
    ) {
      console.log("wall");
      return true;
    }

    for (let i = 0; i < this.recordedPositions.length; i++) {
      const position = this.recordedPositions[i].point;

      if (
        lightCycle.position.x - (this.cellSize - 1) / 2 <= position.x &&
        position.x <= lightCycle.position.x + (this.cellSize - 1) / 2 + 1 &&
        lightCycle.position.y - (this.cellSize - 1) / 2 <= position.y &&
        position.y <= lightCycle.position.y + (this.cellSize - 1) / 2 + 1
      ) {
        return true;
      }
    }

    return false;
  }

  updateCell(newPosition, newColor) {
    for (let i = 0; i < this.recordedPositions.length; i++) {
      const position = this.recordedPositions[i];

      if (position.point === newPosition) {
        position.color = newColor;
        return;
      }
    }

    // There was no position recorded for this point, let's create a new one
    this.recordedPositions.push({
      point: newPosition,
      color: newColor
    });
  }

  finished() {
    const activePlayers = this.lightCycles.reduce(
      (a, v) => a + (v.active ? 1 : 0),
      0
    );
    return activePlayers <= 1;
  }

  getWinner() {
    if (!this.finished()) {
      return null;
    }

    return this.lightCycles.find(e => e.active);
  }

  update() {
    for (let i = 0; i < this.lightCycles.length; i++) {
      let lightCycle = this.lightCycles[i];

      if (!lightCycle.active) {
          continue;
      }
      let previousPosition = lightCycle.position;
      // First we update the positions of the light cycles
      // along side with the records of the cells.
      // console.log(lightCycle.direction);
      lightCycle.position = {
          x: lightCycle.position.x + lightCycle.direction.x * this.cellSize,
          y: lightCycle.position.y + lightCycle.direction.y * this.cellSize
      };

      if (i===0)
      {
        this.my_position = {"x": lightCycle.position.x, "y": lightCycle.position.y};
      }
      else
      {
        this.opponent_position = {"x": lightCycle.position.x, "y": lightCycle.position.y};
      }

      // Then we check if the player is dead and draw the cell
      // in consequence.
      if (!this.playerShouldDie(lightCycle)) {
        this.updateCell(lightCycle.position, lightCycle.color);
        this.updateCell(previousPosition, lightCycle.traceColor);
      } else {
        lightCycle.position = previousPosition;
        lightCycle.active = false;
        this.updateCell(lightCycle.position, "#fff");
      }
    }

    // Finally, we draw the canvas with the update model.
    this.draw();
  }

  draw() {
    // We draw all the canvas with a color

    this.canvas.fillStyle = BACKGROUND_COLOR;
    this.canvas.fillRect(0, 0, this.width, this.height);

    // Now we draw all the position recorded.
    for (let i = 0; i < this.recordedPositions.length; i++) {
      const { point: position, color } = this.recordedPositions[i];

      this.canvas.fillStyle = color;
      this.canvas.fillRect(
        position.x - (this.cellSize - 1) / 2,
        position.y - (this.cellSize - 1) / 2,
        this.cellSize,
        this.cellSize
      );
    }
  }
}

players = [
  {
    name: "Mario",
    position: {
      x: 0,
      y: 0
    },
    direction: { x: 0, y: -1 },
    color: "#8B0000",
    traceColor: "#f00",

    keyBindings: {
      up: 38,
      down: 40,
      left: 37,
      right: 39
    },

    active: true,
    score: 0
  },
  {
    name: "Luigi",
    position: {
      x: 0,
      y: 0
    },
    direction: { x: 1, y: 0 },
    color: "#006400",
    traceColor: "#0f0",

    keyBindings: {
      up: 87,
      down: 83,
      left: 65,
      right: 68
    },

    active: true,
    score: 0
  }
];

function load() {
  const game = new Game("myCanvas", CELL_SIZE);
  game.my_position = {"x": 15, "y": 15};
  game.opponent_position = {"x": 585, "y": 585};
  for (let i = 0; i < players.length; i++) {
      if (i < 1){
          players[i].position = {
      x: CELL_SIZE/2,
      y: CELL_SIZE/2
    };
      }
      else{
              players[i].position = {
      x: Math.floor(
        document.getElementById("myCanvas").width - CELL_SIZE/2
      ),
      y: Math.floor(
        document.getElementById("myCanvas").height - CELL_SIZE/2
      )
    };
      }

    game.addLightCycle(players[i]);
  }
      directions = [
      { x: 0, y: -1 },
      { x: 0, y: 1 },
      { x: 1, y: 0 },
      { x: -1, y: 0 }
    ];
  // 0 1 是下
  // -1 0 是向上
  // 0 -1 向左
  // 1 0 向右
  players[0].direction =
      directions[1];
  players[1].direction =
      directions[3];

  const scoreItems = players.map(e => {
    return `
<li class="nav-item active">
  <a class="nav-link" href="#">${e.name} :: ${e.score}
    <span class="sr-only">(current)</span>
  </a>
</li>
  `;
  });

  document.getElementById("score-list").innerHTML = scoreItems;

  return game;
}

let game = load();
let beginningDate = performance.now();


function main() {
  game.update();
  if (game.finished()) {
    const winner = game.getWinner();
    if (winner) {
      for (let i = 0; i < players.length; i++) {
        if (players[i].name === winner.name) {
          players[i].score += 1;
        }
      }
    }
    game = load();
    beginningDate = performance.now();
  }

  // Decrease the timeout every 2 seconds
  const elapsedTime = performance.now() - beginningDate;
  const decreasedTimeout = 300 - CELL_SIZE * Math.floor(elapsedTime / 900);
  setTimeout(function() {
      //console.log(game.recordedPositions);
      $.ajax({type:"POST", url:"/ajax/add/",
      //data:{'x':lightCycle.direction.x+1, 'y':lightCycle.direction.y+1},
        traditional:true,
      data:{"position":JSON.stringify(game.recordedPositions), "opponent_position":JSON.stringify(game.opponent_position), "my_position": JSON.stringify(game.my_position)},
      async :false,
      dataType:"json",
      success: function(ret){
        if (typeof(game.lightCycles[0].direction) != undefined)
        {
          game.lightCycles[0].direction = { x: ret.x, y: ret.y };
        }
      },
      error: function(rs, e) {
            alert("fail");
      }
      });
    main();
  }, decreasedTimeout);
}

main();
