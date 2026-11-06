"""Labirinto dos Enigmas - interface do jogo em Pygame.

Para jogar: python jogo.py
"""

from __future__ import annotations
import math
import sys
import pygame
from logica import (
    COLS, ROWS, PERIOD, MAX_HEALTH, PUZZLES, Session,
    astar, bfs, hazard, laser_active, route_risk,
)

# Configuracoes da janela, do mapa e das cores
CELL = 32
MAP_W = COLS * CELL
MAP_H = ROWS * CELL
SCREEN_W = 1200
SCREEN_H = 750
MAP_X = 34
MAP_Y = 126
SIDE_X = 804
SIDE_W = 362
FPS = 60
DAMAGE_FLASH_MS = 850
BG = (9, 17, 30)
PANEL = (15, 29, 48)
PANEL_2 = (20, 39, 59)
BORDER = (41, 66, 84)
WHITE = (239, 246, 255)
MUTED = (153, 175, 193)
TEAL = (77, 225, 198)
GOLD = (248, 191, 83)
RED = (253, 107, 126)
PURPLE = (170, 138, 255)
FLOOR = (23, 43, 60)
WALL = (52, 76, 98)
FONT_NAME = "dejavusans"


# Ferramentas para desenhar textos, cartoes e botoes
def font(size: int, bold: bool = False) -> pygame.font.Font:
    """Cria uma fonte Pygame do tamanho solicitado."""
    return pygame.font.SysFont(FONT_NAME, size, bold=bold)


def text(surface: pygame.Surface, message: str, x: int, y: int, size: int = 18, color: tuple = WHITE, bold: bool = False) -> None:
    """Mostra uma linha de texto na tela."""
    image = font(size, bold).render(str(message), True, color)
    surface.blit(image, (x, y))


def wrap(surface: pygame.Surface, message: str, x: int, y: int, width: int, size: int = 16, color: tuple = MUTED, line_height: int = 24) -> int:
    """Quebra textos longos para caberem no painel."""
    words = str(message).split()
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if font(size).size(trial)[0] > width and current:
            text(surface, current, x, y, size, color)
            y += line_height
            current = word
        else:
            current = trial
    if current:
        text(surface, current, x, y, size, color)
        y += line_height
    return y


def rounded(surface: pygame.Surface, rect: tuple, color: tuple, radius: int = 14, border: tuple | None = None) -> None:
    """Desenha um retangulo arredondado."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border is not None:
        pygame.draw.rect(surface, border, rect, width=1, border_radius=radius)


def button(surface: pygame.Surface, rect: pygame.Rect, label: str, mouse: tuple, active: bool = False, accent: tuple = TEAL) -> None:
    """Desenha os botoes e seus estados visuais."""
    hovered = rect.collidepoint(mouse)
    color = (37, 75, 91) if hovered or active else PANEL_2
    rounded(surface, tuple(rect), color, 10, accent if active else BORDER)
    label_image = font(15, bold=True).render(label, True, WHITE if not active else accent)
    surface.blit(label_image, label_image.get_rect(center=rect.center))


def tile_center(pos: tuple[int, int]) -> tuple[int, int]:
    """Converte uma casa da matriz em posicao na tela."""
    row, col = pos
    return (MAP_X + col * CELL + CELL // 2, MAP_Y + row * CELL + CELL // 2)


def draw_diamond(surface: pygame.Surface, x: int, y: int, radius: int, color: tuple) -> None:
    """Desenha um simbolo em formato de losango."""
    pygame.draw.polygon(surface, color, [(x, y - radius), (x + radius, y), (x, y + radius), (x - radius, y)])


# Desenho do labirinto, armadilhas e jogador
def draw_grid(surface: pygame.Surface, session: Session, path: list[tuple[int, int]], mode: str, now: int, last_hit_at: int) -> None:
    """Desenha o mapa, os perigos e a piscada vermelha do jogador."""
    level = session.level
    rounded(surface, (MAP_X - 12, MAP_Y - 12, MAP_W + 24, MAP_H + 24), PANEL, 16, BORDER)
    for row in range(ROWS):
        for col in range(COLS):
            symbol = level.grid[row][col]
            left = MAP_X + col * CELL
            top = MAP_Y + row * CELL
            rect = pygame.Rect(left + 1, top + 1, CELL - 2, CELL - 2)
            if symbol == "#":
                rounded(surface, tuple(rect), WALL, 4)
                pygame.draw.line(surface, (68, 94, 117), rect.topleft, (rect.right, rect.top), 1)
                continue
            rounded(surface, tuple(rect), FLOOR, 4)
            cx, cy = tile_center((row, col))
            if symbol == "R":
                pygame.draw.polygon(surface, (126, 144, 157), [(left + 5, top + 23), (left + 10, top + 8), (left + 22, top + 6), (left + 28, top + 23)])
                pygame.draw.line(surface, (75, 93, 106), (left + 12, top + 14), (left + 21, top + 19), 2)
            elif symbol == "^":
                for offset in (5, 14, 23):
                    pygame.draw.polygon(surface, RED, [(left + offset - 3, top + 25), (left + offset + 2, top + 7), (left + offset + 7, top + 25)])
            elif symbol == "~":
                enabled = laser_active(level.turns)
                shade = PURPLE if enabled else (87, 80, 111)
                pygame.draw.line(surface, shade, (left + 7, cy), (left + 25, cy), 5 if enabled else 2)
                pygame.draw.circle(surface, shade, (left + 6, cy), 4)
                pygame.draw.circle(surface, shade, (left + 26, cy), 4)
            elif symbol == "D":
                shade = TEAL if level.door_open else (195, 132, 97)
                pygame.draw.rect(surface, shade, (left + 8, top + 5, 16, 24), border_radius=3)
                pygame.draw.circle(surface, BG, (left + 20, top + 17), 2)
            elif symbol == "K":
                pygame.draw.circle(surface, GOLD, (cx - 5, cy - 3), 6, 3)
                pygame.draw.line(surface, GOLD, (cx, cy), (cx + 10, cy + 9), 4)
                pygame.draw.line(surface, GOLD, (cx + 6, cy + 6), (cx + 11, cy + 2), 3)
            elif symbol == "E":
                pygame.draw.circle(surface, PURPLE, (cx, cy), 12)
                text(surface, "?", cx - 5, cy - 12, 20, BG, True)
            elif symbol == "S":
                pygame.draw.circle(surface, TEAL, (cx, cy), 12, 3)
                pygame.draw.circle(surface, TEAL, (cx, cy), 4)
    if path:
        shade = TEAL if mode == "safe" else GOLD
        for idx, point in enumerate(path[1:], 1):
            center = tile_center(point)
            pygame.draw.circle(surface, shade, center, 4 if idx % 3 else 5)
    cx, cy = tile_center(level.player)
    pulse = math.sin(now * 0.005) * 2
    elapsed = now - last_hit_at
    flashing = 0 <= elapsed < DAMAGE_FLASH_MS
    red_frame = flashing and (elapsed // 105) % 2 == 0
    body = RED if red_frame else (91, 187, 255)
    aura = (107, 28, 45) if red_frame else (12, 41, 60)
    pygame.draw.circle(surface, aura, (cx, cy), int(16 + pulse))
    pygame.draw.circle(surface, body, (cx, cy), 12)
    pygame.draw.circle(surface, WHITE, (cx + 3, cy - 3), 4)


# Informacoes e controles do painel lateral
def draw_panel(surface: pygame.Surface, session: Session, path: list, route_cost: int, seconds: float, mouse: tuple, buttons: dict, show_debug: bool) -> None:
    """Mostra pontos, vidas, turnos e comparacao de rotas."""
    level = session.level
    rounded(surface, (SIDE_X, 126, SIDE_W, 570), PANEL, 16, BORDER)
    text(surface, "PAINEL DE NAVEGAÇÃO", SIDE_X + 20, 148, 15, TEAL, True)
    text(surface, f"FASE {level.number:02d} / 03", SIDE_X + 20, 186, 24, WHITE, True)
    text(surface, "SISTEMA DE ROTAS E RISCOS", SIDE_X + 20, 222, 12, MUTED)
    pygame.draw.line(surface, BORDER, (SIDE_X + 18, 255), (SIDE_X + SIDE_W - 18, 255), 1)
    metrics = [("PONTOS", str(session.score)), ("TURNOS", str(level.turns)), ("TEMPO", f"{int(seconds)//60:02d}:{int(seconds)%60:02d}")]
    for i, (label, value) in enumerate(metrics):
        mx = SIDE_X + 20 + i * 115
        text(surface, label, mx, 274, 11, MUTED, True)
        text(surface, value, mx, 297, 21, GOLD if i == 0 else WHITE, True)
    pygame.draw.line(surface, BORDER, (SIDE_X + 18, 337), (SIDE_X + SIDE_W - 18, 337), 1)
    text(surface, "INTEGRIDADE", SIDE_X + 20, 350, 12, MUTED, True)
    for life in range(MAX_HEALTH):
        color = RED if life < level.health else (55, 71, 85)
        pygame.draw.circle(surface, color, (SIDE_X + 161 + life * 30, 359), 9)
    text(surface, "CREDENCIAL", SIDE_X + 20, 387, 12, MUTED)
    text(surface, "SIM" if level.has_key else "NÃO", SIDE_X + 180, 386, 14, TEAL if level.has_key else GOLD, True)
    text(surface, "ENIGMA", SIDE_X + 20, 414, 12, MUTED)
    text(surface, "VALIDADO" if level.solved else "PENDENTE", SIDE_X + 180, 413, 14, TEAL if level.solved else GOLD, True)
    text(surface, "PORTA = CHAVE ∧ ENIGMA", SIDE_X + 20, 443, 13, TEAL if level.door_open else MUTED, True)
    pygame.draw.line(surface, BORDER, (SIDE_X + 18, 475), (SIDE_X + SIDE_W - 18, 475), 1)
    text(surface, "PLANEJAMENTO MATEMÁTICO", SIDE_X + 20, 490, 13, WHITE, True)
    for name in ("safe", "short"):
        label = "H • A* ROTA SEGURA" if name == "safe" else "J • BFS MENOR ROTA"
        button(surface, buttons[name], label, mouse, session.hint_mode == name, TEAL if name == "safe" else GOLD)
    if path:
        text(surface, f"Rota: {max(0, len(path)-1)} ações  |  custo: {route_cost}", SIDE_X + 20, 606, 12, TEAL, True)
        if session.hint_mode == "short":
            risk = route_risk(level.grid, path, level.turns)
            text(surface, f"Possíveis impactos na BFS: {risk}", SIDE_X + 20, 627, 12, RED if risk else MUTED)
        else:
            text(surface, "A* inclui tempo e risco na decisão", SIDE_X + 20, 627, 11, MUTED)
    else:
        text(surface, "Compare menor distância × menor risco", SIDE_X + 20, 610, 11, MUTED)
    if show_debug:
        text(surface, "f(n)=g(n)+h(n)  |  h=Manhattan", SIDE_X + 20, 658, 11, PURPLE)
    else:
        text(surface, "M: mostrar fórmula matemática", SIDE_X + 20, 658, 11, MUTED)


# Telas que aparecem sobre o jogo
def overlay(surface: pygame.Surface, session: Session, answer: str, mouse: tuple, buttons: dict) -> None:
    """Mostra as telas de inicio, enigma, vitoria ou derrota."""
    if session.state == "playing":
        return
    shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    shade.fill((5, 12, 22, 218))
    surface.blit(shade, (0, 0))
    modal = (260, 175, 680, 400)
    rounded(surface, modal, PANEL, 22, BORDER)
    if session.state == "intro":
        text(surface, "LABIRINTO DOS ENIGMAS", 310, 223, 30, TEAL, True)
        text(surface, "Missão: sair de um ambiente com riscos", 310, 276, 19, WHITE)
        wrap(surface, "Planeje rotas, colete uma credencial, resolva o enigma e evite espinhos, escombros e lasers que alternam a cada turno.", 310, 312, 585, 17, MUTED, 28)
        text(surface, "BFS procura menos passos. A* considera distância + dano.", 310, 407, 15, GOLD)
        button(surface, buttons["primary"], "ENTER  •  INICIAR SIMULAÇÃO", mouse, True)
    elif session.state == "quiz":
        p = PUZZLES[session.level.number - 1]
        text(surface, "VERIFICAÇÃO MATEMÁTICA", 310, 214, 25, PURPLE, True)
        text(surface, p["question"], 310, 277, 22, WHITE, True)
        rounded(surface, (310, 335, 570, 57), PANEL_2, 10, PURPLE)
        text(surface, answer + "|", 329, 349, 23, GOLD, True)
        if session.hint_open:
            wrap(surface, "DICA: " + p["hint"], 312, 413, 560, 16, GOLD, 25)
        else:
            text(surface, "Pressione I para mostrar uma dica.", 312, 416, 16, MUTED)
        wrap(surface, session.message, 312, 461, 560, 14, MUTED, 21)
        text(surface, "ENTER: confirmar    BACKSPACE: apagar", 312, 521, 14, TEAL)
    elif session.state == "cleared":
        text(surface, "ZONA CONCLUÍDA", 310, 230, 32, TEAL, True)
        text(surface, f"Pontuação acumulada: {session.score}", 310, 303, 24, GOLD)
        wrap(surface, "A decisão matemática correta transforma um ambiente complexo em uma rota viável.", 310, 363, 560, 17, MUTED, 28)
        button(surface, buttons["primary"], "ENTER  •  CONTINUAR", mouse, True)
    elif session.state == "lost":
        text(surface, "RISCO CRÍTICO", 310, 230, 32, RED, True)
        wrap(surface, "Sua integridade chegou a zero. Reavalie o caminho: a rota mais curta nem sempre é a mais segura.", 310, 308, 570, 18, MUTED, 30)
        button(surface, buttons["primary"], "R  •  REINICIAR", mouse, True, RED)
    elif session.state == "victory":
        text(surface, "MISSÃO CONCLUÍDA!", 310, 228, 30, TEAL, True)
        text(surface, f"Pontuação final: {session.score}", 310, 305, 25, GOLD, True)
        text(surface, f"Total de impactos: {session.impacts}", 310, 351, 19, WHITE)
        button(surface, buttons["primary"], "R  •  JOGAR NOVAMENTE", mouse, True)


# Loop principal: eventos, atualizacao e desenho
def main() -> int:
    """Recebe comandos do teclado e executa o loop do jogo."""
    pygame.init()
    pygame.key.set_repeat(160, 100)
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Labirinto dos Enigmas | Matematica Computacional")
    clock = pygame.time.Clock()
    session = Session()
    answer = ""
    path: list[tuple[int, int]] = []
    route_cost = -1
    show_debug = False
    seconds = 0.0
    last_hit_at = -DAMAGE_FLASH_MS
    buttons = {"safe": pygame.Rect(SIDE_X + 20, 522, 318, 35), "short": pygame.Rect(SIDE_X + 20, 563, 318, 35), "primary": pygame.Rect(310, 485, 570, 55)}
    moves = {pygame.K_UP: (-1, 0), pygame.K_w: (-1, 0), pygame.K_DOWN: (1, 0), pygame.K_s: (1, 0), pygame.K_LEFT: (0, -1), pygame.K_a: (0, -1), pygame.K_RIGHT: (0, 1), pygame.K_d: (0, 1), pygame.K_SPACE: (0, 0)}
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        now = pygame.time.get_ticks()
        mouse = pygame.mouse.get_pos()
        if session.state in ("playing", "quiz"):
            seconds += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if session.state == "playing":
                    for name in ("safe", "short"):
                        if buttons[name].collidepoint(event.pos):
                            path, route_cost = session.show_route(name)
                elif buttons["primary"].collidepoint(event.pos):
                    if session.state == "intro":
                        session.begin()
                    elif session.state == "cleared":
                        session.next_level()
                    elif session.state in ("lost", "victory"):
                        session.reset()
                        seconds = 0.0
                        last_hit_at = -DAMAGE_FLASH_MS
                    path = []
                continue
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                running = False
                continue
            if event.key == pygame.K_r and session.state != "quiz":
                session.reset()
                path = []
                answer = ""
                seconds = 0.0
                last_hit_at = -DAMAGE_FLASH_MS
                continue
            if session.state == "intro" and event.key == pygame.K_RETURN:
                session.begin()
                continue
            if session.state == "cleared" and event.key == pygame.K_RETURN:
                session.next_level()
                path = []
                continue
            if session.state == "quiz":
                if event.key == pygame.K_i:
                    session.hint_open = True
                elif event.key == pygame.K_BACKSPACE:
                    answer = answer[:-1]
                elif event.key == pygame.K_RETURN:
                    accepted = session.answer(answer)
                    if accepted:
                        answer = ""
                        path = []
                elif event.unicode.isascii() and event.unicode.isdigit() and len(answer) < 8:
                    answer += event.unicode
                continue
            if session.state != "playing":
                continue
            if event.key == pygame.K_h:
                path, route_cost = session.show_route("safe")
            elif event.key == pygame.K_j:
                path, route_cost = session.show_route("short")
            elif event.key == pygame.K_m:
                show_debug = not show_debug
            elif event.key in moves:
                if now - last_hit_at < DAMAGE_FLASH_MS:
                    continue
                action = session.move(moves[event.key])
                if action in ("damage", "lost"):
                    last_hit_at = now
                path = []
        screen.fill(BG)
        for i in range(0, SCREEN_W, 40):
            pygame.draw.line(screen, (14, 27, 42), (i, 0), (i, SCREEN_H), 1)
        text(screen, "LABIRINTO", MAP_X, 31, 32, WHITE, True)
        text(screen, "DOS ENIGMAS", MAP_X + 205, 33, 29, TEAL, True)
        text(screen, "ROTAS DE RISCO  |  MATEMÁTICA COMPUTACIONAL", MAP_X + 2, 83, 13, MUTED, True)
        draw_grid(screen, session, path, session.hint_mode, now, last_hit_at)
        draw_panel(screen, session, path, route_cost, seconds, mouse, buttons, show_debug)
        rounded(screen, (MAP_X - 12, 638, MAP_W + 24, 58), PANEL, 12, BORDER)
        wrap(screen, session.message, MAP_X + 4, 650, MAP_W - 20, 15, GOLD if "RISCO" in session.message else WHITE, 22)
        text(screen, "WASD/SETAS mover    ESPAÇO esperar    H A* seguro    J BFS curto    M fórmula    R reiniciar    ESC sair", 35, 713, 13, MUTED)
        overlay(screen, session, answer, mouse, buttons)
        pygame.display.flip()
    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())