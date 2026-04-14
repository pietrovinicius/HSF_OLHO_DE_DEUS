# Plano de Correção e Melhoria do Fluxo: WhatsApp Search

Identifiquei com precisão a causa da "tela ficar parada sem digitar" e do problema dos componentes no Playwright:
1. **O Comportamento Fantasma**: O Botânico de Espera (Timeout) atual enxerga que o WhatsApp "mudou de cara". O WhatsApp Web converteu suas caixas de texto `contenteditable` nativas para um novo framework chamado Lexical. Com isso, os antigos seletores `data-tab="3"` muitas vezes não aparecem mais e o Playwright fica "olhando para a tela" durante os 2 minutos esperando a barra até estourar de forma solitária.
2. **Seletores Sequenciais**: Da forma atual, ele testa um seletor e, se o WhatsApp estiver atualizado, ele aguarda 2 minutos inteiros no primeiro falho para só então tentar o segundo.

## Proposed Changes

### Seletores Dinâmicos (CSS/XPath Combinado) e `wait_for_selector` Único
#### [MODIFY] main.py
Vamos modernizar o alvo da busca de contatos e remover o gargalo da espera condicional lenta:
*   Mudar todas as ocorrências de pesquisa para um seletor unificado em formato CSS/XPath OR `,`:
    `'div[title="Caixa de texto de pesquisa"], div[title="Search input textbox"], [data-testid="chat-list-search"]'`
    Essa sintaxe de busca paralela no `wait_for` fará com que qualquer barra de busca nova do WhastApp seja interceptada instantaneamente independentemente de qual layout tenha subitamente caído de atualização.
*   Utilizaremos `.fill` como prioridade, seguido de um disparo artificial do evento `input` que acorda o mecanismo React de preenchimento automático.
*   Encurtar as múltiplas tentativas de exceções `try/except` seguidas e colocar o motor Playwright pra buscar por todos os alvos simutaneamente com apenas um timeout global de 120seg, garantindo que "caso encontre QUALQUER um, clique".

### Correção de Seleção da Caixa de Mensagens
O próprio envio (a caixa de digitar texto do chat) também sofreu modificações na plataforma Lexical do Facebook. Empregaremos a busca avançada por `div[title="Mensagem"]` e `div[aria-placeholder="Digite uma mensagem"]` para estabilizar completamente o fluxo de enviar a string O.S TI.

## Open Questions

- Como essas constantes atualizações são impostas pelo WhatsApp em plano de fundo para alguns PCs e outros não (teste A/B), há necessidade de criarmos um aviso/alerta caso isso ocorra novamente no futuro, disparando imediatamente no seu console sobre a mudança de layout ao invés dele ficar aguardando mudo?

## Verification Plan

Ao ser chancelado, a injeção do código ocorrerá rapidamente pelas rotinas e, sem precisar criar "novas janelas duplas", ele resgatará a atual instância de Chromium focando agressivamente com a flag `.click()` nas caixas visíveis detectadas. Usaremos Playwright Trace ou screenshots temporárias do teste em si para garantir precisão se desejado.
