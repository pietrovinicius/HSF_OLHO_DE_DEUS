import pytest
import os
import re
from datetime import datetime
from unittest.mock import patch, call

# Importar as funções a serem testadas do main.py
# Assumindo que main.py está no mesmo diretório ou no PYTHONPATH
from main import limpar_rtf_para_texto, processar_coagulogramas_criticos, processar_hemogramas_criticos, enviar_whatsapp
import main # Importa o módulo inteiro para acessar MODO_TESTE_WHATSAPP e mockar agora()

# Mock para a função agora() para logs consistentes em testes
def mock_agora():
    return "2024-01-01 12-00-00"

# Substituir a função agora() globalmente para os testes
main.agora = mock_agora

# Limpar o arquivo de log de teste do WhatsApp antes de cada teste que o usa
@pytest.fixture(autouse=True)
def clean_whatsapp_test_log():
    log_file_path = os.path.join(os.getcwd(), main.WHATSAPP_TEST_LOG_FILE)
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
    yield

# Testes para limpar_rtf_para_texto
def test_limpar_rtf_para_texto_basico():
    rtf_input = r"{\rtf1\ansi\deff0{\fonttbl{\f0\fswiss\fcharset0 Arial;}}\pard\sa200\sl276\slmult1\f0\fs24 Hello World!\par}"
    expected_output = "Hello World!"
    assert limpar_rtf_para_texto(rtf_input) == expected_output

def test_limpar_rtf_para_texto_com_acentos():
    rtf_input = r"{\rtf1\ansi\deff0\'c1gua \'e9 \'f3tima}"
    expected_output = "Água é ótima"
    assert limpar_rtf_para_texto(rtf_input) == expected_output

def test_limpar_rtf_para_texto_com_multiplos_espacos_e_linhas():
    rtf_input = r"{\rtf1\ansi\deff0 Teste\par\par\par  com   espacos\par}"
    expected_output = "Teste\ncom espacos"
    assert limpar_rtf_para_texto(rtf_input) == expected_output

def test_limpar_rtf_para_texto_vazio():
    assert limpar_rtf_para_texto("") == ""
    assert limpar_rtf_para_texto(None) == ""

# Testes para processar_coagulogramas_criticos
def test_processar_coagulogramas_criticos_encontrado():
    # Mock de dados brutos do Oracle
    mock_resultados = [
        (12345, "Paciente A", r"{\rtf1\ansi COAGULOGRAMA\par INR: 7,50\par}"),
        (67890, "Paciente B", r"{\rtf1\ansi COAGULOGRAMA\par INR: 1,20\par}"),
        (11223, "Paciente C", r"{\rtf1\ansi HEMOGRAMA\par Hemoglobina: 14,0\par}"),
        (44556, "Paciente D", r"{\rtf1\ansi COAGULOGRAMA\par INR: 6.01\par}"), # Critico com ponto
        (77889, "Paciente E", r"{\rtf1\ansi COAGULOGRAMA\par INR: 5.99\par}"), # Não crítico
    ]
    
    criticos = processar_coagulogramas_criticos(mock_resultados)
    
    assert len(criticos) == 2
    assert criticos[0]["prescricao"] == 12345
    assert criticos[0]["parametro"] == "INR"
    assert criticos[0]["valor"] == 7.5
    assert criticos[1]["prescricao"] == 44556
    assert criticos[1]["parametro"] == "INR"
    assert criticos[1]["valor"] == 6.01

def test_processar_coagulogramas_criticos_nenhum_critico():
    mock_resultados = [
        (12345, "Paciente A", r"{\rtf1\ansi COAGULOGRAMA\par INR: 5,50\par}"),
        (67890, "Paciente B", r"{\rtf1\ansi COAGULOGRAMA\par INR: 1,20\par}"),
        (11223, "Paciente C", r"{\rtf1\ansi HEMOGRAMA\par Hemoglobina: 14,0\par}"),
    ]
    criticos = processar_coagulogramas_criticos(mock_resultados)
    assert len(criticos) == 0

def test_processar_coagulogramas_criticos_formato_invalido():
    mock_resultados = [
        (12345, "Paciente A", r"{\rtf1\ansi COAGULOGRAMA\par INR: ABC\par}"), # Valor não numérico
        (67890, "Paciente B", r"{\rtf1\ansi COAGULOGRAMA\par Sem INR\par}"), # INR não encontrado
    ]
    criticos = processar_coagulogramas_criticos(mock_resultados)
    assert len(criticos) == 0

def test_processar_coagulogramas_criticos_lista_vazia():
    criticos = processar_coagulogramas_criticos([])
    assert len(criticos) == 0

def test_processar_coagulogramas_criticos_none_input():
    criticos = processar_coagulogramas_criticos(None)
    assert len(criticos) == 0

# Testes para processar_hemogramas_criticos
def test_processar_hemogramas_criticos_encontrado():
    # Mock de dados brutos do Oracle com RTF de hemograma
    mock_resultados = [
        (1001, "Paciente X", r"{\rtf1\ansi HEMOGRAMA\par Hemoglobina: 5,5 g/dL\par Hematócrito: 17,0 %\par Leucócitos Totais: 1500 mmb3\par PLAQUETAS: 15 mil/mmb3}"), # Todos críticos
        (1002, "Paciente Y", r"{\rtf1\ansi HEMOGRAMA\par Hemoglobina: 15,0 g/dL\par Hematócrito: 45,0 %\par Leucócitos Totais: 60000 mmb3\par PLAQUETAS: 1200 mil/mmb3}"), # Leucócitos e Plaquetas críticos (altos)
        (1003, "Paciente Z", r"{\rtf1\ansi HEMOGRAMA\par Hemoglobina: 10,0 g/dL\par Hematócrito: 30,0 %\par Leucócitos Totais: 5000 mmb3\par PLAQUETAS: 250 mil/mmb3}"), # Nenhum crítico
        (1004, "Paciente W", r"{\rtf1\ansi COAGULOGRAMA\par INR: 1.5\par}"), # Não é hemograma
    ]

    criticos = processar_hemogramas_criticos(mock_resultados)

    assert len(criticos) == 6 # 4 do 1001, 2 do 1002

    # Verificar o primeiro exame (1001)
    critico_1001_hemo = next(c for c in criticos if c["prescricao"] == 1001 and c["parametro"] == "Hemoglobina")
    assert critico_1001_hemo["valor"] == 5.5
    assert critico_1001_hemo["unidade"] == "g/dL"

    critico_1001_hemato = next(c for c in criticos if c["prescricao"] == 1001 and c["parametro"] == "Hematócrito")
    assert critico_1001_hemato["valor"] == 17.0
    assert critico_1001_hemato["unidade"] == "vol%"

    critico_1001_leuco = next(c for c in criticos if c["prescricao"] == 1001 and c["parametro"] == "Leucócitos")
    assert critico_1001_leuco["valor"] == 1500.0
    assert critico_1001_leuco["unidade"] == "/µL"

    critico_1001_plaquetas = next(c for c in criticos if c["prescricao"] == 1001 and c["parametro"] == "Plaquetas")
    assert critico_1001_plaquetas["valor"] == 15000.0 # 15 mil * 1000
    assert critico_1001_plaquetas["unidade"] == "/uL"

    # Verificar o segundo exame (1002)
    critico_1002_leuco = next(c for c in criticos if c["prescricao"] == 1002 and c["parametro"] == "Leucócitos")
    assert critico_1002_leuco["valor"] == 60000.0
    assert critico_1002_leuco["unidade"] == "/µL"

    critico_1002_plaquetas = next(c for c in criticos if c["prescricao"] == 1002 and c["parametro"] == "Plaquetas")
    assert critico_1002_plaquetas["valor"] == 1200000.0 # 1200 mil * 1000
    assert critico_1002_plaquetas["unidade"] == "/uL"

def test_processar_hemogramas_criticos_nenhum_critico():
    mock_resultados = [
        (1003, "Paciente Z", r"{\rtf1\ansi HEMOGRAMA\par Hemoglobina: 10,0 g/dL\par Hematócrito: 30,0 %\par Leucócitos Totais: 5000 mmb3\par PLAQUETAS: 250 mil/mmb3}"),
        (1004, "Paciente W", r"{\rtf1\ansi COAGULOGRAMA\par INR: 1.5\par}"),
    ]
    criticos = processar_hemogramas_criticos(mock_resultados)
    assert len(criticos) == 0

def test_processar_hemogramas_criticos_formato_invalido():
    mock_resultados = [
        (1001, "Paciente X", r"{\rtf1\ansi HEMOGRAMA\par Hemoglobina: ABC g/dL\par}"), # Valor não numérico
        (1002, "Paciente Y", r"{\rtf1\ansi HEMOGRAMA\par Sem Hemoglobina\par}"), # Parâmetro não encontrado
    ]
    criticos = processar_hemogramas_criticos(mock_resultados)
    assert len(criticos) == 0

def test_processar_hemogramas_criticos_lista_vazia():
    criticos = processar_hemogramas_criticos([])
    assert len(criticos) == 0

def test_processar_hemogramas_criticos_none_input():
    criticos = processar_hemogramas_criticos(None)
    assert len(criticos) == 0

# Teste para enviar_whatsapp em modo de teste
def test_enviar_whatsapp_modo_teste():
    test_messages = [
        ["--- TESTE DE MENSAGENS ---"],
        ["Prescrição 123: Hemoglobina com valor crítico de 5.5 g/dL."],
        ["Prescrição 456: INR com valor crítico de 7.0."],
    ]
    
    # Mock da função registrar_whatsapp_test_log para capturar o que seria escrito no arquivo
    with patch('main.registrar_whatsapp_test_log') as mock_registrar_whatsapp_test_log:
        enviar_whatsapp(test_messages, modo_teste=True)
        
        # Verifica se as chamadas foram feitas corretamente
        expected_calls = [
            call("[MODO DE TESTE] --- INÍCIO DA SIMULAÇÃO DE ENVIO ---"),
            call("[MODO DE TESTE] --- TESTE DE MENSAGENS ---"),
            call("[MODO DE TESTE] Prescrição 123: Hemoglobina com valor crítico de 5.5 g/dL."),
            call("[MODO DE TESTE] Prescrição 456: INR com valor crítico de 7.0."),
            call("[MODO DE TESTE] --- FIM DA SIMULAÇÃO DE ENVIO ---"),
        ]
        mock_registrar_whatsapp_test_log.assert_has_calls(expected_calls, any_order=False)