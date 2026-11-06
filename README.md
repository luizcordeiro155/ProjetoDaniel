# Labirinto dos Enigmas: Rotas de Risco

**Trabalho A03 - Matemática Computacional Aplicada**  
**Professor:** Daniel Henrique Matos de Paiva  
**Integrantes do grupo:**

- **Lucas Gabriel Dias Costa** — RA **326124418**
- **João Guilherme Machado Ferreira** — RA **326128074**
- **Luiz Henrique Cordeiro dos Santos** — RA **326122345**

Projeto acadêmico desenvolvido em **Python com Pygame**. O objetivo é atravessar um labirinto, coletar uma chave, resolver um desafio matemático e chegar a saída, evitando espinhos, entulhos e lasers.

## Problema do mundo real

Em locais como oficinas e galpões, o caminho mais curto nem sempre é o mais seguro: podem existir obstáculos, materiais cortantes ou máquinas que ligam e desligam. O jogo apresenta uma simulação simplificada desse problema e permite comparar **distância** e **risco** ao escolher uma rota. Não é um aplicativo real de segurança industrial.

## Como instalar e jogar

Instale o **Python 3.13** e abra o terminal na pasta onde está `jogo.py`.

```powershell
python -m pip install -r requirements.txt
python jogo.py
```

Se houver várias versões do Python instaladas no Windows, selecione o Python 3.13 no VS Code ou execute o jogo com o caminho completo desse interpretador.

| Tecla | Função |
| --- | --- |
| Setas / WASD | Movimentar o personagem |
| Espaço | Esperar um turno para o laser mudar de estado |
| H | Mostrar rota A* (menos risco) |
| J | Mostrar rota BFS (menos passos) |
| M | Mostrar informações da fórmula A* |
| I | Mostrar dica do enigma |
| Enter | Começar, responder ou avançar |
| R | Reiniciar o jogo |
| Esc | Sair |

## Como o jogo funciona

O mapa é criado automaticamente e possui três fases. O jogador começa com **4 vidas por fase**.

- **Espinho (^):** causa 1 vida e retira 20 pontos da pontuação.
- **Laser (~):** causa o mesmo dano quando está ligado; quando desligado pode ser atravessado.
- **Entulho (R) e parede (#):** impedem o movimento.
- **Chave (K):** vale 40 pontos.
- **Enigma (E):** vale 80 pontos quando respondido corretamente.
- **Porta (D):** abre apenas com a chave e o enigma resolvido.
- **Saída (S):** vale 120 pontos e conclui a fase.

Ao tocar em um espinho ou laser ativo, o personagem **pisca em vermelho por 850 ms e recua automaticamente para uma casa segura**. A casa anterior tem prioridade, mas o programa verifica se ela não possui perigos. A geração dos mapas evita perigos sem pelo menos uma casa segura ao lado.

## Relação com Matemática Computacional

| Conceito | Aplicação no jogo |
| --- | --- |
| **Matrizes** | O labirinto é uma matriz de 15 linhas por 23 colunas. |
| **Grafos** | As casas são vértices e os deslocamentos são arestas. |
| **DFS (profundidade)** | Gera os corredores do labirinto usando pilha e retrocesso. |
| **BFS (largura)** | Encontra o trajeto com menos passos. |
| **A*** | Busca um trajeto de menor custo, considerando distância e perigo. |
| **Lógica booleana** | A porta abre apenas quando `tem_chave AND enigma_resolvido`. |
| **Aritmética modular** | O laser liga e desliga de acordo com `turno % 4`. |
| **Conjuntos** | O sistema verifica casas acessiveis e locais seguros. |

O custo usado no A* é calculado por:

`custo = 1 + 18 * risco`

O valor `risco` é 1 se a casa for perigosa no turno da chegada, ou 0 caso contrário. A heurística usa a **distância Manhattan**:

`h = abs(linha_atual - linha_final) + abs(coluna_atual - coluna_final)`

**Exemplo:** um caminho de 3 passos com um perigo custa `3 + 18 = 21`. Um caminho de 5 passos sem perigo custa `5`. Por isso, o caminho de menor risco pode ser mais longo que o caminho escolhido pelo BFS.

## Arquivos do projeto

```text
ProjetoDaniel/
  jogo.py           # Interface visual em Pygame
  logica.py         # Regras e algoritmos matematicos
  testes.py         # Testes automáticos do jogo
  requirements.txt  # Biblioteca necessária
  README.md         # Explicação do projeto
  .gitignore        # Ignora arquivos temporários do Python
```

Cada função possui uma explicação curta no início; os comentários de cada linha foram removidos para facilitar a leitura.

## Como testar

```powershell
python -m unittest testes -v
```

Os testes verificam os cálculos matemáticos, 500 mapas aleatórios, colisão com espinhos, laser ligado e desligado, retorno a casa segura e conclusão das três fases.

**Observação:** os testes automáticos nao substituem a verificação visual do jogo em um computador com Pygame instalado.

## Apresentação

Na apresentação, explique o problema real, mostre a matriz do mapa, descreva DFS e BFS, compare as rotas do A* e demonstre o dano e o recuo seguro. O projeto é didático e aplica conhecimentos de matemática computacional e lógica de programação.