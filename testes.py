"""Testes repetiveis sem Pygame para confiabilidade da modelagem matematica."""

from __future__ import annotations
import unittest
from logica import (
    ROWS, COLS, START, EXIT, PERIOD, MAX_HEALTH,
    PUZZLES, Session, generate_level, bfs, astar, hazard,
    neighbors, safe_neighbors, safe_retreat, manhattan, route_risk, walkable, laser_active,
)


# Testes dos algoritmos, mapas e regras
class TestMath(unittest.TestCase):
    """Testa formulas e algoritmos de caminhos."""
    def test_manhattan(self) -> None:
        """Confere o calculo da distancia Manhattan."""
        self.assertEqual(manhattan((2, 3), (5, 8)), 8)

    def test_cycle(self) -> None:
        """Verifica quando o laser liga e desliga."""
        self.assertEqual([laser_active(t) for t in range(8)], [True, True, False, False] * 2)

    def test_limits(self) -> None:
        """Testa os limites da matriz."""
        grid = [["." for _ in range(COLS)] for _ in range(ROWS)]
        self.assertFalse(walkable(grid, (-1, 1), True))
        self.assertFalse(walkable(grid, (ROWS, 0), True))
        self.assertFalse(walkable(grid, (0, COLS), True))

    def test_astar_temporal(self) -> None:
        """Confere se esperar pode evitar um laser."""
        grid = [["#" for _ in range(COLS)] for _ in range(ROWS)]
        grid[1][1], grid[1][2] = ".", "~"
        path, cost = astar(grid, (1, 1), (1, 2), 0, True)
        self.assertEqual(path, [(1, 1), (1, 1), (1, 2)])
        self.assertEqual(cost, 2)
        self.assertEqual(route_risk(grid, path, 0), 0)

    def test_bfs_vs_astar(self) -> None:
        """Compara o caminho mais curto com o de menor risco."""
        grid = [["#" for _ in range(COLS)] for _ in range(ROWS)]
        for row in (1, 2):
            for col in range(1, 5):
                grid[row][col] = "."
        grid[1][3] = "^"
        short = bfs(grid, (1, 1), (1, 4), True)
        safe, cost = astar(grid, (1, 1), (1, 4), 0, True)
        self.assertEqual(len(short) - 1, 3)
        self.assertEqual(route_risk(grid, short, 0), 1)
        self.assertEqual(route_risk(grid, safe, 0), 0)
        self.assertEqual(cost, len(safe) - 1)
        self.assertGreater(len(safe), len(short))


class TestGeneration(unittest.TestCase):
    """Verifica se os mapas aleatorios podem ser concluidos."""
    def test_500_seeds(self) -> None:
        """Verifica objetivos e recuos em 500 labirintos."""
        for seed in range(500):
            level = generate_level(seed % 3 + 1, seed)
            with self.subTest(seed=seed):
                self.assertEqual(len(level.grid), ROWS)
                self.assertTrue(all(len(row) == COLS for row in level.grid))
                self.assertTrue(bfs(level.grid, START, level.key, False))
                self.assertTrue(bfs(level.grid, level.key, level.puzzle, False))
                self.assertTrue(bfs(level.grid, level.puzzle, EXIT, True))
                self.assertFalse(bfs(level.grid, START, EXIT, False))
                self.assertTrue(all(not hazard(level.grid, p, 0) for p in level.protected))
                self.assertTrue(all(level.grid[p[0]][p[1]] != "R" for p in level.protected))
                self.assertEqual(level.player, START)
                self.assertEqual(level.health, MAX_HEALTH)
                for row in range(ROWS):
                    for col in range(COLS):
                        if level.grid[row][col] in ("^", "~"):
                            self.assertTrue(safe_neighbors(level.grid, (row, col), False))

    def test_reproducibility(self) -> None:
        """Confere a repeticao de mapas com a mesma semente."""
        one = generate_level(2, 1234)
        two = generate_level(2, 1234)
        self.assertEqual(one.grid, two.grid)
        self.assertEqual(one.key, two.key)
        self.assertEqual(one.puzzle, two.puzzle)


class TestSession(unittest.TestCase):
    """Valida as regras, pontuacao e dano do jogador."""
    def test_solve_and_finish(self) -> None:
        """Simula as tres fases e a vitoria final."""
        session = Session()
        session.reset(seed=77)
        for number in range(1, 4):
            self.assertEqual(session.level.number, number)
            for target in (session.level.key, session.level.puzzle):
                route, _ = astar(session.level.grid, session.level.player, target, session.level.turns, session.level.door_open)
                self.assertTrue(route)
                for previous, nxt in zip(route, route[1:]):
                    session.move((nxt[0] - previous[0], nxt[1] - previous[1]))
                    self.assertNotEqual(session.state, "lost")
            self.assertEqual(session.state, "quiz")
            self.assertFalse(session.answer("abc"))
            self.assertFalse(session.answer("999999999"))
            self.assertTrue(session.answer(PUZZLES[number - 1]["answer"]))
            self.assertTrue(session.level.door_open)
            route, _ = astar(session.level.grid, session.level.player, EXIT, session.level.turns, True)
            for previous, nxt in zip(route, route[1:]):
                session.move((nxt[0] - previous[0], nxt[1] - previous[1]))
                self.assertNotEqual(session.state, "lost")
            self.assertEqual(session.state, "cleared")
            session.next_level(seed=77 + number)
        self.assertEqual(session.state, "victory")
        self.assertEqual(session.impacts, 0)
        self.assertGreater(session.score, 0)

    def test_spike_bounces_to_previous_safe_cell(self) -> None:
        """Confere o dano e o recuo ao pisar no espinho."""
        session = Session()
        session.reset(seed=13)
        spike = next((r, c) for r in range(ROWS) for c in range(COLS) if session.level.grid[r][c] == "^")
        before = safe_neighbors(session.level.grid, spike, False)[0]
        session.level.player = before
        session.score = 35
        health = session.level.health
        moves = (spike[0] - before[0], spike[1] - before[1])
        self.assertEqual(session.move(moves), "damage")
        self.assertEqual(session.level.player, before)
        self.assertEqual(session.level.health, health - 1)
        self.assertEqual(session.score, 15)
        self.assertEqual(session.impacts, 1)
        self.assertEqual(session.level.turns, 1)
        self.assertEqual(session.state, "playing")

    def test_active_laser_bounces_but_inactive_does_not(self) -> None:
        """Verifica o dano apenas quando o laser esta ativo."""
        session = Session()
        session.reset(seed=27)
        laser = next((r, c) for r in range(ROWS) for c in range(COLS) if session.level.grid[r][c] == "~")
        safe = safe_neighbors(session.level.grid, laser, False)[0]
        direction = (laser[0] - safe[0], laser[1] - safe[1])
        session.level.player = safe
        session.level.turns = 1
        self.assertEqual(session.move(direction), "step")
        self.assertEqual(session.level.player, laser)
        self.assertEqual(session.move((0, 0)), "step")
        self.assertEqual(session.move((0, 0)), "damage")
        self.assertEqual(session.level.player, safe)
        self.assertEqual(session.level.health, MAX_HEALTH - 1)
        self.assertEqual(session.impacts, 1)

    def test_last_life_reports_loss_after_retreat(self) -> None:
        """Confere a derrota quando acaba a ultima vida."""
        session = Session()
        session.reset(seed=19)
        spike = next((r, c) for r in range(ROWS) for c in range(COLS) if session.level.grid[r][c] == "^")
        safe = safe_neighbors(session.level.grid, spike, False)[0]
        session.level.player = safe
        session.level.health = 1
        self.assertEqual(session.move((spike[0] - safe[0], spike[1] - safe[1])), "lost")
        self.assertEqual(session.level.health, 0)
        self.assertEqual(session.level.player, safe)
        self.assertEqual(session.state, "lost")

    def test_retreat_rejects_neighboring_hazards(self) -> None:
        """Impede que o recuo termine em outro perigo."""
        grid = [["#" for _ in range(COLS)] for _ in range(ROWS)]
        grid[1][1] = "~"
        grid[1][2] = "^"
        grid[2][2] = "."
        self.assertEqual(safe_retreat(grid, (1, 2), (1, 1), False), (2, 2))

    def test_invalid_actions(self) -> None:
        """Rejeita movimentos e respostas invalidas."""
        session = Session()
        session.reset(seed=9)
        original = session.level.player
        self.assertEqual(session.move((3, 3)), "invalid")
        self.assertEqual(session.level.player, original)
        self.assertEqual(session.level.turns, 0)
        self.assertFalse(session.answer("32"))


if __name__ == "__main__":
    unittest.main()