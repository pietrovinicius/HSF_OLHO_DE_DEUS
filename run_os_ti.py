import sys
import os

# Ensure the project directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import inicializar_oracle_client_global, ordens_de_servico_com_mais_de_2_dias, fechar_playwright

print("Iniciando teste de execucao de OS TI...")
if not inicializar_oracle_client_global():
    print("Falha ao inicializar o cliente Oracle. Saindo.")
    sys.exit(1)

try:
    print("Executando ordens_de_servico_com_mais_de_2_dias()...")
    ordens_de_servico_com_mais_de_2_dias()
    print("Execucao finalizada.")
except Exception as e:
    print(f"Ocorreu uma excecao: {e}")
finally:
    fechar_playwright()
    print("Playwright encerrado.")
