"""LABIRINTO DOS ENIGMAS: ROTAS DE RISCO | Trabalho A03 - Matematica Computacional.

Execute com `python jogo.py` apos instalar o Pygame (`pip install -r requirements.txt`).
Todo comando importante recebe comentario; o guia explica cada linha numerada.
"""

from __future__ import annotations  # Permite recursos modernos de anotacao de tipos.
import math  # Calcula movimentos circulares e animacoes periodicas.
import sys  # Permite finalizar o programa com codigo de retorno.
from pathlib import Path  # Localiza arquivos sem depender do diretorio inicial.
import pygame  # Biblioteca responsavel por janela, desenho, fontes e eventos.
from src.logica import (  # Importa somente a interface publica do modelo matematico.
    COLS, ROWS, PERIOD, MAX_HEALTH, PUZZLES, Session,  # Dimensoes, regras e sessao do jogador.
    astar, bfs, hazard, laser_active, route_risk,  # Algoritmos e ferramentas de analise.
)  # Encerra importacao agrupada por clareza.

CELL = 32  # Cada vertice da matriz ocupa 32 por 32 pixels.
MAP_W = COLS * CELL  # Largura da area de navegacao em pixels.
MAP_H = ROWS * CELL  # Altura da area de navegacao em pixels.
SCREEN_W = 1200  # Largura da janela do simulador.
SCREEN_H = 750  # Altura da janela do simulador.
MAP_X = 34  # Deslocamento horizontal do mapa dentro da janela.
MAP_Y = 126  # Deslocamento vertical do mapa dentro da janela.
SIDE_X = 804  # Coordenada inicial do painel de indicadores.
SIDE_W = 362  # Largura reservada para painel lateral.
FPS = 60  # Frequencia visual, sem alterar o tempo discreto dos algoritmos.
DAMAGE_FLASH_MS = 850  # Animacao de dano: 850 ms de piscadas vermelhas apos o recuo.
BG = (9, 17, 30)  # Cor do fundo do simulador.
PANEL = (15, 29, 48)  # Superficie dos paineis de informacao.
PANEL_2 = (20, 39, 59)  # Tom secundario para caixas e botoes.
BORDER = (41, 66, 84)  # Cor discreta dos contornos.
WHITE = (239, 246, 255)  # Cor de alto contraste para textos principais.
MUTED = (153, 175, 193)  # Cor de apoio para textos secundarios.
TEAL = (77, 225, 198)  # Cor dos objetivos e das rotas seguras.
GOLD = (248, 191, 83)  # Cor da chave e dos destaques de pontuacao.
RED = (253, 107, 126)  # Cor de perigos ativos e vidas perdidas.
PURPLE = (170, 138, 255)  # Cor dos enigmas e dos lasers.
FLOOR = (23, 43, 60)  # Cor das celulas de piso transitavel.
WALL = (52, 76, 98)  # Cor das paredes do labirinto.
FONT_NAME = "dejavusans"  # Fonte com suporte aos caracteres do portugues.


def font(size: int, bold: bool = False) -> pygame.font.Font:  # Constroi fonte sob demanda para cada dimensao.
    return pygame.font.SysFont(FONT_NAME, size, bold=bold)  # Usa fonte do sistema como fallback.


def text(surface: pygame.Surface, message: str, x: int, y: int, size: int = 18, color: tuple = WHITE, bold: bool = False) -> None:  # Desenha uma linha de texto.
    image = font(size, bold).render(str(message), True, color)  # Converte texto para superficie com antialias.
    surface.blit(image, (x, y))  # Cola a superficie de texto na posicao desejada.


def wrap(surface: pygame.Surface, message: str, x: int, y: int, width: int, size: int = 16, color: tuple = MUTED, line_height: int = 24) -> int:  # Quebra texto automaticamente.
    words = str(message).split()  # Divide frase em palavras sem perder a ordem.
    current = ""  # Guarda a linha em montagem.
    for word in words:  # Testa cada palavra da frase.
        trial = (current + " " + word).strip()  # Monta a linha candidata.
        if font(size).size(trial)[0] > width and current:  # Verifica se ultrapassa o limite.
            text(surface, current, x, y, size, color)  # Renderiza a linha que ja estava completa.
            y += line_height  # Passa para a proxima linha vertical.
            current = word  # Inicia nova linha com a palavra atual.
        else:  # Executa quando o texto ainda cabe no limite.
            current = trial  # Continua preenchendo a mesma linha.
    if current:  # A ultima linha precisa ser exibida mesmo sem ultrapassar o limite.
        text(surface, current, x, y, size, color)  # Desenha o restante da frase.
        y += line_height  # Devolve a proxima coordenada livre.
    return y  # Permite empilhar paragrafos sem sobreposicao.


def rounded(surface: pygame.Surface, rect: tuple, color: tuple, radius: int = 14, border: tuple | None = None) -> None:  # Desenha cartao arredondado.
    pygame.draw.rect(surface, color, rect, border_radius=radius)  # Preenche o painel.
    if border is not None:  # Uma borda e opcional.
        pygame.draw.rect(surface, border, rect, width=1, border_radius=radius)  # Desenha contorno suave.


def button(surface: pygame.Surface, rect: pygame.Rect, label: str, mouse: tuple, active: bool = False, accent: tuple = TEAL) -> None:  # Desenha botao com estado visual.
    hovered = rect.collidepoint(mouse)  # Detecta aproximacao do mouse.
    color = (37, 75, 91) if hovered or active else PANEL_2  # Destaca selecao e passagem do ponteiro.
    rounded(surface, tuple(rect), color, 10, accent if active else BORDER)  # Pinta o botao.
    label_image = font(15, bold=True).render(label, True, WHITE if not active else accent)  # Centraliza o texto do botao.
    surface.blit(label_image, label_image.get_rect(center=rect.center))  # Exibe legenda centralizada.


def tile_center(pos: tuple[int, int]) -> tuple[int, int]:  # Converte coordenadas discretas em pixels.
    row, col = pos  # Desempacota linha e coluna do grafo.
    return (MAP_X + col * CELL + CELL // 2, MAP_Y + row * CELL + CELL // 2)  # Centro da celula na tela.


def draw_diamond(surface: pygame.Surface, x: int, y: int, radius: int, color: tuple) -> None:  # Desenha icone geométrico de destaque.
    pygame.draw.polygon(surface, color, [(x, y - radius), (x + radius, y), (x, y + radius), (x - radius, y)])  # Poligono de quatro pontas.


def draw_grid(surface: pygame.Surface, session: Session, path: list[tuple[int, int]], mode: str, now: int, last_hit_at: int) -> None:  # Desenha o mapa e a animacao de impacto.
    level = session.level  # Recupera o mapa e o agente da fase atual.
    rounded(surface, (MAP_X - 12, MAP_Y - 12, MAP_W + 24, MAP_H + 24), PANEL, 16, BORDER)  # Moldura do labirinto.
    for row in range(ROWS):  # Percorre todas as linhas da matriz.
        for col in range(COLS):  # Percorre todas as colunas da linha atual.
            symbol = level.grid[row][col]  # Le o conteudo da celula.
            left = MAP_X + col * CELL  # Calcula a posicao horizontal do quadrado.
            top = MAP_Y + row * CELL  # Calcula a posicao vertical do quadrado.
            rect = pygame.Rect(left + 1, top + 1, CELL - 2, CELL - 2)  # Guarda uma margem entre celulas.
            if symbol == "#":  # Verifica se o vertice e bloqueado por parede.
                rounded(surface, tuple(rect), WALL, 4)  # Desenha a parede resistente.
                pygame.draw.line(surface, (68, 94, 117), rect.topleft, (rect.right, rect.top), 1)  # Acabamento de relevo.
                continue  # Nao ha objetos dentro de uma parede.
            rounded(surface, tuple(rect), FLOOR, 4)  # Desenha o corredor acessivel.
            cx, cy = tile_center((row, col))  # Recupera o centro para desenhar os simbolos.
            if symbol == "R":  # Entulho representa uma barreira fisica.
                pygame.draw.polygon(surface, (126, 144, 157), [(left + 5, top + 23), (left + 10, top + 8), (left + 22, top + 6), (left + 28, top + 23)])  # Bloco de escombros.
                pygame.draw.line(surface, (75, 93, 106), (left + 12, top + 14), (left + 21, top + 19), 2)  # Fissura da pedra.
            elif symbol == "^":  # Espinhos provocam dano permanente ao entrar.
                for offset in (5, 14, 23):  # Repete tres pontas na largura do piso.
                    pygame.draw.polygon(surface, RED, [(left + offset - 3, top + 25), (left + offset + 2, top + 7), (left + offset + 7, top + 25)])  # Triangulo pontiagudo.
            elif symbol == "~":  # Laser utiliza o tempo discreto para definir perigo.
                enabled = laser_active(level.turns)  # Verifica a fase do ciclo modular do obstaculo.
                shade = PURPLE if enabled else (87, 80, 111)  # Laser ativo brilha mais.
                pygame.draw.line(surface, shade, (left + 7, cy), (left + 25, cy), 5 if enabled else 2)  # Emite feixe horizontal.
                pygame.draw.circle(surface, shade, (left + 6, cy), 4)  # Desenha emissor esquerdo.
                pygame.draw.circle(surface, shade, (left + 26, cy), 4)  # Desenha emissor direito.
            elif symbol == "D":  # A porta depende da conjuncao chave E resposta.
                shade = TEAL if level.door_open else (195, 132, 97)  # Altera cor ao desbloquear.
                pygame.draw.rect(surface, shade, (left + 8, top + 5, 16, 24), border_radius=3)  # Desenha a estrutura da porta.
                pygame.draw.circle(surface, BG, (left + 20, top + 17), 2)  # Desenha a fechadura.
            elif symbol == "K":  # Credencial que libera um dos predicados de acesso.
                pygame.draw.circle(surface, GOLD, (cx - 5, cy - 3), 6, 3)  # Parte circular da chave.
                pygame.draw.line(surface, GOLD, (cx, cy), (cx + 10, cy + 9), 4)  # Corpo metalico da chave.
                pygame.draw.line(surface, GOLD, (cx + 6, cy + 6), (cx + 11, cy + 2), 3)  # Dente da chave.
            elif symbol == "E":  # Desafio matematico funciona como checkpoint de logica.
                pygame.draw.circle(surface, PURPLE, (cx, cy), 12)  # Corpo circular do enigma.
                text(surface, "?", cx - 5, cy - 12, 20, BG, True)  # Simbolo de pergunta.
            elif symbol == "S":  # Representa o destino da rota de evacuacao.
                pygame.draw.circle(surface, TEAL, (cx, cy), 12, 3)  # Alvo verde de chegada.
                pygame.draw.circle(surface, TEAL, (cx, cy), 4)  # Nucleo da chegada.
    if path:  # So mostra o planejamento depois da solicitacao de ajuda.
        shade = TEAL if mode == "safe" else GOLD  # Separa rota segura da menor rota geometrica.
        for idx, point in enumerate(path[1:], 1):  # Nao realca a posicao inicial do caminho.
            center = tile_center(point)  # Coordenadas visuais do vertice analisado.
            pygame.draw.circle(surface, shade, center, 4 if idx % 3 else 5)  # Marca etapas do caminho.
    cx, cy = tile_center(level.player)  # Posiciona jogador sobre sua celula atual.
    pulse = math.sin(now * 0.005) * 2  # Pequena animacao usando funcao seno.
    elapsed = now - last_hit_at  # Calcula quantos milissegundos passaram desde o ultimo impacto.
    flashing = 0 <= elapsed < DAMAGE_FLASH_MS  # Define a janela temporal da animacao de dano.
    red_frame = flashing and (elapsed // 105) % 2 == 0  # Alterna vermelho/azul a cada 105 ms.
    body = RED if red_frame else (91, 187, 255)  # Seleciona vermelho durante as piscadas.
    aura = (107, 28, 45) if red_frame else (12, 41, 60)  # O halo acompanha a mudanca de cor.
    pygame.draw.circle(surface, aura, (cx, cy), int(16 + pulse))  # Desenha halo pulsante, vermelho no impacto.
    pygame.draw.circle(surface, body, (cx, cy), 12)  # Desenha o personagem na casa segura apos o recuo.
    pygame.draw.circle(surface, WHITE, (cx + 3, cy - 3), 4)  # Mantem o brilho para facilitar a leitura visual.


def draw_panel(surface: pygame.Surface, session: Session, path: list, route_cost: int, seconds: float, mouse: tuple, buttons: dict, show_debug: bool) -> None:  # Painel direito de matematica aplicada.
    level = session.level  # Permite consultar todos os campos da fase.
    rounded(surface, (SIDE_X, 126, SIDE_W, 570), PANEL, 16, BORDER)  # Cartao de metricas.
    text(surface, "PAINEL DE NAVEGAÇÃO", SIDE_X + 20, 148, 15, TEAL, True)  # Identifica area analitica.
    text(surface, f"FASE {level.number:02d} / 03", SIDE_X + 20, 186, 24, WHITE, True)  # Indica progresso.
    text(surface, "SISTEMA DE ROTAS E RISCOS", SIDE_X + 20, 222, 12, MUTED)  # Resume objetivo do jogo.
    pygame.draw.line(surface, BORDER, (SIDE_X + 18, 255), (SIDE_X + SIDE_W - 18, 255), 1)  # Separa indicadores.
    metrics = [("PONTOS", str(session.score)), ("TURNOS", str(level.turns)), ("TEMPO", f"{int(seconds)//60:02d}:{int(seconds)%60:02d}")]  # Agrupa metricas visiveis.
    for i, (label, value) in enumerate(metrics):  # Desenha colunas alinhadas.
        mx = SIDE_X + 20 + i * 115  # Computa o inicio de cada indicador.
        text(surface, label, mx, 274, 11, MUTED, True)  # Titula indicador.
        text(surface, value, mx, 297, 21, GOLD if i == 0 else WHITE, True)  # Exibe valor atualizado.
    pygame.draw.line(surface, BORDER, (SIDE_X + 18, 337), (SIDE_X + SIDE_W - 18, 337), 1)  # Separa a barra de saude.
    text(surface, "INTEGRIDADE", SIDE_X + 20, 350, 12, MUTED, True)  # Rotulo de vidas.
    for life in range(MAX_HEALTH):  # Desenha quatro indicadores de resistencia.
        color = RED if life < level.health else (55, 71, 85)  # Vidas perdidas ficam apagadas.
        pygame.draw.circle(surface, color, (SIDE_X + 161 + life * 30, 359), 9)  # Sinaliza vida individual.
    text(surface, "CREDENCIAL", SIDE_X + 20, 387, 12, MUTED)  # Primeira condicao da logica.
    text(surface, "SIM" if level.has_key else "NÃO", SIDE_X + 180, 386, 14, TEAL if level.has_key else GOLD, True)  # Booleano da chave.
    text(surface, "ENIGMA", SIDE_X + 20, 414, 12, MUTED)  # Segunda condicao da logica.
    text(surface, "VALIDADO" if level.solved else "PENDENTE", SIDE_X + 180, 413, 14, TEAL if level.solved else GOLD, True)  # Booleano da resposta.
    text(surface, "PORTA = CHAVE ∧ ENIGMA", SIDE_X + 20, 443, 13, TEAL if level.door_open else MUTED, True)  # Formula proposicional de acesso.
    pygame.draw.line(surface, BORDER, (SIDE_X + 18, 475), (SIDE_X + SIDE_W - 18, 475), 1)  # Separa o roteamento.
    text(surface, "PLANEJAMENTO MATEMÁTICO", SIDE_X + 20, 490, 13, WHITE, True)  # Area para BFS e A*.
    for name in ("safe", "short"):  # Desenha um botao para cada criterio de busca.
        label = "H • A* ROTA SEGURA" if name == "safe" else "J • BFS MENOR ROTA"  # Legendas e atalhos.
        button(surface, buttons[name], label, mouse, session.hint_mode == name, TEAL if name == "safe" else GOLD)  # Apresenta modo.
    if path:  # Dados da rota aparecem apenas apos uma consulta.
        text(surface, f"Rota: {max(0, len(path)-1)} ações  |  custo: {route_cost}", SIDE_X + 20, 606, 12, TEAL, True)  # Comprimento e custo.
        if session.hint_mode == "short":  # BFS nao considera penalidades de dano.
            risk = route_risk(level.grid, path, level.turns)  # Conta possiveis colisoes na rota.
            text(surface, f"Possíveis impactos na BFS: {risk}", SIDE_X + 20, 627, 12, RED if risk else MUTED)  # Indicador de risco.
        else:  # Caminho otimizado pelo custo ponderado.
            text(surface, "A* inclui tempo e risco na decisão", SIDE_X + 20, 627, 11, MUTED)  # Explica criterio.
    else:  # Nao ha rota desenhada quando a consulta nao foi solicitada.
        text(surface, "Compare menor distância × menor risco", SIDE_X + 20, 610, 11, MUTED)  # Incentiva comparacao.
    if show_debug:  # Mostra formalizacao opcional para apresentacao academica.
        text(surface, "f(n)=g(n)+h(n)  |  h=Manhattan", SIDE_X + 20, 658, 11, PURPLE)  # Equacao do A*.
    else:  # Indicacao para abrir formula matematica.
        text(surface, "M: mostrar fórmula matemática", SIDE_X + 20, 658, 11, MUTED)  # Legenda de ajuda.


def overlay(surface: pygame.Surface, session: Session, answer: str, mouse: tuple, buttons: dict) -> None:  # Janelas de introducao e estados especiais.
    if session.state == "playing":  # Jogo normal nao precisa de modal.
        return  # Mantem o mapa livre.
    shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)  # Cria camada com transparencia.
    shade.fill((5, 12, 22, 218))  # Escurece o fundo para focar a janela.
    surface.blit(shade, (0, 0))  # Exibe a pelicula sobre o jogo.
    modal = (260, 175, 680, 400)  # Retangulo central comum aos estados.
    rounded(surface, modal, PANEL, 22, BORDER)  # Desenha a caixa principal.
    if session.state == "intro":  # Primeiro contato explica a experiencia.
        text(surface, "LABIRINTO DOS ENIGMAS", 310, 223, 30, TEAL, True)  # Titulo da introducao.
        text(surface, "Missão: sair de um ambiente com riscos", 310, 276, 19, WHITE)  # Contextualiza o problema.
        wrap(surface, "Planeje rotas, colete uma credencial, resolva o enigma e evite espinhos, escombros e lasers que alternam a cada turno.", 310, 312, 585, 17, MUTED, 28)  # Explica a dinamica.
        text(surface, "BFS procura menos passos. A* considera distância + dano.", 310, 407, 15, GOLD)  # Relacao com a disciplina.
        button(surface, buttons["primary"], "ENTER  •  INICIAR SIMULAÇÃO", mouse, True)  # Botao de partida.
    elif session.state == "quiz":  # Entrada numerica permite resolver a prova da fase.
        p = PUZZLES[session.level.number - 1]  # Enigma correspondente a fase atual.
        text(surface, "VERIFICAÇÃO MATEMÁTICA", 310, 214, 25, PURPLE, True)  # Titulo da verificacao.
        text(surface, p["question"], 310, 277, 22, WHITE, True)  # Enunciado principal.
        rounded(surface, (310, 335, 570, 57), PANEL_2, 10, PURPLE)  # Campo grafico para resposta.
        text(surface, answer + "|", 329, 349, 23, GOLD, True)  # Cursor e valor digitado.
        if session.hint_open:  # Exibe ajuda apenas quando solicitada.
            wrap(surface, "DICA: " + p["hint"], 312, 413, 560, 16, GOLD, 25)  # Apresenta a sequencia.
        else:  # Instrucao de como solicitar a ajuda.
            text(surface, "Pressione I para mostrar uma dica.", 312, 416, 16, MUTED)  # Texto explicativo.
        wrap(surface, session.message, 312, 461, 560, 14, MUTED, 21)  # Retorno de validacao.
        text(surface, "ENTER: confirmar    BACKSPACE: apagar", 312, 521, 14, TEAL)  # Comandos do formulario.
    elif session.state == "cleared":  # Etapa encerrada com sucesso.
        text(surface, "ZONA CONCLUÍDA", 310, 230, 32, TEAL, True)  # Mensagem de conquista.
        text(surface, f"Pontuação acumulada: {session.score}", 310, 303, 24, GOLD)  # Resumo da rodada.
        wrap(surface, "A decisão matemática correta transforma um ambiente complexo em uma rota viável.", 310, 363, 560, 17, MUTED, 28)  # Conexao didatica.
        button(surface, buttons["primary"], "ENTER  •  CONTINUAR", mouse, True)  # Passa para outra fase.
    elif session.state == "lost":  # Colisoes esgotaram a integridade do agente.
        text(surface, "RISCO CRÍTICO", 310, 230, 32, RED, True)  # Tela de derrota.
        wrap(surface, "Sua integridade chegou a zero. Reavalie o caminho: a rota mais curta nem sempre é a mais segura.", 310, 308, 570, 18, MUTED, 30)  # Explicacao do erro.
        button(surface, buttons["primary"], "R  •  REINICIAR", mouse, True, RED)  # Possibilita uma nova tentativa.
    elif session.state == "victory":  # Todas as tres fases foram superadas.
        text(surface, "MISSÃO CONCLUÍDA!", 310, 228, 30, TEAL, True)  # Mensagem final.
        text(surface, f"Pontuação final: {session.score}", 310, 305, 25, GOLD, True)  # Resultado da sessao.
        text(surface, f"Total de impactos: {session.impacts}", 310, 351, 19, WHITE)  # Indicador de seguranca.
        button(surface, buttons["primary"], "R  •  JOGAR NOVAMENTE", mouse, True)  # Reinicia a experiencia.


def main() -> int:  # Ponto de entrada da interface Pygame.
    pygame.init()  # Inicializa os modulos de video, teclado e fontes.
    pygame.key.set_repeat(160, 100)  # Permite movimento repetido ao segurar setas.
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))  # Cria janela com dimensoes fixas.
    pygame.display.set_caption("Labirinto dos Enigmas | Matematica Computacional")  # Identifica janela.
    clock = pygame.time.Clock()  # Controla a taxa visual de atualizacao.
    session = Session()  # Instancia o modelo sem misturar logica e desenho.
    answer = ""  # Armazena entrada numerica corrente no desafio.
    path: list[tuple[int, int]] = []  # Lista do caminho calculado por BFS ou A*.
    route_cost = -1  # Custo ponderado da rota inicialmente desconhecido.
    show_debug = False  # Permite exibir formalizacao do A* opcionalmente.
    seconds = 0.0  # Cronometro apenas visual: NAO define o tempo dos lasers.
    last_hit_at = -DAMAGE_FLASH_MS  # Inicialmente nao existe impacto e o jogador permanece azul.
    buttons = {"safe": pygame.Rect(SIDE_X + 20, 522, 318, 35), "short": pygame.Rect(SIDE_X + 20, 563, 318, 35), "primary": pygame.Rect(310, 485, 570, 55)}  # Regioes clicaveis.
    moves = {pygame.K_UP: (-1, 0), pygame.K_w: (-1, 0), pygame.K_DOWN: (1, 0), pygame.K_s: (1, 0), pygame.K_LEFT: (0, -1), pygame.K_a: (0, -1), pygame.K_RIGHT: (0, 1), pygame.K_d: (0, 1), pygame.K_SPACE: (0, 0)}  # Mapa de controles.
    running = True  # Variavel booleana de continuidade do programa.
    while running:  # Loop principal: entrada, atualizacao e desenho.
        dt = clock.tick(FPS) / 1000.0  # Converte duracao do quadro em segundos.
        now = pygame.time.get_ticks()  # Tempo visual utilizado na animacao do jogador.
        mouse = pygame.mouse.get_pos()  # Posicao atual do cursor para efeito hover.
        if session.state in ("playing", "quiz"):  # Cronometro corre durante as duas etapas.
            seconds += dt  # Avanca tempo visual real de forma independente dos turnos.
        for event in pygame.event.get():  # Consome eventos para impedir congelamento do sistema.
            if event.type == pygame.QUIT:  # Usuario clicou em fechar janela.
                running = False  # Encerra loop normalmente.
                continue  # Ignora processamento adicional deste evento.
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clique esquerdo do mouse.
                if session.state == "playing":  # Botoes de rota so funcionam em partida ativa.
                    for name in ("safe", "short"):  # Confere ambos os botoes do painel.
                        if buttons[name].collidepoint(event.pos):  # Verifica se o clique atingiu o botao.
                            path, route_cost = session.show_route(name)  # Executa BFS ou A* do modelo.
                elif buttons["primary"].collidepoint(event.pos):  # Clique no botao de inicio/continuidade.
                    if session.state == "intro":  # Estado inicial da aplicacao.
                        session.begin()  # Inicia a primeira fase.
                    elif session.state == "cleared":  # Fase finalizada com sucesso.
                        session.next_level()  # Avanca para a etapa seguinte.
                    elif session.state in ("lost", "victory"):  # Fim de jogo ou derrota.
                        session.reset()  # Reinicia pontuacao e labirintos.
                        seconds = 0.0  # Reinicia cronometro da partida.
                        last_hit_at = -DAMAGE_FLASH_MS  # Cancela piscadas da partida anterior.
                    path = []  # Esconde rota de qualquer fase anterior.
                continue  # Clique processado; passa ao proximo evento.
            if event.type != pygame.KEYDOWN:  # Eventos de movimento exigem tecla pressionada.
                continue  # Ignora entrada nao relevante.
            if event.key == pygame.K_ESCAPE:  # ESC fecha o programa em qualquer estado.
                running = False  # Finaliza aplicacao sem erros.
                continue  # Nao processa outras operacoes.
            if event.key == pygame.K_r and session.state != "quiz":  # Atalho global para reiniciar, exceto durante enigma.
                session.reset()  # Gera nova partida limpa.
                path = []  # Desliga trilha de navegacao antiga.
                answer = ""  # Limpa campos de texto antigos.
                seconds = 0.0  # Zera cronometro visual.
                last_hit_at = -DAMAGE_FLASH_MS  # Garante que a nova partida comece sem efeito vermelho.
                continue  # Terminou tratamento de reinicio.
            if session.state == "intro" and event.key == pygame.K_RETURN:  # ENTER na tela inicial.
                session.begin()  # Inicia sessao em estado valido.
                continue  # Evita comandos simultaneos.
            if session.state == "cleared" and event.key == pygame.K_RETURN:  # ENTER apos finalizar fase.
                session.next_level()  # Passa a fase 2/3 ou vitoria.
                path = []  # Limpa rota antiga ao mudar o objetivo.
                continue  # Evento concluido.
            if session.state == "quiz":  # Enigma intercepta as entradas de teclado.
                if event.key == pygame.K_i:  # Atalho para dica matematica.
                    session.hint_open = True  # Mostra a pista do enigma.
                elif event.key == pygame.K_BACKSPACE:  # Tecla de apagar.
                    answer = answer[:-1]  # Retira ultimo digito digitado.
                elif event.key == pygame.K_RETURN:  # Valida resposta fornecida.
                    accepted = session.answer(answer)  # Funcao booleana do modelo.
                    if accepted:  # Enigma correto desbloqueia a porta.
                        answer = ""  # Limpa valor que ja foi utilizado.
                        path = []  # Forca nova rota com porta aberta.
                elif event.unicode.isascii() and event.unicode.isdigit() and len(answer) < 8:  # Apenas digitos ASCII permitidos.
                    answer += event.unicode  # Anexa caracter validado sem risco de overflow textual.
                continue  # Impede que o enigma movimente o personagem.
            if session.state != "playing":  # Derrota e vitoria nao aceitam movimento.
                continue  # Espera um comando de reiniciar ou continuar.
            if event.key == pygame.K_h:  # H: rota ponderada e temporal com A*.
                path, route_cost = session.show_route("safe")  # Busca minimizar passos e risco.
            elif event.key == pygame.K_j:  # J: rota geometrica curta com BFS.
                path, route_cost = session.show_route("short")  # Busca minimo numero de passos.
            elif event.key == pygame.K_m:  # M: exibe a funcao matematica A*.
                show_debug = not show_debug  # Alterna modo tecnico para a apresentacao.
            elif event.key in moves:  # Setas, WASD ou espaco fazem acoes validas.
                if now - last_hit_at < DAMAGE_FLASH_MS:  # Durante a piscada, bloqueia tecla repetida contra o mesmo perigo.
                    continue  # Evita perder varias vidas de uma vez segurando a seta.
                action = session.move(moves[event.key])  # Recebe o evento logico da colisao ou do movimento.
                if action in ("damage", "lost"):  # Impactos geram a mesma animacao vermelha.
                    last_hit_at = now  # Inicia o cronometro da piscada sem alterar os turnos dos lasers.
                path = []  # Um caminho consultado fica obsoleto apos cada acao.
        screen.fill(BG)  # Limpa quadro antes de redesenhar tudo.
        for i in range(0, SCREEN_W, 40):  # Mostra grid discreto decorativo no fundo.
            pygame.draw.line(screen, (14, 27, 42), (i, 0), (i, SCREEN_H), 1)  # Linha vertical decorativa.
        text(screen, "LABIRINTO", MAP_X, 31, 32, WHITE, True)  # Marca principal do jogo.
        text(screen, "DOS ENIGMAS", MAP_X + 205, 33, 29, TEAL, True)  # Segunda metade do titulo.
        text(screen, "ROTAS DE RISCO  |  MATEMÁTICA COMPUTACIONAL", MAP_X + 2, 83, 13, MUTED, True)  # Contexto academico.
        draw_grid(screen, session, path, session.hint_mode, now, last_hit_at)  # Renderiza o mapa e a piscada vermelha de impacto.
        draw_panel(screen, session, path, route_cost, seconds, mouse, buttons, show_debug)  # Mostra metricas e botoes.
        rounded(screen, (MAP_X - 12, 638, MAP_W + 24, 58), PANEL, 12, BORDER)  # Barra de mensagens contextual.
        wrap(screen, session.message, MAP_X + 4, 650, MAP_W - 20, 15, GOLD if "RISCO" in session.message else WHITE, 22)  # Informa evento ao jogador.
        text(screen, "WASD/SETAS mover    ESPAÇO esperar    H A* seguro    J BFS curto    M fórmula    R reiniciar    ESC sair", 35, 713, 13, MUTED)  # Lembrete de controles.
        overlay(screen, session, answer, mouse, buttons)  # Exibe modal quando o estado exigir.
        pygame.display.flip()  # Troca o quadro desenhado pelo quadro visivel.
    pygame.quit()  # Fecha os subsistemas graficos com seguranca.
    return 0  # Retorna sucesso ao sistema operacional.


if __name__ == "__main__":  # Impede execucao automatica quando o arquivo e importado.
    sys.exit(main())  # Inicia a interface e propaga o codigo de saida.