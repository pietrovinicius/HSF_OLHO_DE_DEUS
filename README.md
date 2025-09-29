# HSF Olho de Deus 👁️‍🗨️

Sistema de monitoramento em tempo real para valores críticos de exames laboratoriais e indicadores de emergência do Hospital São Francisco.

## 📋 Descrição

O **HSF Olho de Deus** é um sistema de monitoramento que acompanha continuamente:

- **Valores críticos de exames laboratoriais** (Hemograma, Coagulograma, etc.)
- **Tempos de espera na emergência** com alertas automáticos
- **Indicadores de performance** do pronto atendimento

## 🚀 Funcionalidades

### 🔬 Monitoramento de Exames Críticos
- Monitoramento automático de resultados de hemograma
- Detecção de coagulogramas críticos (INR > 5.0)
- Alertas em tempo real para valores fora dos parâmetros normais
- Integração com banco de dados TASY do hospital

### ⏱️ Alertas de Tempo de Espera - Emergência
- **Execução de query** para dados de tempo de espera da emergência
- **Exibição completa** do DataFrame com todos os dados dos pacientes
- **Visualização específica** de colunas importantes:
  - Atendimento
  - Triagem Classificação
  - Tempo Recepção
  - Tempo Final da Fila
  - Espera por médico
  - **Tempo Triagem** (calculado automaticamente em formato HH:MM:SS)

### 🔍 **NOVO: Sistema de Filtros Avançados**
- **Filtro Combinado**: Aplica todos os critérios simultaneamente para identificar casos críticos
- **Filtros Individuais**: Análise separada por critério específico
  - Tempo Recepção > 10 minutos
  - Tempo Triagem > 5 minutos  
  - Espera por Médico > 5 minutos
  - Tempo Final da Fila > 30 minutos
- **Formatação Avançada**: Todos os tempos exibidos em formato HH:MM:SS
- **Chaves Únicas**: Sempre inclui Atendimento e Triagem Classificação para rastreabilidade

### 🚨 **NOVO: Sistema de Alertas Unificados**
- **Mensagens Agrupadas por Paciente**: Todos os tempos críticos de um mesmo paciente são consolidados em uma única mensagem
- **Formato Visual Moderno**: Utiliza emojis e formatação em negrito para melhor legibilidade
- **Informações Completas**: Inclui número do atendimento, nome do paciente, data/hora de início e classificação de triagem
- **Tempos Inteiros**: Correção do problema de dízimas periódicas - todos os tempos são exibidos como números inteiros
- **Critérios de Alerta**:
  - ⏰ Tempo Recepção > 10 minutos
  - ⏰ Tempo Triagem > 5 minutos
  - ⏰ Espera por médico > 5 minutos
  - ⏰ Tempo Final da Fila > 30 minutos

#### Exemplo de Mensagem Unificada:
```
🔴 *ALERTA TEMPO DE EMERGÊNCIA*

Prezados, informo a identificação de tempo(s) crítico(s) de atendimento(s) na EMERGÊNCIA

27/08/2025 às 10h03m

⚠️ TEMPOS ENCONTRADOS ⚠️
🏥 *Atendimento:* 12345
✅ *Paciente:* João da Silva
📅 *Início Atendimento:* 27/08/2025 10:00:00
🔍 *Classificação:* Pouca Urgência (Verde)
⏰ *Tempo Recepção:* 16 minutos
⏰ *Tempo Triagem:* 6 minutos
⏰ *Espera por médico:* 35 minutos
```

### 🖥️ Interface Gráfica
- Interface moderna desenvolvida em Tkinter
- Logs detalhados de todas as operações
- Sistema de notificações visuais

## 🛠️ Tecnologias Utilizadas

- **Python 3.12+**
- **Oracle Database** (conexão via oracledb)
- **Pandas** para manipulação de dados
- **Selenium** para automação web
- **Tkinter** para interface gráfica
- **Oracle Instant Client** para conectividade

## 📦 Instalação

### Pré-requisitos
- Python 3.12 ou superior
- Acesso ao banco de dados TASY do hospital
- Oracle Instant Client (incluído no projeto)

### Passos de Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/HSF_OLHO_DE_DEUS.git
cd HSF_OLHO_DE_DEUS
```

2. **Crie e ative o ambiente virtual:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Execute o sistema:**
```bash
python main.py
```

## 📁 Estrutura do Projeto

```
HSF_OLHO_DE_DEUS/
├── main.py                                    # Arquivo principal do sistema
├── requirements.txt                           # Dependências Python
├── .gitignore                                # Arquivos ignorados pelo Git
├── README.md                                 # Documentação do projeto
├── HSF - TODOS - TEMPO DE ESPERA EMERGENCIA.sql  # Query de tempo de espera
├── HSF - RESULTADOS EXAMES *.sql            # Queries de exames
├── instantclient-basiclite-windows.x64-*/   # Oracle Instant Client
└── TABELA DE VALORES CRÍTICOS.odt           # Documentação de valores críticos
```

## 🔧 Configuração

### Banco de Dados
O sistema se conecta automaticamente ao banco TASY usando as configurações padrão do hospital. Certifique-se de que:

- O Oracle Instant Client está configurado
- A conectividade com o servidor `10.1.1.11:1521` está disponível
- As credenciais de acesso estão corretas

### Queries SQL
O sistema utiliza queries específicas localizadas nos arquivos `.sql` do projeto para:
- Buscar resultados de exames com intervalos específicos
- Monitorar tempos de espera na emergência
- Identificar valores críticos

## 📊 Funcionalidades Principais

### Monitoramento de Exames
```python
# Exemplo de uso das funções de tempo de espera
df = tempo_espera_emergencia()
exibir_dataframe_tempo_espera(df)
exibir_colunas_especificas_tempo_espera(df)
```

### **NOVO: Sistema de Filtros de Tempo de Espera**
```python
# Filtro combinado - aplica todos os critérios simultaneamente
exibir_registros_filtrados_tempo_espera(df)

# Filtros individuais - análise separada por critério
exibir_filtros_individuais_tempo_espera(df)
```

#### Funções de Formatação de Tempo
```python
# Converte minutos decimais para formato HH:MM:SS
formatar_minutos_para_hhmmss(65.5)  # Retorna: "01:05:30"

# Converte strings de tempo para minutos inteiros (CORRIGIDO)
converter_tempo_para_minutos("01:05:30")  # Retorna: 66 (inteiro, sem dízimas)
converter_tempo_para_minutos("00:06:07")  # Retorna: 6 (inteiro, sem dízimas)
```

#### **NOVA: Função de Alertas Unificados**
```python
# Processa todos os alertas de tempo agrupados por paciente
processar_alertas_tempo_unificado(df)

# Substitui as funções individuais:
# - processar_alertas_tempo_recepcao(df)
# - processar_alertas_tempo_triagem(df) 
# - processar_alertas_espera_medico(df)
# - processar_alertas_tempo_final_fila(df)
```

#### Critérios de Filtro Aplicados
- **Atendimento** > 0 (sempre aplicado)
- **Triagem Classificação** não nula (sempre aplicado)
- **Tempo Recepção** > 10 minutos
- **Tempo Triagem** > 5 minutos
- **Espera por Médico** > 5 minutos
- **Tempo Final da Fila** > 30 minutos e não nulo

### Processamento de Coagulogramas
- Identifica automaticamente valores de INR > 5.0
- Gera alertas para casos críticos
- Registra logs detalhados de todas as ocorrências

## 🚨 Alertas e Notificações

O sistema monitora continuamente e gera alertas para:
- Valores críticos de hemograma
- Coagulogramas com INR elevado
- Tempos de espera excessivos na emergência
- Falhas de conectividade com o banco de dados

## 📝 Logs

Todos os eventos são registrados em `log.txt` com timestamps detalhados:
- Início e fim de operações
- Erros de conectividade
- Resultados de queries
- Alertas gerados

## 🤝 Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é de uso interno do Hospital São Francisco.

## 📞 Suporte

Para suporte técnico, entre em contato com a equipe de TI do hospital.

---

**Desenvolvido para o Hospital São Francisco** 🏥
*Sistema de Monitoramento em Tempo Real*