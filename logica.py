"""Regras e algoritmos matematicos do Labirinto dos Enigmas.

Matriz, DFS, BFS, A*, espinhos, lasers e pontuacao.
"""

from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
import heapq
import random
from typing import Iterable

# Mapa, controles e desafios das tres fases
ROWS = 15
COLS = 23
START = (1, 1)
EXIT = (ROWS - 2, COLS - 2)
PERIOD = 4
DAMAGE_PENALTY = 18
MAX_HEALTH = 4
DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))

PUZZLES = (
    {"question": "Complete: 2, 4, 8, 16, ?", "answer": "32", "hint": "Multiplique cada termo por 2.", "why": "Progressao geometrica: a(n) = 2 elevado a (n + 1)."},
    {"question": "Complete: 1, 1, 2, 3, 5, ?", "answer": "8", "hint": "Some os dois termos anteriores.", "why": "Recorrencia de Fibonacci: F(n) = F(n-1) + F(n-2)."},
    {"question": "Complete: 1, 4, 9, 16, ?", "answer": "25", "hint": "Os termos sao quadrados perfeitos.", "why": "Sequencia quadratica: a(n) = n ao quadrado."},
)

Position = tuple[int, int]


# Funcoes de apoio para movimentos e seguranca
def add(pos: Position, offset: Position) -> Position:
    """Soma duas coordenadas do labirinto."""
    return (pos[0] + offset[0], pos[1] + offset[1])


def inside(pos: Position) -> bool:
    """Confere se a posicao esta dentro da matriz."""
    return 0 <= pos[0] < ROWS and 0 <= pos[1] < COLS


def manhattan(a: Position, b: Position) -> int:
    """Calcula a distancia entre duas casas sem movimentos diagonais."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def laser_active(turn: int) -> bool:
    """Identifica se o laser esta ligado pelo turno atual."""
    return turn % PERIOD in (0, 1)


def hazard(grid: list[list[str]], pos: Position, turn: int) -> bool:
    """Verifica se uma casa causa dano neste turno."""
    tile = grid[pos[0]][pos[1]]
    return tile == "^" or (tile == "~" and laser_active(turn))


def walkable(grid: list[list[str]], pos: Position, door_open: bool) -> bool:
    """Confere se a casa permite passagem, considerando a porta."""
    if not inside(pos):
        return False
    tile = grid[pos[0]][pos[1]]
    return tile not in ("#", "R") and (tile != "D" or door_open)


def neighbors(grid: list[list[str]], pos: Position, door_open: bool) -> list[Position]:
    """Lista as casas ao lado que podem ser percorridas."""
    resultado = []
    for direcao in DIRECTIONS:
        vizinho = add(pos, direcao)
        if walkable(grid, vizinho, door_open):
            resultado.append(vizinho)
    return resultado


def safe_neighbors(grid: list[list[str]], pos: Position, door_open: bool) -> list[Position]:
    """Encontra casas vizinhas sem espinhos nem lasers."""
    return [candidate for candidate in neighbors(grid, pos, door_open) if grid[candidate[0]][candidate[1]] not in ("^", "~")]


def safe_retreat(grid: list[list[str]], impact: Position, previous: Position, door_open: bool) -> Position:
    """Afasta o jogador do perigo e o leva ate uma casa segura."""
    options = safe_neighbors(grid, impact, door_open)
    if previous in options:
        return previous
    if options:
        return min(options, key=lambda p: (grid[p[0]][p[1]] != ".", manhattan(p, START), p))
    queue = deque([impact])
    visited = {impact}
    while queue:
        current = queue.popleft()
        for candidate in neighbors(grid, current, door_open):
            if candidate in visited:
                continue
            if grid[candidate[0]][candidate[1]] not in ("^", "~"):
                return candidate
            visited.add(candidate)
            queue.append(candidate)
    return previous


# Algoritmo BFS: encontra o caminho com menos passos
def bfs(grid: list[list[str]], origin: Position, goal: Position, door_open: bool = False) -> list[Position]:
    """Encontra o caminho com menos movimentos usando uma fila."""
    if not walkable(grid, origin, door_open) or not walkable(grid, goal, door_open):
        return []
    queue = deque([origin])
    parent: dict[Position, Position | None] = {origin: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = parent[current]
            return path[::-1]
        for nxt in neighbors(grid, current, door_open):
            if nxt not in parent:
                parent[nxt] = current
                queue.append(nxt)
    return []


def reachable(grid: list[list[str]], origin: Position, door_open: bool = False) -> set[Position]:
    """Reune todas as casas acessiveis a partir de uma origem."""
    found = {origin}
    queue = deque([origin])
    while queue:
        current = queue.popleft()
        for nxt in neighbors(grid, current, door_open):
            if nxt not in found:
                found.add(nxt)
                queue.append(nxt)
    return found


# Algoritmo A*: compara distancia, tempo e risco de danos
def astar(grid: list[list[str]], origin: Position, goal: Position, turn: int, door_open: bool, risk_weight: int = DAMAGE_PENALTY) -> tuple[list[Position], int]:
    """A*: nos sao (linha, coluna, tempo modulo 4); g = passos + peso * impactos."""
    if not walkable(grid, origin, door_open) or not walkable(grid, goal, door_open):
        return [], -1
    first = (origin, turn % PERIOD)
    costs = {first: 0}
    parent: dict[tuple[Position, int], tuple[Position, int] | None] = {first: None}
    heap = [(manhattan(origin, goal), 0, 0, first)]
    counter = 0
    while heap:
        _, g, _, state = heapq.heappop(heap)
        if g != costs.get(state):
            continue
        pos, phase = state
        if pos == goal:
            path = []
            while state is not None:
                path.append(state[0])
                state = parent[state]
            return path[::-1], g
        next_phase = (phase + 1) % PERIOD
        options = neighbors(grid, pos, door_open) + [pos]
        for nxt in options:
            extra = risk_weight if hazard(grid, nxt, next_phase) else 0
            new_g = g + 1 + extra
            next_state = (nxt, next_phase)
            if new_g < costs.get(next_state, float("inf")):
                costs[next_state] = new_g
                parent[next_state] = (pos, phase)
                counter += 1
                heuristic = manhattan(nxt, goal)
                heapq.heappush(heap, (new_g + heuristic, new_g, counter, next_state))
    return [], -1


def route_risk(grid: list[list[str]], path: list[Position], turn: int) -> int:
    """Conta quantos perigos existem em uma rota prevista."""
    return sum(int(hazard(grid, pos, turn + step)) for step, pos in enumerate(path[1:], 1))


# Geracao de caminhos extras que respeitam a porta trancada
def _open_loops(grid: list[list[str]], door: Position, rng: random.Random, number: int) -> None:
    """Abre caminhos alternativos sem permitir contornar a porta."""
    before = reachable(grid, START, False)
    after = reachable(grid, EXIT, False)
    candidates = []
    for r in range(1, ROWS - 1):
        for c in range(1, COLS - 1):
            p = (r, c)
            if grid[r][c] != "#" or p == door:
                continue
            adj = [add(p, d) for d in DIRECTIONS if grid[add(p, d)[0]][add(p, d)[1]] != "#"]
            if len(adj) < 2:
                continue
            if all(a in before for a in adj) or all(a in after for a in adj):
                candidates.append(p)
    rng.shuffle(candidates)
    for p in candidates[:number]:
        grid[p[0]][p[1]] = "."


# Dados e regras de uma fase
@dataclass
class Level:
    """Guarda o mapa e os dados da fase atual."""
    grid: list[list[str]]
    number: int
    start: Position
    exit: Position
    door: Position
    key: Position
    puzzle: Position
    player: Position = START
    has_key: bool = False
    solved: bool = False
    turns: int = 0
    health: int = MAX_HEALTH
    protected: set[Position] = field(default_factory=set)

    @property
    def door_open(self) -> bool:
        """A porta abre quando a chave e o enigma foram obtidos."""
        return self.has_key and self.solved

    @property
    def objective(self) -> Position:
        """Informa se o proximo alvo e chave, enigma ou saida."""
        if not self.has_key:
            return self.key
        if not self.solved:
            return self.puzzle
        return self.exit


# DFS: gera corredores, depois distribui objetivos e obstaculos
def generate_level(number: int, seed: int | None = None) -> Level:
    """Gera um novo mapa aleatorio com objetivos e obstaculos."""
    rng = random.Random(seed)
    grid = [["#" for _ in range(COLS)] for _ in range(ROWS)]
    grid[START[0]][START[1]] = "."
    stack = [START]
    while stack:
        current = stack[-1]
        directions = list(DIRECTIONS)
        rng.shuffle(directions)
        carved = False
        for direction in directions:
            next_pos = add(current, (2 * direction[0], 2 * direction[1]))
            if not (0 < next_pos[0] < ROWS - 1 and 0 < next_pos[1] < COLS - 1):
                continue
            if grid[next_pos[0]][next_pos[1]] != "#":
                continue
            mid = add(current, direction)
            grid[mid[0]][mid[1]] = "."
            grid[next_pos[0]][next_pos[1]] = "."
            stack.append(next_pos)
            carved = True
            break
        if not carved:
            stack.pop()
    path = bfs(grid, START, EXIT, True)
    if len(path) < 5:
        raise ValueError("Labirinto gerado sem percurso suficiente")
    index = max(2, min(int(len(path) * 0.68), len(path) - 3))
    door = path[index]
    grid[door[0]][door[1]] = "D"
    _open_loops(grid, door, rng, number * 3 + 7)
    before = reachable(grid, START, False)
    candidates = [p for p in before if p != START and manhattan(p, START) > 3]
    if len(candidates) < 2:
        raise ValueError("Nao existem celulas para os objetivos")
    key = rng.choice(sorted(candidates))
    distant = [p for p in candidates if p != key and len(bfs(grid, key, p, False)) >= 7]
    puzzle = rng.choice(sorted(distant or [p for p in candidates if p != key]))
    grid[key[0]][key[1]] = "K"
    grid[puzzle[0]][puzzle[1]] = "E"
    grid[EXIT[0]][EXIT[1]] = "S"
    safe = set(bfs(grid, START, key, False))
    safe.update(bfs(grid, key, puzzle, False))
    safe.update(bfs(grid, puzzle, EXIT, True))
    forbidden = safe | {START, key, puzzle, door, EXIT}
    available = sorted(p for p in reachable(grid, START, True) if p not in forbidden and grid[p[0]][p[1]] == ".")
    rng.shuffle(available)
    rubble_n = min(2 + number, len(available) // 5)
    spike_n = min(6 + 2 * number, max(0, (len(available) - rubble_n) // 2))
    laser_n = min(5 + 2 * number, max(0, len(available) - rubble_n - spike_n))
    for pos in available[:rubble_n]:
        grid[pos[0]][pos[1]] = "R"
    for symbol, limit in (("^", spike_n), ("~", laser_n)):
        placed = 0
        for pos in available[rubble_n:]:
            if grid[pos[0]][pos[1]] != ".":
                continue
            grid[pos[0]][pos[1]] = symbol
            affected = [pos] + [p for p in neighbors(grid, pos, False) if grid[p[0]][p[1]] in ("^", "~")]
            if not all(safe_neighbors(grid, danger, False) for danger in affected):
                grid[pos[0]][pos[1]] = "."
                continue
            placed += 1
            if placed >= limit:
                break
    result = Level(grid, number, START, EXIT, door, key, puzzle, protected=safe)
    if not bfs(grid, START, key, False) or not bfs(grid, key, puzzle, False):
        raise AssertionError("Objetivos inacessiveis")
    if not bfs(grid, puzzle, EXIT, True) or bfs(grid, START, EXIT, False):
        raise AssertionError("Porta nao separa as areas")
    return result


# Dados e regras de uma fase
@dataclass
# Controle do jogo e das regras de pontuacao
class Session:
    """Controla os movimentos, as vidas, os desafios e a pontuacao."""
    level: Level = field(default_factory=lambda: generate_level(1))
    score: int = 0
    state: str = "intro"
    message: str = "Encontre a credencial e atravesse com seguranca."
    hint_open: bool = False
    hint_mode: str = "none"
    hinted: bool = False
    steps: int = 0
    impacts: int = 0

    def reset(self, seed: int | None = None) -> None:
        """Inicia uma partida nova com os valores padrao."""
        self.level = generate_level(1, seed)
        self.score = 0
        self.state = "playing"
        self.message = "Procure a chave. Use H para rota mais segura."
        self.hint_mode = "none"
        self.hint_open = False
        self.hinted = False
        self.steps = 0
        self.impacts = 0

    def begin(self) -> None:
        """Sai da tela inicial e inicia o jogo."""
        self.reset()

    def move(self, delta: Position) -> str:
        """Executa um movimento e verifica perigo, itens e saida."""
        if self.state != "playing":
            return "blocked"
        if delta not in DIRECTIONS + ((0, 0),):
            self.message = "Movimento invalido."
            return "invalid"
        previous = self.level.player
        nxt = add(previous, delta)
        if not walkable(self.level.grid, nxt, self.level.door_open):
            self.message = "Caminho bloqueado ou porta ainda trancada."
            return "blocked"
        self.level.turns += 1
        self.steps += 1
        self.level.player = nxt
        tile = self.level.grid[nxt[0]][nxt[1]]
        if hazard(self.level.grid, nxt, self.level.turns):
            self.level.health -= 1
            self.impacts += 1
            self.score = max(0, self.score - 20)
            retreat = safe_retreat(self.level.grid, nxt, previous, self.level.door_open)
            self.level.player = retreat
            self.message = "RISCO! -1 vida, -20 pontos. Recuo para uma casa segura!"
            if self.level.health <= 0:
                self.state = "lost"
                return "lost"
            return "damage"
        elif delta == (0, 0):
            self.message = "Voce aguardou um turno. Fase do laser alterada."
        if tile == "K" and not self.level.has_key:
            self.level.has_key = True
            self.level.grid[nxt[0]][nxt[1]] = "."
            self.score += 40
            self.message = "Credencial obtida! Procure o desafio matematico."
            return "key"
        if tile == "E" and not self.level.solved:
            if not self.level.has_key:
                self.message = "Primeiro obtenha a credencial de acesso."
                return "need_key"
            self.state = "quiz"
            self.hint_open = False
            self.message = "Resolva a sequencia para validar o acesso."
            return "quiz"
        if tile == "S":
            if not self.level.door_open:
                self.message = "Credencial e enigma sao obrigatorios."
                return "locked"
            self.score += 120
            self.state = "cleared"
            self.message = "Area concluida! Pressione ENTER para continuar."
            return "cleared"
        return "step"

    def answer(self, value: str) -> bool:
        """Confere a resposta do enigma e libera a porta."""
        if self.state != "quiz":
            return False
        puzzle = PUZZLES[self.level.number - 1]
        cleaned = value.strip()
        if not cleaned.isascii() or not cleaned.isdigit() or len(cleaned) > 8:
            self.message = "Digite apenas numeros inteiros (ate 8 digitos)."
            return False
        if cleaned != puzzle["answer"]:
            self.message = "Resposta incorreta. Analise a regra da sequencia."
            return False
        self.level.solved = True
        p = self.level.puzzle
        self.level.grid[p[0]][p[1]] = "."
        self.score += 80
        self.state = "playing"
        self.message = puzzle["why"] + " A porta foi liberada!"
        return True

    def next_level(self, seed: int | None = None) -> None:
        """Avanca de fase ou conclui a partida."""
        if self.state != "cleared":
            return
        if self.level.number == len(PUZZLES):
            self.state = "victory"
            self.message = "Todas as zonas foram atravessadas!"
            return
        self.level = generate_level(self.level.number + 1, seed)
        self.hint_mode = "none"
        self.hinted = False
        self.state = "playing"
        self.message = "Nova zona. Avalie os riscos antes de escolher a rota."

    def show_route(self, mode: str) -> tuple[list[Position], int]:
        """Exibe a rota BFS curta ou a rota A* mais segura."""
        if mode not in ("safe", "short"):
            raise ValueError("Modo de rota desconhecido")
        if self.state != "playing":
            return [], -1
        self.hint_mode = mode
        if not self.hinted:
            self.score = max(0, self.score - 5)
            self.hinted = True
        if mode == "safe":
            route, cost = astar(self.level.grid, self.level.player, self.level.objective, self.level.turns, self.level.door_open)
            self.message = "Rota segura: minimiza passos + penalidade de risco."
            return route, cost
        route = bfs(self.level.grid, self.level.player, self.level.objective, self.level.door_open)
        self.message = "Menor rota: pode atravessar espinhos e lasers ativos!"
        return route, len(route) - 1 if route else -1