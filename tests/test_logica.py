"""Testes repetiveis sem Pygame para confiabilidade da modelagem matematica."""

from __future__ import annotations  # Permite anotacoes padronizadas.
import unittest  # Biblioteca de testes ja incluida no Python.
from src.logica import (  # Componentes logicos testados sem abrir janela.
    ROWS, COLS, START, EXIT, PERIOD, MAX_HEALTH,  # Constantes do grafo.
    PUZZLES, Session, generate_level, bfs, astar, hazard,  # Funcoes e objetos testados.
    neighbors, safe_neighbors, safe_retreat, manhattan, route_risk, walkable, laser_active,  # Auxiliares e mecanica de recuo.
)  # Fim do conjunto de importacoes.


class TestMath(unittest.TestCase):  # Testa formulas discretas independentes do jogo.
    def test_manhattan(self) -> None:  # Distancia usa norma L1.
        self.assertEqual(manhattan((2, 3), (5, 8)), 8)  # |2-5| + |3-8| = 8.

    def test_cycle(self) -> None:  # Testa modulo 4 dos lasers.
        self.assertEqual([laser_active(t) for t in range(8)], [True, True, False, False] * 2)  # Metade ativa.

    def test_limits(self) -> None:  # Confere que movimento nao acessa fora dos limites.
        grid = [["." for _ in range(COLS)] for _ in range(ROWS)]  # Grade aberta para isolar fronteira.
        self.assertFalse(walkable(grid, (-1, 1), True))  # Linha negativa bloqueada.
        self.assertFalse(walkable(grid, (ROWS, 0), True))  # Linha acima do maximo.
        self.assertFalse(walkable(grid, (0, COLS), True))  # Coluna acima do maximo.

    def test_astar_temporal(self) -> None:  # Esperar evita risco temporario quando e vantajoso.
        grid = [["#" for _ in range(COLS)] for _ in range(ROWS)]  # Grade fechada.
        grid[1][1], grid[1][2] = ".", "~"  # Corredor com um laser no destino.
        path, cost = astar(grid, (1, 1), (1, 2), 0, True)  # Inicio em fase 0.
        self.assertEqual(path, [(1, 1), (1, 1), (1, 2)])  # Aguarda para entrar no turno 2.
        self.assertEqual(cost, 2)  # Dois turnos sem penalidade.
        self.assertEqual(route_risk(grid, path, 0), 0)  # Sem contato com laser ativo.

    def test_bfs_vs_astar(self) -> None:  # Compara distancia geometrica e seguranca.
        grid = [["#" for _ in range(COLS)] for _ in range(ROWS)]  # Grade isolada.
        for row in (1, 2):  # Duas linhas acessiveis para o desvio.
            for col in range(1, 5):  # Quatro colunas de conexao.
                grid[row][col] = "."  # Libera um retangulo conectado.
        grid[1][3] = "^"  # Adiciona espinhos ao caminho curto.
        short = bfs(grid, (1, 1), (1, 4), True)  # Caminho com tres passos.
        safe, cost = astar(grid, (1, 1), (1, 4), 0, True)  # Minimiza custo com risco.
        self.assertEqual(len(short) - 1, 3)  # BFS escolhe distancia geometrica.
        self.assertEqual(route_risk(grid, short, 0), 1)  # BFS nao foge dos espinhos.
        self.assertEqual(route_risk(grid, safe, 0), 0)  # A* evita espinhos.
        self.assertEqual(cost, len(safe) - 1)  # Sem danos, o custo soma apenas passos.
        self.assertGreater(len(safe), len(short))  # A rota segura pode ser mais longa.


class TestGeneration(unittest.TestCase):  # Valida muitas geracoes aleatorias.
    def test_500_seeds(self) -> None:  # Testa reproducibilidade e invariantes.
        for seed in range(500):  # Repeticao para detectar mapas raros impossiveis.
            level = generate_level(seed % 3 + 1, seed)  # Fases 1 a 3 com seeds diferentes.
            with self.subTest(seed=seed):  # Identifica exatamente o seed quando houver erro.
                self.assertEqual(len(level.grid), ROWS)  # Quantidade correta de linhas.
                self.assertTrue(all(len(row) == COLS for row in level.grid))  # Quantidade de colunas.
                self.assertTrue(bfs(level.grid, START, level.key, False))  # Chave disponivel.
                self.assertTrue(bfs(level.grid, level.key, level.puzzle, False))  # Enigma disponivel.
                self.assertTrue(bfs(level.grid, level.puzzle, EXIT, True))  # Saida apos abertura.
                self.assertFalse(bfs(level.grid, START, EXIT, False))  # Porta realmente impede passagem.
                self.assertTrue(all(not hazard(level.grid, p, 0) for p in level.protected))  # Rota reservada sem perigo.
                self.assertTrue(all(level.grid[p[0]][p[1]] != "R" for p in level.protected))  # Sem entulho na rota.
                self.assertEqual(level.player, START)  # Jogador inicial consistente.
                self.assertEqual(level.health, MAX_HEALTH)  # Integridade restaurada.
                for row in range(ROWS):  # Varre a matriz para conferir o novo invariante de seguranca.
                    for col in range(COLS):  # Analisa cada celula de todos os mapas pseudoaleatorios.
                        if level.grid[row][col] in ("^", "~"):  # Espinhos e lasers devem permitir recuo.
                            self.assertTrue(safe_neighbors(level.grid, (row, col), False))  # Pelo menos uma casa adjacente sempre segura.

    def test_reproducibility(self) -> None:  # Mesma seed gera mesma configuracao.
        one = generate_level(2, 1234)  # Primeira geracao.
        two = generate_level(2, 1234)  # Geracao repetida.
        self.assertEqual(one.grid, two.grid)  # Matriz identica na mesma seed.
        self.assertEqual(one.key, two.key)  # Chave na mesma posicao.
        self.assertEqual(one.puzzle, two.puzzle)  # Enigma na mesma posicao.


class TestSession(unittest.TestCase):  # Verifica maquina de estados e tratamento de erro.
    def test_solve_and_finish(self) -> None:  # Executa as tres fases sem Pygame.
        session = Session()  # Nova sessao logica.
        session.reset(seed=77)  # Mapa inicial reproduzivel.
        for number in range(1, 4):  # Percorre fases numeradas de 1 a 3.
            self.assertEqual(session.level.number, number)  # Confere fase ativa.
            for target in (session.level.key, session.level.puzzle):  # Primeiro chave; depois enigma.
                route, _ = astar(session.level.grid, session.level.player, target, session.level.turns, session.level.door_open)  # Rota com risco.
                self.assertTrue(route)  # Caminho deve existir.
                for previous, nxt in zip(route, route[1:]):  # Percorre cada aresta, incluindo espera.
                    session.move((nxt[0] - previous[0], nxt[1] - previous[1]))  # Movimento ortogonal permitido.
                    self.assertNotEqual(session.state, "lost")  # Rota segura nao pode causar derrota.
            self.assertEqual(session.state, "quiz")  # Enigma foi alcancado.
            self.assertFalse(session.answer("abc"))  # Resposta nao numerica rejeitada.
            self.assertFalse(session.answer("999999999"))  # Entrada excessiva rejeitada.
            self.assertTrue(session.answer(PUZZLES[number - 1]["answer"]))  # Resposta da fase correta.
            self.assertTrue(session.level.door_open)  # AND de condicoes habilita porta.
            route, _ = astar(session.level.grid, session.level.player, EXIT, session.level.turns, True)  # Busca ate saida.
            for previous, nxt in zip(route, route[1:]):  # Caminha pela rota escolhida.
                session.move((nxt[0] - previous[0], nxt[1] - previous[1]))  # Executa um turno por acao.
                self.assertNotEqual(session.state, "lost")  # Sem danos letais na rota segura.
            self.assertEqual(session.state, "cleared")  # Saida conquistada.
            session.next_level(seed=77 + number)  # Avanca ou vence apos a terceira.
        self.assertEqual(session.state, "victory")  # Verifica condicao de finalizacao.
        self.assertEqual(session.impacts, 0)  # Roteamento ponderado eliminou impactos.
        self.assertGreater(session.score, 0)  # Jogador acumulou pontos.

    def test_spike_bounces_to_previous_safe_cell(self) -> None:  # Verifica dano e recuo imediato apos espinho.
        session = Session()  # Cria sessao independente de testes anteriores.
        session.reset(seed=13)  # Usa seed deterministica que contem espinhos.
        spike = next((r, c) for r in range(ROWS) for c in range(COLS) if session.level.grid[r][c] == "^")  # Encontra espinho real no mapa.
        before = safe_neighbors(session.level.grid, spike, False)[0]  # Seleciona uma casa lateral sem riscos.
        session.level.player = before  # Coloca jogador no corredor vizinho ao espinho.
        session.score = 35  # Permite conferir desconto de vinte pontos.
        health = session.level.health  # Guarda quantidade de vidas anterior ao contato.
        moves = (spike[0] - before[0], spike[1] - before[1])  # Calcula deslocamento ortogonal unitario.
        self.assertEqual(session.move(moves), "damage")  # Espinho retorna evento de animacao.
        self.assertEqual(session.level.player, before)  # O personagem retorna uma casa ao corredor seguro.
        self.assertEqual(session.level.health, health - 1)  # Desconta exatamente uma vida.
        self.assertEqual(session.score, 15)  # Desconta vinte pontos sem alterar bonus.
        self.assertEqual(session.impacts, 1)  # Colisao e contabilizada uma vez.
        self.assertEqual(session.level.turns, 1)  # Movimento com dano tambem conta como turno.
        self.assertEqual(session.state, "playing")  # Com vidas restantes a partida continua.

    def test_active_laser_bounces_but_inactive_does_not(self) -> None:  # Diferencia ativacao temporal do laser.
        session = Session()  # Sessao isolada para testar aritmetica modular.
        session.reset(seed=27)  # Gera um mapa reproducivel com lasers.
        laser = next((r, c) for r in range(ROWS) for c in range(COLS) if session.level.grid[r][c] == "~")  # Seleciona laser real.
        safe = safe_neighbors(session.level.grid, laser, False)[0]  # Posicao lateral sem risco.
        direction = (laser[0] - safe[0], laser[1] - safe[1])  # Vetor de aproximacao ao laser.
        session.level.player = safe  # Prepara primeiro contato a partir da casa segura.
        session.level.turns = 1  # Proximo movimento no turno 2: laser desligado.
        self.assertEqual(session.move(direction), "step")  # Laser desligado permite atravessar sem dano.
        self.assertEqual(session.level.player, laser)  # Jogador permanece na casa do laser desligado.
        self.assertEqual(session.move((0, 0)), "step")  # Espera turno 3 sem dano.
        self.assertEqual(session.move((0, 0)), "damage")  # No turno 4, laser ativo provoca dano.
        self.assertEqual(session.level.player, safe)  # Risco ao esperar empurra para um vizinho seguro.
        self.assertEqual(session.level.health, MAX_HEALTH - 1)  # Laser causa somente um impacto.
        self.assertEqual(session.impacts, 1)  # Nenhum dano extra quando estava desligado.

    def test_last_life_reports_loss_after_retreat(self) -> None:  # O recuo tambem funciona ao perder a ultima vida.
        session = Session()  # Instancia modelo sob teste.
        session.reset(seed=19)  # Gera mapa com espinhos e pisos.
        spike = next((r, c) for r in range(ROWS) for c in range(COLS) if session.level.grid[r][c] == "^")  # Seleciona risco.
        safe = safe_neighbors(session.level.grid, spike, False)[0]  # Define refugio lateral.
        session.level.player = safe  # Parte de local livre de riscos.
        session.level.health = 1  # Resta uma unica vida.
        self.assertEqual(session.move((spike[0] - safe[0], spike[1] - safe[1])), "lost")  # Impacto final encerra a sessao.
        self.assertEqual(session.level.health, 0)  # Vida nunca fica negativa.
        self.assertEqual(session.level.player, safe)  # Recuo para casa segura ainda e aplicado.
        self.assertEqual(session.state, "lost")  # Estado passa a derrota.

    def test_retreat_rejects_neighboring_hazards(self) -> None:  # Nunca empurra o jogador para espinho ou outro laser.
        grid = [["#" for _ in range(COLS)] for _ in range(ROWS)]  # Grade artificial para isolar colisao.
        grid[1][1] = "~"  # Casa de origem e um laser (naquele instante desligado).
        grid[1][2] = "^"  # Casa do impacto e um espinho.
        grid[2][2] = "."  # Refugio valido em outra direcao ortogonal.
        self.assertEqual(safe_retreat(grid, (1, 2), (1, 1), False), (2, 2))  # Nunca escolhe laser como casa segura.

    def test_invalid_actions(self) -> None:  # Limites e entradas nao mudam a partida indevidamente.
        session = Session()  # Cria sessao independente.
        session.reset(seed=9)  # Define fase conhecida.
        original = session.level.player  # Guarda posicao para comparacao.
        self.assertEqual(session.move((3, 3)), "invalid")  # Movimento diagonal invalido.
        self.assertEqual(session.level.player, original)  # Protege a posicao do jogador.
        self.assertEqual(session.level.turns, 0)  # Entrada invalida nao avanca o turno.
        self.assertFalse(session.answer("32"))  # Nao responde sem modal aberto.


if __name__ == "__main__":  # Permite rodar diretamente como script de teste.
    unittest.main()  # Descobre e executa os casos escritos acima.