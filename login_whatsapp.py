import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import get_wa_page, fechar_playwright

print("Iniciando Playwright para Login no WhatsApp...")
print("OBS: Iremos abrir os dois perfis ('geral' e 'emergencia') em sequencia para você escanear o QR Code de ambos se necessario.")

try:
    print("Acessando perfil: wpp_geral")
    page_geral = get_wa_page("geral")
    if "web.whatsapp.com" not in page_geral.url:
        page_geral.goto("https://web.whatsapp.com")
    print("1/2 - Por favor, escaneie o QR Code no navegador para o perfil GERAL.")
    print("Aguardando 60 segundos...")
    for i in range(60, 0, -10):
        print(f"Tempo restante GERAL: {i}s")
        time.sleep(10)
    print("Tempo GERAL encerrado.")
    
    print("Acessando perfil: wpp_emergencia")
    page_emergencia = get_wa_page("emergencia")
    if "web.whatsapp.com" not in page_emergencia.url:
        page_emergencia.goto("https://web.whatsapp.com")
    print("2/2 - Por favor, escaneie o QR Code no navegador para o perfil EMERGENCIA.")
    print("Aguardando 60 segundos...")
    for i in range(60, 0, -10):
        print(f"Tempo restante EMERGENCIA: {i}s")
        time.sleep(10)
    print("Tempo EMERGENCIA encerrado.")
    
except Exception as e:
    print(f"Ocorreu uma excecao: {e}")
finally:
    fechar_playwright()
    print("Playwright encerrado. Sucesso!")
