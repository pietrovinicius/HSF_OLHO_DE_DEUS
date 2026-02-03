# Changelog

## [Unreleased]

### Adicionado
- **Documentação**: Criado arquivo `INTERFACE_GRAFICA.md` com guia completo de manutenção e extensão da GUI.
- **Interface Gráfica**: Implementada interface moderna com CustomTkinter (`main_gui.py`) com logs em tempo real e controle de execução.
- **Arquitetura**: Refatoração do `main.py` para separar lógica de negócio (backend) da interface.
- **Testes**: Adicionados testes unitários robustos com Pytest cobrindo conexão de banco, envio de WhatsApp e lógica de loop.
- **Monitoramento**: Implementada execução em thread separada (Worker) para não travar a interface.

### Alterado
- Refatorado `main.py` para ser importável como módulo.
- Melhorada a gestão de conexão com banco de dados usando context managers.

### Corrigido
- Ajustado o comportamento do botão "Executar" para iniciar o modo de monitoramento contínuo em vez de execução única.
- Restaurado arquivo `HSF - RESULTADOS EXAMES HEMOGRAMA COM INTERVALO DE 58 MINUTOS.sql` que estava ausente, corrigindo erro de execução.
- Corrigido erro de seletor do WhatsApp Web que impedia o envio de mensagens. Agora utiliza múltiplos seletores robustos para encontrar o campo de pesquisa.
- Corrigido erro de indentação (`IndentationError`) no `main.py` introduzido na atualização anterior.
