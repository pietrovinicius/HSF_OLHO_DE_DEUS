# Changelog

## [3.2.1] - 2026-04-14
### Alterado
- **Ordem de Auto-start**: Ajustada a sequência de inicialização para enviar as **O.S. Encerradas Hoje** primeiro, seguidas pelas **O.S. Atrasadas (>2 dias)**.

## [3.2.0] - 2026-04-14
### Adicionado
- **Monitoramento de OS Encerradas Hoje (TI)**: Nova funcionalidade que reporta todas as ordens de serviço finalizadas no dia, agrupadas alfabeticamente por analista. Inclui descrições curtas e totais diários.
- **Automação Inteligente**: Integração do novo fluxo no ciclo principal de disparo, garantindo visibilidade da produtividade diária no grupo de WhatsApp da TI.

## [3.1.7] - 2026-04-14
### Adicionado
- **Categoria 'Sem Analista'**: O monitoramento de O.S. TI agora inclui uma seção específica para ordens pendentes sem analista atribuído, exibida após a lista de analistas ativos, garantindo cobertura total da fila.

## [3.1.6] - 2026-04-14
### Alterado
- **Comportamento de Auto-start**: Removida a execução do ciclo completo (TI + Emergência + Lab) ao iniciar o app. Agora, apenas o fluxo de **O.S. TI** é disparado automaticamente para agilizar a primeira entrega sem prender o robô em ciclos longos desnecessários.
- **Bumping de Versão**: Sincronização da versão interna para 3.1.6.

## [3.1.5] - 2026-04-14
### Adicionado
- **Logs de Auditoria Elite**: Implementada a rastreabilidade completa na função de O.S. TI, com logs para contagem de analistas e extração de indicadores de atraso.
- **Confirmações Instantâneas**: Todas as interações com o WhatsApp agora registram o sucesso e o tamanho das mensagens enviadas para os grupos no `log.txt`.

### Corrigido
- **Bug de Escopo**: Corrigida a variável indefinida `atendimento` no log de emergência que causava falhas silenciosas.
- **Gestão de Processos**: Implementada rotina de limpeza para evitar conflitos de instâncias do Chromium no Windows.

## [3.1.4] - 2026-04-14
### Alterado
- **Unificação de Contexto**: Removido o isolamento entre "Geral" e "Emergência". O robô agora utiliza uma única instância e perfil do Chromium (`wpp_geral`) para todas as notificações, evitando a abertura de múltiplas janelas (Redução de overhead e melhora na UX).
- **Fluxo de Laboratório**: Adicionados logs de verificação explícita ("Nenhum exame crítico detectado") para garantir transparência quando a lista de exames vinda do banco está vazia.

## [3.1.3] - 2026-04-14
### Adicionado
- **Suporte WhatsApp Business**: Implementados seletores específicos para a versão Business do WhatsApp Web, focando em elementos `input` para busca e filtros por `aria-label` para a caixa de mensagens.
- **Robustez de Selectors**: Adicionados fallbacks idiomáticos (Inglês/Português) para placeholders e títulos.

## [3.1.2] - 2026-04-14
### Adicionado
- **Diagnóstico Inteligente**: Nova função `esperar_e_diagnosticar_whatsapp` que captura screenshots automáticos em `temp/debug_whatsapp.png` caso a busca demore mais de 15s.
- **Detecção de Estado**: Implementada verificação automática de QR Code para alertar sobre sessões deslogadas nos logs.

### Alterado
- **Resiliência de Busca**: Adicionado fallback para o seletor `div[role="textbox"]`, aumentando a compatibilidade com o framework Lexical.
- **Auditoria Visual**: Refatorada a ordem de captura de screenshots em blocos de erro para garantir a gravação antes do fechamento do contexto.

## [3.1.1] - 2026-04-14
### Corrigido
- **Playwright Hang**: Corrigido travamento na inicialização do contexto persistente através da remoção de inicialização dupla redundante do Chromium.
- **Estabilidade Windows**: Adicionados argumentos de hardware (`--disable-gpu`, `--disable-software-rasterizer`) para prevenir deadlocks em drivers de vídeo durante o lançamento do navegador.

## [3.1.0] - 2026-04-14
### Adicionado
- **Resiliência WhatsApp**: Implementação de constantes unificadas de seletores (`WPP_SEARCH_SELECTOR`, `WPP_MESSAGE_SELECTOR`) compatíveis com o framework Lexical da Meta.
- **Lógica de Input**: Adotado uso de `.fill()` com pré-limpeza via `Control+A` + `Backspace` para garantir gatilhos de estado no React/Lexical.

### Alterado
- **Performance**: Redução de timeouts redundantes e otimização do tempo de espera de pesquisa para 120s globais.
- **Logging**: Melhoria nas mensagens de erro e alertas de interface para falhas de layout.

## [3.0.0] - 2026-04-14

### Alterado
- **Core Engine**: Migração completa de Selenium para **Playwright (Sync API)** conforme diretrizes `GEMINI.md`.
- **Automação**: Implementada gestão de contextos persistentes para WhatsApp Web, eliminando dependência de `webdriver-manager` e `pyautogui`.
- **Resiliência**: Adicionada função de Auditoria Visual (screenshots automáticos em erro).
- **Performance**: Limpeza do ciclo de vida do navegador entre iterações do loop principal.
- **Fluxo de Trabalho**: Reordenado ciclo de monitoramento para priorizar O.S. TI como primeira tarefa.
- **Interface (GUI)**: Implementado auto-start do fluxo ao abrir o app e reset automático do `log.txt` na inicialização.

## [2.2.1] - 2026-04-14

### Corrigido
- **Monitoramento TI**: Corrigido erro de tipagem (`TypeError: str vs float`) na comparação da idade das Ordens de Serviço.
- **WhatsApp Web**: Atualizados seletores de busca para incluir `data-testid="chat-list-search"` e estratégias via CSS/XPah para maior resiliência no WhatsApp Business.

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
