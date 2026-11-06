# Labirinto dos Enigmas: Rotas de Risco

**Trabalho A03 — Matemática Computacional Aplicada / Lógica e Algoritmos**  
**Professor:** Daniel Henrique Matos de Paiva  
**Estudante:** Luiz Henrique Cordeiro dos Santos — **RA:** 326122345  
**Equipe:** preencher os nomes e RAs dos demais integrantes antes da entrega (enunciado: 3 a 5 alunos).

> Um jogo em **Python e Pygame** que transforma o planejamento de deslocamento seguro em um problema de grafos, matrizes, lógica proposicional e otimização. **Não usa Portugol**.

**Visualização do mapa e comparação das rotas:** disponíveis no pacote ZIP completo, na pasta `assets/`.

## Problema do mundo real

Em galpões, oficinas e áreas de manutenção, deslocar-se do ponto de entrada até um destino exige considerar **obstruções**, **materiais cortantes**, **máquinas com funcionamento cíclico** e **restrições de acesso**. A rota mais curta nem sempre tem o menor risco. O jogo simula esse problema de forma **didática**: entulhos são bloqueios, espinhos representam objetos perfurantes, lasers representam risco temporal de máquina, chave/enigma simulam duas condições de autorização. O simulador **não é sistema certificado para segurança ou evacuação real**.

## Instalação e execução (Windows, Linux ou macOS)

Requer **Python 3.11+**. Abra o terminal na pasta do repositório:

```bash
python -m pip install -r requirements.txt
python jogo.py
```

Se seu Windows usa `py` em vez de `python`, execute `py -m pip install -r requirements.txt` e `py jogo.py`.

### Controles

| Comando | Ação |
|---|---|
| **Setas / WASD** | Mover uma célula por turno |
| **Espaço** | Esperar um turno (útil para evitar laser ativo) |
| **H** | A* temporal: rota de custo ponderado mínimo |
| **J** | BFS: rota mais curta em número de passos |
| **M** | Mostrar fórmula heurística no painel |
| **I** | Exibir dica quando o enigma estiver aberto |
| **Enter** | Iniciar, confirmar resposta ou avançar |
| **Backspace** | Apagar um dígito da resposta |
| **R** | Reiniciar (fora do enigma) |
| **Esc** | Sair |

Os botões do painel permitem selecionar BFS e A* com mouse.

## Elementos do mapa

| Célula | Significado | Regra |
|---|---|---|
| `#` | Parede | Não transitável |
| `.` | Piso | Transitável |
| `R` | Entulho | Não transitável |
| `^` | Espinhos | Ao entrar, perde 1 vida e 20 pontos; pisca em vermelho e recua para casa vizinha segura |
| `~` | Laser | Quando ativo (`turno % 4 ∈ {0, 1}`), aplica o mesmo dano e recuo; desligado pode ser atravessado |
| `K` | Chave/credencial | +40 pontos |
| `E` | Enigma | +80 pontos se correta |
| `D` | Porta | Abre somente com chave **E** enigma resolvido |
| `S` | Saída | +120 pontos e avança fase |

Cada fase começa com 4 vidas. Dica de rota custa 5 pontos, no máximo uma vez por fase. O desafio possui 3 fases progressivas e pontuação máxima sem penalidades de **720 pontos** (240 por fase).

### Nova mecânica: dano, recuo e piscada vermelha

Ao **entrar em espinhos** ou entrar/esperar em um **laser ativo**, o personagem perde **1 vida e 20 pontos** e é deslocado **imediatamente para uma casa ortogonal vizinha segura**. O algoritmo prioriza a **casa anterior**, desde que não seja um perigo; se o jogador estava parado sobre um laser que ligou, escolhe outro refúgio lateral (prefere piso livre). O personagem pisca entre azul e **vermelho por 850 ms**, com um curto bloqueio dos movimentos durante a animação para impedir que uma tecla segurada provoque vários danos em sequência. O cronômetro visual não altera os turnos discretos do laser.

Na **geração do labirinto**, cada espinho e laser deve possuir **ao menos um vizinho transitável sem perigos**, mesmo que os lasers estejam desligados. Se um novo obstáculo deixaria um perigo cercado, sua instalação é desfeita. Isso evita recuo para outra armadilha. Existe ainda uma busca BFS defensiva para localizar uma casa segura mais distante em mapas modificados manualmente que violem a garantia de vizinhança.

**Regra matemática de adjacência segura:** dado o local do impacto `p=(r,c)`, o conjunto de refúgios `Nₛ(p)` reúne células transitáveis `q` tais que `|qᵣ-r| + |q꜀-c| = 1` e `A[q] ∉ {^,~}`. Nos mapas gerados, `Nₛ(p) ≠ ∅` para todo perigo. Esta regra é separada do cálculo de custo do A*: as rotas planejadas ainda são estimativas com penalidade de risco, não uma simulação de todos os recuos.

## Matemática Computacional aplicada

**1. Matrizes:** o mapa é uma matriz `15 × 23` (`A ∈ Σ^(15×23)`); cada célula é indexada por `(linha, coluna)`.

**2. Teoria dos grafos:** todo corredor é um vértice `v ∈ V`; movimentos ortogonais são arestas `E`. `G=(V,E)`, com até quatro vizinhos por vértice, e uma aresta de esperar no grafo temporal.

**3. Busca em profundidade (DFS):** uma pilha LIFO gera os corredores com retrocesso. A árvore de corredores resultante é conectada; a porta é colocada num ponto articulador antes das aberturas extras. Algumas paredes são removidas sem criar passagem que contorne a porta.

**4. Busca em largura (BFS):** uma fila FIFO percorre vértices por níveis e fornece um caminho com **mínimo de movimentos**, sem levar em consideração o dano das células.

**5. Busca A* com tempo discreto:** estados são `(linha, coluna, turno mod 4)`, incluindo a ação de esperar. O custo de uma transição é `c = 1 + 18·I(risco na chegada)`. O algoritmo minimiza `J(π) = Σ c` usando `f(n)=g(n)+h(n)` e heurística admissível Manhattan `h(n)=|r-r_alvo|+|c-c_alvo|`.

**6. Lógica proposicional:** `PORTA_ABERTA = TEM_CHAVE ∧ ENIGMA_RESOLVIDO`. A conjunção só é verdadeira quando as duas condições são satisfeitas.

**7. Aritmética modular:** o laser está ativo se `turno mod 4` é 0 ou 1; esperar ou escolher outra rota altera o instante de chegada.

**8. Invariantes e conjuntos:** os caminhos para a credencial, o enigma e a saída são protegidos durante a colocação de perigos. A porta separa regiões conexas antes do desbloqueio. Geração usa `set` para operações de pertinência, união e áreas alcançáveis.

**Exemplo de trade-off:** caminho curto com 3 ações e 1 espinho custa `3+18=21`. Um desvio de 5 ações sem risco custa `5`. A* seleciona o desvio; BFS seleciona o percurso de 3 passos.

## Como o código foi organizado

| Arquivo | Responsabilidade |
|---|---|
| [`jogo.py`](jogo.py) | Interface, desenho Pygame, teclado, modal, animação e HUD |
| [`src/logica.py`](src/logica.py) | Matriz, geração DFS, BFS, A* temporal, regras, validações e pontuação |
| [`tests/test_logica.py`](tests/test_logica.py) | Testes determinísticos, situações de risco e 500 mapas com sementes |
| [`docs/GUIA_LINHA_A_LINHA.md`](docs/GUIA_LINHA_A_LINHA.md) | Explicação numerada de cada linha de código Python |
| `docs/RELATORIO_PROJETO.docx` (no ZIP completo) | Documento descritivo acadêmico em Word |
| `slides/APRESENTACAO_PROJETO.pptx` (no ZIP completo) | Apresentação PowerPoint para defesa de 10 a 15 minutos |

O código Python contém comentários **linha a linha** nas instruções significativas. O guia complementar apresenta **cada linha numerada**, inclusive importações, decoradores, controles e chamadas gráficas.


### Materiais finais (pacote ZIP)

O **pacote completo do projeto**, distribuído junto à entrega acadêmica, contém o código-fonte, as imagens, o relatório editável (`.docx`), o relatório em PDF e os slides (`.pptx`). **Os arquivos binários de Word/PowerPoint/PDF não estão presentes nesta branch GitHub**; eles são fornecidos no ZIP de entrega para download. Os arquivos `.md` do repositório contêm as explicações matemáticas e a documentação linha por linha.

## Testes e verificação

```bash
python -m unittest discover -s tests -v
python -m compileall -q jogo.py src tests
```

Casos incluem: 500 sementes de mapas, presença de rota para cada etapa, porta obrigatória, rota protegida sem obstáculos, **refúgio adjacente para cada perigo**, impacto/recuo de espinho e laser, laser desligado, perda da última vida, reprodutibilidade, limites da matriz, laser modular, BFS vs A*, espera temporal, validação de respostas e conclusão de 3 fases.

> Observação de ambiente: a lógica pode ser testada sem Pygame; a biblioteca gráfica é exigida para abrir a janela. Validar também a execução com janela e teclado no computador de apresentação.

## Roteiro de apresentação

- **1–2 min:** problema real, objetivo e elementos do jogo.
- **3–4 min:** matriz, grafo, DFS, BFS e A* temporal.
- **2 min:** lógica proposicional, aritmética modular e custo de risco.
- **2–4 min:** demonstração com espinhos/laser e comparação de rotas.
- **1–2 min:** resultados dos testes, limites e melhorias.

## Limitações e extensões

O modelo usa pesos didáticos fixos, movimentação discreta, quatro direções e sensores perfeitos. Ele não modela geometria contínua, probabilidade de falha, múltiplas pessoas ou protocolos industriais reais. Futuras extensões: estimativa de probabilidade de risco, Dijkstra como baseline, multiagentes, comparação experimental com métricas e registros de telemetria.

## Créditos

Projeto acadêmico para o professor **Daniel Henrique Matos de Paiva**, disciplina de **Matemática Computacional Aplicada**. Baseado no jogo anterior “Labirinto dos Enigmas”, expandido para modelar avaliação de risco e caminhos alternativos.