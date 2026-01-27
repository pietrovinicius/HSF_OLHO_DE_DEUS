# Changelog

## [Unreleased]

### Adicionado
- Implementado loop infinito na execução via interface gráfica (GUI).
- O aplicativo agora executa o ciclo de monitoramento e aguarda a próxima hora cheia para executar novamente.
- Adicionado botão "Parar Execução" que interrompe imediatamente a espera e o monitoramento.
- Adicionados testes unitários para a lógica de loop da GUI (`test_gui_loop.py`).

### Corrigido
- Ajustado o comportamento do botão "Executar" para iniciar o modo de monitoramento contínuo em vez de execução única.
- Restaurado arquivo `HSF - RESULTADOS EXAMES HEMOGRAMA COM INTERVALO DE 58 MINUTOS.sql` que estava ausente, corrigindo erro de execução.
- Corrigido erro de seletor do WhatsApp Web que impedia o envio de mensagens. Agora utiliza múltiplos seletores robustos para encontrar o campo de pesquisa.
- Corrigido erro de indentação (`IndentationError`) no `main.py` introduzido na atualização anterior.
