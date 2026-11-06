# Fundamentos matemáticos do Labirinto dos Enigmas: Rotas de Risco

## 1. Problema formal

Dado um ambiente discretizado em 15 linhas por 23 colunas, encontrar uma sequência de ações entre a entrada e a saída que satisfaça restrições lógicas de autorização e minimize custo total de deslocamento mais penalidade de perigos. Cada deslocamento altera o estado da posição; esperar não altera a posição, mas altera o instante de chegada em relação aos lasers.

As observações de galpão industrial são uma **analogia pedagógica**, e não um modelo validado para tomar decisões de segurança real.

## 2. Matriz e coordenadas

`A ∈ Σ^(15×23)`, em que `Σ={#,.,R,^,~,K,E,D,S}`; posição `p=(i,j)` com `0≤i<15` e `0≤j<23`. A função `inside` preserva os limites. O Pygame transforma uma coordenada discreta em centro de pixel por `x=MAP_X+32·j+16`, `y=MAP_Y+32·i+16`.

## 3. Grafo espacial

`G=(V,E)`, sendo `V` o conjunto de células transitáveis e `E={(u,v): ||u-v||₁=1}`, sujeito à porta. A norma `L1` é Manhattan: `d₁((r,c),(u,v))=|r-u|+|c-v|`. Os vértices possuem grau ≤4. Uma porta fechada elimina temporariamente o vértice do grafo acessível.

A geração DFS iterativa com pilha de posições impõe conexidade e inicialmente não cria ciclos. A função `_open_loops` introduz arestas alternativas dentro das duas regiões separadas pela porta, sem ligá-las indevidamente. Isso viabiliza escolhas de rota.

## 4. Busca em profundidade (DFS)

Mantemos uma pilha LIFO. Para a célula atual, embaralhamos as quatro direções, tentamos avançar duas células e removemos a parede intermediária. Se nenhuma direção funciona, retiramos o topo (retrocesso). O número de operações é linear em vértices e arestas do mapa, `O(|V|+|E|)`, na modelagem por adjacência.

## 5. Busca em largura (BFS)

BFS usa uma fila FIFO e um dicionário `parent`. Primeiro descobre os nós a distância 1, depois 2, depois 3. Em grafo não ponderado, o primeiro encontro do alvo fornece distância mínima em arestas. Tempo `O(|V|+|E|)` e espaço `O(|V|)`.

A BFS não considera dano: o menor caminho em passos pode passar por espinhos.

## 6. A* com tempo discreto

O estado expandido é `s=(v,τ)`, com `τ=t mod 4` e `v∈V`. Ações permitidas: andar ortogonalmente ou esperar. Cada ação incrementa `τ` em 1 (módulo 4). A função de risco `ρ(v,τ)` vale 1 para espinhos, 1 para laser nos instantes 0 ou 1 do ciclo, e 0 em outros casos.

Custo de aresta: `c(s,s') = 1 + 18·ρ(v',τ')`. Função objetivo: `J(π)=∑_(a∈π) c(a)`; custo sempre positivo e finito. A* escolhe estados com menor `f(s)=g(s)+h(s)`, onde `g` é o custo acumulado e `h` é a distância Manhattan restante. Como cada ação custa ao menos 1 e um deslocamento altera Manhattan em no máximo 1, `h` não superestima o custo real e é admissível; a primeira solução encontrada com a fila de prioridade implementada é ótima para este custo.

**Importante:** o risco é uma **penalidade fixa por contato**, não uma probabilidade estatística. O termo temporal tem no máximo `4·|V|` estados. O custo fixo 18 serve para tornar uma rota sem dano mais atrativa mesmo que use alguns passos extras; não garante ausência de dano se não houver alternativa.

## 7. Proposição de acesso

Seja `K∈{0,1}` o estado de ter chave e `Q∈{0,1}` o estado de enigma resolvido. A porta está aberta se e somente se `D=K∧Q`.

| K | Q | D = K ∧ Q |
|---:|---:|---:|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

Na implementação, o enigma exige primeiro a chave, reforçando o protocolo de duas etapas.

## 8. Conjuntos, conectividade e invariantes

Antes de posicionar obstáculos, calculamos um caminho da entrada até K, de K a E e de E até S. A união destes conjuntos forma `P = P₁ ∪ P₂ ∪ P₃`. A colocação de espinhos, lasers e entulho usa apenas as células de `V \ P`. Assim, existe pelo menos um percurso sem risco em cada trecho obrigatório.

Verificamos programaticamente `BFS(início,K)` e `BFS(K,E)` com porta fechada e `BFS(E,saída)` com porta aberta, além de `BFS(início,saída)=∅` com a porta fechada. Essas propriedades evitam mapas impossíveis ou portas inúteis.

## 9. Modelagem do impacto e do recuo seguro

Um contato com espinho (`^`) ou laser ativo (`~` no turno de chegada) decrementa a integridade e a pontuação: `vidas' = vidas - 1` e `pontos' = max(0, pontos - 20)`.

Ao sofrer dano na célula `p=(r,c)`, definimos o conjunto `N_s(p) = {q ∈ V : ||q-p||₁ = 1, A[q] ∉ {^,~}}`, usando a transitabilidade da porta no estado atual. O recuo prefere a posição de origem `q_anterior ∈ N_s(p)`; caso não pertença ao conjunto, escolhe uma alternativa adjacente livre de perigo. Quando `N_s(p)` é vazio apenas em um **mapa manualmente modificado**, a defesa do código recorre à BFS para encontrar uma célula segura mais distante.

Durante a geração do mapa, cada novo perigo é validado para preservar `∀p ∈ H, |N_s(p)| ≥ 1`, em que `H` é o conjunto de espinhos e lasers. Se o novo perigo eliminaria o último refúgio de um risco existente, o programa desfaz a alteração. A garantia vale para os mapas oficiais mesmo antes de a porta ser aberta.

No Pygame, um evento `damage` inicia uma animação visual vermelha por **850 milissegundos**, alternando cores em intervalos de 105 ms. Nesse intervalo a entrada de movimento fica brevemente suspensa, protegendo contra múltiplos impactos causados pela repetição automática da mesma tecla. A animação ocorre em tempo real e não avança o relógio de turnos dos lasers.

**Limitação do planejador:** BFS/A* calculam custos de atravessar perigos, mas não inserem o recuo na transição do estado planejado; o caminho seguro tende a evitar riscos, enquanto uma rota curta passando por perigo pode exigir novo planejamento após a colisão.

## 10. Exemplo de otimização

Considere dois caminhos hipotéticos:

- `P_curto`: 3 ações, 1 contato com espinho ⇒ `J=3+18·1=21`.
- `P_seguro`: 5 ações, 0 contatos ⇒ `J=5+18·0=5`.

A BFS prefere `P_curto`, pois minimiza apenas passos. A* prefere `P_seguro`, pois minimiza o custo ponderado. Em lasers, A* pode preferir **esperar** 1 turno e entrar em seguida quando o perigo estiver desativado.

## 11. Sequências e recorrências

Os desafios utilizam crescimento geométrico (`2,4,8,16,32`), recorrência de Fibonacci (`1,1,2,3,5,8`) e quadrados perfeitos (`1²,2²,3²,4²,5²`). A validação utiliza comparação de strings numéricas sem executar expressões arbitrárias.

## 12. Qualidade, testes e limites

São testados 500 labirintos pseudoaleatórios por semente, além de propriedades lógicas e cenários de roteamento. Isso verifica invariantes nas amostras testadas, mas **não é prova matemática** de correção universal. O modelo abstrai dinâmica industrial e não deve orientar movimentação real em ambientes perigosos.