# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [2.0.0] - 2026-01-22

### Adicionado
- **Interface Gráfica (GUI)**: Nova interface moderna usando CustomTkinter (`gui_app.py`) com:
  - Botão "Executar Ciclo Completo"
  - Botão "Parar Execução"
  - Área de logs em tempo real
  - Indicadores de status
- **Testes Unitários**: Suíte de testes com Pytest (`test_main.py`) cobrindo:
  - Limpeza de RTF
  - Conversão de tempo
  - Validação de conexão e drivers
- **Callback de Logs**: Sistema de hooks em `registrar_log` para integração com GUI.

### Alterado
- **Refatoração do Main**: Lógica de execução extraída para função `executar_ciclo_completo()`.
- **Arquitetura**: Separação clara entre interface e lógica de negócio.
- **Ambiente Virtual**: Recriado e atualizado com novas dependências (`customtkinter`, `pytest`).
- **Arredondamento de Tempo**: Corrigido para arredondamento tradicional (0.5 arredonda para cima) em vez de "bankers rounding".

### Dependências
- Adicionado `customtkinter`
- Adicionado `pytest` e `pytest-mock`
