"""
Testes Unitários para HSF Olho de Deus.

Testes focados nas funções principais do sistema de monitoramento.

Autor: @PLima
Data: 22/01/2026
"""

import pytest
from datetime import datetime
from main import (
    limpar_rtf_para_texto,
    converter_tempo_para_minutos,
    agora,
    driver_is_alive
)


class TestLimparRTF:
    """Testes para a função limpar_rtf_para_texto."""
    
    def test_limpar_rtf_basico(self):
        """Testa limpeza básica de RTF."""
        rtf_input = r"{\rtf1\ansi Texto simples}"
        resultado = limpar_rtf_para_texto(rtf_input)
        assert "Texto simples" in resultado
        assert "rtf1" not in resultado
        assert "{" not in resultado
        
    def test_limpar_rtf_acentos(self):
        """Testa conversão de acentos RTF."""
        rtf_input = r"{\rtf1 \'e1\'e9\'ed\'f3\'fa}"
        resultado = limpar_rtf_para_texto(rtf_input)
        assert "á" in resultado or "e1" in resultado
        
    def test_limpar_rtf_vazio(self):
        """Testa com string vazia."""
        resultado = limpar_rtf_para_texto("")
        assert resultado == ""
        
    def test_limpar_rtf_none(self):
        """Testa com None."""
        resultado = limpar_rtf_para_texto(None)
        assert resultado == ""


class TestConverterTempo:
    """Testes para a função converter_tempo_para_minutos."""
    
    def test_converter_tempo_formato_hhmmss(self):
        """Testa conversão de formato HH:MM:SS."""
        assert converter_tempo_para_minutos("01:05:30") == 66
        assert converter_tempo_para_minutos("00:06:07") == 6
        assert converter_tempo_para_minutos("02:00:00") == 120
        
    def test_converter_tempo_formato_hhmm(self):
        """Testa conversão de formato HH:MM."""
        assert converter_tempo_para_minutos("01:30") == 90
        assert converter_tempo_para_minutos("00:15") == 15
        
    def test_converter_tempo_zero(self):
        """Testa com tempo zero."""
        assert converter_tempo_para_minutos("00:00:00") == 0
        assert converter_tempo_para_minutos("00:00") == 0
        
    def test_converter_tempo_invalido(self):
        """Testa com valores inválidos."""
        assert converter_tempo_para_minutos("") == 0
        assert converter_tempo_para_minutos("invalid") == 0
        assert converter_tempo_para_minutos(None) == 0
        
    def test_converter_tempo_sem_segundos(self):
        """Testa tempo sem segundos."""
        resultado = converter_tempo_para_minutos("01:05")
        assert resultado == 65


class TestAgora:
    """Testes para a função agora."""
    
    def test_agora_formato(self):
        """Testa se retorna string no formato correto."""
        resultado = agora()
        assert isinstance(resultado, str)
        assert len(resultado) == 19  # YYYY-MM-DD HH-MM-SS
        
    def test_agora_contem_data(self):
        """Testa se contém data atual."""
        resultado = agora()
        ano_atual = str(datetime.now().year)
        assert ano_atual in resultado


class TestDriverIsAlive:
    """Testes para a função driver_is_alive."""
    
    def test_driver_none(self):
        """Testa com driver None."""
        assert driver_is_alive(None) is False
        
    def test_driver_mock_alive(self, mocker):
        """Testa com driver mockado ativo."""
        mock_driver = mocker.Mock()
        mock_driver.current_url = "https://web.whatsapp.com"
        assert driver_is_alive(mock_driver) is True
        
    def test_driver_mock_dead(self, mocker):
        """Testa com driver mockado inativo."""
        mock_driver = mocker.Mock()
        # Configurar PropertyMock na classe do objeto mockado
        # Isso garante que acessar .current_url dispare o side_effect
        type(mock_driver).current_url = mocker.PropertyMock(
            side_effect=Exception("Driver closed")
        )
        assert driver_is_alive(mock_driver) is False


class TestProcessarCoagulogramas:
    """Testes para processamento de coagulogramas (mock)."""
    
    def test_processar_coagulogramas_vazio(self):
        """Testa com lista vazia."""
        from main import processar_coagulogramas_criticos
        resultado = processar_coagulogramas_criticos([])
        assert resultado == []
        
    def test_processar_coagulogramas_none(self):
        """Testa com None."""
        from main import processar_coagulogramas_criticos
        resultado = processar_coagulogramas_criticos(None)
        assert resultado == []


# Configuração do pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
