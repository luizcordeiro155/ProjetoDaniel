# Guia de leitura — explicação linha por linha do código Python

**Projeto:** Labirinto dos Enigmas: Rotas de Risco  
**Disciplina:** Matemática Computacional Aplicada  
**Professor:** Daniel Henrique Matos de Paiva  
**Autor identificado:** Luiz Henrique Cordeiro dos Santos — RA 326122345

## Como usar o material

Leia primeiro [`CONCEITOS_MATEMATICOS.md`](CONCEITOS_MATEMATICOS.md) e depois acompanhe o arquivo `.py` com a tabela correspondente. **Cada linha não vazia** dos três arquivos está enumerada aqui; instruções significativas possuem **comentários explicativos diretamente no código-fonte**. Os números de linha correspondem aos arquivos atualizados da branch `main`.

**Glossário:** `=` atribuição; `==` comparação; `!=` diferente; `and` conjunção; `or` disjunção; `not` negação; `+=` soma acumulada; `%` resto modular; `//` divisão inteira; `[]` indexação/lista; `{}` conjunto/dicionário; `[::-1]` inversão de lista; `None` ausência; `return` resultado; `continue` próxima iteração; `break` saída do laço; `self` instância; `@dataclass` classe de dados; `@property` atributo calculado; `->` anotação de retorno.

**Novo mecanismo de colisão:** `safe_neighbors` identifica refúgios adjacentes, `safe_retreat` prioriza a casa anterior e procura alternativa quando necessário. A geração preserva `N_s(p) ≠ ∅` para cada perigo. `Session.move` desconta vida e pontuação, e `jogo.py` faz o personagem piscar em vermelho durante 850 ms sem adicionar turnos ao laser.

---


## Arquivo `src/logica.py`

**405 linhas físicas.** Inclui instruções, comentários, linhas em branco e blocos de texto.

| Linha | Instrução / trecho | Explicação |
|---:|---|---|
| 1 | `"""Modelo matematico puro: matriz, grafo, DFS, BFS, A* temporal e regras.` | Texto documental que contextualiza a estrutura ou a função. |
| 3 | `Este modulo nao importa Pygame: a simulacao pode ser testada sem abrir janelas.` | Parte do bloco de código; a finalidade é indicada pelo contexto e pelos comentários adjacentes. |
| 4 | `Cada operacao significativa traz comentario e o guia detalha as linhas.` | Parte do bloco de código; a finalidade é indicada pelo contexto e pelos comentários adjacentes. |
| 5 | `"""` | Texto documental que contextualiza a estrutura ou a função. |
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
| 64 | `def safe_neighbors(grid: list[list[str]], pos: Position, door_open: bool) -> list[Position]:` | Refugios vizinhos sem perigos permanentes ou temporarios. |
| 65 | `return [candidate for candidate in neighbors(grid, pos, door_open) if grid[candidate[0]][candidate[1]] not in ("^", "~")]` | Espinho e laser nunca contam como casa segura, mesmo desligados. |
| 68 | `def safe_retreat(grid: list[list[str]], impact: Position, previous: Position, door_open: bool) -> Position:` | Escolhe uma casa segura depois da colisao. |
| 69 | `options = safe_neighbors(grid, impact, door_open)` | Consulta as casas imediatamente ao lado do impacto. |
| 70 | `if previous in options:` | Prioriza voltar exatamente uma casa, para onde o jogador estava. |
| 71 | `return previous` | Recuo intuitivo e seguro quando a casa anterior nao e um perigo. |
| 72 | `if options:` | O jogador pode ter esperado sobre um laser que acabou de ligar. |
| 73 | `return min(options, key=lambda p: (grid[p[0]][p[1]] != ".", manhattan(p, START), p))` | Prefere piso vazio, depois desempate estavel. |
| 74 | `queue = deque([impact])` | Defesa contra mapas adulterados que nao tenham refugio vizinho. |
| 75 | `visited = {impact}` | Evita visitar repetidamente os mesmos vertices durante o resgate. |
| 76 | `while queue:` | Busca o primeiro piso seguro alcançavel, caso a regra de geracao tenha sido violada. |
| 77 | `current = queue.popleft()` | BFS encontra a alternativa mais proxima em movimentos. |
| 78 | `for candidate in neighbors(grid, current, door_open):` | Percorre as quatro adjacencias transitaveis. |
| 79 | `if candidate in visited:` | Um vertice ja visitado nao precisa ser reprocessado. |
| 80 | `continue` | Evita ciclos infinitos no mapa editado manualmente. |
| 81 | `if grid[candidate[0]][candidate[1]] not in ("^", "~"):` | Um local sem perigo encerra o resgate. |
| 82 | `return candidate` | Somente neste caso defensivo o recuo pode superar uma casa. |
| 83 | `visited.add(candidate)` | Registra uma celula perigosa para continuar a procura. |
| 84 | `queue.append(candidate)` | Amplia a pesquisa ate encontrar um refugio acessivel. |
| 85 | `return previous` | Situacao impossivel nos mapas oficiais: conserva a ultima coordenada. |
| 88 | `def bfs(grid: list[list[str]], origin: Position, goal: Position, door_open: bool = False) -> list[Position]:` | Menor caminho por passos. |
| 89 | `if not walkable(grid, origin, door_open) or not walkable(grid, goal, door_open):` | Valida os extremos. |
| 90 | `return []` | Caminho vazio indica objetivo indisponivel. |
| 91 | `queue = deque([origin])` | Fila FIFO com o primeiro vertice. |
| 92 | `parent: dict[Position, Position \| None] = {origin: None}` | Marca visitados e seus predecessores. |
| 93 | `while queue:` | Continua ate achar o destino ou esgotar vertice. |
| 94 | `current = queue.popleft()` | Retira o vertice mais antigo da fila. |
| 95 | `if current == goal:` | BFS encontrou o alvo com o menor numero de arestas. |
| 96 | `path = []` | Acumula caminho invertido a partir do objetivo. |
| 97 | `while current is not None:` | Reconstrucao usando os predecessores. |
| 98 | `path.append(current)` | Salva cada posicao da rota. |
| 99 | `current = parent[current]` | Volta para o pai deste vertice. |
| 100 | `return path[::-1]` | Retorna o trajeto em ordem de ida. |
| 101 | `for nxt in neighbors(grid, current, door_open):` | Explora adjacentes validos. |
| 102 | `if nxt not in parent:` | Cada posicao e visitada apenas uma vez. |
| 103 | `parent[nxt] = current` | Salva a aresta usada para chegar ao vizinho. |
| 104 | `queue.append(nxt)` | Agenda o vizinho para a busca em largura. |
| 105 | `return []` | Destino inalcançavel nas regras fornecidas. |
| 108 | `def reachable(grid: list[list[str]], origin: Position, door_open: bool = False) -> set[Position]:` | Componente conectada. |
| 109 | `found = {origin}` | Conjunto de vertices que ja foram descobertos. |
| 110 | `queue = deque([origin])` | Inicia a exploracao da componente. |
| 111 | `while queue:` | Continua ate visitar toda a area acessivel. |
| 112 | `current = queue.popleft()` | Retira o proximo vertice da fila. |
| 113 | `for nxt in neighbors(grid, current, door_open):` | Considera cada vizinho. |
| 114 | `if nxt not in found:` | Impede repeticao e ciclos infinitos. |
| 115 | `found.add(nxt)` | Registra o vertice como acessivel. |
| 116 | `queue.append(nxt)` | Visita depois os vizinhos dele. |
| 117 | `return found` | Devolve o conjunto de posicoes alcançaveis. |
| 120 | `def astar(grid: list[list[str]], origin: Position, goal: Position, turn: int, door_open: bool, risk_weight: int = DAMAGE_PENALTY) -> tuple[list[Position], int]:` | Rota de custo minimo com tempo. |
| 121 | `"""A*: nos sao (linha, coluna, tempo modulo 4); g = passos + peso * impactos."""` | Define o criterio de otimizacao. |
| 122 | `if not walkable(grid, origin, door_open) or not walkable(grid, goal, door_open):` | Protege extremos. |
| 123 | `return [], -1` | Falha de planejamento tratada explicitamente. |
| 124 | `first = (origin, turn % PERIOD)` | Estado inclui posicao e fase dos lasers. |
| 125 | `costs = {first: 0}` | Melhor distancia ponderada conhecida para cada estado. |
| 126 | `parent: dict[tuple[Position, int], tuple[Position, int] \| None] = {first: None}` | Predecessores. |
| 127 | `heap = [(manhattan(origin, goal), 0, 0, first)]` | Prioridade f = g + h e desempate. |
| 128 | `counter = 0` | Ordenacao estavel sem comparar objetos complexos. |
| 129 | `while heap:` | Processa o melhor estado ainda pendente. |
| 130 | `_, g, _, state = heapq.heappop(heap)` | Recupera menor custo estimado. |
| 131 | `if g != costs.get(state):` | Descarta entradas antigas de menor prioridade. |
| 132 | `continue` | O estado ja recebeu uma rota melhor. |
| 133 | `pos, phase = state` | Separa vertice e instante modular. |
| 134 | `if pos == goal:` | A heuristica consistente garante custo minimo no primeiro encontro. |
| 135 | `path = []` | Armazena a trajetoria da chegada ate a origem. |
| 136 | `while state is not None:` | Reconstrucao dos antecessores. |
| 137 | `path.append(state[0])` | Guarda so a posicao; repeticoes representam esperar. |
| 138 | `state = parent[state]` | Retrocede pelo caminho otimo. |
| 139 | `return path[::-1], g` | Entrega rota e custo total acumulado. |
| 140 | `next_phase = (phase + 1) % PERIOD` | Cada acao gasta um turno, inclusive esperar. |
| 141 | `options = neighbors(grid, pos, door_open) + [pos]` | Quatro direcoes e acao ESPERAR. |
| 142 | `for nxt in options:` | Avalia transicoes do grafo expandido no tempo. |
| 143 | `extra = risk_weight if hazard(grid, nxt, next_phase) else 0` | Penaliza risco na chegada. |
| 144 | `new_g = g + 1 + extra` | Custo de movimento + custo do risco. |
| 145 | `next_state = (nxt, next_phase)` | Mesmo lugar em outro tempo e um estado distinto. |
| 146 | `if new_g < costs.get(next_state, float("inf")):` | Relaxamento de aresta tipo Dijkstra. |
| 147 | `costs[next_state] = new_g` | Atualiza o menor custo conhecido. |
| 148 | `parent[next_state] = (pos, phase)` | Registra predecessor da melhor transicao. |
| 149 | `counter += 1` | Atualiza desempate da fila de prioridade. |
| 150 | `heuristic = manhattan(nxt, goal)` | Nunca superestima passos restantes. |
| 151 | `heapq.heappush(heap, (new_g + heuristic, new_g, counter, next_state))` | Agenda candidato. |
| 152 | `return [], -1` | O destino nao foi encontrado. |
| 155 | `def route_risk(grid: list[list[str]], path: list[Position], turn: int) -> int:` | Conta impactos potenciais. |
| 156 | `return sum(int(hazard(grid, pos, turn + step)) for step, pos in enumerate(path[1:], 1))` | Considera o tempo de cada passo. |
| 159 | `def _open_loops(grid: list[list[str]], door: Position, rng: random.Random, number: int) -> None:` | Cria alternativas sem contornar porta. |
| 160 | `before = reachable(grid, START, False)` | Area de entrada antes da porta. |
| 161 | `after = reachable(grid, EXIT, False)` | Area apos a porta na arvore original. |
| 162 | `candidates = []` | Armazena paredes elegiveis a remocao. |
| 163 | `for r in range(1, ROWS - 1):` | Nao altera o contorno exterior. |
| 164 | `for c in range(1, COLS - 1):` | Percorre as celulas internas. |
| 165 | `p = (r, c)` | Coordenada atual da parede. |
| 166 | `if grid[r][c] != "#" or p == door:` | Somente paredes interiores. |
| 167 | `continue` | Nao reabre a porta que controla o acesso. |
| 168 | `adj = [add(p, d) for d in DIRECTIONS if grid[add(p, d)[0]][add(p, d)[1]] != "#"]` | Lados ja abertos. |
| 169 | `if len(adj) < 2:` | Uma passagem sem dois vizinhos nao cria alternativa. |
| 170 | `continue` | Preserva um grau minimo de utilidade. |
| 171 | `if all(a in before for a in adj) or all(a in after for a in adj):` | Nao liga regioes opostas. |
| 172 | `candidates.append(p)` | Possivel corredor alternativo seguro. |
| 173 | `rng.shuffle(candidates)` | Varia a estrutura de ciclos em cada fase. |
| 174 | `for p in candidates[:number]:` | Abre um numero limitado de caminhos extras. |
| 175 | `grid[p[0]][p[1]] = "."` | Converte parede em corredor. |
| 178 | `@dataclass` | Gera automaticamente inicializador e representacao dos campos. |
| 179 | `class Level:` | Estrutura de dados de uma fase da simulacao. |
| 180 | `grid: list[list[str]]` | Matriz de caracteres do ambiente. |
| 181 | `number: int` | Numero da fase (1, 2, 3). |
| 182 | `start: Position` | Posicao de nascimento do jogador. |
| 183 | `exit: Position` | Vertice objetivo final. |
| 184 | `door: Position` | Porta que controla acesso a regiao final. |
| 185 | `key: Position` | Credencial necessaria para desbloqueio. |
| 186 | `puzzle: Position` | Ponto de verificacao logica. |
| 187 | `player: Position = START` | Posicao atual do agente. |
| 188 | `has_key: bool = False` | Booleano de credencial encontrada. |
| 189 | `solved: bool = False` | Booleano de desafio resolvido. |
| 190 | `turns: int = 0` | Quantidade de acoes validas ja realizadas. |
| 191 | `health: int = MAX_HEALTH` | Vidas restantes da fase. |
| 192 | `protected: set[Position] = field(default_factory=set)` | Uma rota garantidamente sem riscos. |
| 194 | `@property` | Transforma metodo em atributo calculado de maneira segura. |
| 195 | `def door_open(self) -> bool:` | Implementa operador logico de conjuncao. |
| 196 | `return self.has_key and self.solved` | Porta abre somente quando K e E sao verdadeiros. |
| 198 | `@property` | Consulta o objetivo atual com sintaxe de atributo. |
| 199 | `def objective(self) -> Position:` | Seleciona o alvo da proxima orientacao. |
| 200 | `if not self.has_key:` | Se falta credencial, procura a chave. |
| 201 | `return self.key` | Primeiro ponto de interesse. |
| 202 | `if not self.solved:` | Se a chave existe mas nao houve verificacao. |
| 203 | `return self.puzzle` | Segundo ponto de interesse. |
| 204 | `return self.exit` | Apos atender as condicoes, busca a saida. |
| 207 | `def generate_level(number: int, seed: int \| None = None) -> Level:` | Construcao reproduzivel por semente. |
| 208 | `rng = random.Random(seed)` | Gerador local permite testar mapas identicos. |
| 209 | `grid = [["#" for _ in range(COLS)] for _ in range(ROWS)]` | Matriz totalmente bloqueada. |
| 210 | `grid[START[0]][START[1]] = "."` | Libera a origem do percurso. |
| 211 | `stack = [START]` | Pilha LIFO usada pela busca em profundidade iterativa. |
| 212 | `while stack:` | Enquanto houver um ramo a ser explorado. |
| 213 | `current = stack[-1]` | Examina o topo da pilha sem retira-lo. |
| 214 | `directions = list(DIRECTIONS)` | Cria lista mutavel das quatro direcoes. |
| 215 | `rng.shuffle(directions)` | Escolhe as possibilidades em ordem aleatoria. |
| 216 | `carved = False` | Supoe inicialmente que o vertice e um beco sem saida. |
| 217 | `for direction in directions:` | Tenta abrir corredor em cada sentido. |
| 218 | `next_pos = add(current, (2 * direction[0], 2 * direction[1]))` | Salta duas celulas. |
| 219 | `if not (0 < next_pos[0] < ROWS - 1 and 0 < next_pos[1] < COLS - 1):` | Limites interiores. |
| 220 | `continue` | Descarta movimento que sairia da grade. |
| 221 | `if grid[next_pos[0]][next_pos[1]] != "#":` | DFS evita visitar celula ja aberta. |
| 222 | `continue` | Preserva a arvore de corredores durante a geracao. |
| 223 | `mid = add(current, direction)` | Parede intermediaria entre os dois vertices. |
| 224 | `grid[mid[0]][mid[1]] = "."` | Abre a passagem de conexao. |
| 225 | `grid[next_pos[0]][next_pos[1]] = "."` | Marca a nova sala como visitada. |
| 226 | `stack.append(next_pos)` | Avanca a busca em profundidade. |
| 227 | `carved = True` | Indica que foi possivel continuar. |
| 228 | `break` | Explora a nova ramificacao antes das demais. |
| 229 | `if not carved:` | Nenhuma direcao disponivel nesta ramificacao. |
| 230 | `stack.pop()` | Backtracking: retorna ao vertice anterior. |
| 231 | `path = bfs(grid, START, EXIT, True)` | O labirinto conectado possui caminho a saida. |
| 232 | `if len(path) < 5:` | Condicao defensiva para configuracoes anormais. |
| 233 | `raise ValueError("Labirinto gerado sem percurso suficiente")` | Evita acesso fora de indice. |
| 234 | `index = max(2, min(int(len(path) * 0.68), len(path) - 3))` | Porta perto de 68% do trajeto. |
| 235 | `door = path[index]` | Posiciona um controle de acesso no caminho obrigatorio. |
| 236 | `grid[door[0]][door[1]] = "D"` | Retirar o vertice separa duas componentes. |
| 237 | `_open_loops(grid, door, rng, number * 3 + 7)` | Cria percursos alternativos dentro de cada zona. |
| 238 | `before = reachable(grid, START, False)` | Calcula locais acessiveis antes da porta. |
| 239 | `candidates = [p for p in before if p != START and manhattan(p, START) > 3]` | Locais da credencial. |
| 240 | `if len(candidates) < 2:` | Valida a quantidade minima de posicoes. |
| 241 | `raise ValueError("Nao existem celulas para os objetivos")` | Falha legivel e deterministica. |
| 242 | `key = rng.choice(sorted(candidates))` | Escolhe local para encontrar a chave. |
| 243 | `distant = [p for p in candidates if p != key and len(bfs(grid, key, p, False)) >= 7]` | Distancia minima do enigma. |
| 244 | `puzzle = rng.choice(sorted(distant or [p for p in candidates if p != key]))` | Evita sobreposicao. |
| 245 | `grid[key[0]][key[1]] = "K"` | Adiciona credencial ao mapa. |
| 246 | `grid[puzzle[0]][puzzle[1]] = "E"` | Adiciona ponto de verificacao. |
| 247 | `grid[EXIT[0]][EXIT[1]] = "S"` | Marca a saida. |
| 248 | `safe = set(bfs(grid, START, key, False))` | Resguarda um caminho sem riscos ate K. |
| 249 | `safe.update(bfs(grid, key, puzzle, False))` | Resguarda percurso de K ate E. |
| 250 | `safe.update(bfs(grid, puzzle, EXIT, True))` | Resguarda E ate S apos a abertura. |
| 251 | `forbidden = safe \| {START, key, puzzle, door, EXIT}` | Nunca instala perigos no corredor garantido. |
| 252 | `available = sorted(p for p in reachable(grid, START, True) if p not in forbidden and grid[p[0]][p[1]] == ".")` | Celulas candidatas. |
| 253 | `rng.shuffle(available)` | Distribui eventos de risco entre ramos alternativos. |
| 254 | `rubble_n = min(2 + number, len(available) // 5)` | Escombros bloqueiam definitivamente. |
| 255 | `spike_n = min(6 + 2 * number, max(0, (len(available) - rubble_n) // 2))` | Espinhos causam dano. |
| 256 | `laser_n = min(5 + 2 * number, max(0, len(available) - rubble_n - spike_n))` | Laser e temporal. |
| 257 | `for pos in available[:rubble_n]:` | Converte alguns corredores em obstaculos solidos. |
| 258 | `grid[pos[0]][pos[1]] = "R"` | Representa caixa, entulho ou passagem obstruida. |
| 259 | `for symbol, limit in (("^", spike_n), ("~", laser_n)):` | Distribui espinhos e lasers respeitando o limite de cada tipo. |
| 260 | `placed = 0` | Conta apenas obstaculos validados matematicamente. |
| 261 | `for pos in available[rubble_n:]:` | Examina corredores restantes na ordem aleatoria gerada. |
| 262 | `if grid[pos[0]][pos[1]] != ".":` | Nao reutiliza casas com perigo ja instalado. |
| 263 | `continue` | Evita sobreposicao de dois riscos na mesma celula. |
| 264 | `grid[pos[0]][pos[1]] = symbol` | Instala o perigo de maneira provisoria. |
| 265 | `affected = [pos] + [p for p in neighbors(grid, pos, False) if grid[p[0]][p[1]] in ("^", "~")]` | Inclui riscos vizinhos potencialmente isolados. |
| 266 | `if not all(safe_neighbors(grid, danger, False) for danger in affected):` | Todo perigo deve permitir recuo lateral para casa segura. |
| 267 | `grid[pos[0]][pos[1]] = "."` | Desfaz a instalacao que bloquearia todos os refugios. |
| 268 | `continue` | Busca outro local sem comprometer a jogabilidade. |
| 269 | `placed += 1` | Confirma um obstaculo com vizinhanca segura. |
| 270 | `if placed >= limit:` | Respeita a quantidade maxima definida para a fase. |
| 271 | `break` | Finaliza o posicionamento deste tipo de risco. |
| 272 | `result = Level(grid, number, START, EXIT, door, key, puzzle, protected=safe)` | Monta a fase tipada. |
| 273 | `if not bfs(grid, START, key, False) or not bfs(grid, key, puzzle, False):` | Confirma acesso pre-porta. |
| 274 | `raise AssertionError("Objetivos inacessiveis")` | Invariante de jogabilidade. |
| 275 | `if not bfs(grid, puzzle, EXIT, True) or bfs(grid, START, EXIT, False):` | Garante porta obrigatoria. |
| 276 | `raise AssertionError("Porta nao separa as areas")` | Evita fase que descumpre as regras. |
| 277 | `return result` | Entrega uma fase valida, deterministica por seed. |
| 280 | `@dataclass` | Gera a estrutura de controle de partida. |
| 281 | `class Session:` | Armazena eventos, pontuacao, vidas e progresso. |
| 282 | `level: Level = field(default_factory=lambda: generate_level(1))` | Primeira fase automaticamente. |
| 283 | `score: int = 0` | Pontuacao acumulada do jogador. |
| 284 | `state: str = "intro"` | intro, playing, quiz, cleared, lost ou victory. |
| 285 | `message: str = "Encontre a credencial e atravesse com seguranca."` | Aviso contextual. |
| 286 | `hint_open: bool = False` | Controla exibicao da resposta auxiliar. |
| 287 | `hint_mode: str = "none"` | none, safe ou short. |
| 288 | `hinted: bool = False` | Evita desconto repetido da mesma fase. |
| 289 | `steps: int = 0` | Quantidade de movimentos validos da partida. |
| 290 | `impacts: int = 0` | Quantidade total de contatos com perigos. |
| 292 | `def reset(self, seed: int \| None = None) -> None:` | Reinicia a partida completamente. |
| 293 | `self.level = generate_level(1, seed)` | Novo mapa inicial reproduzivel se preciso. |
| 294 | `self.score = 0` | Zera placar total. |
| 295 | `self.state = "playing"` | Reativa movimentos. |
| 296 | `self.message = "Procure a chave. Use H para rota mais segura."` | Instrucao inicial. |
| 297 | `self.hint_mode = "none"` | Oculta dicas antigas. |
| 298 | `self.hint_open = False` | Fecha informacao de enigma. |
| 299 | `self.hinted = False` | Restabelece penalidade de dica por fase. |
| 300 | `self.steps = 0` | Zera contador de movimentos. |
| 301 | `self.impacts = 0` | Zera contador de impactos. |
| 303 | `def begin(self) -> None:` | Sai do menu e comeca uma sessao nova. |
| 304 | `self.reset()` | Centraliza inicializacao na rotina validada. |
| 306 | `def move(self, delta: Position) -> str:` | Executa uma acao ortogonal ou espera. |
| 307 | `if self.state != "playing":` | Respeita a maquina de estados. |
| 308 | `return "blocked"` | Teclas de movimento nao atuam fora da partida. |
| 309 | `if delta not in DIRECTIONS + ((0, 0),):` | Entrada deve ser uma das cinco acoes. |
| 310 | `self.message = "Movimento invalido."` | Informa erro sem avancar tempo. |
| 311 | `return "invalid"` | Nao permite teletransporte diagonal. |
| 312 | `previous = self.level.player` | Guarda a casa de origem como primeira opcao de recuo seguro. |
| 313 | `nxt = add(previous, delta)` | Calcula o candidato de deslocamento. |
| 314 | `if not walkable(self.level.grid, nxt, self.level.door_open):` | Aplica restricoes espaciais. |
| 315 | `self.message = "Caminho bloqueado ou porta ainda trancada."` | Explica impedimento. |
| 316 | `return "blocked"` | Movimento recusado; relogio da simulacao nao avanca. |
| 317 | `self.level.turns += 1` | Tempo discreto avanca apenas com acao valida. |
| 318 | `self.steps += 1` | Registra acoes validas para metricas. |
| 319 | `self.level.player = nxt` | Atualiza a coordenada atual do personagem. |
| 320 | `tile = self.level.grid[nxt[0]][nxt[1]]` | Le o objeto presente na nova celula. |
| 321 | `if hazard(self.level.grid, nxt, self.level.turns):` | Detecta espinhos ou laser ligado no turno da chegada. |
| 322 | `self.level.health -= 1` | Remove exatamente uma vida por colisao. |
| 323 | `self.impacts += 1` | Registra um unico impacto para esta acao. |
| 324 | `self.score = max(0, self.score - 20)` | Desconta vinte pontos sem permitir placar negativo. |
| 325 | `retreat = safe_retreat(self.level.grid, nxt, previous, self.level.door_open)` | Procura uma casa segura ao lado do perigo. |
| 326 | `self.level.player = retreat` | Afasta imediatamente o personagem da celula que causou dano. |
| 327 | `self.message = "RISCO! -1 vida, -20 pontos. Recuo para uma casa segura!"` | Explica o efeito na interface. |
| 328 | `if self.level.health <= 0:` | Se as vidas acabaram, a colisao encerra a partida. |
| 329 | `self.state = "lost"` | Mostra a tela de derrota mesmo apos o recuo. |
| 330 | `return "lost"` | Informa que houve derrota por impacto. |
| 331 | `return "damage"` | Notifica o Pygame para piscar o personagem em vermelho. |
| 332 | `elif delta == (0, 0):` | Trata a acao de esperar um turno parado. |
| 333 | `self.message = "Voce aguardou um turno. Fase do laser alterada."` | Explica tempo. |
| 334 | `if tile == "K" and not self.level.has_key:` | Encontrou a credencial. |
| 335 | `self.level.has_key = True` | Atualiza primeira proposicao da porta. |
| 336 | `self.level.grid[nxt[0]][nxt[1]] = "."` | Remove item recolhido. |
| 337 | `self.score += 40` | Recompensa da credencial. |
| 338 | `self.message = "Credencial obtida! Procure o desafio matematico."` | Proximo objetivo. |
| 339 | `return "key"` | Evento para a camada grafica. |
| 340 | `if tile == "E" and not self.level.solved:` | Encontrou local da verificacao. |
| 341 | `if not self.level.has_key:` | Verifica pre-requisito do desafio. |
| 342 | `self.message = "Primeiro obtenha a credencial de acesso."` | Impede salto de etapa. |
| 343 | `return "need_key"` | Informa a regra aplicada. |
| 344 | `self.state = "quiz"` | Troca o controle do jogo para caixa do enigma. |
| 345 | `self.hint_open = False` | Oculta inicialmente a dica textual. |
| 346 | `self.message = "Resolva a sequencia para validar o acesso."` | Mensagem de orientacao. |
| 347 | `return "quiz"` | Interface abre o modal. |
| 348 | `if tile == "S":` | O jogador alcancou a saida da fase. |
| 349 | `if not self.level.door_open:` | Checa conjuncao de credencial e verificacao. |
| 350 | `self.message = "Credencial e enigma sao obrigatorios."` | Recusa conclusao invalida. |
| 351 | `return "locked"` | Mantem o jogador na fase. |
| 352 | `self.score += 120` | Recompensa final de conclusao da etapa. |
| 353 | `self.state = "cleared"` | Registra que a fase foi concluida. |
| 354 | `self.message = "Area concluida! Pressione ENTER para continuar."` | Instrucao da interface. |
| 355 | `return "cleared"` | Envia evento para celebracao visual. |
| 356 | `return "step"` | Movimento comum sem objetivo especifico. |
| 358 | `def answer(self, value: str) -> bool:` | Valida a digitacao do desafio. |
| 359 | `if self.state != "quiz":` | Protege contra resposta fora de contexto. |
| 360 | `return False` | Entrada nao tem efeito sem enigma aberto. |
| 361 | `puzzle = PUZZLES[self.level.number - 1]` | Usa indice zero para a fase. |
| 362 | `cleaned = value.strip()` | Remove espacos externos sem alterar numeros. |
| 363 | `if not cleaned.isascii() or not cleaned.isdigit() or len(cleaned) > 8:` | Entrada numerica segura. |
| 364 | `self.message = "Digite apenas numeros inteiros (ate 8 digitos)."` | Tratamento de erro. |
| 365 | `return False` | Mantem o enigma aberto para nova tentativa. |
| 366 | `if cleaned != puzzle["answer"]:` | Compara com a resposta matematica correta. |
| 367 | `self.message = "Resposta incorreta. Analise a regra da sequencia."` | Feedback formativo. |
| 368 | `return False` | Evita desbloqueio sem validacao. |
| 369 | `self.level.solved = True` | Marca a segunda condicao booleana como verdadeira. |
| 370 | `p = self.level.puzzle` | Recupera a coordenada do enigma. |
| 371 | `self.level.grid[p[0]][p[1]] = "."` | Transforma o ponto em corredor comum. |
| 372 | `self.score += 80` | Recompensa pela solucao matematica. |
| 373 | `self.state = "playing"` | Devolve controles de movimento ao jogador. |
| 374 | `self.message = puzzle["why"] + " A porta foi liberada!"` | Explica o resultado. |
| 375 | `return True` | Indica sucesso da resposta. |
| 377 | `def next_level(self, seed: int \| None = None) -> None:` | Controla transicao de fases. |
| 378 | `if self.state != "cleared":` | Exige conclusao anterior. |
| 379 | `return` | Ignora tentativa fora de contexto. |
| 380 | `if self.level.number == len(PUZZLES):` | Ultima fase ja foi resolvida. |
| 381 | `self.state = "victory"` | Marca vitoria final da partida. |
| 382 | `self.message = "Todas as zonas foram atravessadas!"` | Conclusao do jogo. |
| 383 | `return` | Mantem a pontuacao e a tela final. |
| 384 | `self.level = generate_level(self.level.number + 1, seed)` | Novo labirinto mais desafiador. |
| 385 | `self.hint_mode = "none"` | Dicas antigas nao migram para outra fase. |
| 386 | `self.hinted = False` | Recupera a possibilidade de dica com custo. |
| 387 | `self.state = "playing"` | Ativa movimentacao na nova area. |
| 388 | `self.message = "Nova zona. Avalie os riscos antes de escolher a rota."` | Instrucao. |
| 390 | `def show_route(self, mode: str) -> tuple[list[Position], int]:` | Consulta rota da fase atual. |
| 391 | `if mode not in ("safe", "short"):` | Valida opcao escolhida. |
| 392 | `raise ValueError("Modo de rota desconhecido")` | Erro de chamada explicito. |
| 393 | `if self.state != "playing":` | Disponibiliza rotas apenas durante a partida. |
| 394 | `return [], -1` | Nao calcula na introducao ou nos desafios. |
| 395 | `self.hint_mode = mode` | Atualiza opcao da interface. |
| 396 | `if not self.hinted:` | Cobra dica uma vez por fase, nao a cada passo. |
| 397 | `self.score = max(0, self.score - 5)` | Penaliza assistencia de navegacao. |
| 398 | `self.hinted = True` | Marca que o desconto ja foi aplicado. |
| 399 | `if mode == "safe":` | Escolha de otimizacao com risco. |
| 400 | `route, cost = astar(self.level.grid, self.level.player, self.level.objective, self.level.turns, self.level.door_open)` | A* temporal ponderado. |
| 401 | `self.message = "Rota segura: minimiza passos + penalidade de risco."` | Informa criterio. |
| 402 | `return route, cost` | Devolve custo ponderado e coordenadas. |
| 403 | `route = bfs(self.level.grid, self.level.player, self.level.objective, self.level.door_open)` | Menor rota geometrica. |
| 404 | `self.message = "Menor rota: pode atravessar espinhos e lasers ativos!"` | Alerta do criterio. |
| 405 | `return route, len(route) - 1 if route else -1` | Numero de passos do caminho. |


---


## Arquivo `jogo.py`

**341 linhas físicas.** Inclui instruções, comentários, linhas em branco e blocos de texto.

| Linha | Instrução / trecho | Explicação |
|---:|---|---|
| 1 | `"""LABIRINTO DOS ENIGMAS: ROTAS DE RISCO \| Trabalho A03 - Matematica Computacional.` | Texto documental que contextualiza a estrutura ou a função. |
| 3 | `Execute com \`python jogo.py\` apos instalar o Pygame (\`pip install -r requirements.txt\`).` | Parte do bloco de código; a finalidade é indicada pelo contexto e pelos comentários adjacentes. |
| 4 | `Todo comando importante recebe comentario; o guia explica cada linha numerada.` | Parte do bloco de código; a finalidade é indicada pelo contexto e pelos comentários adjacentes. |
| 5 | `"""` | Texto documental que contextualiza a estrutura ou a função. |
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
| 27 | `DAMAGE_FLASH_MS = 850` | Animacao de dano: 850 ms de piscadas vermelhas apos o recuo. |
| 28 | `BG = (9, 17, 30)` | Cor do fundo do simulador. |
| 29 | `PANEL = (15, 29, 48)` | Superficie dos paineis de informacao. |
| 30 | `PANEL_2 = (20, 39, 59)` | Tom secundario para caixas e botoes. |
| 31 | `BORDER = (41, 66, 84)` | Cor discreta dos contornos. |
| 32 | `WHITE = (239, 246, 255)` | Cor de alto contraste para textos principais. |
| 33 | `MUTED = (153, 175, 193)` | Cor de apoio para textos secundarios. |
| 34 | `TEAL = (77, 225, 198)` | Cor dos objetivos e das rotas seguras. |
| 35 | `GOLD = (248, 191, 83)` | Cor da chave e dos destaques de pontuacao. |
| 36 | `RED = (253, 107, 126)` | Cor de perigos ativos e vidas perdidas. |
| 37 | `PURPLE = (170, 138, 255)` | Cor dos enigmas e dos lasers. |
| 38 | `FLOOR = (23, 43, 60)` | Cor das celulas de piso transitavel. |
| 39 | `WALL = (52, 76, 98)` | Cor das paredes do labirinto. |
| 40 | `FONT_NAME = "dejavusans"` | Fonte com suporte aos caracteres do portugues. |
| 43 | `def font(size: int, bold: bool = False) -> pygame.font.Font:` | Constroi fonte sob demanda para cada dimensao. |
| 44 | `return pygame.font.SysFont(FONT_NAME, size, bold=bold)` | Usa fonte do sistema como fallback. |
| 47 | `def text(surface: pygame.Surface, message: str, x: int, y: int, size: int = 18, color: tuple = WHITE, bold: bool = False) -> None:` | Desenha uma linha de texto. |
| 48 | `image = font(size, bold).render(str(message), True, color)` | Converte texto para superficie com antialias. |
| 49 | `surface.blit(image, (x, y))` | Cola a superficie de texto na posicao desejada. |
| 52 | `def wrap(surface: pygame.Surface, message: str, x: int, y: int, width: int, size: int = 16, color: tuple = MUTED, line_height: int = 24) -> int:` | Quebra texto automaticamente. |
| 53 | `words = str(message).split()` | Divide frase em palavras sem perder a ordem. |
| 54 | `current = ""` | Guarda a linha em montagem. |
| 55 | `for word in words:` | Testa cada palavra da frase. |
| 56 | `trial = (current + " " + word).strip()` | Monta a linha candidata. |
| 57 | `if font(size).size(trial)[0] > width and current:` | Verifica se ultrapassa o limite. |
| 58 | `text(surface, current, x, y, size, color)` | Renderiza a linha que ja estava completa. |
| 59 | `y += line_height` | Passa para a proxima linha vertical. |
| 60 | `current = word` | Inicia nova linha com a palavra atual. |
| 61 | `else:` | Executa quando o texto ainda cabe no limite. |
| 62 | `current = trial` | Continua preenchendo a mesma linha. |
| 63 | `if current:` | A ultima linha precisa ser exibida mesmo sem ultrapassar o limite. |
| 64 | `text(surface, current, x, y, size, color)` | Desenha o restante da frase. |
| 65 | `y += line_height` | Devolve a proxima coordenada livre. |
| 66 | `return y` | Permite empilhar paragrafos sem sobreposicao. |
| 69 | `def rounded(surface: pygame.Surface, rect: tuple, color: tuple, radius: int = 14, border: tuple \| None = None) -> None:` | Desenha cartao arredondado. |
| 70 | `pygame.draw.rect(surface, color, rect, border_radius=radius)` | Preenche o painel. |
| 71 | `if border is not None:` | Uma borda e opcional. |
| 72 | `pygame.draw.rect(surface, border, rect, width=1, border_radius=radius)` | Desenha contorno suave. |
| 75 | `def button(surface: pygame.Surface, rect: pygame.Rect, label: str, mouse: tuple, active: bool = False, accent: tuple = TEAL) -> None:` | Desenha botao com estado visual. |
| 76 | `hovered = rect.collidepoint(mouse)` | Detecta aproximacao do mouse. |
| 77 | `color = (37, 75, 91) if hovered or active else PANEL_2` | Destaca selecao e passagem do ponteiro. |
| 78 | `rounded(surface, tuple(rect), color, 10, accent if active else BORDER)` | Pinta o botao. |
| 79 | `label_image = font(15, bold=True).render(label, True, WHITE if not active else accent)` | Centraliza o texto do botao. |
| 80 | `surface.blit(label_image, label_image.get_rect(center=rect.center))` | Exibe legenda centralizada. |
| 83 | `def tile_center(pos: tuple[int, int]) -> tuple[int, int]:` | Converte coordenadas discretas em pixels. |
| 84 | `row, col = pos` | Desempacota linha e coluna do grafo. |
| 85 | `return (MAP_X + col * CELL + CELL // 2, MAP_Y + row * CELL + CELL // 2)` | Centro da celula na tela. |
| 88 | `def draw_diamond(surface: pygame.Surface, x: int, y: int, radius: int, color: tuple) -> None:` | Desenha icone geométrico de destaque. |
| 89 | `pygame.draw.polygon(surface, color, [(x, y - radius), (x + radius, y), (x, y + radius), (x - radius, y)])` | Poligono de quatro pontas. |
| 92 | `def draw_grid(surface: pygame.Surface, session: Session, path: list[tuple[int, int]], mode: str, now: int, last_hit_at: int) -> None:` | Desenha o mapa e a animacao de impacto. |
| 93 | `level = session.level` | Recupera o mapa e o agente da fase atual. |
| 94 | `rounded(surface, (MAP_X - 12, MAP_Y - 12, MAP_W + 24, MAP_H + 24), PANEL, 16, BORDER)` | Moldura do labirinto. |
| 95 | `for row in range(ROWS):` | Percorre todas as linhas da matriz. |
| 96 | `for col in range(COLS):` | Percorre todas as colunas da linha atual. |
| 97 | `symbol = level.grid[row][col]` | Le o conteudo da celula. |
| 98 | `left = MAP_X + col * CELL` | Calcula a posicao horizontal do quadrado. |
| 99 | `top = MAP_Y + row * CELL` | Calcula a posicao vertical do quadrado. |
| 100 | `rect = pygame.Rect(left + 1, top + 1, CELL - 2, CELL - 2)` | Guarda uma margem entre celulas. |
| 101 | `if symbol == "#":` | Verifica se o vertice e bloqueado por parede. |
| 102 | `rounded(surface, tuple(rect), WALL, 4)` | Desenha a parede resistente. |
| 103 | `pygame.draw.line(surface, (68, 94, 117), rect.topleft, (rect.right, rect.top), 1)` | Acabamento de relevo. |
| 104 | `continue` | Nao ha objetos dentro de uma parede. |
| 105 | `rounded(surface, tuple(rect), FLOOR, 4)` | Desenha o corredor acessivel. |
| 106 | `cx, cy = tile_center((row, col))` | Recupera o centro para desenhar os simbolos. |
| 107 | `if symbol == "R":` | Entulho representa uma barreira fisica. |
| 108 | `pygame.draw.polygon(surface, (126, 144, 157), [(left + 5, top + 23), (left + 10, top + 8), (left + 22, top + 6), (left + 28, top + 23)])` | Bloco de escombros. |
| 109 | `pygame.draw.line(surface, (75, 93, 106), (left + 12, top + 14), (left + 21, top + 19), 2)` | Fissura da pedra. |
| 110 | `elif symbol == "^":` | Espinhos provocam dano permanente ao entrar. |
| 111 | `for offset in (5, 14, 23):` | Repete tres pontas na largura do piso. |
| 112 | `pygame.draw.polygon(surface, RED, [(left + offset - 3, top + 25), (left + offset + 2, top + 7), (left + offset + 7, top + 25)])` | Triangulo pontiagudo. |
| 113 | `elif symbol == "~":` | Laser utiliza o tempo discreto para definir perigo. |
| 114 | `enabled = laser_active(level.turns)` | Verifica a fase do ciclo modular do obstaculo. |
| 115 | `shade = PURPLE if enabled else (87, 80, 111)` | Laser ativo brilha mais. |
| 116 | `pygame.draw.line(surface, shade, (left + 7, cy), (left + 25, cy), 5 if enabled else 2)` | Emite feixe horizontal. |
| 117 | `pygame.draw.circle(surface, shade, (left + 6, cy), 4)` | Desenha emissor esquerdo. |
| 118 | `pygame.draw.circle(surface, shade, (left + 26, cy), 4)` | Desenha emissor direito. |
| 119 | `elif symbol == "D":` | A porta depende da conjuncao chave E resposta. |
| 120 | `shade = TEAL if level.door_open else (195, 132, 97)` | Altera cor ao desbloquear. |
| 121 | `pygame.draw.rect(surface, shade, (left + 8, top + 5, 16, 24), border_radius=3)` | Desenha a estrutura da porta. |
| 122 | `pygame.draw.circle(surface, BG, (left + 20, top + 17), 2)` | Desenha a fechadura. |
| 123 | `elif symbol == "K":` | Credencial que libera um dos predicados de acesso. |
| 124 | `pygame.draw.circle(surface, GOLD, (cx - 5, cy - 3), 6, 3)` | Parte circular da chave. |
| 125 | `pygame.draw.line(surface, GOLD, (cx, cy), (cx + 10, cy + 9), 4)` | Corpo metalico da chave. |
| 126 | `pygame.draw.line(surface, GOLD, (cx + 6, cy + 6), (cx + 11, cy + 2), 3)` | Dente da chave. |
| 127 | `elif symbol == "E":` | Desafio matematico funciona como checkpoint de logica. |
| 128 | `pygame.draw.circle(surface, PURPLE, (cx, cy), 12)` | Corpo circular do enigma. |
| 129 | `text(surface, "?", cx - 5, cy - 12, 20, BG, True)` | Simbolo de pergunta. |
| 130 | `elif symbol == "S":` | Representa o destino da rota de evacuacao. |
| 131 | `pygame.draw.circle(surface, TEAL, (cx, cy), 12, 3)` | Alvo verde de chegada. |
| 132 | `pygame.draw.circle(surface, TEAL, (cx, cy), 4)` | Nucleo da chegada. |
| 133 | `if path:` | So mostra o planejamento depois da solicitacao de ajuda. |
| 134 | `shade = TEAL if mode == "safe" else GOLD` | Separa rota segura da menor rota geometrica. |
| 135 | `for idx, point in enumerate(path[1:], 1):` | Nao realca a posicao inicial do caminho. |
| 136 | `center = tile_center(point)` | Coordenadas visuais do vertice analisado. |
| 137 | `pygame.draw.circle(surface, shade, center, 4 if idx % 3 else 5)` | Marca etapas do caminho. |
| 138 | `cx, cy = tile_center(level.player)` | Posiciona jogador sobre sua celula atual. |
| 139 | `pulse = math.sin(now * 0.005) * 2` | Pequena animacao usando funcao seno. |
| 140 | `elapsed = now - last_hit_at` | Calcula quantos milissegundos passaram desde o ultimo impacto. |
| 141 | `flashing = 0 <= elapsed < DAMAGE_FLASH_MS` | Define a janela temporal da animacao de dano. |
| 142 | `red_frame = flashing and (elapsed // 105) % 2 == 0` | Alterna vermelho/azul a cada 105 ms. |
| 143 | `body = RED if red_frame else (91, 187, 255)` | Seleciona vermelho durante as piscadas. |
| 144 | `aura = (107, 28, 45) if red_frame else (12, 41, 60)` | O halo acompanha a mudanca de cor. |
| 145 | `pygame.draw.circle(surface, aura, (cx, cy), int(16 + pulse))` | Desenha halo pulsante, vermelho no impacto. |
| 146 | `pygame.draw.circle(surface, body, (cx, cy), 12)` | Desenha o personagem na casa segura apos o recuo. |
| 147 | `pygame.draw.circle(surface, WHITE, (cx + 3, cy - 3), 4)` | Mantem o brilho para facilitar a leitura visual. |
| 150 | `def draw_panel(surface: pygame.Surface, session: Session, path: list, route_cost: int, seconds: float, mouse: tuple, buttons: dict, show_debug: bool) -> None:` | Painel direito de matematica aplicada. |
| 151 | `level = session.level` | Permite consultar todos os campos da fase. |
| 152 | `rounded(surface, (SIDE_X, 126, SIDE_W, 570), PANEL, 16, BORDER)` | Cartao de metricas. |
| 153 | `text(surface, "PAINEL DE NAVEGAÇÃO", SIDE_X + 20, 148, 15, TEAL, True)` | Identifica area analitica. |
| 154 | `text(surface, f"FASE {level.number:02d} / 03", SIDE_X + 20, 186, 24, WHITE, True)` | Indica progresso. |
| 155 | `text(surface, "SISTEMA DE ROTAS E RISCOS", SIDE_X + 20, 222, 12, MUTED)` | Resume objetivo do jogo. |
| 156 | `pygame.draw.line(surface, BORDER, (SIDE_X + 18, 255), (SIDE_X + SIDE_W - 18, 255), 1)` | Separa indicadores. |
| 157 | `metrics = [("PONTOS", str(session.score)), ("TURNOS", str(level.turns)), ("TEMPO", f"{int(seconds)//60:02d}:{int(seconds)%60:02d}")]` | Agrupa metricas visiveis. |
| 158 | `for i, (label, value) in enumerate(metrics):` | Desenha colunas alinhadas. |
| 159 | `mx = SIDE_X + 20 + i * 115` | Computa o inicio de cada indicador. |
| 160 | `text(surface, label, mx, 274, 11, MUTED, True)` | Titula indicador. |
| 161 | `text(surface, value, mx, 297, 21, GOLD if i == 0 else WHITE, True)` | Exibe valor atualizado. |
| 162 | `pygame.draw.line(surface, BORDER, (SIDE_X + 18, 337), (SIDE_X + SIDE_W - 18, 337), 1)` | Separa a barra de saude. |
| 163 | `text(surface, "INTEGRIDADE", SIDE_X + 20, 350, 12, MUTED, True)` | Rotulo de vidas. |
| 164 | `for life in range(MAX_HEALTH):` | Desenha quatro indicadores de resistencia. |
| 165 | `color = RED if life < level.health else (55, 71, 85)` | Vidas perdidas ficam apagadas. |
| 166 | `pygame.draw.circle(surface, color, (SIDE_X + 161 + life * 30, 359), 9)` | Sinaliza vida individual. |
| 167 | `text(surface, "CREDENCIAL", SIDE_X + 20, 387, 12, MUTED)` | Primeira condicao da logica. |
| 168 | `text(surface, "SIM" if level.has_key else "NÃO", SIDE_X + 180, 386, 14, TEAL if level.has_key else GOLD, True)` | Booleano da chave. |
| 169 | `text(surface, "ENIGMA", SIDE_X + 20, 414, 12, MUTED)` | Segunda condicao da logica. |
| 170 | `text(surface, "VALIDADO" if level.solved else "PENDENTE", SIDE_X + 180, 413, 14, TEAL if level.solved else GOLD, True)` | Booleano da resposta. |
| 171 | `text(surface, "PORTA = CHAVE ∧ ENIGMA", SIDE_X + 20, 443, 13, TEAL if level.door_open else MUTED, True)` | Formula proposicional de acesso. |
| 172 | `pygame.draw.line(surface, BORDER, (SIDE_X + 18, 475), (SIDE_X + SIDE_W - 18, 475), 1)` | Separa o roteamento. |
| 173 | `text(surface, "PLANEJAMENTO MATEMÁTICO", SIDE_X + 20, 490, 13, WHITE, True)` | Area para BFS e A*. |
| 174 | `for name in ("safe", "short"):` | Desenha um botao para cada criterio de busca. |
| 175 | `label = "H • A* ROTA SEGURA" if name == "safe" else "J • BFS MENOR ROTA"` | Legendas e atalhos. |
| 176 | `button(surface, buttons[name], label, mouse, session.hint_mode == name, TEAL if name == "safe" else GOLD)` | Apresenta modo. |
| 177 | `if path:` | Dados da rota aparecem apenas apos uma consulta. |
| 178 | `text(surface, f"Rota: {max(0, len(path)-1)} ações  \|  custo: {route_cost}", SIDE_X + 20, 606, 12, TEAL, True)` | Comprimento e custo. |
| 179 | `if session.hint_mode == "short":` | BFS nao considera penalidades de dano. |
| 180 | `risk = route_risk(level.grid, path, level.turns)` | Conta possiveis colisoes na rota. |
| 181 | `text(surface, f"Possíveis impactos na BFS: {risk}", SIDE_X + 20, 627, 12, RED if risk else MUTED)` | Indicador de risco. |
| 182 | `else:` | Caminho otimizado pelo custo ponderado. |
| 183 | `text(surface, "A* inclui tempo e risco na decisão", SIDE_X + 20, 627, 11, MUTED)` | Explica criterio. |
| 184 | `else:` | Nao ha rota desenhada quando a consulta nao foi solicitada. |
| 185 | `text(surface, "Compare menor distância × menor risco", SIDE_X + 20, 610, 11, MUTED)` | Incentiva comparacao. |
| 186 | `if show_debug:` | Mostra formalizacao opcional para apresentacao academica. |
| 187 | `text(surface, "f(n)=g(n)+h(n)  \|  h=Manhattan", SIDE_X + 20, 658, 11, PURPLE)` | Equacao do A*. |
| 188 | `else:` | Indicacao para abrir formula matematica. |
| 189 | `text(surface, "M: mostrar fórmula matemática", SIDE_X + 20, 658, 11, MUTED)` | Legenda de ajuda. |
| 192 | `def overlay(surface: pygame.Surface, session: Session, answer: str, mouse: tuple, buttons: dict) -> None:` | Janelas de introducao e estados especiais. |
| 193 | `if session.state == "playing":` | Jogo normal nao precisa de modal. |
| 194 | `return` | Mantem o mapa livre. |
| 195 | `shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)` | Cria camada com transparencia. |
| 196 | `shade.fill((5, 12, 22, 218))` | Escurece o fundo para focar a janela. |
| 197 | `surface.blit(shade, (0, 0))` | Exibe a pelicula sobre o jogo. |
| 198 | `modal = (260, 175, 680, 400)` | Retangulo central comum aos estados. |
| 199 | `rounded(surface, modal, PANEL, 22, BORDER)` | Desenha a caixa principal. |
| 200 | `if session.state == "intro":` | Primeiro contato explica a experiencia. |
| 201 | `text(surface, "LABIRINTO DOS ENIGMAS", 310, 223, 30, TEAL, True)` | Titulo da introducao. |
| 202 | `text(surface, "Missão: sair de um ambiente com riscos", 310, 276, 19, WHITE)` | Contextualiza o problema. |
| 203 | `wrap(surface, "Planeje rotas, colete uma credencial, resolva o enigma e evite espinhos, escombros e lasers que alternam a cada turno.", 310, 312, 585, 17, MUTED, 28)` | Explica a dinamica. |
| 204 | `text(surface, "BFS procura menos passos. A* considera distância + dano.", 310, 407, 15, GOLD)` | Relacao com a disciplina. |
| 205 | `button(surface, buttons["primary"], "ENTER  •  INICIAR SIMULAÇÃO", mouse, True)` | Botao de partida. |
| 206 | `elif session.state == "quiz":` | Entrada numerica permite resolver a prova da fase. |
| 207 | `p = PUZZLES[session.level.number - 1]` | Enigma correspondente a fase atual. |
| 208 | `text(surface, "VERIFICAÇÃO MATEMÁTICA", 310, 214, 25, PURPLE, True)` | Titulo da verificacao. |
| 209 | `text(surface, p["question"], 310, 277, 22, WHITE, True)` | Enunciado principal. |
| 210 | `rounded(surface, (310, 335, 570, 57), PANEL_2, 10, PURPLE)` | Campo grafico para resposta. |
| 211 | `text(surface, answer + "\|", 329, 349, 23, GOLD, True)` | Cursor e valor digitado. |
| 212 | `if session.hint_open:` | Exibe ajuda apenas quando solicitada. |
| 213 | `wrap(surface, "DICA: " + p["hint"], 312, 413, 560, 16, GOLD, 25)` | Apresenta a sequencia. |
| 214 | `else:` | Instrucao de como solicitar a ajuda. |
| 215 | `text(surface, "Pressione I para mostrar uma dica.", 312, 416, 16, MUTED)` | Texto explicativo. |
| 216 | `wrap(surface, session.message, 312, 461, 560, 14, MUTED, 21)` | Retorno de validacao. |
| 217 | `text(surface, "ENTER: confirmar    BACKSPACE: apagar", 312, 521, 14, TEAL)` | Comandos do formulario. |
| 218 | `elif session.state == "cleared":` | Etapa encerrada com sucesso. |
| 219 | `text(surface, "ZONA CONCLUÍDA", 310, 230, 32, TEAL, True)` | Mensagem de conquista. |
| 220 | `text(surface, f"Pontuação acumulada: {session.score}", 310, 303, 24, GOLD)` | Resumo da rodada. |
| 221 | `wrap(surface, "A decisão matemática correta transforma um ambiente complexo em uma rota viável.", 310, 363, 560, 17, MUTED, 28)` | Conexao didatica. |
| 222 | `button(surface, buttons["primary"], "ENTER  •  CONTINUAR", mouse, True)` | Passa para outra fase. |
| 223 | `elif session.state == "lost":` | Colisoes esgotaram a integridade do agente. |
| 224 | `text(surface, "RISCO CRÍTICO", 310, 230, 32, RED, True)` | Tela de derrota. |
| 225 | `wrap(surface, "Sua integridade chegou a zero. Reavalie o caminho: a rota mais curta nem sempre é a mais segura.", 310, 308, 570, 18, MUTED, 30)` | Explicacao do erro. |
| 226 | `button(surface, buttons["primary"], "R  •  REINICIAR", mouse, True, RED)` | Possibilita uma nova tentativa. |
| 227 | `elif session.state == "victory":` | Todas as tres fases foram superadas. |
| 228 | `text(surface, "MISSÃO CONCLUÍDA!", 310, 228, 30, TEAL, True)` | Mensagem final. |
| 229 | `text(surface, f"Pontuação final: {session.score}", 310, 305, 25, GOLD, True)` | Resultado da sessao. |
| 230 | `text(surface, f"Total de impactos: {session.impacts}", 310, 351, 19, WHITE)` | Indicador de seguranca. |
| 231 | `button(surface, buttons["primary"], "R  •  JOGAR NOVAMENTE", mouse, True)` | Reinicia a experiencia. |
| 234 | `def main() -> int:` | Ponto de entrada da interface Pygame. |
| 235 | `pygame.init()` | Inicializa os modulos de video, teclado e fontes. |
| 236 | `pygame.key.set_repeat(160, 100)` | Permite movimento repetido ao segurar setas. |
| 237 | `screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))` | Cria janela com dimensoes fixas. |
| 238 | `pygame.display.set_caption("Labirinto dos Enigmas \| Matematica Computacional")` | Identifica janela. |
| 239 | `clock = pygame.time.Clock()` | Controla a taxa visual de atualizacao. |
| 240 | `session = Session()` | Instancia o modelo sem misturar logica e desenho. |
| 241 | `answer = ""` | Armazena entrada numerica corrente no desafio. |
| 242 | `path: list[tuple[int, int]] = []` | Lista do caminho calculado por BFS ou A*. |
| 243 | `route_cost = -1` | Custo ponderado da rota inicialmente desconhecido. |
| 244 | `show_debug = False` | Permite exibir formalizacao do A* opcionalmente. |
| 245 | `seconds = 0.0` | Cronometro apenas visual: NAO define o tempo dos lasers. |
| 246 | `last_hit_at = -DAMAGE_FLASH_MS` | Inicialmente nao existe impacto e o jogador permanece azul. |
| 247 | `buttons = {"safe": pygame.Rect(SIDE_X + 20, 522, 318, 35), "short": pygame.Rect(SIDE_X + 20, 563, 318, 35), "primary": pygame.Rect(310, 485, 570, 55)}` | Regioes clicaveis. |
| 248 | `moves = {pygame.K_UP: (-1, 0), pygame.K_w: (-1, 0), pygame.K_DOWN: (1, 0), pygame.K_s: (1, 0), pygame.K_LEFT: (0, -1), pygame.K_a: (0, -1), pygame.K_RIGHT: (0, 1), pygame.K_d: (0, 1), pygame.K_SPACE: (0, 0)}` | Mapa de controles. |
| 249 | `running = True` | Variavel booleana de continuidade do programa. |
| 250 | `while running:` | Loop principal: entrada, atualizacao e desenho. |
| 251 | `dt = clock.tick(FPS) / 1000.0` | Converte duracao do quadro em segundos. |
| 252 | `now = pygame.time.get_ticks()` | Tempo visual utilizado na animacao do jogador. |
| 253 | `mouse = pygame.mouse.get_pos()` | Posicao atual do cursor para efeito hover. |
| 254 | `if session.state in ("playing", "quiz"):` | Cronometro corre durante as duas etapas. |
| 255 | `seconds += dt` | Avanca tempo visual real de forma independente dos turnos. |
| 256 | `for event in pygame.event.get():` | Consome eventos para impedir congelamento do sistema. |
| 257 | `if event.type == pygame.QUIT:` | Usuario clicou em fechar janela. |
| 258 | `running = False` | Encerra loop normalmente. |
| 259 | `continue` | Ignora processamento adicional deste evento. |
| 260 | `if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:` | Clique esquerdo do mouse. |
| 261 | `if session.state == "playing":` | Botoes de rota so funcionam em partida ativa. |
| 262 | `for name in ("safe", "short"):` | Confere ambos os botoes do painel. |
| 263 | `if buttons[name].collidepoint(event.pos):` | Verifica se o clique atingiu o botao. |
| 264 | `path, route_cost = session.show_route(name)` | Executa BFS ou A* do modelo. |
| 265 | `elif buttons["primary"].collidepoint(event.pos):` | Clique no botao de inicio/continuidade. |
| 266 | `if session.state == "intro":` | Estado inicial da aplicacao. |
| 267 | `session.begin()` | Inicia a primeira fase. |
| 268 | `elif session.state == "cleared":` | Fase finalizada com sucesso. |
| 269 | `session.next_level()` | Avanca para a etapa seguinte. |
| 270 | `elif session.state in ("lost", "victory"):` | Fim de jogo ou derrota. |
| 271 | `session.reset()` | Reinicia pontuacao e labirintos. |
| 272 | `seconds = 0.0` | Reinicia cronometro da partida. |
| 273 | `last_hit_at = -DAMAGE_FLASH_MS` | Cancela piscadas da partida anterior. |
| 274 | `path = []` | Esconde rota de qualquer fase anterior. |
| 275 | `continue` | Clique processado; passa ao proximo evento. |
| 276 | `if event.type != pygame.KEYDOWN:` | Eventos de movimento exigem tecla pressionada. |
| 277 | `continue` | Ignora entrada nao relevante. |
| 278 | `if event.key == pygame.K_ESCAPE:` | ESC fecha o programa em qualquer estado. |
| 279 | `running = False` | Finaliza aplicacao sem erros. |
| 280 | `continue` | Nao processa outras operacoes. |
| 281 | `if event.key == pygame.K_r and session.state != "quiz":` | Atalho global para reiniciar, exceto durante enigma. |
| 282 | `session.reset()` | Gera nova partida limpa. |
| 283 | `path = []` | Desliga trilha de navegacao antiga. |
| 284 | `answer = ""` | Limpa campos de texto antigos. |
| 285 | `seconds = 0.0` | Zera cronometro visual. |
| 286 | `last_hit_at = -DAMAGE_FLASH_MS` | Garante que a nova partida comece sem efeito vermelho. |
| 287 | `continue` | Terminou tratamento de reinicio. |
| 288 | `if session.state == "intro" and event.key == pygame.K_RETURN:` | ENTER na tela inicial. |
| 289 | `session.begin()` | Inicia sessao em estado valido. |
| 290 | `continue` | Evita comandos simultaneos. |
| 291 | `if session.state == "cleared" and event.key == pygame.K_RETURN:` | ENTER apos finalizar fase. |
| 292 | `session.next_level()` | Passa a fase 2/3 ou vitoria. |
| 293 | `path = []` | Limpa rota antiga ao mudar o objetivo. |
| 294 | `continue` | Evento concluido. |
| 295 | `if session.state == "quiz":` | Enigma intercepta as entradas de teclado. |
| 296 | `if event.key == pygame.K_i:` | Atalho para dica matematica. |
| 297 | `session.hint_open = True` | Mostra a pista do enigma. |
| 298 | `elif event.key == pygame.K_BACKSPACE:` | Tecla de apagar. |
| 299 | `answer = answer[:-1]` | Retira ultimo digito digitado. |
| 300 | `elif event.key == pygame.K_RETURN:` | Valida resposta fornecida. |
| 301 | `accepted = session.answer(answer)` | Funcao booleana do modelo. |
| 302 | `if accepted:` | Enigma correto desbloqueia a porta. |
| 303 | `answer = ""` | Limpa valor que ja foi utilizado. |
| 304 | `path = []` | Forca nova rota com porta aberta. |
| 305 | `elif event.unicode.isascii() and event.unicode.isdigit() and len(answer) < 8:` | Apenas digitos ASCII permitidos. |
| 306 | `answer += event.unicode` | Anexa caracter validado sem risco de overflow textual. |
| 307 | `continue` | Impede que o enigma movimente o personagem. |
| 308 | `if session.state != "playing":` | Derrota e vitoria nao aceitam movimento. |
| 309 | `continue` | Espera um comando de reiniciar ou continuar. |
| 310 | `if event.key == pygame.K_h:` | H: rota ponderada e temporal com A*. |
| 311 | `path, route_cost = session.show_route("safe")` | Busca minimizar passos e risco. |
| 312 | `elif event.key == pygame.K_j:` | J: rota geometrica curta com BFS. |
| 313 | `path, route_cost = session.show_route("short")` | Busca minimo numero de passos. |
| 314 | `elif event.key == pygame.K_m:` | M: exibe a funcao matematica A*. |
| 315 | `show_debug = not show_debug` | Alterna modo tecnico para a apresentacao. |
| 316 | `elif event.key in moves:` | Setas, WASD ou espaco fazem acoes validas. |
| 317 | `if now - last_hit_at < DAMAGE_FLASH_MS:` | Durante a piscada, bloqueia tecla repetida contra o mesmo perigo. |
| 318 | `continue` | Evita perder varias vidas de uma vez segurando a seta. |
| 319 | `action = session.move(moves[event.key])` | Recebe o evento logico da colisao ou do movimento. |
| 320 | `if action in ("damage", "lost"):` | Impactos geram a mesma animacao vermelha. |
| 321 | `last_hit_at = now` | Inicia o cronometro da piscada sem alterar os turnos dos lasers. |
| 322 | `path = []` | Um caminho consultado fica obsoleto apos cada acao. |
| 323 | `screen.fill(BG)` | Limpa quadro antes de redesenhar tudo. |
| 324 | `for i in range(0, SCREEN_W, 40):` | Mostra grid discreto decorativo no fundo. |
| 325 | `pygame.draw.line(screen, (14, 27, 42), (i, 0), (i, SCREEN_H), 1)` | Linha vertical decorativa. |
| 326 | `text(screen, "LABIRINTO", MAP_X, 31, 32, WHITE, True)` | Marca principal do jogo. |
| 327 | `text(screen, "DOS ENIGMAS", MAP_X + 205, 33, 29, TEAL, True)` | Segunda metade do titulo. |
| 328 | `text(screen, "ROTAS DE RISCO  \|  MATEMÁTICA COMPUTACIONAL", MAP_X + 2, 83, 13, MUTED, True)` | Contexto academico. |
| 329 | `draw_grid(screen, session, path, session.hint_mode, now, last_hit_at)` | Renderiza o mapa e a piscada vermelha de impacto. |
| 330 | `draw_panel(screen, session, path, route_cost, seconds, mouse, buttons, show_debug)` | Mostra metricas e botoes. |
| 331 | `rounded(screen, (MAP_X - 12, 638, MAP_W + 24, 58), PANEL, 12, BORDER)` | Barra de mensagens contextual. |
| 332 | `wrap(screen, session.message, MAP_X + 4, 650, MAP_W - 20, 15, GOLD if "RISCO" in session.message else WHITE, 22)` | Informa evento ao jogador. |
| 333 | `text(screen, "WASD/SETAS mover    ESPAÇO esperar    H A* seguro    J BFS curto    M fórmula    R reiniciar    ESC sair", 35, 713, 13, MUTED)` | Lembrete de controles. |
| 334 | `overlay(screen, session, answer, mouse, buttons)` | Exibe modal quando o estado exigir. |
| 335 | `pygame.display.flip()` | Troca o quadro desenhado pelo quadro visivel. |
| 336 | `pygame.quit()` | Fecha os subsistemas graficos com seguranca. |
| 337 | `return 0` | Retorna sucesso ao sistema operacional. |
| 340 | `if __name__ == "__main__":` | Impede execucao automatica quando o arquivo e importado. |
| 341 | `sys.exit(main())` | Inicia a interface e propaga o codigo de saida. |


---


## Arquivo `tests/test_logica.py`

**166 linhas físicas.** Inclui instruções, comentários, linhas em branco e blocos de texto.

| Linha | Instrução / trecho | Explicação |
|---:|---|---|
| 1 | `"""Testes repetiveis sem Pygame para confiabilidade da modelagem matematica."""` | Texto documental que contextualiza a estrutura ou a função. |
| 3 | `from __future__ import annotations` | Permite anotacoes padronizadas. |
| 4 | `import unittest` | Biblioteca de testes ja incluida no Python. |
| 5 | `from src.logica import (` | Componentes logicos testados sem abrir janela. |
| 6 | `ROWS, COLS, START, EXIT, PERIOD, MAX_HEALTH,` | Constantes do grafo. |
| 7 | `PUZZLES, Session, generate_level, bfs, astar, hazard,` | Funcoes e objetos testados. |
| 8 | `neighbors, safe_neighbors, safe_retreat, manhattan, route_risk, walkable, laser_active,` | Auxiliares e mecanica de recuo. |
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
| 63 | `for row in range(ROWS):` | Varre a matriz para conferir o novo invariante de seguranca. |
| 64 | `for col in range(COLS):` | Analisa cada celula de todos os mapas pseudoaleatorios. |
| 65 | `if level.grid[row][col] in ("^", "~"):` | Espinhos e lasers devem permitir recuo. |
| 66 | `self.assertTrue(safe_neighbors(level.grid, (row, col), False))` | Pelo menos uma casa adjacente sempre segura. |
| 68 | `def test_reproducibility(self) -> None:` | Mesma seed gera mesma configuracao. |
| 69 | `one = generate_level(2, 1234)` | Primeira geracao. |
| 70 | `two = generate_level(2, 1234)` | Geracao repetida. |
| 71 | `self.assertEqual(one.grid, two.grid)` | Matriz identica na mesma seed. |
| 72 | `self.assertEqual(one.key, two.key)` | Chave na mesma posicao. |
| 73 | `self.assertEqual(one.puzzle, two.puzzle)` | Enigma na mesma posicao. |
| 76 | `class TestSession(unittest.TestCase):` | Verifica maquina de estados e tratamento de erro. |
| 77 | `def test_solve_and_finish(self) -> None:` | Executa as tres fases sem Pygame. |
| 78 | `session = Session()` | Nova sessao logica. |
| 79 | `session.reset(seed=77)` | Mapa inicial reproduzivel. |
| 80 | `for number in range(1, 4):` | Percorre fases numeradas de 1 a 3. |
| 81 | `self.assertEqual(session.level.number, number)` | Confere fase ativa. |
| 82 | `for target in (session.level.key, session.level.puzzle):` | Primeiro chave; depois enigma. |
| 83 | `route, _ = astar(session.level.grid, session.level.player, target, session.level.turns, session.level.door_open)` | Rota com risco. |
| 84 | `self.assertTrue(route)` | Caminho deve existir. |
| 85 | `for previous, nxt in zip(route, route[1:]):` | Percorre cada aresta, incluindo espera. |
| 86 | `session.move((nxt[0] - previous[0], nxt[1] - previous[1]))` | Movimento ortogonal permitido. |
| 87 | `self.assertNotEqual(session.state, "lost")` | Rota segura nao pode causar derrota. |
| 88 | `self.assertEqual(session.state, "quiz")` | Enigma foi alcancado. |
| 89 | `self.assertFalse(session.answer("abc"))` | Resposta nao numerica rejeitada. |
| 90 | `self.assertFalse(session.answer("999999999"))` | Entrada excessiva rejeitada. |
| 91 | `self.assertTrue(session.answer(PUZZLES[number - 1]["answer"]))` | Resposta da fase correta. |
| 92 | `self.assertTrue(session.level.door_open)` | AND de condicoes habilita porta. |
| 93 | `route, _ = astar(session.level.grid, session.level.player, EXIT, session.level.turns, True)` | Busca ate saida. |
| 94 | `for previous, nxt in zip(route, route[1:]):` | Caminha pela rota escolhida. |
| 95 | `session.move((nxt[0] - previous[0], nxt[1] - previous[1]))` | Executa um turno por acao. |
| 96 | `self.assertNotEqual(session.state, "lost")` | Sem danos letais na rota segura. |
| 97 | `self.assertEqual(session.state, "cleared")` | Saida conquistada. |
| 98 | `session.next_level(seed=77 + number)` | Avanca ou vence apos a terceira. |
| 99 | `self.assertEqual(session.state, "victory")` | Verifica condicao de finalizacao. |
| 100 | `self.assertEqual(session.impacts, 0)` | Roteamento ponderado eliminou impactos. |
| 101 | `self.assertGreater(session.score, 0)` | Jogador acumulou pontos. |
| 103 | `def test_spike_bounces_to_previous_safe_cell(self) -> None:` | Verifica dano e recuo imediato apos espinho. |
| 104 | `session = Session()` | Cria sessao independente de testes anteriores. |
| 105 | `session.reset(seed=13)` | Usa seed deterministica que contem espinhos. |
| 106 | `spike = next((r, c) for r in range(ROWS) for c in range(COLS) if session.level.grid[r][c] == "^")` | Encontra espinho real no mapa. |
| 107 | `before = safe_neighbors(session.level.grid, spike, False)[0]` | Seleciona uma casa lateral sem riscos. |
| 108 | `session.level.player = before` | Coloca jogador no corredor vizinho ao espinho. |
| 109 | `session.score = 35` | Permite conferir desconto de vinte pontos. |
| 110 | `health = session.level.health` | Guarda quantidade de vidas anterior ao contato. |
| 111 | `moves = (spike[0] - before[0], spike[1] - before[1])` | Calcula deslocamento ortogonal unitario. |
| 112 | `self.assertEqual(session.move(moves), "damage")` | Espinho retorna evento de animacao. |
| 113 | `self.assertEqual(session.level.player, before)` | O personagem retorna uma casa ao corredor seguro. |
| 114 | `self.assertEqual(session.level.health, health - 1)` | Desconta exatamente uma vida. |
| 115 | `self.assertEqual(session.score, 15)` | Desconta vinte pontos sem alterar bonus. |
| 116 | `self.assertEqual(session.impacts, 1)` | Colisao e contabilizada uma vez. |
| 117 | `self.assertEqual(session.level.turns, 1)` | Movimento com dano tambem conta como turno. |
| 118 | `self.assertEqual(session.state, "playing")` | Com vidas restantes a partida continua. |
| 120 | `def test_active_laser_bounces_but_inactive_does_not(self) -> None:` | Diferencia ativacao temporal do laser. |
| 121 | `session = Session()` | Sessao isolada para testar aritmetica modular. |
| 122 | `session.reset(seed=27)` | Gera um mapa reproducivel com lasers. |
| 123 | `laser = next((r, c) for r in range(ROWS) for c in range(COLS) if session.level.grid[r][c] == "~")` | Seleciona laser real. |
| 124 | `safe = safe_neighbors(session.level.grid, laser, False)[0]` | Posicao lateral sem risco. |
| 125 | `direction = (laser[0] - safe[0], laser[1] - safe[1])` | Vetor de aproximacao ao laser. |
| 126 | `session.level.player = safe` | Prepara primeiro contato a partir da casa segura. |
| 127 | `session.level.turns = 1` | Proximo movimento no turno 2: laser desligado. |
| 128 | `self.assertEqual(session.move(direction), "step")` | Laser desligado permite atravessar sem dano. |
| 129 | `self.assertEqual(session.level.player, laser)` | Jogador permanece na casa do laser desligado. |
| 130 | `self.assertEqual(session.move((0, 0)), "step")` | Espera turno 3 sem dano. |
| 131 | `self.assertEqual(session.move((0, 0)), "damage")` | No turno 4, laser ativo provoca dano. |
| 132 | `self.assertEqual(session.level.player, safe)` | Risco ao esperar empurra para um vizinho seguro. |
| 133 | `self.assertEqual(session.level.health, MAX_HEALTH - 1)` | Laser causa somente um impacto. |
| 134 | `self.assertEqual(session.impacts, 1)` | Nenhum dano extra quando estava desligado. |
| 136 | `def test_last_life_reports_loss_after_retreat(self) -> None:` | O recuo tambem funciona ao perder a ultima vida. |
| 137 | `session = Session()` | Instancia modelo sob teste. |
| 138 | `session.reset(seed=19)` | Gera mapa com espinhos e pisos. |
| 139 | `spike = next((r, c) for r in range(ROWS) for c in range(COLS) if session.level.grid[r][c] == "^")` | Seleciona risco. |
| 140 | `safe = safe_neighbors(session.level.grid, spike, False)[0]` | Define refugio lateral. |
| 141 | `session.level.player = safe` | Parte de local livre de riscos. |
| 142 | `session.level.health = 1` | Resta uma unica vida. |
| 143 | `self.assertEqual(session.move((spike[0] - safe[0], spike[1] - safe[1])), "lost")` | Impacto final encerra a sessao. |
| 144 | `self.assertEqual(session.level.health, 0)` | Vida nunca fica negativa. |
| 145 | `self.assertEqual(session.level.player, safe)` | Recuo para casa segura ainda e aplicado. |
| 146 | `self.assertEqual(session.state, "lost")` | Estado passa a derrota. |
| 148 | `def test_retreat_rejects_neighboring_hazards(self) -> None:` | Nunca empurra o jogador para espinho ou outro laser. |
| 149 | `grid = [["#" for _ in range(COLS)] for _ in range(ROWS)]` | Grade artificial para isolar colisao. |
| 150 | `grid[1][1] = "~"` | Casa de origem e um laser (naquele instante desligado). |
| 151 | `grid[1][2] = "^"` | Casa do impacto e um espinho. |
| 152 | `grid[2][2] = "."` | Refugio valido em outra direcao ortogonal. |
| 153 | `self.assertEqual(safe_retreat(grid, (1, 2), (1, 1), False), (2, 2))` | Nunca escolhe laser como casa segura. |
| 155 | `def test_invalid_actions(self) -> None:` | Limites e entradas nao mudam a partida indevidamente. |
| 156 | `session = Session()` | Cria sessao independente. |
| 157 | `session.reset(seed=9)` | Define fase conhecida. |
| 158 | `original = session.level.player` | Guarda posicao para comparacao. |
| 159 | `self.assertEqual(session.move((3, 3)), "invalid")` | Movimento diagonal invalido. |
| 160 | `self.assertEqual(session.level.player, original)` | Protege a posicao do jogador. |
| 161 | `self.assertEqual(session.level.turns, 0)` | Entrada invalida nao avanca o turno. |
| 162 | `self.assertFalse(session.answer("32"))` | Nao responde sem modal aberto. |
| 165 | `if __name__ == "__main__":` | Permite rodar diretamente como script de teste. |
| 166 | `unittest.main()` | Descobre e executa os casos escritos acima. |


---