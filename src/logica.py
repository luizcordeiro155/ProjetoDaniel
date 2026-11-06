"""Modelo matematico puro: matriz, grafo, DFS, BFS, A* temporal e regras.

Este modulo nao importa Pygame: a simulacao pode ser testada sem abrir janelas.
Cada operacao significativa traz comentario e o guia detalha as linhas.
"""

from __future__ import annotations  # Permite anotacoes de tipos modernas.
from collections import deque  # Implementa a fila FIFO utilizada na BFS.
from dataclasses import dataclass, field  # Organiza os dados da fase.
import heapq  # Implementa a fila de prioridade de menor custo do A*.
import random  # Sorteia ramificacoes, objetos e posicoes dos obstaculos.
from typing import Iterable  # Declara colecoes de coordenadas nos tipos.

ROWS = 15  # Quantidade impar de linhas na matriz do mapa.
COLS = 23  # Quantidade impar de colunas da matriz.
START = (1, 1)  # Primeira celula aberta: linha 1 e coluna 1.
EXIT = (ROWS - 2, COLS - 2)  # Saida interna do canto inferior direito.
PERIOD = 4  # Laser repete o seu ciclo a cada quatro turnos.
DAMAGE_PENALTY = 18  # Peso de risco: A* prefere contornar perigos.
MAX_HEALTH = 4  # Quantidade inicial de vidas em cada fase.
DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))  # Cima, baixo, esquerda, direita.

PUZZLES = (  # Sequencia de enigmas aplicada nas tres fases.
    {"question": "Complete: 2, 4, 8, 16, ?", "answer": "32", "hint": "Multiplique cada termo por 2.", "why": "Progressao geometrica: a(n) = 2 elevado a (n + 1)."},  # Primeiro desafio: potencia de base 2.
    {"question": "Complete: 1, 1, 2, 3, 5, ?", "answer": "8", "hint": "Some os dois termos anteriores.", "why": "Recorrencia de Fibonacci: F(n) = F(n-1) + F(n-2)."},  # Segundo desafio: recorrencia aditiva.
    {"question": "Complete: 1, 4, 9, 16, ?", "answer": "25", "hint": "Os termos sao quadrados perfeitos.", "why": "Sequencia quadratica: a(n) = n ao quadrado."},  # Terceiro desafio: quadrados perfeitos.
)  # Encerra a tupla imutavel de enigmas.

Position = tuple[int, int]  # Cada vertice equivale a coordenada (linha, coluna).


def add(pos: Position, offset: Position) -> Position:  # Soma coordenadas para deslocar no grafo.
    return (pos[0] + offset[0], pos[1] + offset[1])  # Novo vertice apos um movimento.


def inside(pos: Position) -> bool:  # Protege os acessos contra indices fora da matriz.
    return 0 <= pos[0] < ROWS and 0 <= pos[1] < COLS  # Verdadeiro apenas dentro da grade.


def manhattan(a: Position, b: Position) -> int:  # Calcula limite inferior da distancia ortogonal.
    return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Soma de distancias absolutas.


def laser_active(turn: int) -> bool:  # Testa o perigo periodico com aritmetica modular.
    return turn % PERIOD in (0, 1)  # Laser ativo em duas fases de cada ciclo.


def hazard(grid: list[list[str]], pos: Position, turn: int) -> bool:  # Consulta risco na chegada.
    tile = grid[pos[0]][pos[1]]  # Le o simbolo armazenado na matriz.
    return tile == "^" or (tile == "~" and laser_active(turn))  # Espinho sempre ou laser ativo.


def walkable(grid: list[list[str]], pos: Position, door_open: bool) -> bool:  # Verifica transitabilidade.
    if not inside(pos):  # Impede coordenadas negativas ou maiores que o mapa.
        return False  # Celula fora do mapa nunca pode ser usada.
    tile = grid[pos[0]][pos[1]]  # Le o conteudo de uma posicao valida.
    return tile not in ("#", "R") and (tile != "D" or door_open)  # Paredes/escombros bloqueiam.


def neighbors(grid: list[list[str]], pos: Position, door_open: bool) -> list[Position]:  # Adjacencias do grafo.
    return [candidate for delta in DIRECTIONS if walkable(grid, (candidate := add(pos, delta)), door_open)]  # Quatro movimentos ortogonais validos.


def bfs(grid: list[list[str]], origin: Position, goal: Position, door_open: bool = False) -> list[Position]:  # Menor caminho por passos.
    if not walkable(grid, origin, door_open) or not walkable(grid, goal, door_open):  # Valida os extremos.
        return []  # Caminho vazio indica objetivo indisponivel.
    queue = deque([origin])  # Fila FIFO com o primeiro vertice.
    parent: dict[Position, Position | None] = {origin: None}  # Marca visitados e seus predecessores.
    while queue:  # Continua ate achar o destino ou esgotar vertice.
        current = queue.popleft()  # Retira o vertice mais antigo da fila.
        if current == goal:  # BFS encontrou o alvo com o menor numero de arestas.
            path = []  # Acumula caminho invertido a partir do objetivo.
            while current is not None:  # Reconstrucao usando os predecessores.
                path.append(current)  # Salva cada posicao da rota.
                current = parent[current]  # Volta para o pai deste vertice.
            return path[::-1]  # Retorna o trajeto em ordem de ida.
        for nxt in neighbors(grid, current, door_open):  # Explora adjacentes validos.
            if nxt not in parent:  # Cada posicao e visitada apenas uma vez.
                parent[nxt] = current  # Salva a aresta usada para chegar ao vizinho.
                queue.append(nxt)  # Agenda o vizinho para a busca em largura.
    return []  # Destino inalcançavel nas regras fornecidas.


def reachable(grid: list[list[str]], origin: Position, door_open: bool = False) -> set[Position]:  # Componente conectada.
    found = {origin}  # Conjunto de vertices que ja foram descobertos.
    queue = deque([origin])  # Inicia a exploracao da componente.
    while queue:  # Continua ate visitar toda a area acessivel.
        current = queue.popleft()  # Retira o proximo vertice da fila.
        for nxt in neighbors(grid, current, door_open):  # Considera cada vizinho.
            if nxt not in found:  # Impede repeticao e ciclos infinitos.
                found.add(nxt)  # Registra o vertice como acessivel.
                queue.append(nxt)  # Visita depois os vizinhos dele.
    return found  # Devolve o conjunto de posicoes alcançaveis.


def astar(grid: list[list[str]], origin: Position, goal: Position, turn: int, door_open: bool, risk_weight: int = DAMAGE_PENALTY) -> tuple[list[Position], int]:  # Rota de custo minimo com tempo.
    """A*: nos sao (linha, coluna, tempo modulo 4); g = passos + peso * impactos."""  # Define o criterio de otimizacao.
    if not walkable(grid, origin, door_open) or not walkable(grid, goal, door_open):  # Protege extremos.
        return [], -1  # Falha de planejamento tratada explicitamente.
    first = (origin, turn % PERIOD)  # Estado inclui posicao e fase dos lasers.
    costs = {first: 0}  # Melhor distancia ponderada conhecida para cada estado.
    parent: dict[tuple[Position, int], tuple[Position, int] | None] = {first: None}  # Predecessores.
    heap = [(manhattan(origin, goal), 0, 0, first)]  # Prioridade f = g + h e desempate.
    counter = 0  # Ordenacao estavel sem comparar objetos complexos.
    while heap:  # Processa o melhor estado ainda pendente.
        _, g, _, state = heapq.heappop(heap)  # Recupera menor custo estimado.
        if g != costs.get(state):  # Descarta entradas antigas de menor prioridade.
            continue  # O estado ja recebeu uma rota melhor.
        pos, phase = state  # Separa vertice e instante modular.
        if pos == goal:  # A heuristica consistente garante custo minimo no primeiro encontro.
            path = []  # Armazena a trajetoria da chegada ate a origem.
            while state is not None:  # Reconstrucao dos antecessores.
                path.append(state[0])  # Guarda so a posicao; repeticoes representam esperar.
                state = parent[state]  # Retrocede pelo caminho otimo.
            return path[::-1], g  # Entrega rota e custo total acumulado.
        next_phase = (phase + 1) % PERIOD  # Cada acao gasta um turno, inclusive esperar.
        options = neighbors(grid, pos, door_open) + [pos]  # Quatro direcoes e acao ESPERAR.
        for nxt in options:  # Avalia transicoes do grafo expandido no tempo.
            extra = risk_weight if hazard(grid, nxt, next_phase) else 0  # Penaliza risco na chegada.
            new_g = g + 1 + extra  # Custo de movimento + custo do risco.
            next_state = (nxt, next_phase)  # Mesmo lugar em outro tempo e um estado distinto.
            if new_g < costs.get(next_state, float("inf")):  # Relaxamento de aresta tipo Dijkstra.
                costs[next_state] = new_g  # Atualiza o menor custo conhecido.
                parent[next_state] = (pos, phase)  # Registra predecessor da melhor transicao.
                counter += 1  # Atualiza desempate da fila de prioridade.
                heuristic = manhattan(nxt, goal)  # Nunca superestima passos restantes.
                heapq.heappush(heap, (new_g + heuristic, new_g, counter, next_state))  # Agenda candidato.
    return [], -1  # O destino nao foi encontrado.


def route_risk(grid: list[list[str]], path: list[Position], turn: int) -> int:  # Conta impactos potenciais.
    return sum(int(hazard(grid, pos, turn + step)) for step, pos in enumerate(path[1:], 1))  # Considera o tempo de cada passo.


def _open_loops(grid: list[list[str]], door: Position, rng: random.Random, number: int) -> None:  # Cria alternativas sem contornar porta.
    before = reachable(grid, START, False)  # Area de entrada antes da porta.
    after = reachable(grid, EXIT, False)  # Area apos a porta na arvore original.
    candidates = []  # Armazena paredes elegiveis a remocao.
    for r in range(1, ROWS - 1):  # Nao altera o contorno exterior.
        for c in range(1, COLS - 1):  # Percorre as celulas internas.
            p = (r, c)  # Coordenada atual da parede.
            if grid[r][c] != "#" or p == door:  # Somente paredes interiores.
                continue  # Nao reabre a porta que controla o acesso.
            adj = [add(p, d) for d in DIRECTIONS if grid[add(p, d)[0]][add(p, d)[1]] != "#"]  # Lados ja abertos.
            if len(adj) < 2:  # Uma passagem sem dois vizinhos nao cria alternativa.
                continue  # Preserva um grau minimo de utilidade.
            if all(a in before for a in adj) or all(a in after for a in adj):  # Nao liga regioes opostas.
                candidates.append(p)  # Possivel corredor alternativo seguro.
    rng.shuffle(candidates)  # Varia a estrutura de ciclos em cada fase.
    for p in candidates[:number]:  # Abre um numero limitado de caminhos extras.
        grid[p[0]][p[1]] = "."  # Converte parede em corredor.


@dataclass  # Gera automaticamente inicializador e representacao dos campos.
class Level:  # Estrutura de dados de uma fase da simulacao.
    grid: list[list[str]]  # Matriz de caracteres do ambiente.
    number: int  # Numero da fase (1, 2, 3).
    start: Position  # Posicao de nascimento do jogador.
    exit: Position  # Vertice objetivo final.
    door: Position  # Porta que controla acesso a regiao final.
    key: Position  # Credencial necessaria para desbloqueio.
    puzzle: Position  # Ponto de verificacao logica.
    player: Position = START  # Posicao atual do agente.
    has_key: bool = False  # Booleano de credencial encontrada.
    solved: bool = False  # Booleano de desafio resolvido.
    turns: int = 0  # Quantidade de acoes validas ja realizadas.
    health: int = MAX_HEALTH  # Vidas restantes da fase.
    protected: set[Position] = field(default_factory=set)  # Uma rota garantidamente sem riscos.

    @property  # Transforma metodo em atributo calculado de maneira segura.
    def door_open(self) -> bool:  # Implementa operador logico de conjuncao.
        return self.has_key and self.solved  # Porta abre somente quando K e E sao verdadeiros.

    @property  # Consulta o objetivo atual com sintaxe de atributo.
    def objective(self) -> Position:  # Seleciona o alvo da proxima orientacao.
        if not self.has_key:  # Se falta credencial, procura a chave.
            return self.key  # Primeiro ponto de interesse.
        if not self.solved:  # Se a chave existe mas nao houve verificacao.
            return self.puzzle  # Segundo ponto de interesse.
        return self.exit  # Apos atender as condicoes, busca a saida.


def generate_level(number: int, seed: int | None = None) -> Level:  # Construcao reproduzivel por semente.
    rng = random.Random(seed)  # Gerador local permite testar mapas identicos.
    grid = [["#" for _ in range(COLS)] for _ in range(ROWS)]  # Matriz totalmente bloqueada.
    grid[START[0]][START[1]] = "."  # Libera a origem do percurso.
    stack = [START]  # Pilha LIFO usada pela busca em profundidade iterativa.
    while stack:  # Enquanto houver um ramo a ser explorado.
        current = stack[-1]  # Examina o topo da pilha sem retira-lo.
        directions = list(DIRECTIONS)  # Cria lista mutavel das quatro direcoes.
        rng.shuffle(directions)  # Escolhe as possibilidades em ordem aleatoria.
        carved = False  # Supoe inicialmente que o vertice e um beco sem saida.
        for direction in directions:  # Tenta abrir corredor em cada sentido.
            next_pos = add(current, (2 * direction[0], 2 * direction[1]))  # Salta duas celulas.
            if not (0 < next_pos[0] < ROWS - 1 and 0 < next_pos[1] < COLS - 1):  # Limites interiores.
                continue  # Descarta movimento que sairia da grade.
            if grid[next_pos[0]][next_pos[1]] != "#":  # DFS evita visitar celula ja aberta.
                continue  # Preserva a arvore de corredores durante a geracao.
            mid = add(current, direction)  # Parede intermediaria entre os dois vertices.
            grid[mid[0]][mid[1]] = "."  # Abre a passagem de conexao.
            grid[next_pos[0]][next_pos[1]] = "."  # Marca a nova sala como visitada.
            stack.append(next_pos)  # Avanca a busca em profundidade.
            carved = True  # Indica que foi possivel continuar.
            break  # Explora a nova ramificacao antes das demais.
        if not carved:  # Nenhuma direcao disponivel nesta ramificacao.
            stack.pop()  # Backtracking: retorna ao vertice anterior.
    path = bfs(grid, START, EXIT, True)  # O labirinto conectado possui caminho a saida.
    if len(path) < 5:  # Condicao defensiva para configuracoes anormais.
        raise ValueError("Labirinto gerado sem percurso suficiente")  # Evita acesso fora de indice.
    index = max(2, min(int(len(path) * 0.68), len(path) - 3))  # Porta perto de 68% do trajeto.
    door = path[index]  # Posiciona um controle de acesso no caminho obrigatorio.
    grid[door[0]][door[1]] = "D"  # Retirar o vertice separa duas componentes.
    _open_loops(grid, door, rng, number * 3 + 7)  # Cria percursos alternativos dentro de cada zona.
    before = reachable(grid, START, False)  # Calcula locais acessiveis antes da porta.
    candidates = [p for p in before if p != START and manhattan(p, START) > 3]  # Locais da credencial.
    if len(candidates) < 2:  # Valida a quantidade minima de posicoes.
        raise ValueError("Nao existem celulas para os objetivos")  # Falha legivel e deterministica.
    key = rng.choice(sorted(candidates))  # Escolhe local para encontrar a chave.
    distant = [p for p in candidates if p != key and len(bfs(grid, key, p, False)) >= 7]  # Distancia minima do enigma.
    puzzle = rng.choice(sorted(distant or [p for p in candidates if p != key]))  # Evita sobreposicao.
    grid[key[0]][key[1]] = "K"  # Adiciona credencial ao mapa.
    grid[puzzle[0]][puzzle[1]] = "E"  # Adiciona ponto de verificacao.
    grid[EXIT[0]][EXIT[1]] = "S"  # Marca a saida.
    safe = set(bfs(grid, START, key, False))  # Resguarda um caminho sem riscos ate K.
    safe.update(bfs(grid, key, puzzle, False))  # Resguarda percurso de K ate E.
    safe.update(bfs(grid, puzzle, EXIT, True))  # Resguarda E ate S apos a abertura.
    forbidden = safe | {START, key, puzzle, door, EXIT}  # Nunca instala perigos no corredor garantido.
    available = sorted(p for p in reachable(grid, START, True) if p not in forbidden and grid[p[0]][p[1]] == ".")  # Celulas candidatas.
    rng.shuffle(available)  # Distribui eventos de risco entre ramos alternativos.
    rubble_n = min(2 + number, len(available) // 5)  # Escombros bloqueiam definitivamente.
    spike_n = min(6 + 2 * number, max(0, (len(available) - rubble_n) // 2))  # Espinhos causam dano.
    laser_n = min(5 + 2 * number, max(0, len(available) - rubble_n - spike_n))  # Laser e temporal.
    for pos in available[:rubble_n]:  # Converte alguns corredores em obstaculos solidos.
        grid[pos[0]][pos[1]] = "R"  # Representa caixa, entulho ou passagem obstruida.
    for pos in available[rubble_n:rubble_n + spike_n]:  # Seleciona pontos com espinhos.
        grid[pos[0]][pos[1]] = "^"  # Representa risco permanente de contato.
    for pos in available[rubble_n + spike_n:rubble_n + spike_n + laser_n]:  # Seleciona perigos ciclicos.
        grid[pos[0]][pos[1]] = "~"  # Representa equipamento com acionamento periodico.
    result = Level(grid, number, START, EXIT, door, key, puzzle, protected=safe)  # Monta a fase tipada.
    if not bfs(grid, START, key, False) or not bfs(grid, key, puzzle, False):  # Confirma acesso pre-porta.
        raise AssertionError("Objetivos inacessiveis")  # Invariante de jogabilidade.
    if not bfs(grid, puzzle, EXIT, True) or bfs(grid, START, EXIT, False):  # Garante porta obrigatoria.
        raise AssertionError("Porta nao separa as areas")  # Evita fase que descumpre as regras.
    return result  # Entrega uma fase valida, deterministica por seed.


@dataclass  # Gera a estrutura de controle de partida.
class Session:  # Armazena eventos, pontuacao, vidas e progresso.
    level: Level = field(default_factory=lambda: generate_level(1))  # Primeira fase automaticamente.
    score: int = 0  # Pontuacao acumulada do jogador.
    state: str = "intro"  # intro, playing, quiz, cleared, lost ou victory.
    message: str = "Encontre a credencial e atravesse com seguranca."  # Aviso contextual.
    hint_open: bool = False  # Controla exibicao da resposta auxiliar.
    hint_mode: str = "none"  # none, safe ou short.
    hinted: bool = False  # Evita desconto repetido da mesma fase.
    steps: int = 0  # Quantidade de movimentos validos da partida.
    impacts: int = 0  # Quantidade total de contatos com perigos.

    def reset(self, seed: int | None = None) -> None:  # Reinicia a partida completamente.
        self.level = generate_level(1, seed)  # Novo mapa inicial reproduzivel se preciso.
        self.score = 0  # Zera placar total.
        self.state = "playing"  # Reativa movimentos.
        self.message = "Procure a chave. Use H para rota mais segura."  # Instrucao inicial.
        self.hint_mode = "none"  # Oculta dicas antigas.
        self.hint_open = False  # Fecha informacao de enigma.
        self.hinted = False  # Restabelece penalidade de dica por fase.
        self.steps = 0  # Zera contador de movimentos.
        self.impacts = 0  # Zera contador de impactos.

    def begin(self) -> None:  # Sai do menu e comeca uma sessao nova.
        self.reset()  # Centraliza inicializacao na rotina validada.

    def move(self, delta: Position) -> str:  # Executa uma acao ortogonal ou espera.
        if self.state != "playing":  # Respeita a maquina de estados.
            return "blocked"  # Teclas de movimento nao atuam fora da partida.
        if delta not in DIRECTIONS + ((0, 0),):  # Entrada deve ser uma das cinco acoes.
            self.message = "Movimento invalido."  # Informa erro sem avancar tempo.
            return "invalid"  # Nao permite teletransporte diagonal.
        nxt = add(self.level.player, delta)  # Calcula o candidato de deslocamento.
        if not walkable(self.level.grid, nxt, self.level.door_open):  # Aplica restricoes espaciais.
            self.message = "Caminho bloqueado ou porta ainda trancada."  # Explica impedimento.
            return "blocked"  # Movimento recusado; relogio da simulacao nao avanca.
        self.level.turns += 1  # Tempo discreto avanca apenas com acao valida.
        self.steps += 1  # Registra acoes validas para metricas.
        self.level.player = nxt  # Atualiza a coordenada atual do personagem.
        tile = self.level.grid[nxt[0]][nxt[1]]  # Le o objeto presente na nova celula.
        if hazard(self.level.grid, nxt, self.level.turns):  # Consulta risco no novo instante.
            self.level.health -= 1  # Subtrai uma vida por contato danoso.
            self.impacts += 1  # Acumula eventos de risco observados.
            self.score = max(0, self.score - 20)  # Penalidade sem pontuacao negativa.
            self.message = "RISCO! Espinhos ou laser ativo: -1 vida e -20 pontos."  # Feedback preciso.
            if self.level.health <= 0:  # Detecta fim das vidas.
                self.state = "lost"  # Abre tela de derrota.
                return "lost"  # Para o restante da avaliacao da celula.
        elif delta == (0, 0):  # Trata a acao de esperar um turno parado.
            self.message = "Voce aguardou um turno. Fase do laser alterada."  # Explica tempo.
        if tile == "K" and not self.level.has_key:  # Encontrou a credencial.
            self.level.has_key = True  # Atualiza primeira proposicao da porta.
            self.level.grid[nxt[0]][nxt[1]] = "."  # Remove item recolhido.
            self.score += 40  # Recompensa da credencial.
            self.message = "Credencial obtida! Procure o desafio matematico."  # Proximo objetivo.
            return "key"  # Evento para a camada grafica.
        if tile == "E" and not self.level.solved:  # Encontrou local da verificacao.
            if not self.level.has_key:  # Verifica pre-requisito do desafio.
                self.message = "Primeiro obtenha a credencial de acesso."  # Impede salto de etapa.
                return "need_key"  # Informa a regra aplicada.
            self.state = "quiz"  # Troca o controle do jogo para caixa do enigma.
            self.hint_open = False  # Oculta inicialmente a dica textual.
            self.message = "Resolva a sequencia para validar o acesso."  # Mensagem de orientacao.
            return "quiz"  # Interface abre o modal.
        if tile == "S":  # O jogador alcancou a saida da fase.
            if not self.level.door_open:  # Checa conjuncao de credencial e verificacao.
                self.message = "Credencial e enigma sao obrigatorios."  # Recusa conclusao invalida.
                return "locked"  # Mantem o jogador na fase.
            self.score += 120  # Recompensa final de conclusao da etapa.
            self.state = "cleared"  # Registra que a fase foi concluida.
            self.message = "Area concluida! Pressione ENTER para continuar."  # Instrucao da interface.
            return "cleared"  # Envia evento para celebracao visual.
        return "step"  # Movimento comum sem objetivo especifico.

    def answer(self, value: str) -> bool:  # Valida a digitacao do desafio.
        if self.state != "quiz":  # Protege contra resposta fora de contexto.
            return False  # Entrada nao tem efeito sem enigma aberto.
        puzzle = PUZZLES[self.level.number - 1]  # Usa indice zero para a fase.
        cleaned = value.strip()  # Remove espacos externos sem alterar numeros.
        if not cleaned.isascii() or not cleaned.isdigit() or len(cleaned) > 8:  # Entrada numerica segura.
            self.message = "Digite apenas numeros inteiros (ate 8 digitos)."  # Tratamento de erro.
            return False  # Mantem o enigma aberto para nova tentativa.
        if cleaned != puzzle["answer"]:  # Compara com a resposta matematica correta.
            self.message = "Resposta incorreta. Analise a regra da sequencia."  # Feedback formativo.
            return False  # Evita desbloqueio sem validacao.
        self.level.solved = True  # Marca a segunda condicao booleana como verdadeira.
        p = self.level.puzzle  # Recupera a coordenada do enigma.
        self.level.grid[p[0]][p[1]] = "."  # Transforma o ponto em corredor comum.
        self.score += 80  # Recompensa pela solucao matematica.
        self.state = "playing"  # Devolve controles de movimento ao jogador.
        self.message = puzzle["why"] + " A porta foi liberada!"  # Explica o resultado.
        return True  # Indica sucesso da resposta.

    def next_level(self, seed: int | None = None) -> None:  # Controla transicao de fases.
        if self.state != "cleared":  # Exige conclusao anterior.
            return  # Ignora tentativa fora de contexto.
        if self.level.number == len(PUZZLES):  # Ultima fase ja foi resolvida.
            self.state = "victory"  # Marca vitoria final da partida.
            self.message = "Todas as zonas foram atravessadas!"  # Conclusao do jogo.
            return  # Mantem a pontuacao e a tela final.
        self.level = generate_level(self.level.number + 1, seed)  # Novo labirinto mais desafiador.
        self.hint_mode = "none"  # Dicas antigas nao migram para outra fase.
        self.hinted = False  # Recupera a possibilidade de dica com custo.
        self.state = "playing"  # Ativa movimentacao na nova area.
        self.message = "Nova zona. Avalie os riscos antes de escolher a rota."  # Instrucao.

    def show_route(self, mode: str) -> tuple[list[Position], int]:  # Consulta rota da fase atual.
        if mode not in ("safe", "short"):  # Valida opcao escolhida.
            raise ValueError("Modo de rota desconhecido")  # Erro de chamada explicito.
        if self.state != "playing":  # Disponibiliza rotas apenas durante a partida.
            return [], -1  # Nao calcula na introducao ou nos desafios.
        self.hint_mode = mode  # Atualiza opcao da interface.
        if not self.hinted:  # Cobra dica uma vez por fase, nao a cada passo.
            self.score = max(0, self.score - 5)  # Penaliza assistencia de navegacao.
            self.hinted = True  # Marca que o desconto ja foi aplicado.
        if mode == "safe":  # Escolha de otimizacao com risco.
            route, cost = astar(self.level.grid, self.level.player, self.level.objective, self.level.turns, self.level.door_open)  # A* temporal ponderado.
            self.message = "Rota segura: minimiza passos + penalidade de risco."  # Informa criterio.
            return route, cost  # Devolve custo ponderado e coordenadas.
        route = bfs(self.level.grid, self.level.player, self.level.objective, self.level.door_open)  # Menor rota geometrica.
        self.message = "Menor rota: pode atravessar espinhos e lasers ativos!"  # Alerta do criterio.
        return route, len(route) - 1 if route else -1  # Numero de passos do caminho.