# API do ambiente

Guia rápido para quem vai construir agentes ou a interface. Todo o código fica em
`src/minesweeper/environment/` e é importado assim:

```python
from minesweeper.environment import Game, get_config, GameConfig, HIDDEN, FLAGGED
```

## Criar uma partida

```python
game = Game(get_config("easy"), seed=42)       # easy 9x9/10, medium 16x16/40, hard 16x30/99
game = Game(GameConfig(rows=8, cols=8, mines=12), seed=1)   # tamanho livre
```

As minas só são sorteadas na primeira jogada `reveal`, por isso a primeira jogada nunca
é mina. Quando há espaço, as vizinhas da primeira célula também ficam livres, então o
jogo começa abrindo uma região. Com a mesma `seed` e a mesma primeira jogada, o tabuleiro
é sempre o mesmo (útil para comparar agentes).

## Ações (atuadores)

| Método | O que faz |
|---|---|
| `game.reveal(row, col)` | Abre a célula. Um 0 abre as vizinhas em cascata. |
| `game.flag(row, col)` / `game.unflag(row, col)` | Coloca ou tira bandeira. |
| `game.toggle_flag(row, col)` | Alterna a bandeira (para a CLI). |

Cada ação devolve um `MoveResult` com `revealed` (células abertas nesta jogada),
`hit_mine`, `status` e `changed` (`False` se a jogada não teve efeito, por exemplo abrir
uma célula com bandeira). Jogar fora do tabuleiro ou depois do fim gera `InvalidMoveError`.

## Percepção (sensores)

`game.observe()` devolve um `Observation` imutável, com **apenas** o que um jogador vê:

* `obs.grid[row][col]`: `HIDDEN` (-1), `FLAGGED` (-2) ou o número de 0 a 8;
* `obs.rows`, `obs.cols`, `obs.total_mines`, `obs.mines_left`, `obs.status`, `obs.moves`;
* auxiliares: `hidden_cells()`, `flagged_cells()`, `revealed_cells()`, `neighbors(r, c)`,
  `frontier()` (números que ainda tocam células fechadas, ou seja, as restrições do CSP),
  `is_first_move`, `is_over`.

O agente deve receber só o `Observation`. A posição real das minas
(`game.mine_positions()`) só fica disponível depois que a partida termina, para a
interface mostrar o tabuleiro final e para os experimentos.

## Fim de jogo

`game.status` é `GameStatus.IN_PROGRESS`, `WON` (todas as células sem mina abertas) ou
`LOST` (abriu uma mina; a célula fica em `game.exploded_cell`). Bandeiras não são
necessárias para vencer.

## Exemplo: agente aleatório

```python
import random
from minesweeper.environment import Game, get_config

game = Game(get_config("easy"), seed=42)
rng = random.Random(42)
while not game.is_over:
    obs = game.observe()
    game.reveal(*rng.choice(obs.hidden_cells()))
print(game.status, game.revealed_count)
```
