# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [2.1.1] - 2026-01-22

### Corrigido
- **Erro Crítico DPI-1047**: Resolvido problema de inicialização múltipla do Oracle Client que causava falha na execução do script.
  - Implementada inicialização global (`inicializar_oracle_client_global`) no início da execução.
  - Removidas inicializações locais redundantes nas funções `tempo_espera_emergencia`, `resultados_exames_intervalo_58_min` e `resultados_hemogramas_intervalo_58_min`.

## [2.1.0] - 2026-01-22

### Alterado
- **Agendamento de Execução**: Ajustado loop principal em `main.py` para sincronizar a execução com o início de cada hora (ex: 10h, 11h, 12h), em vez de intervalos fixos de 3600s.
- **Query SQL**: Revertida a lógica de `HSF - TODOS - TEMPO DE ESPERA EMERGENCIA.sql` para buscar apenas dados da **última hora** (`sysdate - 1/24`), garantindo conformidade com a execução horária e evitando alertas duplicados do dia inteiro.

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
