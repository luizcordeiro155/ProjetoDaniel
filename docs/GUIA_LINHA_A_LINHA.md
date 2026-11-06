# Guia de leitura — explicação linha por linha do código Python

**Projeto:** Labirinto dos Enigmas: Rotas de Risco  
**Disciplina:** Matemática Computacional Aplicada  
**Professor:** Daniel Henrique Matos de Paiva  
**Autor identificado:** Luiz Henrique Cordeiro dos Santos — RA 326122345

## Como usar o material

Leia primeiro [`CONCEITOS_MATEMATICOS.md`](CONCEITOS_MATEMATICOS.md) e depois acompanhe o arquivo `.py` com a tabela correspondente. **Cada linha não vazia** dos três arquivos está enumerada aqui; as instruções têm **comentários diretamente no código-fonte**. Linhas de docstring descrevem o bloco e linhas compostas só por símbolos encerram uma estrutura aberta. Os números de linha refletem esta versão do projeto.

**Glossário de leitura:** `=` atribuição; `==` comparação; `!=` diferente; `and` conjunção; `or` disjunção; `not` negação; `+=` soma acumulada; `%` resto modular; `//` divisão inteira; `[]` indexação/lista; `{}` conjunto/dicionário; `[::-1]` lista invertida; `None` ausência de valor; `return` resultado da função; `continue` próxima iteração; `break` encerra laço; `yield` produção preguiçosa (não usada); `self` instância atual; `@dataclass` automatização de campos; `@property` atributo calculado; `->` tipo de retorno. `set` é conjunto, `deque` implementa fila, `heapq` implementa prioridade.

**Aviso:** comentários explicam o comportamento da linha, e não substituem o raciocínio global dos algoritmos. O grafo temporal é modelado por `(célula, turno mod 4)` e o custo é `1 + 18` por impacto; a BFS ignora riscos e o A* minimiza o custo.


---

## Arquivo `src/logica.py`

[Trecho do código-fonte](../../src/logica.py) — 368 linhas físicas.

| Linha | Instrução / trecho | Explicação |
|---:|---|---|
| 1 | `"""Modelo matematico puro: matriz, grafo, DFS, BFS, A* temporal e regras.` | Inicia ou encerra uma docstring: texto documental que descreve o propósito do módulo ou função. |
| 3 | `Este modulo nao importa Pygame: a simulacao pode ser testada sem abrir janelas.` | Executa ou configura a operação mostrada; a expressão é detalhada nos comentários do fonte. |
| 4 | `Cada operacao significativa traz comentario e o guia detalha as linhas.` | Executa ou configura a operação mostrada; a expressão é detalhada nos comentários do fonte. |
| 5 | `"""` | Inicia ou encerra uma docstring: texto documental que descreve o propósito do módulo ou função. |
| 7 | `from __future__ import annotations` | Permite anotacoes de tipos modernas. |
| 8 | `from collections import deque` | Implementa a fila FIFO utilizada na BFS. |
| 9 | `from dataclasses import dataclass, field` | Organiza os dados da fase. |
| 10 | `import heapq` | Implementa a fila de prioridade de menor custo do A*. |
| 11 | `import random` | Sorteia ramificacoes, objetos e posicoes dos obstaculos. |
| 12 | `from typing import Iterable` | Declara colecoes de coordenadas nos tipos. |
| 14 | `ROWS = 15` | Quantidade impar de linhas na matriz do mapa. |
| 15 | `COLS = 23` | Quantidade impar de colunas da matriz. |
| 16 | `START = (1, 1)` | Primeira celula aberta: linha 1 e coluna 1. |
| 17 | `EXIT = (ROWS - 2, COLS - 2)` | Saida interna do canto inferior direito. |
| 18 | `PERIOD = 4` | Laser repete o seu ciclo a cada quatro turnos. |
| 19 | `DAMAGE_PENALTY = 18` | Peso de risco: A* prefere contornar perigos. |
| 20 | `MAX_HEALTH = 4` | Quantidade inicial de vidas em cada fase. |
| 21 | `DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))` | Cima, baixo, esquerda, direita. |
| 23 | `PUZZLES = (` | Sequencia de enigmas aplicada nas tres fases. |
| 24 | `{"question": "Complete: 2, 4, 8, 16, ?", "answer": "32", "hint": "Multiplique cada termo por 2.", "why": "Progressao geometrica: a(n) = 2 elevado a (n + 1)."},` | Primeiro desafio: potencia de base 2. |
| 25 | `{"question": "Complete: 1, 1, 2, 3, 5, ?", "answer": "8", "hint": "Some os dois termos anteriores.", "why": "Recorrencia de Fibonacci: F(n) = F(n-1) + F(n-2)."},` | Segundo desafio: recorrencia aditiva. |
| 26 | `{"question": "Complete: 1, 4, 9, 16, ?", "answer": "25", "hint": "Os termos sao quadrados perfeitos.", "why": "Sequencia quadratica: a(n) = n ao quadrado."},` | Terceiro desafio: quadrados perfeitos. |
| 27 | `)` | Encerra a tupla imutavel de enigmas. |
| 29 | `Position = tuple[int, int]` | Cada vertice equivale a coordenada (linha, coluna). |
| 32 | `def add(pos: Position, offset: Position) -> Position:` | Soma coordenadas para deslocar no grafo. |
| 33 | `return (pos[0] + offset[0], pos[1] + offset[1])` | Novo vertice apos um movimento. |
| 36 | `def inside(pos: Position) -> bool:` | Protege os acessos contra indices fora da matriz. |
| 37 | `return 0 <= pos[0] < ROWS and 0 <= pos[1] < COLS` | Verdadeiro apenas dentro da grade. |
| 40 | `def manhattan(a: Position, b: Position) -> int:` | Calcula limite inferior da distancia ortogonal. |
| 41 | `return abs(a[0] - b[0]) + abs(a[1] - b[1])` | Soma de distancias absolutas. |
| 44 | `def laser_active(turn: int) -> bool:` | Testa o perigo periodico com aritmetica modular. |
| 45 | `return turn % PERIOD in (0, 1)` | Laser ativo em duas fases de cada ciclo. |
| 48 | `def hazard(grid: list[list[str]], pos: Position, turn: int) -> bool:` | Consulta risco na chegada. |
| 49 | `tile = grid[pos[0]][pos[1]]` | Le o simbolo armazenado na matriz. |
| 50 | `return tile == "^" or (tile == "~" and laser_active(turn))` | Espinho sempre ou laser ativo. |
| 53 | `def walkable(grid: list[list[str]], pos: Position, door_open: bool) -> bool:` | Verifica transitabilidade. |
| 54 | `if not inside(pos):` | Impede coordenadas negativas ou maiores que o mapa. |
| 55 | `return False` | Celula fora do mapa nunca pode ser usada. |
| 56 | `tile = grid[pos[0]][pos[1]]` | Le o conteudo de uma posicao valida. |
| 57 | `return tile not in ("#", "R") and (tile != "D" or door_open)` | Paredes/escombros bloqueiam. |
| 60 | `def neighbors(grid: list[list[str]], pos: Position, door_open: bool) -> list[Position]:` | Adjacencias do grafo. |
| 61 | `return [candidate for delta in DIRECTIONS if walkable(grid, (candidate := add(pos, delta)), door_open)]` | Quatro movimentos ortogonais validos. |
| 64 | `def bfs(grid: list[list[str]], origin: Position, goal: Position, door_open: bool = False) -> list[Position]:` | Menor caminho por passos. |
| 65 | `if not walkable(grid, origin, door_open) or not walkable(grid, goal, door_open):` | Valida os extremos. |
| 66 | `return []` | Caminho vazio indica objetivo indisponivel. |
| 67 | `queue = deque([origin])` | Fila FIFO com o primeiro vertice. |
| 68 | `parent: dict[Position, Position \| None] = {origin: None}` | Marca visitados e seus predecessores. |
| 69 | `while queue:` | Continua ate achar o destino ou esgotar vertice. |
| 70 | `current = queue.popleft()` | Retira o vertice mais antigo da fila. |
| 71 | `if current == goal:` | BFS encontrou o alvo com o menor numero de arestas. |
| 72 | `path = []` | Acumula caminho invertido a partir do objetivo. |
| 73 | `while current is not None:` | Reconstrucao usando os predecessores. |
| 74 | `path.append(current)` | Salva cada posicao da rota. |
| 75 | `current = parent[current]` | Volta para o pai deste vertice. |
| 76 | `return path[::-1]` | Retorna o trajeto em ordem de ida. |
| 77 | `for nxt in neighbors(grid, current, door_open):` | Explora adjacentes validos. |
| 78 | `if nxt not in parent:` | Cada posicao e visitada apenas uma vez. |
| 79 | `parent[nxt] = current` | Salva a aresta usada para chegar ao vizinho. |
| 80 | `queue.append(nxt)` | Agenda o vizinho para a busca em largura. |
| 81 | `return []` | Destino inalcançavel nas regras fornecidas. |
| 84 | `def reachable(grid: list[list[str]], origin: Position, door_open: bool = False) -> set[Position]:` | Componente conectada. |
| 85 | `found = {origin}` | Conjunto de vertices que ja foram descobertos. |
| 86 | `queue = deque([origin])` | Inicia a exploracao da componente. |
| 87 | `while queue:` | Continua ate visitar toda a area acessivel. |
| 88 | `current = queue.popleft()` | Retira o proximo vertice da fila. |
| 89 | `for nxt in neighbors(grid, current, door_open):` | Considera cada vizinho. |
| 90 | `if nxt not in found:` | Impede repeticao e ciclos infinitos. |
| 91 | `found.add(nxt)` | Registra o vertice como acessivel. |
| 92 | `queue.append(nxt)` | Visita depois os vizinhos dele. |
| 93 | `return found` | Devolve o conjunto de posicoes alcançaveis. |
| 96 | `def astar(grid: list[list[str]], origin: Position, goal: Position, turn: int, door_open: bool, risk_weight: int = DAMAGE_PENALTY) -> tuple[list[Position], int]:` | Rota de custo minimo com tempo. |
| 97 | `"""A*: nos sao (linha, coluna, tempo modulo 4); g = passos + peso * impactos."""` | Define o criterio de otimizacao. |
| 98 | `if not walkable(grid, origin, door_open) or not walkable(grid, goal, door_open):` | Protege extremos. |
| 99 | `return [], -1` | Falha de planejamento tratada explicitamente. |
| 100 | `first = (origin, turn % PERIOD)` | Estado inclui posicao e fase dos lasers. |
| 101 | `costs = {first: 0}` | Melhor distancia ponderada conhecida para cada estado. |
| 102 | `parent: dict[tuple[Position, int], tuple[Position, int] \| None] = {first: None}` | Predecessores. |
| 103 | `heap = [(manhattan(origin, goal), 0, 0, first)]` | Prioridade f = g + h e desempate. |
| 104 | `counter = 0` | Ordenacao estavel sem comparar objetos complexos. |
| 105 | `while heap:` | Processa o melhor estado ainda pendente. |
| 106 | `_, g, _, state = heapq.heappop(heap)` | Recupera menor custo estimado. |
| 107 | `if g != costs.get(state):` | Descarta entradas antigas de menor prioridade. |
| 108 | `continue` | O estado ja recebeu uma rota melhor. |
| 109 | `pos, phase = state` | Separa vertice e instante modular. |
| 110 | `if pos == goal:` | A heuristica consistente garante custo minimo no primeiro encontro. |
| 111 | `path = []` | Armazena a trajetoria da chegada ate a origem. |
| 112 | `while state is not None:` | Reconstrucao dos antecessores. |
| 113 | `path.append(state[0])` | Guarda so a posicao; repeticoes representam esperar. |
| 114 | `state = parent[state]` | Retrocede pelo caminho otimo. |
| 115 | `return path[::-1], g` | Entrega rota e custo total acumulado. |
| 116 | `next_phase = (phase + 1) % PERIOD` | Cada acao gasta um turno, inclusive esperar. |
| 117 | `options = neighbors(grid, pos, door_open) + [pos]` | Quatro direcoes e acao ESPERAR. |
| 118 | `for nxt in options:` | Avalia transicoes do grafo expandido no tempo. |
| 119 | `extra = risk_weight if hazard(grid, nxt, next_phase) else 0` | Penaliza risco na chegada. |
| 120 | `new_g = g + 1 + extra` | Custo de movimento + custo do risco. |
| 121 | `next_state = (nxt, next_phase)` | Mesmo lugar em outro tempo e um estado distinto. |
| 122 | `if new_g < costs.get(next_state, float("inf")):` | Relaxamento de aresta tipo Dijkstra. |
| 123 | `costs[next_state] = new_g` | Atualiza o menor custo conhecido. |
| 124 | `parent[next_state] = (pos, phase)` | Registra predecessor da melhor transicao. |
| 125 | `counter += 1` | Atualiza desempate da fila de prioridade. |
| 126 | `heuristic = manhattan(nxt, goal)` | Nunca superestima passos restantes. |
| 127 | `heapq.heappush(heap, (new_g + heuristic, new_g, counter, next_state))` | Agenda candidato. |
| 128 | `return [], -1` | O destino nao foi encontrado. |
| 131 | `def route_risk(grid: list[list[str]], path: list[Position], turn: int) -> int:` | Conta impactos potenciais. |
| 132 | `return sum(int(hazard(grid, pos, turn + step)) for step, pos in enumerate(path[1:], 1))` | Considera o tempo de cada passo. |
| 135 | `def _open_loops(grid: list[list[str]], door: Position, rng: random.Random, number: int) -> None:` | Cria alternativas sem contornar porta. |
| 136 | `before = reachable(grid, START, False)` | Area de entrada antes da porta. |
| 137 | `after = reachable(grid, EXIT, False)` | Area apos a porta na arvore original. |
| 138 | `candidates = []` | Armazena paredes elegiveis a remocao. |
| 139 | `for r in range(1, ROWS - 1):` | Nao altera o contorno exterior. |
| 140 | `for c in range(1, COLS - 1):` | Percorre as celulas internas. |
| 141 | `p = (r, c)` | Coordenada atual da parede. |
| 142 | `if grid[r][c] != "#" or p == door:` | Somente paredes interiores. |
| 143 | `continue` | Nao reabre a porta que controla o acesso. |
| 144 | `adj = [add(p, d) for d in DIRECTIONS if grid[add(p, d)[0]][add(p, d)[1]] != "#"]` | Lados ja abertos. |
| 145 | `if len(adj) < 2:` | Uma passagem sem dois vizinhos nao cria alternativa. |
| 146 | `continue` | Preserva um grau minimo de utilidade. |
| 147 | `if all(a in before for a in adj) or all(a in after for a in adj):` | Nao liga regioes opostas. |
| 148 | `candidates.append(p)` | Possivel corredor alternativo seguro. |
| 149 | `rng.shuffle(candidates)` | Varia a estrutura de ciclos em cada fase. |
| 150 | `for p in candidates[:number]:` | Abre um numero limitado de caminhos extras. |
| 151 | `grid[p[0]][p[1]] = "."` | Converte parede em corredor. |
| 154 | `@dataclass` | Gera automaticamente inicializador e representacao dos campos. |
| 155 | `class Level:` | Estrutura de dados de uma fase da simulacao. |
| 156 | `grid: list[list[str]]` | Matriz de caracteres do ambiente. |
| 157 | `number: int` | Numero da fase (1, 2, 3). |
| 158 | `start: Position` | Posicao de nascimento do jogador. |
| 159 | `exit: Position` | Vertice objetivo final. |
| 160 | `door: Position` | Porta que controla acesso a regiao final. |
| 161 | `key: Position` | Credencial necessaria para desbloqueio. |
| 162 | `puzzle: Position` | Ponto de verificacao logica. |
| 163 | `player: Position = START` | Posicao atual do agente. |
| 164 | `has_key: bool = False` | Booleano de credencial encontrada. |
| 165 | `solved: bool = False` | Booleano de desafio resolvido. |
| 166 | `turns: int = 0` | Quantidade de acoes validas ja realizadas. |
| 167 | `health: int = MAX_HEALTH` | Vidas restantes da fase. |
| 168 | `protected: set[Position] = field(default_factory=set)` | Uma rota garantidamente sem riscos. |
| 170 | `@property` | Transforma metodo em atributo calculado de maneira segura. |
| 171 | `def door_open(self) -> bool:` | Implementa operador logico de conjuncao. |
| 172 | `return self.has_key and self.solved` | Porta abre somente quando K e E sao verdadeiros. |
| 174 | `@property` | Consulta o objetivo atual com sintaxe de atributo. |
| 175 | `def objective(self) -> Position:` | Seleciona o alvo da proxima orientacao. |
| 176 | `if not self.has_key:` | Se falta credencial, procura a chave. |
| 177 | `return self.key` | Primeiro ponto de interesse. |
| 178 | `if not self.solved:` | Se a chave existe mas nao houve verificacao. |
| 179 | `return self.puzzle` | Segundo ponto de interesse. |
| 180 | `return self.exit` | Apos atender as condicoes, busca a saida. |
| 183 | `def generate_level(number: int, seed: int \| None = None) -> Level:` | Construcao reproduzivel por semente. |
| 184 | `rng = random.Random(seed)` | Gerador local permite testar mapas identicos. |
| 185 | `grid = [["#" for _ in range(COLS)] for _ in range(ROWS)]` | Matriz totalmente bloqueada. |
| 186 | `grid[START[0]][START[1]] = "."` | Libera a origem do percurso. |
| 187 | `stack = [START]` | Pilha LIFO usada pela busca em profundidade iterativa. |
| 188 | `while stack:` | Enquanto houver um ramo a ser explorado. |
| 189 | `current = stack[-1]` | Examina o topo da pilha sem retira-lo. |
| 190 | `directions = list(DIRECTIONS)` | Cria lista mutavel das quatro direcoes. |
| 191 | `rng.shuffle(directions)` | Escolhe as possibilidades em ordem aleatoria. |
| 192 | `carved = False` | Supoe inicialmente que o vertice e um beco sem saida. |
| 193 | `for direction in directions:` | Tenta abrir corredor em cada sentido. |
| 194 | `next_pos = add(current, (2 * direction[0], 2 * direction[1]))` | Salta duas celulas. |
| 195 | `if not (0 < next_pos[0] < ROWS - 1 and 0 < next_pos[1] < COLS - 1):` | Limites interiores. |
| 196 | `continue` | Descarta movimento que sairia da grade. |
| 197 | `if grid[next_pos[0]][next_pos[1]] != "#":` | DFS evita visitar celula ja aberta. |
| 198 | `continue` | Preserva a arvore de corredores durante a geracao. |
| 199 | `mid = add(current, direction)` | Parede intermediaria entre os dois vertices. |
| 200 | `grid[mid[0]][mid[1]] = "."` | Abre a passagem de conexao. |
| 201 | `grid[next_pos[0]][next_pos[1]] = "."` | Marca a nova sala como visitada. |
| 202 | `stack.append(next_pos)` | Avanca a busca em profundidade. |
| 203 | `carved = True` | Indica que foi possivel continuar. |
| 204 | `break` | Explora a nova ramificacao antes das demais. |
| 205 | `if not carved:` | Nenhuma direcao disponivel nesta ramificacao. |
| 206 | `stack.pop()` | Backtracking: retorna ao vertice anterior. |
| 207 | `path = bfs(grid, START, EXIT, True)` | O labirinto conectado possui caminho a saida. |
| 208 | `if len(path) < 5:` | Condicao defensiva para configuracoes anormais. |
| 209 | `raise ValueError("Labirinto gerado sem percurso suficiente")` | Evita acesso fora de indice. |
| 210 | `index = max(2, min(int(len(path) * 0.68), len(path) - 3))` | Porta perto de 68% do trajeto. |
| 211 | `door = path[index]` | Posiciona um controle de acesso no caminho obrigatorio. |
| 212 | `grid[door[0]][door[1]] = "D"` | Retirar o vertice separa duas componentes. |
| 213 | `_open_loops(grid, door, rng, number * 3 + 7)` | Cria percursos alternativos dentro de cada zona. |
| 214 | `before = reachable(grid, START, False)` | Calcula locais acessiveis antes da porta. |
| 215 | `candidates = [p for p in before if p != START and manhattan(p, START) > 3]` | Locais da credencial. |
| 216 | `if len(candidates) < 2:` | Valida a quantidade minima de posicoes. |
| 217 | `raise ValueError("Nao existem celulas para os objetivos")` | Falha legivel e deterministica. |
| 218 | `key = rng.choice(sorted(candidates))` | Escolhe local para encontrar a chave. |
| 219 | `distant = [p for p in candidates if p != key and len(bfs(grid, key, p, False)) >= 7]` | Distancia minima do enigma. |
| 220 | `puzzle = rng.choice(sorted(distant or [p for p in candidates if p != key]))` | Evita sobreposicao. |
| 221 | `grid[key[0]][key[1]] = "K"` | Adiciona credencial ao mapa. |
| 222 | `grid[puzzle[0]][puzzle[1]] = "E"` | Adiciona ponto de verificacao. |
| 223 | `grid[EXIT[0]][EXIT[1]] = "S"` | Marca a saida. |
| 224 | `safe = set(bfs(grid, START, key, False))` | Resguarda um caminho sem riscos ate K. |
| 225 | `safe.update(bfs(grid, key, puzzle, False))` | Resguarda percurso de K ate E. |
| 226 | `safe.update(bfs(grid, puzzle, EXIT, True))` | Resguarda E ate S apos a abertura. |
| 227 | `forbidden = safe \| {START, key, puzzle, door, EXIT}` | Nunca instala perigos no corredor garantido. |
| 228 | `available = sorted(p for p in reachable(grid, START, True) if p not in forbidden and grid[p[0]][p[1]] == ".")` | Celulas candidatas. |
| 229 | `rng.shuffle(available)` | Distribui eventos de risco entre ramos alternativos. |
| 230 | `rubble_n = min(2 + number, len(available) // 5)` | Escombros bloqueiam definitivamente. |
| 231 | `spike_n = min(6 + 2 * number, max(0, (len(available) - rubble_n) // 2))` | Espinhos causam dano. |
| 232 | `laser_n = min(5 + 2 * number, max(0, len(available) - rubble_n - spike_n))` | Laser e temporal. |
| 233 | `for pos in available[:rubble_n]:` | Converte alguns corredores em obstaculos solidos. |
| 234 | `grid[pos[0]][pos[1]] = "R"` | Representa caixa, entulho ou passagem obstruida. |
| 235 | `for pos in available[rubble_n:rubble_n + spike_n]:` | Seleciona pontos com espinhos. |
| 236 | `grid[pos[0]][pos[1]] = "^"` | Representa risco permanente de contato. |
| 237 | `for pos in available[rubble_n + spike_n:rubble_n + spike_n + laser_n]:` | Seleciona perigos ciclicos. |
| 238 | `grid[pos[0]][pos[1]] = "~"` | Representa equipamento com acionamento periodico. |
| 239 | `result = Level(grid, number, START, EXIT, door, key, puzzle, protected=safe)` | Monta a fase tipada. |
| 240 | `if not bfs(grid, START, key, False) or not bfs(grid, key, puzzle, False):` | Confirma acesso pre-porta. |
| 241 | `raise AssertionError("Objetivos inacessiveis")` | Invariante de jogabilidade. |
| 242 | `if not bfs(grid, puzzle, EXIT, True) or bfs(grid, START, EXIT, False):` | Garante porta obrigatoria. |
| 243 | `raise AssertionError("Porta nao separa as areas")` | Evita fase que descumpre as regras. |
| 244 | `return result` | Entrega uma fase valida, deterministica por seed. |
| 247 | `@dataclass` | Gera a estrutura de controle de partida. |
| 248 | `class Session:` | Armazena eventos, pontuacao, vidas e progresso. |
| 249 | `level: Level = field(default_factory=lambda: generate_level(1))` | Primeira fase automaticamente. |
| 250 | `score: int = 0` | Pontuacao acumulada do jogador. |
| 251 | `state: str = "intro"` | intro, playing, quiz, cleared, lost ou victory. |
| 252 | `message: str = "Encontre a credencial e atravesse com seguranca."` | Aviso contextual. |
| 253 | `hint_open: bool = False` | Controla exibicao da resposta auxiliar. |
| 254 | `hint_mode: str = "none"` | none, safe ou short. |
| 255 | `hinted: bool = False` | Evita desconto repetido da mesma fase. |
| 256 | `steps: int = 0` | Quantidade de movimentos validos da partida. |
| 257 | `impacts: int = 0` | Quantidade total de contatos com perigos. |
| 259 | `def reset(self, seed: int \| None = None) -> None:` | Reinicia a partida completamente. |
| 260 | `self.level = generate_level(1, seed)` | Novo mapa inicial reproduzivel se preciso. |
| 261 | `self.score = 0` | Zera placar total. |
| 262 | `self.state = "playing"` | Reativa movimentos. |
| 263 | `self.message = "Procure a chave. Use H para rota mais segura."` | Instrucao inicial. |
| 264 | `self.hint_mode = "none"` | Oculta dicas antigas. |
| 265 | `self.hint_open = False` | Fecha informacao de enigma. |
| 266 | `self.hinted = False` | Restabelece penalidade de dica por fase. |
| 267 | `self.steps = 0` | Zera contador de movimentos. |
| 268 | `self.impacts = 0` | Zera contador de impactos. |
| 270 | `def begin(self) -> None:` | Sai do menu e comeca uma sessao nova. |
| 271 | `self.reset()` | Centraliza inicializacao na rotina validada. |
| 273 | `def move(self, delta: Position) -> str:` | Executa uma acao ortogonal ou espera. |
| 274 | `if self.state != "playing":` | Respeita a maquina de estados. |
| 275 | `return "blocked"` | Teclas de movimento nao atuam fora da partida. |
| 276 | `if delta not in DIRECTIONS + ((0, 0),):` | Entrada deve ser uma das cinco acoes. |
| 277 | `self.message = "Movimento invalido."` | Informa erro sem avancar tempo. |
| 278 | `return "invalid"` | Nao permite teletransporte diagonal. |
| 279 | `nxt = add(self.level.player, delta)` | Calcula o candidato de deslocamento. |
| 280 | `if not walkable(self.level.grid, nxt, self.level.door_open):` | Aplica restricoes espaciais. |
| 281 | `self.message = "Caminho bloqueado ou porta ainda trancada."` | Explica impedimento. |
| 282 | `return "blocked"` | Movimento recusado; relogio da simulacao nao avanca. |
| 283 | `self.level.turns += 1` | Tempo discreto avanca apenas com acao valida. |
| 284 | `self.steps += 1` | Registra acoes validas para metricas. |
| 285 | `self.level.player = nxt` | Atualiza a coordenada atual do personagem. |
| 286 | `tile = self.level.grid[nxt[0]][nxt[1]]` | Le o objeto presente na nova celula. |
| 287 | `if hazard(self.level.grid, nxt, self.level.turns):` | Consulta risco no novo instante. |
| 288 | `self.level.health -= 1` | Subtrai uma vida por contato danoso. |
| 289 | `self.impacts += 1` | Acumula eventos de risco observados. |
| 290 | `self.score = max(0, self.score - 20)` | Penalidade sem pontuacao negativa. |
| 291 | `self.message = "RISCO! Espinhos ou laser ativo: -1 vida e -20 pontos."` | Feedback preciso. |
| 292 | `if self.level.health <= 0:` | Detecta fim das vidas. |
| 293 | `self.state = "lost"` | Abre tela de derrota. |
| 294 | `return "lost"` | Para o restante da avaliacao da celula. |
| 295 | `elif delta == (0, 0):` | Trata a acao de esperar um turno parado. |
| 296 | `self.message = "Voce aguardou um turno. Fase do laser alterada."` | Explica tempo. |
| 297 | `if tile == "K" and not self.level.has_key:` | Encontrou a credencial. |
| 298 | `self.level.has_key = True` | Atualiza primeira proposicao da porta. |
| 299 | `self.level.grid[nxt[0]][nxt[1]] = "."` | Remove item recolhido. |
| 300 | `self.score += 40` | Recompensa da credencial. |
| 301 | `self.message = "Credencial obtida! Procure o desafio matematico."` | Proximo objetivo. |
| 302 | `return "key"` | Evento para a camada grafica. |
| 303 | `if tile == "E" and not self.level.solved:` | Encontrou local da verificacao. |
| 304 | `if not self.level.has_key:` | Verifica pre-requisito do desafio. |
| 305 | `self.message = "Primeiro obtenha a credencial de acesso."` | Impede salto de etapa. |
| 306 | `return "need_key"` | Informa a regra aplicada. |
| 307 | `self.state = "quiz"` | Troca o controle do jogo para caixa do enigma. |
| 308 | `self.hint_open = False` | Oculta inicialmente a dica textual. |
| 309 | `self.message = "Resolva a sequencia para validar o acesso."` | Mensagem de orientacao. |
| 310 | `return "quiz"` | Interface abre o modal. |
| 311 | `if tile == "S":` | O jogador alcancou a saida da fase. |
| 312 | `if not self.level.door_open:` | Checa conjuncao de credencial e verificacao. |
| 313 | `self.message = "Credencial e enigma sao obrigatorios."` | Recusa conclusao invalida. |
| 314 | `return "locked"` | Mantem o jogador na fase. |
| 315 | `self.score += 120` | Recompensa final de conclusao da etapa. |
| 316 | `self.state = "cleared"` | Registra que a fase foi concluida. |
| 317 | `self.message = "Area concluida! Pressione ENTER para continuar."` | Instrucao da interface. |
| 318 | `return "cleared"` | Envia evento para celebracao visual. |
| 319 | `return "step"` | Movimento comum sem objetivo especifico. |
| 321 | `def answer(self, value: str) -> bool:` | Valida a digitacao do desafio. |
| 322 | `if self.state != "quiz":` | Protege contra resposta fora de contexto. |
| 323 | `return False` | Entrada nao tem efeito sem enigma aberto. |
| 324 | `puzzle = PUZZLES[self.level.number - 1]` | Usa indice zero para a fase. |
| 325 | `cleaned = value.strip()` | Remove espacos externos sem alterar numeros. |
| 326 | `if not cleaned.isascii() or not cleaned.isdigit() or len(cleaned) > 8:` | Entrada numerica segura. |
| 327 | `self.message = "Digite apenas numeros inteiros (ate 8 digitos)."` | Tratamento de erro. |
| 328 | `return False` | Mantem o enigma aberto para nova tentativa. |
| 329 | `if cleaned != puzzle["answer"]:` | Compara com a resposta matematica correta. |
| 330 | `self.message = "Resposta incorreta. Analise a regra da sequencia."` | Feedback formativo. |
| 331 | `return False` | Evita desbloqueio sem validacao. |
| 332 | `self.level.solved = True` | Marca a segunda condicao booleana como verdadeira. |
| 333 | `p = self.level.puzzle` | Recupera a coordenada do enigma. |
| 334 | `self.level.grid[p[0]][p[1]] = "."` | Transforma o ponto em corredor comum. |
| 335 | `self.score += 80` | Recompensa pela solucao matematica. |
| 336 | `self.state = "playing"` | Devolve controles de movimento ao jogador. |
| 337 | `self.message = puzzle["why"] + " A porta foi liberada!"` | Explica o resultado. |
| 338 | `return True` | Indica sucesso da resposta. |
| 340 | `def next_level(self, seed: int \| None = None) -> None:` | Controla transicao de fases. |
| 341 | `if self.state != "cleared":` | Exige conclusao anterior. |
| 342 | `return` | Ignora tentativa fora de contexto. |
| 343 | `if self.level.number == len(PUZZLES):` | Ultima fase ja foi resolvida. |
| 344 | `self.state = "victory"` | Marca vitoria final da partida. |
| 345 | `self.message = "Todas as zonas foram atravessadas!"` | Conclusao do jogo. |
| 346 | `return` | Mantem a pontuacao e a tela final. |
| 347 | `self.level = generate_level(self.level.number + 1, seed)` | Novo labirinto mais desafiador. |
| 348 | `self.hint_mode = "none"` | Dicas antigas nao migram para outra fase. |
| 349 | `self.hinted = False` | Recupera a possibilidade de dica com custo. |
| 350 | `self.state = "playing"` | Ativa movimentacao na nova area. |
| 351 | `self.message = "Nova zona. Avalie os riscos antes de escolher a rota."` | Instrucao. |
| 353 | `def show_route(self, mode: str) -> tuple[list[Position], int]:` | Consulta rota da fase atual. |
| 354 | `if mode not in ("safe", "short"):` | Valida opcao escolhida. |
| 355 | `raise ValueError("Modo de rota desconhecido")` | Erro de chamada explicito. |
| 356 | `if self.state != "playing":` | Disponibiliza rotas apenas durante a partida. |
| 357 | `return [], -1` | Nao calcula na introducao ou nos desafios. |
| 358 | `self.hint_mode = mode` | Atualiza opcao da interface. |
| 359 | `if not self.hinted:` | Cobra dica uma vez por fase, nao a cada passo. |
| 360 | `self.score = max(0, self.score - 5)` | Penaliza assistencia de navegacao. |
| 361 | `self.hinted = True` | Marca que o desconto ja foi aplicado. |
| 362 | `if mode == "safe":` | Escolha de otimizacao com risco. |
| 363 | `route, cost = astar(self.level.grid, self.level.player, self.level.objective, self.level.turns, self.level.door_open)` | A* temporal ponderado. |
| 364 | `self.message = "Rota segura: minimiza passos + penalidade de risco."` | Informa criterio. |
| 365 | `return route, cost` | Devolve custo ponderado e coordenadas. |
| 366 | `route = bfs(self.level.grid, self.level.player, self.level.objective, self.level.door_open)` | Menor rota geometrica. |
| 367 | `self.message = "Menor rota: pode atravessar espinhos e lasers ativos!"` | Alerta do criterio. |
| 368 | `return route, len(route) - 1 if route else -1` | Numero de passos do caminho. |

**Cobertura:** 325 linhas não vazias explicadas (inclui instruções, docstrings, comentários e estruturas).


---

## Arquivo `jogo.py`

[Trecho do código-fonte](../jogo.py) — 328 linhas físicas.

| Linha | Instrução / trecho | Explicação |
|---:|---|---|
| 1 | `"""LABIRINTO DOS ENIGMAS: ROTAS DE RISCO \| Trabalho A03 - Matematica Computacional.` | Inicia ou encerra uma docstring: texto documental que descreve o propósito do módulo ou função. |
| 3 | `Execute com \`python jogo.py\` apos instalar o Pygame (\`pip install -r requirements.txt\`).` | Executa ou configura a operação mostrada; a expressão é detalhada nos comentários do fonte. |
| 4 | `Todo comando importante recebe comentario; o guia explica cada linha numerada.` | Executa ou configura a operação mostrada; a expressão é detalhada nos comentários do fonte. |
| 5 | `"""` | Inicia ou encerra uma docstring: texto documental que descreve o propósito do módulo ou função. |
| 7 | `from __future__ import annotations` | Permite recursos modernos de anotacao de tipos. |
| 8 | `import math` | Calcula movimentos circulares e animacoes periodicas. |
| 9 | `import sys` | Permite finalizar o programa com codigo de retorno. |
| 10 | `from pathlib import Path` | Localiza arquivos sem depender do diretorio inicial. |
| 11 | `import pygame` | Biblioteca responsavel por janela, desenho, fontes e eventos. |
| 12 | `from src.logica import (` | Importa somente a interface publica do modelo matematico. |
| 13 | `COLS, ROWS, PERIOD, MAX_HEALTH, PUZZLES, Session,` | Dimensoes, regras e sessao do jogador. |
| 14 | `astar, bfs, hazard, laser_active, route_risk,` | Algoritmos e ferramentas de analise. |
| 15 | `)` | Encerra importacao agrupada por clareza. |
| 17 | `CELL = 32` | Cada vertice da matriz ocupa 32 por 32 pixels. |
| 18 | `MAP_W = COLS * CELL` | Largura da area de navegacao em pixels. |
| 19 | `MAP_H = ROWS * CELL` | Altura da area de navegacao em pixels. |
| 20 | `SCREEN_W = 1200` | Largura da janela do simulador. |
| 21 | `SCREEN_H = 750` | Altura da janela do simulador. |
| 22 | `MAP_X = 34` | Deslocamento horizontal do mapa dentro da janela. |
| 23 | `MAP_Y = 126` | Deslocamento vertical do mapa dentro da janela. |
| 24 | `SIDE_X = 804` | Coordenada inicial do painel de indicadores. |
| 25 | `SIDE_W = 362` | Largura reservada para painel lateral. |
| 26 | `FPS = 60` | Frequencia visual, sem alterar o tempo discreto dos algoritmos. |
| 27 | `BG = (9, 17, 30)` | Cor do fundo do simulador. |
| 28 | `PANEL = (15, 29, 48)` | Superficie dos paineis de informacao. |
| 29 | `PANEL_2 = (20, 39, 59)` | Tom secundario para caixas e botoes. |
| 30 | `BORDER = (41, 66, 84)` | Cor discreta dos contornos. |
| 31 | `WHITE = (239, 246, 255)` | Cor de alto contraste para textos principais. |
| 32 | `MUTED = (153, 175, 193)` | Cor de apoio para textos secundarios. |
| 33 | `TEAL = (77, 225, 198)` | Cor dos objetivos e das rotas seguras. |
| 34 | `GOLD = (248, 191, 83)` | Cor da chave e dos destaques de pontuacao. |
| 35 | `RED = (253, 107, 126)` | Cor de perigos ativos e vidas perdidas. |
| 36 | `PURPLE = (170, 138, 255)` | Cor dos enigmas e dos lasers. |
| 37 | `FLOOR = (23, 43, 60)` | Cor das celulas de piso transitavel. |
| 38 | `WALL = (52, 76, 98)` | Cor das paredes do labirinto. |
| 39 | `FONT_NAME = "dejavusans"` | Fonte com suporte aos caracteres do portugues. |
| 42 | `def font(size: int, bold: bool = False) -> pygame.font.Font:` | Constroi fonte sob demanda para cada dimensao. |
| 43 | `return pygame.font.SysFont(FONT_NAME, size, bold=bold)` | Usa fonte do sistema como fallback. |
| 46 | `def text(surface: pygame.Surface, message: str, x: int, y: int, size: int = 18, color: tuple = WHITE, bold: bool = False) -> None:` | Desenha uma linha de texto. |
| 47 | `image = font(size, bold).render(str(message), True, color)` | Converte texto para superficie com antialias. |
| 48 | `surface.blit(image, (x, y))` | Cola a superficie de texto na posicao desejada. |
| 51 | `def wrap(surface: pygame.Surface, message: str, x: int, y: int, width: int, size: int = 16, color: tuple = MUTED, line_height: int = 24) -> int:` | Quebra texto automaticamente. |
| 52 | `words = str(message).split()` | Divide frase em palavras sem perder a ordem. |
| 53 | `current = ""` | Guarda a linha em montagem. |
| 54 | `for word in words:` | Testa cada palavra da frase. |
| 55 | `trial = (current + " " + word).strip()` | Monta a linha candidata. |
| 56 | `if font(size).size(trial)[0] > width and current:` | Verifica se ultrapassa o limite. |
| 57 | `text(surface, current, x, y, size, color)` | Renderiza a linha que ja estava completa. |
| 58 | `y += line_height` | Passa para a proxima linha vertical. |
| 59 | `current = word` | Inicia nova linha com a palavra atual. |
| 60 | `else:` | Executa quando o texto ainda cabe no limite. |
| 61 | `current = trial` | Continua preenchendo a mesma linha. |
| 62 | `if current:` | A ultima linha precisa ser exibida mesmo sem ultrapassar o limite. |
| 63 | `text(surface, current, x, y, size, color)` | Desenha o restante da frase. |
| 64 | `y += line_height` | Devolve a proxima coordenada livre. |
| 65 | `return y` | Permite empilhar paragrafos sem sobreposicao. |
| 68 | `def rounded(surface: pygame.Surface, rect: tuple, color: tuple, radius: int = 14, border: tuple \| None = None) -> None:` | Desenha cartao arredondado. |
| 69 | `pygame.draw.rect(surface, color, rect, border_radius=radius)` | Preenche o painel. |
| 70 | `if border is not None:` | Uma borda e opcional. |
| 71 | `pygame.draw.rect(surface, border, rect, width=1, border_radius=radius)` | Desenha contorno suave. |
| 74 | `def button(surface: pygame.Surface, rect: pygame.Rect, label: str, mouse: tuple, active: bool = False, accent: tuple = TEAL) -> None:` | Desenha botao com estado visual. |
| 75 | `hovered = rect.collidepoint(mouse)` | Detecta aproximacao do mouse. |
| 76 | `color = (37, 75, 91) if hovered or active else PANEL_2` | Destaca selecao e passagem do ponteiro. |
| 77 | `rounded(surface, tuple(rect), color, 10, accent if active else BORDER)` | Pinta o botao. |
| 78 | `label_image = font(15, bold=True).render(label, True, WHITE if not active else accent)` | Centraliza o texto do botao. |
| 79 | `surface.blit(label_image, label_image.get_rect(center=rect.center))` | Exibe legenda centralizada. |
| 82 | `def tile_center(pos: tuple[int, int]) -> tuple[int, int]:` | Converte coordenadas discretas em pixels. |
| 83 | `row, col = pos` | Desempacota linha e coluna do grafo. |
| 84 | `return (MAP_X + col * CELL + CELL // 2, MAP_Y + row * CELL + CELL // 2)` | Centro da celula na tela. |
| 87 | `def draw_diamond(surface: pygame.Surface, x: int, y: int, radius: int, color: tuple) -> None:` | Desenha icone geométrico de destaque. |
| 88 | `pygame.draw.polygon(surface, color, [(x, y - radius), (x + radius, y), (x, y + radius), (x - radius, y)])` | Poligono de quatro pontas. |
| 91 | `def draw_grid(surface: pygame.Surface, session: Session, path: list[tuple[int, int]], mode: str, now: int) -> None:` | Desenha a representacao do grafo no labirinto. |
| 92 | `level = session.level` | Recupera o mapa e o agente da fase atual. |
| 93 | `rounded(surface, (MAP_X - 12, MAP_Y - 12, MAP_W + 24, MAP_H + 24), PANEL, 16, BORDER)` | Moldura do labirinto. |
| 94 | `for row in range(ROWS):` | Percorre todas as linhas da matriz. |
| 95 | `for col in range(COLS):` | Percorre todas as colunas da linha atual. |
| 96 | `symbol = level.grid[row][col]` | Le o conteudo da celula. |
| 97 | `left = MAP_X + col * CELL` | Calcula a posicao horizontal do quadrado. |
| 98 | `top = MAP_Y + row * CELL` | Calcula a posicao vertical do quadrado. |
| 99 | `rect = pygame.Rect(left + 1, top + 1, CELL - 2, CELL - 2)` | Guarda uma margem entre celulas. |
| 100 | `if symbol == "#":` | Verifica se o vertice e bloqueado por parede. |
| 101 | `rounded(surface, tuple(rect), WALL, 4)` | Desenha a parede resistente. |
| 102 | `pygame.draw.line(surface, (68, 94, 117), rect.topleft, (rect.right, rect.top), 1)` | Acabamento de relevo. |
| 103 | `continue` | Nao ha objetos dentro de uma parede. |
| 104 | `rounded(surface, tuple(rect), FLOOR, 4)` | Desenha o corredor acessivel. |
| 105 | `cx, cy = tile_center((row, col))` | Recupera o centro para desenhar os simbolos. |
| 106 | `if symbol == "R":` | Entulho representa uma barreira fisica. |
| 107 | `pygame.draw.polygon(surface, (126, 144, 157), [(left + 5, top + 23), (left + 10, top + 8), (left + 22, top + 6), (left + 28, top + 23)])` | Bloco de escombros. |
| 108 | `pygame.draw.line(surface, (75, 93, 106), (left + 12, top + 14), (left + 21, top + 19), 2)` | Fissura da pedra. |
| 109 | `elif symbol == "^":` | Espinhos provocam dano permanente ao entrar. |
| 110 | `for offset in (5, 14, 23):` | Repete tres pontas na largura do piso. |
| 111 | `pygame.draw.polygon(surface, RED, [(left + offset - 3, top + 25), (left + offset + 2, top + 7), (left + offset + 7, top + 25)])` | Triangulo pontiagudo. |
| 112 | `elif symbol == "~":` | Laser utiliza o tempo discreto para definir perigo. |
| 113 | `enabled = laser_active(level.turns)` | Verifica a fase do ciclo modular do obstaculo. |
| 114 | `shade = PURPLE if enabled else (87, 80, 111)` | Laser ativo brilha mais. |
| 115 | `pygame.draw.line(surface, shade, (left + 7, cy), (left + 25, cy), 5 if enabled else 2)` | Emite feixe horizontal. |
| 116 | `pygame.draw.circle(surface, shade, (left + 6, cy), 4)` | Desenha emissor esquerdo. |
| 117 | `pygame.draw.circle(surface, shade, (left + 26, cy), 4)` | Desenha emissor direito. |
| 118 | `elif symbol == "D":` | A porta depende da conjuncao chave E resposta. |
| 119 | `shade = TEAL if level.door_open else (195, 132, 97)` | Altera cor ao desbloquear. |
| 120 | `pygame.draw.rect(surface, shade, (left + 8, top + 5, 16, 24), border_radius=3)` | Desenha a estrutura da porta. |
| 121 | `pygame.draw.circle(surface, BG, (left + 20, top + 17), 2)` | Desenha a fechadura. |
| 122 | `elif symbol == "K":` | Credencial que libera um dos predicados de acesso. |
| 123 | `pygame.draw.circle(surface, GOLD, (cx - 5, cy - 3), 6, 3)` | Parte circular da chave. |
| 124 | `pygame.draw.line(surface, GOLD, (cx, cy), (cx + 10, cy + 9), 4)` | Corpo metalico da chave. |
| 125 | `pygame.draw.line(surface, GOLD, (cx + 6, cy + 6), (cx + 11, cy + 2), 3)` | Dente da chave. |
| 126 | `elif symbol == "E":` | Desafio matematico funciona como checkpoint de logica. |
| 127 | `pygame.draw.circle(surface, PURPLE, (cx, cy), 12)` | Corpo circular do enigma. |
| 128 | `text(surface, "?", cx - 5, cy - 12, 20, BG, True)` | Simbolo de pergunta. |
| 129 | `elif symbol == "S":` | Representa o destino da rota de evacuacao. |
| 130 | `pygame.draw.circle(surface, TEAL, (cx, cy), 12, 3)` | Alvo verde de chegada. |
| 131 | `pygame.draw.circle(surface, TEAL, (cx, cy), 4)` | Nucleo da chegada. |
| 132 | `if path:` | So mostra o planejamento depois da solicitacao de ajuda. |
| 133 | `shade = TEAL if mode == "safe" else GOLD` | Separa rota segura da menor rota geometrica. |
| 134 | `for idx, point in enumerate(path[1:], 1):` | Nao realca a posicao inicial do caminho. |
| 135 | `center = tile_center(point)` | Coordenadas visuais do vertice analisado. |
| 136 | `pygame.draw.circle(surface, shade, center, 4 if idx % 3 else 5)` | Marca etapas do caminho. |
| 137 | `cx, cy = tile_center(level.player)` | Posiciona jogador sobre sua celula atual. |
| 138 | `pulse = math.sin(now * 0.005) * 2` | Pequena animacao usando funcao seno. |
| 139 | `pygame.draw.circle(surface, (12, 41, 60), (cx, cy), int(16 + pulse))` | Halo de destaque do agente. |
| 140 | `pygame.draw.circle(surface, (91, 187, 255), (cx, cy), 12)` | Corpo circular do jogador. |
| 141 | `pygame.draw.circle(surface, WHITE, (cx + 3, cy - 3), 4)` | Reflexo sobre o personagem. |
| 144 | `def draw_panel(surface: pygame.Surface, session: Session, path: list, route_cost: int, seconds: float, mouse: tuple, buttons: dict, show_debug: bool) -> None:` | Painel direito de matematica aplicada. |
| 145 | `level = session.level` | Permite consultar todos os campos da fase. |
| 146 | `rounded(surface, (SIDE_X, 126, SIDE_W, 570), PANEL, 16, BORDER)` | Cartao de metricas. |
| 147 | `text(surface, "PAINEL DE NAVEGAÇÃO", SIDE_X + 20, 148, 15, TEAL, True)` | Identifica area analitica. |
| 148 | `text(surface, f"FASE {level.number:02d} / 03", SIDE_X + 20, 186, 24, WHITE, True)` | Indica progresso. |
| 149 | `text(surface, "SISTEMA DE ROTAS E RISCOS", SIDE_X + 20, 222, 12, MUTED)` | Resume objetivo do jogo. |
| 150 | `pygame.draw.line(surface, BORDER, (SIDE_X + 18, 255), (SIDE_X + SIDE_W - 18, 255), 1)` | Separa indicadores. |
| 151 | `metrics = [("PONTOS", str(session.score)), ("TURNOS", str(level.turns)), ("TEMPO", f"{int(seconds)//60:02d}:{int(seconds)%60:02d}")]` | Agrupa metricas visiveis. |
| 152 | `for i, (label, value) in enumerate(metrics):` | Desenha colunas alinhadas. |
| 153 | `mx = SIDE_X + 20 + i * 115` | Computa o inicio de cada indicador. |
| 154 | `text(surface, label, mx, 274, 11, MUTED, True)` | Titula indicador. |
| 155 | `text(surface, value, mx, 297, 21, GOLD if i == 0 else WHITE, True)` | Exibe valor atualizado. |
| 156 | `pygame.draw.line(surface, BORDER, (SIDE_X + 18, 337), (SIDE_X + SIDE_W - 18, 337), 1)` | Separa a barra de saude. |
| 157 | `text(surface, "INTEGRIDADE", SIDE_X + 20, 350, 12, MUTED, True)` | Rotulo de vidas. |
| 158 | `for life in range(MAX_HEALTH):` | Desenha quatro indicadores de resistencia. |
| 159 | `color = RED if life < level.health else (55, 71, 85)` | Vidas perdidas ficam apagadas. |
| 160 | `pygame.draw.circle(surface, color, (SIDE_X + 161 + life * 30, 359), 9)` | Sinaliza vida individual. |
| 161 | `text(surface, "CREDENCIAL", SIDE_X + 20, 387, 12, MUTED)` | Primeira condicao da logica. |
| 162 | `text(surface, "SIM" if level.has_key else "NÃO", SIDE_X + 180, 386, 14, TEAL if level.has_key else GOLD, True)` | Booleano da chave. |
| 163 | `text(surface, "ENIGMA", SIDE_X + 20, 414, 12, MUTED)` | Segunda condicao da logica. |
| 164 | `text(surface, "VALIDADO" if level.solved else "PENDENTE", SIDE_X + 180, 413, 14, TEAL if level.solved else GOLD, True)` | Booleano da resposta. |
| 165 | `text(surface, "PORTA = CHAVE ∧ ENIGMA", SIDE_X + 20, 443, 13, TEAL if level.door_open else MUTED, True)` | Formula proposicional de acesso. |
| 166 | `pygame.draw.line(surface, BORDER, (SIDE_X + 18, 475), (SIDE_X + SIDE_W - 18, 475), 1)` | Separa o roteamento. |
| 167 | `text(surface, "PLANEJAMENTO MATEMÁTICO", SIDE_X + 20, 490, 13, WHITE, True)` | Area para BFS e A*. |
| 168 | `for name in ("safe", "short"):` | Desenha um botao para cada criterio de busca. |
| 169 | `label = "H • A* ROTA SEGURA" if name == "safe" else "J • BFS MENOR ROTA"` | Legendas e atalhos. |
| 170 | `button(surface, buttons[name], label, mouse, session.hint_mode == name, TEAL if name == "safe" else GOLD)` | Apresenta modo. |
| 171 | `if path:` | Dados da rota aparecem apenas apos uma consulta. |
| 172 | `text(surface, f"Rota: {max(0, len(path)-1)} ações  \|  custo: {route_cost}", SIDE_X + 20, 606, 12, TEAL, True)` | Comprimento e custo. |
| 173 | `if session.hint_mode == "short":` | BFS nao considera penalidades de dano. |
| 174 | `risk = route_risk(level.grid, path, level.turns)` | Conta possiveis colisoes na rota. |
| 175 | `text(surface, f"Possíveis impactos na BFS: {risk}", SIDE_X + 20, 627, 12, RED if risk else MUTED)` | Indicador de risco. |
| 176 | `else:` | Caminho otimizado pelo custo ponderado. |
| 177 | `text(surface, "A* inclui tempo e risco na decisão", SIDE_X + 20, 627, 11, MUTED)` | Explica criterio. |
| 178 | `else:` | Nao ha rota desenhada quando a consulta nao foi solicitada. |
| 179 | `text(surface, "Compare menor distância × menor risco", SIDE_X + 20, 610, 11, MUTED)` | Incentiva comparacao. |
| 180 | `if show_debug:` | Mostra formalizacao opcional para apresentacao academica. |
| 181 | `text(surface, "f(n)=g(n)+h(n)  \|  h=Manhattan", SIDE_X + 20, 658, 11, PURPLE)` | Equacao do A*. |
| 182 | `else:` | Indicacao para abrir formula matematica. |
| 183 | `text(surface, "M: mostrar fórmula matemática", SIDE_X + 20, 658, 11, MUTED)` | Legenda de ajuda. |
| 186 | `def overlay(surface: pygame.Surface, session: Session, answer: str, mouse: tuple, buttons: dict) -> None:` | Janelas de introducao e estados especiais. |
| 187 | `if session.state == "playing":` | Jogo normal nao precisa de modal. |
| 188 | `return` | Mantem o mapa livre. |
| 189 | `shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)` | Cria camada com transparencia. |
| 190 | `shade.fill((5, 12, 22, 218))` | Escurece o fundo para focar a janela. |
| 191 | `surface.blit(shade, (0, 0))` | Exibe a pelicula sobre o jogo. |
| 192 | `modal = (260, 175, 680, 400)` | Retangulo central comum aos estados. |
| 193 | `rounded(surface, modal, PANEL, 22, BORDER)` | Desenha a caixa principal. |
| 194 | `if session.state == "intro":` | Primeiro contato explica a experiencia. |
| 195 | `text(surface, "LABIRINTO DOS ENIGMAS", 310, 223, 30, TEAL, True)` | Titulo da introducao. |
| 196 | `text(surface, "Missão: sair de um ambiente com riscos", 310, 276, 19, WHITE)` | Contextualiza o problema. |
| 197 | `wrap(surface, "Planeje rotas, colete uma credencial, resolva o enigma e evite espinhos, escombros e lasers que alternam a cada turno.", 310, 312, 585, 17, MUTED, 28)` | Explica a dinamica. |
| 198 | `text(surface, "BFS procura menos passos. A* considera distância + dano.", 310, 407, 15, GOLD)` | Relacao com a disciplina. |
| 199 | `button(surface, buttons["primary"], "ENTER  •  INICIAR SIMULAÇÃO", mouse, True)` | Botao de partida. |
| 200 | `elif session.state == "quiz":` | Entrada numerica permite resolver a prova da fase. |
| 201 | `p = PUZZLES[session.level.number - 1]` | Enigma correspondente a fase atual. |
| 202 | `text(surface, "VERIFICAÇÃO MATEMÁTICA", 310, 214, 25, PURPLE, True)` | Titulo da verificacao. |
| 203 | `text(surface, p["question"], 310, 277, 22, WHITE, True)` | Enunciado principal. |
| 204 | `rounded(surface, (310, 335, 570, 57), PANEL_2, 10, PURPLE)` | Campo grafico para resposta. |
| 205 | `text(surface, answer + "\|", 329, 349, 23, GOLD, True)` | Cursor e valor digitado. |
| 206 | `if session.hint_open:` | Exibe ajuda apenas quando solicitada. |
| 207 | `wrap(surface, "DICA: " + p["hint"], 312, 413, 560, 16, GOLD, 25)` | Apresenta a sequencia. |
| 208 | `else:` | Instrucao de como solicitar a ajuda. |
| 209 | `text(surface, "Pressione I para mostrar uma dica.", 312, 416, 16, MUTED)` | Texto explicativo. |
| 210 | `wrap(surface, session.message, 312, 461, 560, 14, MUTED, 21)` | Retorno de validacao. |
| 211 | `text(surface, "ENTER: confirmar    BACKSPACE: apagar", 312, 521, 14, TEAL)` | Comandos do formulario. |
| 212 | `elif session.state == "cleared":` | Etapa encerrada com sucesso. |
| 213 | `text(surface, "ZONA CONCLUÍDA", 310, 230, 32, TEAL, True)` | Mensagem de conquista. |
| 214 | `text(surface, f"Pontuação acumulada: {session.score}", 310, 303, 24, GOLD)` | Resumo da rodada. |
| 215 | `wrap(surface, "A decisão matemática correta transforma um ambiente complexo em uma rota viável.", 310, 363, 560, 17, MUTED, 28)` | Conexao didatica. |
| 216 | `button(surface, buttons["primary"], "ENTER  •  CONTINUAR", mouse, True)` | Passa para outra fase. |
| 217 | `elif session.state == "lost":` | Colisoes esgotaram a integridade do agente. |
| 218 | `text(surface, "RISCO CRÍTICO", 310, 230, 32, RED, True)` | Tela de derrota. |
| 219 | `wrap(surface, "Sua integridade chegou a zero. Reavalie o caminho: a rota mais curta nem sempre é a mais segura.", 310, 308, 570, 18, MUTED, 30)` | Explicacao do erro. |
| 220 | `button(surface, buttons["primary"], "R  •  REINICIAR", mouse, True, RED)` | Possibilita uma nova tentativa. |
| 221 | `elif session.state == "victory":` | Todas as tres fases foram superadas. |
| 222 | `text(surface, "MISSÃO CONCLUÍDA!", 310, 228, 30, TEAL, True)` | Mensagem final. |
| 223 | `text(surface, f"Pontuação final: {session.score}", 310, 305, 25, GOLD, True)` | Resultado da sessao. |
| 224 | `text(surface, f"Total de impactos: {session.impacts}", 310, 351, 19, WHITE)` | Indicador de seguranca. |
| 225 | `button(surface, buttons["primary"], "R  •  JOGAR NOVAMENTE", mouse, True)` | Reinicia a experiencia. |
| 228 | `def main() -> int:` | Ponto de entrada da interface Pygame. |
| 229 | `pygame.init()` | Inicializa os modulos de video, teclado e fontes. |
| 230 | `pygame.key.set_repeat(160, 100)` | Permite movimento repetido ao segurar setas. |
| 231 | `screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))` | Cria janela com dimensoes fixas. |
| 232 | `pygame.display.set_caption("Labirinto dos Enigmas \| Matematica Computacional")` | Identifica janela. |
| 233 | `clock = pygame.time.Clock()` | Controla a taxa visual de atualizacao. |
| 234 | `session = Session()` | Instancia o modelo sem misturar logica e desenho. |
| 235 | `answer = ""` | Armazena entrada numerica corrente no desafio. |
| 236 | `path: list[tuple[int, int]] = []` | Lista do caminho calculado por BFS ou A*. |
| 237 | `route_cost = -1` | Custo ponderado da rota inicialmente desconhecido. |
| 238 | `show_debug = False` | Permite exibir formalizacao do A* opcionalmente. |
| 239 | `seconds = 0.0` | Cronometro apenas visual: NAO define o tempo dos lasers. |
| 240 | `buttons = {"safe": pygame.Rect(SIDE_X + 20, 522, 318, 35), "short": pygame.Rect(SIDE_X + 20, 563, 318, 35), "primary": pygame.Rect(310, 485, 570, 55)}` | Regioes clicaveis. |
| 241 | `moves = {pygame.K_UP: (-1, 0), pygame.K_w: (-1, 0), pygame.K_DOWN: (1, 0), pygame.K_s: (1, 0), pygame.K_LEFT: (0, -1), pygame.K_a: (0, -1), pygame.K_RIGHT: (0, 1), pygame.K_d: (0, 1), pygame.K_SPACE: (0, 0)}` | Mapa de controles. |
| 242 | `running = True` | Variavel booleana de continuidade do programa. |
| 243 | `while running:` | Loop principal: entrada, atualizacao e desenho. |
| 244 | `dt = clock.tick(FPS) / 1000.0` | Converte duracao do quadro em segundos. |
| 245 | `now = pygame.time.get_ticks()` | Tempo visual utilizado na animacao do jogador. |
| 246 | `mouse = pygame.mouse.get_pos()` | Posicao atual do cursor para efeito hover. |
| 247 | `if session.state in ("playing", "quiz"):` | Cronometro corre durante as duas etapas. |
| 248 | `seconds += dt` | Avanca tempo visual real de forma independente dos turnos. |
| 249 | `for event in pygame.event.get():` | Consome eventos para impedir congelamento do sistema. |
| 250 | `if event.type == pygame.QUIT:` | Usuario clicou em fechar janela. |
| 251 | `running = False` | Encerra loop normalmente. |
| 252 | `continue` | Ignora processamento adicional deste evento. |
| 253 | `if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:` | Clique esquerdo do mouse. |
| 254 | `if session.state == "playing":` | Botoes de rota so funcionam em partida ativa. |
| 255 | `for name in ("safe", "short"):` | Confere ambos os botoes do painel. |
| 256 | `if buttons[name].collidepoint(event.pos):` | Verifica se o clique atingiu o botao. |
| 257 | `path, route_cost = session.show_route(name)` | Executa BFS ou A* do modelo. |
| 258 | `elif buttons["primary"].collidepoint(event.pos):` | Clique no botao de inicio/continuidade. |
| 259 | `if session.state == "intro":` | Estado inicial da aplicacao. |
| 260 | `session.begin()` | Inicia a primeira fase. |
| 261 | `elif session.state == "cleared":` | Fase finalizada com sucesso. |
| 262 | `session.next_level()` | Avanca para a etapa seguinte. |
| 263 | `elif session.state in ("lost", "victory"):` | Fim de jogo ou derrota. |
| 264 | `session.reset()` | Reinicia pontuacao e labirintos. |
| 265 | `seconds = 0.0` | Reinicia cronometro da partida. |
| 266 | `path = []` | Esconde rota de qualquer fase anterior. |
| 267 | `continue` | Clique processado; passa ao proximo evento. |
| 268 | `if event.type != pygame.KEYDOWN:` | Eventos de movimento exigem tecla pressionada. |
| 269 | `continue` | Ignora entrada nao relevante. |
| 270 | `if event.key == pygame.K_ESCAPE:` | ESC fecha o programa em qualquer estado. |
| 271 | `running = False` | Finaliza aplicacao sem erros. |
| 272 | `continue` | Nao processa outras operacoes. |
| 273 | `if event.key == pygame.K_r and session.state != "quiz":` | Atalho global para reiniciar, exceto durante enigma. |
| 274 | `session.reset()` | Gera nova partida limpa. |
| 275 | `path = []` | Desliga trilha de navegacao antiga. |
| 276 | `answer = ""` | Limpa campos de texto antigos. |
| 277 | `seconds = 0.0` | Zera cronometro visual. |
| 278 | `continue` | Terminou tratamento de reinicio. |
| 279 | `if session.state == "intro" and event.key == pygame.K_RETURN:` | ENTER na tela inicial. |
| 280 | `session.begin()` | Inicia sessao em estado valido. |
| 281 | `continue` | Evita comandos simultaneos. |
| 282 | `if session.state == "cleared" and event.key == pygame.K_RETURN:` | ENTER apos finalizar fase. |
| 283 | `session.next_level()` | Passa a fase 2/3 ou vitoria. |
| 284 | `path = []` | Limpa rota antiga ao mudar o objetivo. |
| 285 | `continue` | Evento concluido. |
| 286 | `if session.state == "quiz":` | Enigma intercepta as entradas de teclado. |
| 287 | `if event.key == pygame.K_i:` | Atalho para dica matematica. |
| 288 | `session.hint_open = True` | Mostra a pista do enigma. |
| 289 | `elif event.key == pygame.K_BACKSPACE:` | Tecla de apagar. |
| 290 | `answer = answer[:-1]` | Retira ultimo digito digitado. |
| 291 | `elif event.key == pygame.K_RETURN:` | Valida resposta fornecida. |
| 292 | `accepted = session.answer(answer)` | Funcao booleana do modelo. |
| 293 | `if accepted:` | Enigma correto desbloqueia a porta. |
| 294 | `answer = ""` | Limpa valor que ja foi utilizado. |
| 295 | `path = []` | Forca nova rota com porta aberta. |
| 296 | `elif event.unicode.isascii() and event.unicode.isdigit() and len(answer) < 8:` | Apenas digitos ASCII permitidos. |
| 297 | `answer += event.unicode` | Anexa caracter validado sem risco de overflow textual. |
| 298 | `continue` | Impede que o enigma movimente o personagem. |
| 299 | `if session.state != "playing":` | Derrota e vitoria nao aceitam movimento. |
| 300 | `continue` | Espera um comando de reiniciar ou continuar. |
| 301 | `if event.key == pygame.K_h:` | H: rota ponderada e temporal com A*. |
| 302 | `path, route_cost = session.show_route("safe")` | Busca minimizar passos e risco. |
| 303 | `elif event.key == pygame.K_j:` | J: rota geometrica curta com BFS. |
| 304 | `path, route_cost = session.show_route("short")` | Busca minimo numero de passos. |
| 305 | `elif event.key == pygame.K_m:` | M: exibe a funcao matematica A*. |
| 306 | `show_debug = not show_debug` | Alterna modo tecnico para a apresentacao. |
| 307 | `elif event.key in moves:` | Setas, WASD ou espaco fazem acoes validas. |
| 308 | `session.move(moves[event.key])` | Atualiza grafo, objetos, impactos e pontuacao. |
| 309 | `path = []` | Um caminho consultado fica obsoleto apos cada acao. |
| 310 | `screen.fill(BG)` | Limpa quadro antes de redesenhar tudo. |
| 311 | `for i in range(0, SCREEN_W, 40):` | Mostra grid discreto decorativo no fundo. |
| 312 | `pygame.draw.line(screen, (14, 27, 42), (i, 0), (i, SCREEN_H), 1)` | Linha vertical decorativa. |
| 313 | `text(screen, "LABIRINTO", MAP_X, 31, 32, WHITE, True)` | Marca principal do jogo. |
| 314 | `text(screen, "DOS ENIGMAS", MAP_X + 205, 33, 29, TEAL, True)` | Segunda metade do titulo. |
| 315 | `text(screen, "ROTAS DE RISCO  \|  MATEMÁTICA COMPUTACIONAL", MAP_X + 2, 83, 13, MUTED, True)` | Contexto academico. |
| 316 | `draw_grid(screen, session, path, session.hint_mode, now)` | Renderiza a grade sobre o painel. |
| 317 | `draw_panel(screen, session, path, route_cost, seconds, mouse, buttons, show_debug)` | Mostra metricas e botoes. |
| 318 | `rounded(screen, (MAP_X - 12, 638, MAP_W + 24, 58), PANEL, 12, BORDER)` | Barra de mensagens contextual. |
| 319 | `wrap(screen, session.message, MAP_X + 4, 650, MAP_W - 20, 15, GOLD if "RISCO" in session.message else WHITE, 22)` | Informa evento ao jogador. |
| 320 | `text(screen, "WASD/SETAS mover    ESPAÇO esperar    H A* seguro    J BFS curto    M fórmula    R reiniciar    ESC sair", 35, 713, 13, MUTED)` | Lembrete de controles. |
| 321 | `overlay(screen, session, answer, mouse, buttons)` | Exibe modal quando o estado exigir. |
| 322 | `pygame.display.flip()` | Troca o quadro desenhado pelo quadro visivel. |
| 323 | `pygame.quit()` | Fecha os subsistemas graficos com seguranca. |
| 324 | `return 0` | Retorna sucesso ao sistema operacional. |
| 327 | `if __name__ == "__main__":` | Impede execucao automatica quando o arquivo e importado. |
| 328 | `sys.exit(main())` | Inicia a interface e propaga o codigo de saida. |

**Cobertura:** 301 linhas não vazias explicadas (inclui instruções, docstrings, comentários e estruturas).


---

## Arquivo `tests/test_logica.py`

[Trecho do código-fonte](../../tests/test_logica.py) — 110 linhas físicas.

| Linha | Instrução / trecho | Explicação |
|---:|---|---|
| 1 | `"""Testes repetiveis sem Pygame para confiabilidade da modelagem matematica."""` | Inicia ou encerra uma docstring: texto documental que descreve o propósito do módulo ou função. |
| 3 | `from __future__ import annotations` | Permite anotacoes padronizadas. |
| 4 | `import unittest` | Biblioteca de testes ja incluida no Python. |
| 5 | `from src.logica import (` | Componentes logicos testados sem abrir janela. |
| 6 | `ROWS, COLS, START, EXIT, PERIOD, MAX_HEALTH,` | Constantes do grafo. |
| 7 | `PUZZLES, Session, generate_level, bfs, astar, hazard,` | Funcoes e objetos testados. |
| 8 | `neighbors, manhattan, route_risk, walkable, laser_active,` | Auxiliares validados. |
| 9 | `)` | Fim do conjunto de importacoes. |
| 12 | `class TestMath(unittest.TestCase):` | Testa formulas discretas independentes do jogo. |
| 13 | `def test_manhattan(self) -> None:` | Distancia usa norma L1. |
| 14 | `self.assertEqual(manhattan((2, 3), (5, 8)), 8)` | \|2-5\| + \|3-8\| = 8. |
| 16 | `def test_cycle(self) -> None:` | Testa modulo 4 dos lasers. |
| 17 | `self.assertEqual([laser_active(t) for t in range(8)], [True, True, False, False] * 2)` | Metade ativa. |
| 19 | `def test_limits(self) -> None:` | Confere que movimento nao acessa fora dos limites. |
| 20 | `grid = [["." for _ in range(COLS)] for _ in range(ROWS)]` | Grade aberta para isolar fronteira. |
| 21 | `self.assertFalse(walkable(grid, (-1, 1), True))` | Linha negativa bloqueada. |
| 22 | `self.assertFalse(walkable(grid, (ROWS, 0), True))` | Linha acima do maximo. |
| 23 | `self.assertFalse(walkable(grid, (0, COLS), True))` | Coluna acima do maximo. |
| 25 | `def test_astar_temporal(self) -> None:` | Esperar evita risco temporario quando e vantajoso. |
| 26 | `grid = [["#" for _ in range(COLS)] for _ in range(ROWS)]` | Grade fechada. |
| 27 | `grid[1][1], grid[1][2] = ".", "~"` | Corredor com um laser no destino. |
| 28 | `path, cost = astar(grid, (1, 1), (1, 2), 0, True)` | Inicio em fase 0. |
| 29 | `self.assertEqual(path, [(1, 1), (1, 1), (1, 2)])` | Aguarda para entrar no turno 2. |
| 30 | `self.assertEqual(cost, 2)` | Dois turnos sem penalidade. |
| 31 | `self.assertEqual(route_risk(grid, path, 0), 0)` | Sem contato com laser ativo. |
| 33 | `def test_bfs_vs_astar(self) -> None:` | Compara distancia geometrica e seguranca. |
| 34 | `grid = [["#" for _ in range(COLS)] for _ in range(ROWS)]` | Grade isolada. |
| 35 | `for row in (1, 2):` | Duas linhas acessiveis para o desvio. |
| 36 | `for col in range(1, 5):` | Quatro colunas de conexao. |
| 37 | `grid[row][col] = "."` | Libera um retangulo conectado. |
| 38 | `grid[1][3] = "^"` | Adiciona espinhos ao caminho curto. |
| 39 | `short = bfs(grid, (1, 1), (1, 4), True)` | Caminho com tres passos. |
| 40 | `safe, cost = astar(grid, (1, 1), (1, 4), 0, True)` | Minimiza custo com risco. |
| 41 | `self.assertEqual(len(short) - 1, 3)` | BFS escolhe distancia geometrica. |
| 42 | `self.assertEqual(route_risk(grid, short, 0), 1)` | BFS nao foge dos espinhos. |
| 43 | `self.assertEqual(route_risk(grid, safe, 0), 0)` | A* evita espinhos. |
| 44 | `self.assertEqual(cost, len(safe) - 1)` | Sem danos, o custo soma apenas passos. |
| 45 | `self.assertGreater(len(safe), len(short))` | A rota segura pode ser mais longa. |
| 48 | `class TestGeneration(unittest.TestCase):` | Valida muitas geracoes aleatorias. |
| 49 | `def test_500_seeds(self) -> None:` | Testa reproducibilidade e invariantes. |
| 50 | `for seed in range(500):` | Repeticao para detectar mapas raros impossiveis. |
| 51 | `level = generate_level(seed % 3 + 1, seed)` | Fases 1 a 3 com seeds diferentes. |
| 52 | `with self.subTest(seed=seed):` | Identifica exatamente o seed quando houver erro. |
| 53 | `self.assertEqual(len(level.grid), ROWS)` | Quantidade correta de linhas. |
| 54 | `self.assertTrue(all(len(row) == COLS for row in level.grid))` | Quantidade de colunas. |
| 55 | `self.assertTrue(bfs(level.grid, START, level.key, False))` | Chave disponivel. |
| 56 | `self.assertTrue(bfs(level.grid, level.key, level.puzzle, False))` | Enigma disponivel. |
| 57 | `self.assertTrue(bfs(level.grid, level.puzzle, EXIT, True))` | Saida apos abertura. |
| 58 | `self.assertFalse(bfs(level.grid, START, EXIT, False))` | Porta realmente impede passagem. |
| 59 | `self.assertTrue(all(not hazard(level.grid, p, 0) for p in level.protected))` | Rota reservada sem perigo. |
| 60 | `self.assertTrue(all(level.grid[p[0]][p[1]] != "R" for p in level.protected))` | Sem entulho na rota. |
| 61 | `self.assertEqual(level.player, START)` | Jogador inicial consistente. |
| 62 | `self.assertEqual(level.health, MAX_HEALTH)` | Integridade restaurada. |
| 64 | `def test_reproducibility(self) -> None:` | Mesma seed gera mesma configuracao. |
| 65 | `one = generate_level(2, 1234)` | Primeira geracao. |
| 66 | `two = generate_level(2, 1234)` | Geracao repetida. |
| 67 | `self.assertEqual(one.grid, two.grid)` | Matriz identica na mesma seed. |
| 68 | `self.assertEqual(one.key, two.key)` | Chave na mesma posicao. |
| 69 | `self.assertEqual(one.puzzle, two.puzzle)` | Enigma na mesma posicao. |
| 72 | `class TestSession(unittest.TestCase):` | Verifica maquina de estados e tratamento de erro. |
| 73 | `def test_solve_and_finish(self) -> None:` | Executa as tres fases sem Pygame. |
| 74 | `session = Session()` | Nova sessao logica. |
| 75 | `session.reset(seed=77)` | Mapa inicial reproduzivel. |
| 76 | `for number in range(1, 4):` | Percorre fases numeradas de 1 a 3. |
| 77 | `self.assertEqual(session.level.number, number)` | Confere fase ativa. |
| 78 | `for target in (session.level.key, session.level.puzzle):` | Primeiro chave; depois enigma. |
| 79 | `route, _ = astar(session.level.grid, session.level.player, target, session.level.turns, session.level.door_open)` | Rota com risco. |
| 80 | `self.assertTrue(route)` | Caminho deve existir. |
| 81 | `for previous, nxt in zip(route, route[1:]):` | Percorre cada aresta, incluindo espera. |
| 82 | `session.move((nxt[0] - previous[0], nxt[1] - previous[1]))` | Movimento ortogonal permitido. |
| 83 | `self.assertNotEqual(session.state, "lost")` | Rota segura nao pode causar derrota. |
| 84 | `self.assertEqual(session.state, "quiz")` | Enigma foi alcancado. |
| 85 | `self.assertFalse(session.answer("abc"))` | Resposta nao numerica rejeitada. |
| 86 | `self.assertFalse(session.answer("999999999"))` | Entrada excessiva rejeitada. |
| 87 | `self.assertTrue(session.answer(PUZZLES[number - 1]["answer"]))` | Resposta da fase correta. |
| 88 | `self.assertTrue(session.level.door_open)` | AND de condicoes habilita porta. |
| 89 | `route, _ = astar(session.level.grid, session.level.player, EXIT, session.level.turns, True)` | Busca ate saida. |
| 90 | `for previous, nxt in zip(route, route[1:]):` | Caminha pela rota escolhida. |
| 91 | `session.move((nxt[0] - previous[0], nxt[1] - previous[1]))` | Executa um turno por acao. |
| 92 | `self.assertNotEqual(session.state, "lost")` | Sem danos letais na rota segura. |
| 93 | `self.assertEqual(session.state, "cleared")` | Saida conquistada. |
| 94 | `session.next_level(seed=77 + number)` | Avanca ou vence apos a terceira. |
| 95 | `self.assertEqual(session.state, "victory")` | Verifica condicao de finalizacao. |
| 96 | `self.assertEqual(session.impacts, 0)` | Roteamento ponderado eliminou impactos. |
| 97 | `self.assertGreater(session.score, 0)` | Jogador acumulou pontos. |
| 99 | `def test_invalid_actions(self) -> None:` | Limites e entradas nao mudam a partida indevidamente. |
| 100 | `session = Session()` | Cria sessao independente. |
| 101 | `session.reset(seed=9)` | Define fase conhecida. |
| 102 | `original = session.level.player` | Guarda posicao para comparacao. |
| 103 | `self.assertEqual(session.move((3, 3)), "invalid")` | Movimento diagonal invalido. |
| 104 | `self.assertEqual(session.level.player, original)` | Protege a posicao do jogador. |
| 105 | `self.assertEqual(session.level.turns, 0)` | Entrada invalida nao avanca o turno. |
| 106 | `self.assertFalse(session.answer("32"))` | Nao responde sem modal aberto. |
| 109 | `if __name__ == "__main__":` | Permite rodar diretamente como script de teste. |
| 110 | `unittest.main()` | Descobre e executa os casos escritos acima. |

**Cobertura:** 95 linhas não vazias explicadas (inclui instruções, docstrings, comentários e estruturas).