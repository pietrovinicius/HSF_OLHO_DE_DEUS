"""
Testes para validar a inclusão da informação da fila (DS_FILA) 
nas mensagens de alerta do sistema HSF Olho de Deus.

Este módulo testa especificamente a funcionalidade adicionada na função
processar_alertas_tempo_unificado para incluir a fila do paciente.
"""

import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os

# Adicionar o diretório atual ao path para importar o main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar as funções necessárias do main.py
from main import processar_alertas_tempo_unificado, converter_tempo_para_minutos


class TestProcessarAlertasTempoUnificado(unittest.TestCase):
    """
    Classe de teste para validar a funcionalidade de inclusão da fila
    nas mensagens de alerta do WhatsApp.
    """
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.dados_teste = {
            'NR_ATENDIMENTO': [12345, 67890, 11111],
            'PACIENTE': ['João da Silva', 'Maria Santos', 'Pedro Oliveira'],
            'TRIAGEM_CLASSIFICACAO': ['Pouca Urgência (Verde)', 'Urgência (Amarelo)', 'Emergência (Vermelho)'],
            'ATENDIMENTO_PACIENTE_DT_INICIO': ['27/08/2025 10:00:00', '27/08/2025 11:30:00', '27/08/2025 09:15:00'],
            'DS_FILA': ['Emergência Adulto', 'Emergência Pediátrica', 'Trauma'],
            'TOTAL_RECEP': ['00:15:30', '00:12:45', '00:12:20'],  # Todos > 10 min
            'TEMPO_ESPERA_ATEND': ['00:35:15', '00:08:30', '00:45:10'],  # Todos > 5 min
            'PACIENTE_SENHA_FILA_FIM': ['00:25:40', '00:35:20', '00:35:50'],  # Todos > 30 min
            'DT_INICIO_TRIAGEM': ['2025-08-27 10:15:30', '2025-08-27 11:38:45', '2025-08-27 09:27:20'],
            'DT_FIM_TRIAGEM': ['2025-08-27 10:21:45', '2025-08-27 11:45:15', '2025-08-27 09:30:40']  # Triagem > 5 min
        }
        
    def criar_dataframe_teste(self, dados_customizados=None):
        """
        Cria um DataFrame de teste com dados simulados.
        
        Args:
            dados_customizados (dict, optional): Dados personalizados para sobrescrever os padrão
            
        Returns:
            pandas.DataFrame: DataFrame com dados de teste
        """
        dados = self.dados_teste.copy()
        if dados_customizados:
            dados.update(dados_customizados)
        return pd.DataFrame(dados)
    
    @patch('main.enviar_whatsapp_emergencia')
    @patch('main.registrar_log')
    def test_fila_incluida_na_mensagem_com_tempos_criticos(self, mock_log, mock_whatsapp):
        """
        Testa se a informação da fila é incluída corretamente na mensagem
        quando há pacientes com tempos críticos.
        """
        # Criar DataFrame com tempos críticos
        df_teste = self.criar_dataframe_teste()
        
        # Executar a função
        processar_alertas_tempo_unificado(df_teste)
        
        # Verificar se o WhatsApp foi chamado
        self.assertTrue(mock_whatsapp.called)
        
        # Obter a mensagem enviada
        mensagem_enviada = mock_whatsapp.call_args[0][0]
        
        # Verificar se a fila está presente na mensagem
        self.assertIn('🎯 *Fila:* Emergência Adulto', mensagem_enviada)
        self.assertIn('🎯 *Fila:* Emergência Pediátrica', mensagem_enviada)
        self.assertIn('🎯 *Fila:* Trauma', mensagem_enviada)
        
        # Verificar estrutura da mensagem
        self.assertIn('🏥 *Atendimento:*', mensagem_enviada)
        self.assertIn('✅ *Paciente:*', mensagem_enviada)
        self.assertIn('📅 *Início Atendimento:*', mensagem_enviada)
        self.assertIn('🔍 *Classificação:*', mensagem_enviada)
    
    @patch('main.enviar_whatsapp_emergencia')
    @patch('main.registrar_log')
    def test_fila_na_quando_ds_fila_ausente(self, mock_log, mock_whatsapp):
        """
        Testa se a função trata corretamente quando a coluna DS_FILA está ausente,
        usando 'N/A' como valor padrão.
        """
        # Criar DataFrame sem a coluna DS_FILA
        dados_sem_fila = self.dados_teste.copy()
        del dados_sem_fila['DS_FILA']
        df_teste = pd.DataFrame(dados_sem_fila)
        
        # Executar a função
        processar_alertas_tempo_unificado(df_teste)
        
        # Verificar se o WhatsApp foi chamado
        self.assertTrue(mock_whatsapp.called)
        
        # Obter a mensagem enviada
        mensagem_enviada = mock_whatsapp.call_args[0][0]
        
        # Verificar se 'N/A' é usado quando DS_FILA não existe
        self.assertIn('🎯 *Fila:* N/A', mensagem_enviada)
    
    @patch('main.enviar_whatsapp_emergencia')
    @patch('main.registrar_log')
    def test_fila_na_quando_ds_fila_vazio(self, mock_log, mock_whatsapp):
        """
        Testa se a função trata corretamente quando DS_FILA tem valores vazios ou None.
        """
        # Criar DataFrame com valores vazios na coluna DS_FILA
        dados_fila_vazia = self.dados_teste.copy()
        dados_fila_vazia['DS_FILA'] = [None, '', 'Trauma']
        df_teste = pd.DataFrame(dados_fila_vazia)
        
        # Executar a função
        processar_alertas_tempo_unificado(df_teste)
        
        # Verificar se o WhatsApp foi chamado
        self.assertTrue(mock_whatsapp.called)
        
        # Obter a mensagem enviada
        mensagem_enviada = mock_whatsapp.call_args[0][0]
        
        # Verificar se 'N/A' é usado para valores vazios e None
        linhas_mensagem = mensagem_enviada.split('\n')
        filas_encontradas = [linha for linha in linhas_mensagem if '🎯 *Fila:*' in linha]
        
        # Deve haver pelo menos uma fila válida (Trauma) e N/A para os vazios
        self.assertTrue(any('Trauma' in fila for fila in filas_encontradas))
    
    @patch('main.enviar_whatsapp_emergencia')
    @patch('main.registrar_log')
    def test_sem_tempos_criticos_nao_inclui_fila(self, mock_log, mock_whatsapp):
        """
        Testa se quando não há tempos críticos, a mensagem não inclui informações de fila.
        """
        # Criar DataFrame com tempos normais (não críticos)
        dados_normais = {
            'NR_ATENDIMENTO': [99999],
            'PACIENTE': ['Paciente Normal'],
            'TRIAGEM_CLASSIFICACAO': ['Pouca Urgência (Verde)'],
            'ATENDIMENTO_PACIENTE_DT_INICIO': ['27/08/2025 10:00:00'],
            'DS_FILA': ['Emergência Adulto'],
            'TOTAL_RECEP': ['00:05:30'],  # Menor que 10 min
            'TEMPO_ESPERA_ATEND': ['00:03:15'],  # Menor que 5 min
            'PACIENTE_SENHA_FILA_FIM': ['00:15:20'],  # Menor que 30 min
            'DT_INICIO_TRIAGEM': ['2025-08-27 10:05:30'],
            'DT_FIM_TRIAGEM': ['2025-08-27 10:08:45']  # Triagem de 3 min (menor que 5)
        }
        df_teste = pd.DataFrame(dados_normais)
        
        # Executar a função
        processar_alertas_tempo_unificado(df_teste)
        
        # Verificar se o WhatsApp foi chamado
        self.assertTrue(mock_whatsapp.called)
        
        # Obter a mensagem enviada
        mensagem_enviada = mock_whatsapp.call_args[0][0]
        
        # Verificar se é mensagem de situação normal (sem fila)
        self.assertIn('✅ Situação Normal', mensagem_enviada)
        self.assertNotIn('🎯 *Fila:*', mensagem_enviada)
    
    def test_converter_tempo_para_minutos(self):
        """
        Testa a função auxiliar converter_tempo_para_minutos.
        """
        # Testes com diferentes formatos
        self.assertEqual(converter_tempo_para_minutos('01:05:30'), 65)  # 1h5m30s = 65min (arredondado)
        self.assertEqual(converter_tempo_para_minutos('00:15:00'), 15)  # 15 minutos
        self.assertEqual(converter_tempo_para_minutos('02:30'), 150)    # 2h30m = 150min
        self.assertEqual(converter_tempo_para_minutos('00:03:11'), 3)   # 3min11s ≈ 3min
        self.assertEqual(converter_tempo_para_minutos(None), 0)         # None = 0
        self.assertEqual(converter_tempo_para_minutos(''), 0)           # String vazia = 0
    
    @patch('main.enviar_whatsapp_emergencia')
    @patch('main.registrar_log')
    def test_multiplos_pacientes_com_filas_diferentes(self, mock_log, mock_whatsapp):
        """
        Testa se múltiplos pacientes com filas diferentes são processados corretamente.
        """
        # Criar DataFrame com múltiplos pacientes e filas diferentes
        df_teste = self.criar_dataframe_teste()
        
        # Executar a função
        processar_alertas_tempo_unificado(df_teste)
        
        # Verificar se o WhatsApp foi chamado
        self.assertTrue(mock_whatsapp.called)
        
        # Obter a mensagem enviada
        mensagem_enviada = mock_whatsapp.call_args[0][0]
        
        # Verificar se todas as filas estão presentes
        filas_esperadas = ['Emergência Adulto', 'Emergência Pediátrica', 'Trauma']
        for fila in filas_esperadas:
            self.assertIn(f'🎯 *Fila:* {fila}', mensagem_enviada)
        
        # Verificar se há separadores entre pacientes
        self.assertIn('─' * 40, mensagem_enviada)


def executar_testes():
    """
    Função para executar todos os testes e exibir resultados.
    """
    print("🧪 Iniciando testes para validação da funcionalidade de fila...")
    print("=" * 60)
    
    # Criar suite de testes
    suite = unittest.TestLoader().loadTestsFromTestCase(TestProcessarAlertasTempoUnificado)
    
    # Executar testes com verbosidade
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    print("\n" + "=" * 60)
    print(f"📊 Resumo dos Testes:")
    print(f"   ✅ Testes executados: {resultado.testsRun}")
    print(f"   ❌ Falhas: {len(resultado.failures)}")
    print(f"   🚫 Erros: {len(resultado.errors)}")
    
    if resultado.wasSuccessful():
        print("   🎉 Todos os testes passaram com sucesso!")
        return True
    else:
        print("   ⚠️  Alguns testes falharam. Verifique os detalhes acima.")
        return False


if __name__ == '__main__':
    # Executar testes quando o arquivo for executado diretamente
    executar_testes()