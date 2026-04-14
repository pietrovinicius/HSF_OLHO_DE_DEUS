# Changelog

## [2.2.0] - 2026-04-14

### Adicionado
- **Monitoramento TI**: Implementada funcionalidade para rastrear Ordens de Serviço (OS) com mais de 2 dias de atraso.
- **Relatórios Automatizados**: Envio de indicadores de OS por analista via WhatsApp para o grupo "HSF - O.S. TI".
- **Arquitetura**: Criada função genérica `enviar_whatsapp_grupo` para suporte a múltiplos grupos com alta resiliência.

### Alterado
- **WhatsApp**: Refatoração interna para centralizar lógica de envio e reduzir duplicidade de código.

## [2.1.0] - 2026-04-14

### Adicionado
- **Versionamento**: Sistema de versão centralizado em `version.py`.
- **Interface Gráfica**: Display da versão atual no rodapé da janela (inferior direito).

### Alterado
- **Instant Client**: Refatorada descoberta de diretório no `main.py` para suporte multi-plataforma (Windows/macOS) e nova estrutura em `util/`.
- **Changelog**: Reestruturação para seguir o padrão `[Versão] - Data`.

### Corrigido
- **Sintaxe**: Corrigido `SyntaxWarning` (invalid escape sequence) no docstring da função `encontrar_diretorio_instantclient`.

## [2.0.0] - 2026-04-07

### Adicionado
- **Documentação**: Criado arquivo `INTERFACE_GRAFICA.md` com guia completo de manutenção e extensão da GUI.
- **Interface Gráfica**: Implementada interface moderna com CustomTkinter (`gui_app.py`) com logs em tempo real e controle de execução.
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
