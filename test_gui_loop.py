
import unittest
from unittest.mock import MagicMock, patch
import threading
import time
from datetime import datetime, timedelta
import gui_app

class TestGUILoop(unittest.TestCase):
    
    @patch('gui_app.ctk')
    @patch('gui_app.inicializar_oracle_client_global')
    @patch('gui_app.set_log_callback')
    def setUp(self, mock_log_callback, mock_init_oracle, mock_ctk):
        # Setup mocks to avoid GUI creation issues
        self.app = gui_app.HSFApp()
        self.app.adicionar_log = MagicMock()
        self.app.update_idletasks = MagicMock()
        self.app.after = MagicMock()
        
    def tearDown(self):
        if self.app.executando:
            self.app.parar_execucao()
            
    @patch('main.executar_ciclo_completo')
    def test_loop_execution_and_stop(self, mock_executar_ciclo):
        """Testa se o loop executa e para corretamente."""
        
        # Configurar mock para não falhar
        mock_executar_ciclo.return_value = True
        
        # Iniciar o ciclo
        self.app.executar_ciclo()
        self.assertTrue(self.app.executando)
        self.assertFalse(self.app.stop_event.is_set())
        
        # Aguardar um pouco para garantir que a thread iniciou e rodou pelo menos uma vez
        time.sleep(0.5)
        
        # Verificar se o ciclo foi chamado
        mock_executar_ciclo.assert_called()
        
        # Parar a execução
        self.app.parar_execucao()
        
        # Verificar se o evento de parada foi setado
        self.assertTrue(self.app.stop_event.is_set())
        self.assertTrue(self.app.parar_loop)
        
    @patch('main.executar_ciclo_completo')
    def test_wait_interruption(self, mock_executar_ciclo):
        """Testa se a espera é interrompida imediatamente ao parar."""
        mock_executar_ciclo.return_value = True
        
        # Vamos usar um timeout pequeno no wait real, mas queremos verificar se ele sai qdo setamos o evento
        # Na verdade, o codigo usa self.stop_event.wait(timeout), que retorna True se setado.
        
        # Iniciar execução
        self.app.executar_ciclo()
        time.sleep(0.5) # Deixa rodar o primeiro ciclo
        
        # Resetar mock para verificar chamadas subsequentes (não deve haver se pararmos logo)
        mock_executar_ciclo.reset_mock()
        
        # O app deve estar em "wait" agora (pois o próximo ciclo é só daqui a 1h)
        # Vamos parar
        start_time = time.time()
        self.app.parar_execucao()
        end_time = time.time()
        
        # A parada deve ser quase instantânea, não deve esperar 1 hora
        self.assertLess(end_time - start_time, 2.0)
        self.assertTrue(self.app.stop_event.is_set())

if __name__ == '__main__':
    unittest.main()
