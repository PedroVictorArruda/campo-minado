# Modelagem PEAS e ambiente

## PEAS

| Elemento | Descrição |
|---|---|
| **Desempenho (Performance)** | Vencer a partida (abrir todas as células sem mina). Métricas secundárias: proporção de células seguras abertas, número de chutes (jogadas sem certeza lógica), tempo por jogada. |
| **Ambiente (Environment)** | Tabuleiro retangular L × A com N minas distribuídas aleatoriamente (com *seed* para reprodutibilidade). A primeira jogada é sempre segura. |
| **Atuadores (Actuators)** | `reveal(row, col)` e `flag(row, col)` (bandeira). |
| **Sensores (Sensors)** | Estado visível de cada célula: fechada, marcada ou aberta com um número de 0 a 8 (minas vizinhas). Também o total de minas do tabuleiro. |

## Propriedades do ambiente

| Propriedade | Classificação | Justificativa |
|---|---|---|
| Observabilidade | Parcialmente observável | A posição das minas é oculta; o agente só vê os números revelados. |
| Determinismo | Determinístico após a geração | Uma vez sorteado o tabuleiro, cada ação tem resultado fixo. A incerteza vem do desconhecimento, não do acaso nas transições. |
| Episódico ou sequencial | Sequencial | Cada célula aberta muda a informação disponível para as próximas decisões. |
| Estático ou dinâmico | Estático | O tabuleiro não muda enquanto o agente decide. |
| Discreto ou contínuo | Discreto | Número finito de células, estados e ações. |
| Agentes | Agente único | Não há adversário. |

## Arquitetura do agente

O agente é **baseado em conhecimento com raciocínio probabilístico**:

1. **Percepção**: lê o tabuleiro visível.
2. **Base de conhecimento**: cada número aberto gera uma restrição
   "a soma das minas nas células vizinhas fechadas é igual a k".
3. **Inferência lógica**: aplica regras e busca com restrições (CSP) para achar células certamente seguras ou certamente minas.
4. **Inferência probabilística**: quando nada é certo, calcula P(mina | evidência) para cada célula fechada.
5. **Decisão**: abre a célula com menor P(mina), o que maximiza a utilidade esperada.

## Agentes previstos (para comparação)

| Agente | Ideia | Conteúdo da disciplina |
|---|---|---|
| Aleatório | Abre uma célula fechada qualquer | Linha de base |
| Lógico simples | Regras locais sobre cada número | Agentes lógicos |
| CSP | *Backtracking* sobre as células da fronteira | Busca e satisfação de restrições |
| Probabilístico | Conta configurações consistentes e calcula P(mina) | Incerteza, Teorema de Bayes |
| Monte Carlo (opcional) | Estima P(mina) por amostragem | Inferência aproximada |
