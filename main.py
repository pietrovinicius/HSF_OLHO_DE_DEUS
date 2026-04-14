#03/06/2025
#@PLima
#arquivo principal para execução do projeto

#cd c:\Pietro\Projetos\HSF_OLHO_DE_DEUS
#python -m venv .venv
#Set-ExecutionPolicy RemoteSigned
#.venv\Scripts\activate
#pip install -r requirements.txt
#python main.py


import os
import sys
import time
from datetime import datetime, timedelta
# import tkinter as tk  # Removido - não precisamos mais da interface gráfica
from multiprocessing import Process, Event # Importar Event
import oracledb
import re
import pandas as pd
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

# VARIÁVEIS GLOBAIS PARA GERENCIAMENTO DO PLAYWRIGHT
# Mantém instâncias para reutilização entre chamadas (Playwright Pro)
playwright_manager = None
browser_instance = None
page_whatsapp_global = None
page_emergencia_global = None

# SELETORES WHATSAPP (LEXICAL/META COMPATIBLE & BUSINESS SUPPORT)
WPP_SEARCH_SELECTOR = 'input[placeholder="Pesquisar ou começar uma nova conversa"], input[placeholder="Search or start new chat"], [data-testid="chat-list-search"], input[role="textbox"], div[role="textbox"]'
WPP_MESSAGE_SELECTOR = 'div[role="textbox"][aria-label^="Digite uma mensagem"], div[role="textbox"][aria-label^="Type a message"], [data-testid="conversation-compose-box-input"], div[title="Mensagem"]'
WPP_QRCODE_SELECTOR = 'canvas[aria-label="Scan me!"], [data-testid="qrcode"]'

# Variável global para controlar inicialização do Oracle Client
oracle_client_inicializado = False

def inicializar_oracle_client_global():
    """
    Inicializa o Oracle Client uma única vez para toda a aplicação.
    Deve ser chamado no início do programa.
    """
    global oracle_client_inicializado
    
    if oracle_client_inicializado:
        registrar_log("Oracle Client já inicializado anteriormente.")
        return True
        
    try:
        registrar_log("Inicializando Oracle Client globalmente...")
        caminho_instantclient = encontrar_diretorio_instantclient()
        
        if caminho_instantclient:
            try:
                oracledb.init_oracle_client(lib_dir=caminho_instantclient)
                oracle_client_inicializado = True
                registrar_log(f"Oracle Client inicializado com sucesso em: {caminho_instantclient}")
                return True
            except oracledb.Error as e:
                # Se já estiver inicializado (erro comum se chamar 2x), apenas loga e segue
                if "DPI-1047" in str(e): 
                    registrar_log("Oracle Client já estava inicializado (DPI-1047).")
                    oracle_client_inicializado = True
                    return True
                else:
                    registrar_log(f"Erro ao inicializar Oracle Client: {e}")
                    return False
        else:
            registrar_log("ERRO CRÍTICO: Diretório do Instant Client não encontrado.")
            return False
            
    except Exception as e:
        registrar_log(f"Erro inesperado ao inicializar Oracle Client: {e}")
        return False

def page_is_alive(page: Page) -> bool:
    """
    Verifica se a página do Playwright ainda está ativa e funcional.
    """
    if page is None:
        return False
    try:
        return not page.is_closed()
    except Exception:
        return False

def fechar_playwright():
    """
    Finaliza todas as instâncias do Playwright e fecha o navegador.
    """
    global playwright_manager, browser_instance, page_whatsapp_global, page_emergencia_global
    
    registrar_log("Encerrando instâncias do Playwright...")
    
    try:
        if page_whatsapp_global:
            page_whatsapp_global.context.close()
        if page_emergencia_global:
            page_emergencia_global.context.close()
        if browser_instance:
            browser_instance.close()
        if playwright_manager:
            playwright_manager.stop()
            
        registrar_log("Playwright encerrado com sucesso.")
    except Exception as e:
        registrar_log(f"Erro ao encerrar Playwright: {e}")
    finally:
        playwright_manager = None
        browser_instance = None
        page_whatsapp_global = None
        page_emergencia_global = None

def inicializar_playwright_engine():
    """Garante que o motor Playwright Sync esteja rodando."""
    global playwright_manager
    
    if playwright_manager is None:
        registrar_log("Iniciando Playwright Sync Engine...")
        playwright_manager = sync_playwright().start()
    return playwright_manager

def get_wa_page(tipo: str = "geral") -> Page:
    """
    Obtém ou cria uma página com contexto persistente único para o WhatsApp.
    Unificado conforme solicitação do usuário (v3.1.4).
    O parâmetro 'tipo' é mantido apenas para compatibilidade de assinatura.
    """
    global page_whatsapp_global
    
    # 1. Garante motor rodando
    inicializar_playwright_engine()
    
    # 2. Perfil Unificado (Entregando sempre o mesmo perfil independente do tipo)
    profile_dir = "wpp_geral"
    page_ref = page_whatsapp_global
        
    # Verifica se a página ainda está viva
    if page_is_alive(page_ref):
        return page_ref
        
    registrar_log(f"Criando novo contexto persistente para WhatsApp ({tipo})...")
    
    # Caminho do perfil (Playwright Pro - Context Isolation)
    dir_path = os.path.dirname(os.path.abspath(__file__))
    user_data_dir = os.path.join(dir_path, "profile", profile_dir)
    os.makedirs(user_data_dir, exist_ok=True)
    
    # Playwright Pro Arguments - Máxima Estabilidade em Windows
    browser_args = [
        "--no-sandbox", 
        "--disable-dev-shm-usage",
        "--disable-gpu", # Evita hangs em drivers de vídeo
        "--disable-software-rasterizer",
        "--disable-extensions",
        "--no-first-run",
        "--disable-notifications"
    ]
    
    try:
        context = playwright_manager.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            no_viewport=True,
            args=browser_args,
            slow_mo=50 # Pequeno delay para estabilidade de eventos
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        
        # Armazena globalmente
        page_whatsapp_global = page
            
        return page
    except Exception as e:
        registrar_log(f"ERRO CRÍTICO ao lançar contexto persistente: {e}")
        # Tentar limpar motor em caso de falha catastrófica
        fechar_playwright()
        raise

def esperar_e_diagnosticar_whatsapp(page: Page, timeout: int = 120000) -> Page:
    """
    Aguarda a barra de pesquisa do WhatsApp com diagnóstico inteligente.
    Se demorar, verifica QR Code e tira screenshot.
    """
    registrar_log("Aguardando barra de pesquisa (Diagnóstico Ativo)...")
    
    # Pasta de debug
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    debug_path = os.path.join(temp_dir, "debug_whatsapp.png")

    try:
        # 1. Espera curta inicial (15s)
        page.wait_for_selector(WPP_SEARCH_SELECTOR, state="visible", timeout=15000)
        return page
    except Exception:
        registrar_log("Busca demorando mais de 15s. Analisando tela...")
        
        # 2. Diagnóstico Visual
        try:
            page.screenshot(path=debug_path)
            registrar_log(f"Screenshot de diagnóstico salvo em: {debug_path}")
        except: pass

        # 3. Verificar QR Code
        if page.locator(WPP_QRCODE_SELECTOR).count() > 0:
            registrar_log("⚠️ AVISO: WhatsApp está deslogado (QR Code detectado). Intervenção manual necessária.")
        else:
            registrar_log("QR Code não detectado. Aguardando carregamento total da interface...")

        # 4. Espera o restante do tempo
        page.wait_for_selector(WPP_SEARCH_SELECTOR, state="visible", timeout=timeout - 15000)
        return page

def agora():
    agora = datetime.now()
    agora = agora.strftime("%Y-%m-%d %H-%M-%S")
    return str(agora)

# Variável global para callback de logs (usado pela GUI)
_log_callback = None

def set_log_callback(callback):
    """Define uma função de callback para receber logs em tempo real."""
    global _log_callback
    _log_callback = callback

def registrar_log(texto):
    """Função para registrar um texto em um arquivo de log."""
    diretorio_atual = os.getcwd()
    caminho_arquivo = os.path.join(diretorio_atual, 'log.txt')
    
    # Timestamp formatado
    timestamp = agora()
    
    # Print no console
    print(f"{timestamp} - {texto}")
    
    # Enviar para callback se existir (para GUI)
    if _log_callback:
        try:
            # Envia apenas o texto, a GUI adiciona seu próprio timestamp se necessário
            _log_callback(texto)
        except Exception:
            pass

    # Abre o arquivo em modo de append (adiciona texto ao final)
    with open(caminho_arquivo, 'a', encoding='utf-8') as arquivo:
        arquivo.write(f"{timestamp} - {texto}\n")

def encontrar_diretorio_instantclient() -> str | None:
    r"""
    Localiza o diretório do Oracle Instant Client baseado no Sistema Operacional.
    Caminhos esperados (dentro da pasta util):
    - Windows: util\instantclient-basiclite-windows
    - macOS: util\instantclient-basiclite-macos
    """
    registrar_log("encontrar_diretorio_instantclient - INÍCIO")
    
    # Obtém o diretório do script atual
    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    
    # Mapeamento por plataforma
    plataforma = sys.platform
    registrar_log(f"Plataforma detectada: {plataforma}")
    
    if plataforma == "win32":
        sub_pasta = os.path.join("util", "instantclient-basiclite-windows")
    elif plataforma == "darwin":
        sub_pasta = os.path.join("util", "instantclient-basiclite-macos")
    else:
        registrar_log(f"Sistema operacional '{plataforma}' não suportado automaticamente.")
        registrar_log("encontrar_diretorio_instantclient - FIM")
        return None

    caminho_completo = os.path.join(diretorio_base, sub_pasta)

    if os.path.exists(caminho_completo):
        registrar_log(f"Diretório Instant Client encontrado: {caminho_completo}")
        registrar_log("encontrar_diretorio_instantclient - FIM")
        return caminho_completo
    
    registrar_log(f"ERRO: Pasta não encontrada em: {caminho_completo}")
    registrar_log("encontrar_diretorio_instantclient - FIM")
    return None
  
def resultados_exames_intervalo_58_min():
    try:
        registrar_log(f'resultados_exames_intervalo_58_min - INICIO')

        # Inicialização do Oracle Client removida (agora é global)
        # caminho_instantclient = encontrar_diretorio_instantclient()
        # if caminho_instantclient:
        #     oracledb.init_oracle_client(lib_dir=caminho_instantclient)
        # else:
        #     registrar_log("Erro ao localizar o Instant Client. Verifique o nome da pasta e o caminho.")

        connection = oracledb.connect(user="TASY", password="aloisk", dsn="192.168.5.9:1521/TASYPRD")

        with connection:
            with connection.cursor() as cursor:
                #CARREGAR E EXECUTAR AQUI A HSF - RESULTADOS EXAMES COM INTERVALO DE 58 MINUTOS.SQL
                sql_file_name = 'HSF - RESULTADOS EXAMES COM INTERVALO DE 58 MINUTOS.sql'
                sql_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), sql_file_name)

                if not os.path.exists(sql_file_path):
                    registrar_log(f"Arquivo SQL não encontrado: {sql_file_path}")
                    return # Sai da função se o arquivo não existir

                with open(sql_file_path, 'r', encoding='utf-8') as f:
                    sql_query = f.read()

                registrar_log(f"Executando query SQL do arquivo: {sql_file_name}")
                cursor.execute(sql_query)
                resultados = cursor.fetchall()
                registrar_log(f"Query executada. {len(resultados)} linhas retornadas.")

                # Resultados são retornados para serem usados pela função de WhatsApp
                # for row in resultados: print(row)

        registrar_log(f'resultados_exames_intervalo_58_min - FIM')
        return resultados # Retorna a lista de resultados

    except oracledb.Error as erro:
        registrar_log(f"resultados_exames_intervalo_58_min - Erro no Oracle DB: {erro}")
        return None # Retorna None em caso de erro
    except Exception as erro: # Captura outros erros que não sejam do DB
        registrar_log(f"resultados_exames_intervalo_58_min - Erro geral: {erro}")
        return None # Retorna None em caso de erro

def resultados_hemogramas_intervalo_58_min():
    try:
        registrar_log(f'resultados_hemogramas_intervalo_58_min - INICIO')

        # Inicialização do Oracle Client removida (agora é global)
        # caminho_instantclient = encontrar_diretorio_instantclient()
        # if caminho_instantclient:
        #     oracledb.init_oracle_client(lib_dir=caminho_instantclient)
        # else:
        #     registrar_log("Erro ao localizar o Instant Client. Verifique o nome da pasta e o caminho.")

        connection = oracledb.connect(user="TASY", password="aloisk", dsn="192.168.5.9:1521/TASYPRD")

        with connection:
            with connection.cursor() as cursor:
                #CARREGAR E EXECUTAR AQUI A HSF - RESULTADOS EXAMES COM INTERVALO DE 5 MINUTOS.SQL
                sql_file_name = 'HSF - RESULTADOS EXAMES HEMOGRAMA COM INTERVALO DE 58 MINUTOS.sql'
                sql_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), sql_file_name)

                if not os.path.exists(sql_file_path):
                    registrar_log(f"Arquivo SQL não encontrado: {sql_file_path}")
                    return # Sai da função se o arquivo não existir

                with open(sql_file_path, 'r', encoding='utf-8') as f:
                    sql_query = f.read()

                registrar_log(f"Executando query SQL do arquivo: {sql_file_name}")
                cursor.execute(sql_query)
                resultados = cursor.fetchall()
                registrar_log(f"Query executada. {len(resultados)} linhas retornadas.")
                # Resultados são retornados para serem usados pela função de WhatsApp
                # for row in resultados: print(row)

        registrar_log(f'resultados_hemogramas_intervalo_58_min - FIM')
        return resultados # Retorna a lista de resultados

    except oracledb.Error as erro:
        registrar_log(f"resultados_exames_intervalo_58_min - Erro no Oracle DB: {erro}")
        return None # Retorna None em caso de erro
    except Exception as erro: # Captura outros erros que não sejam do DB
        registrar_log(f"resultados_exames_intervalo_58_min - Erro geral: {erro}")
        return None # Retorna None em caso de erro

def limpar_rtf_para_texto(rtf_text):
    """
    Limpa uma string RTF, removendo tags comuns e convertendo entidades
    para um texto mais próximo do plano.
    """
    if not rtf_text:
        return ""

    text = str(rtf_text) # Garantir que é uma string

    # 1. Remover blocos de controle RTF e tags comuns
    # Regex mais robusta para remover control words RTF (ex: \b, \par, \fs22)
    text = re.sub(r'\\[a-zA-Z0-9*]+(-?\d+)? ?', '', text)
    # Remover grupos RTF complexos, incluindo aqueles com informações de fonte, cor, etc.
    # Esta regex tenta ser mais abrangente.
    text = re.sub(r'\{\*?\\[^{}]+;\}|\{\*?(\\[a-zA-Z0-9]+)+\s*\}', '', text)
    # Remover chaves restantes que podem não ter sido pegas
    text = re.sub(r'[{}]', '', text) # Remove chaves restantes

    # 2. Converter entidades de caracteres RTF comuns
    # Adicione mais conforme necessário

    replacements = {
        "\\'e1": "á", "\\'E1": "Á",
        "\\'e9": "é", "\\'E9": "É",
        "\\'ed": "í", "\\'ED": "Í",
        "\\'f3": "ó", "\\'F3": "Ó",
        "\\'fa": "ú", "\\'FA": "Ú",
        "\\'e7": "ç", "\\'C7": "Ç",
        "\\'e3": "ã", "\\'E3": "Ã",
        "\\'f5": "õ", "\\'F5": "Õ",
        "\\'fc": "ü", "\\'FC": "Ü",
        "\\~": "~", # Tilde
        "\\^": "^", # Caret
        "." : "", # Ponto
        ";" : "",
        "default" : "",
        "Valores de Refer" : "",
        "eancia" : "",
        "\\'": "",
        "Courier" : "",
        "NewMicrosoft" : "",
        "Sans" : "",
        "Serif" : "",
        # Valores de referência a serem removidos
        "4,4 a 5,9 3,8 a 5,2 Milhões/mmb3": "",
        "13,0 a 18,0 12,0 a 16,0 g/dL": "",
        "40,0 a 53,0 35,0 a 47,0 %": "",
        "80,0 a 100,0 fl": "",
        "26,0 a 34 pg": "",
        "32,0 a 36,0 g/dL": "",
        "11,5 a 16,0 %": "",
        
        # Adicione outras entidades comuns que você encontrar
    }
    for rtf_code, char_code in replacements.items():
        text = text.replace(rtf_code, char_code)

    # 3. Remover múltiplos espaços e linhas em branco
    text = re.sub(r' +', ' ', text) # Substitui múltiplos espaços por un único espaço
    text = re.sub(r'(\r\n|\r|\n){2,}', '\n', text).strip() # Remove linhas em branco excessivas

    return text

def enviar_whatsapp_emergencia(mensagem_texto: str, modo_teste: bool = False):
    """
    Envia mensagem via WhatsApp para o grupo HSF - RECEPÇÃO - TEMPOS DA EMERGÊNCIA.
    Versão migrada para Playwright (Sync API) conforme GEMINI.md.
    """
    registrar_log("enviar_whatsapp_emergencia (Playwright) - INÍCIO")
    
    if not mensagem_texto or not mensagem_texto.strip():
        registrar_log("Nenhuma mensagem para enviar.")
        return
        
    if "Situação Normal - Nenhum paciente com tempos críticos" in mensagem_texto:
        registrar_log("Situação normal detectada - não enviando mensagem")
        return

    if modo_teste:
        registrar_log(f"[MODO TESTE] Mensagem Emergência: {mensagem_texto}")
        return

    page = get_wa_page()
    
    try:
        # 1. Navegação e Verificação de Estado
        if "web.whatsapp.com" not in page.url:
            registrar_log("Navegando para WhatsApp Web...")
            page.goto("https://web.whatsapp.com")
            page.wait_for_load_state("networkidle")
        
        registrar_log("Aguardando interface do WhatsApp (Sincronizando Mensagens)...")
        
        # 2. Localização do Campo de Pesquisa - Unificada e Dinâmica (Lexical Support)
        try:
            esperar_e_diagnosticar_whatsapp(page)
            campo_pesquisa = page.locator(WPP_SEARCH_SELECTOR).first
        except Exception:
            # Auditoria Visual Imediata (Rule GEMINI.md)
            try:
                screenshot_path = os.path.join(os.getcwd(), "temp", f"error_search_{agora().replace(':', '-')}.png")
                page.screenshot(path=screenshot_path)
                registrar_log(f"Screenshot de erro salva em: {screenshot_path}")
            except: pass

            registrar_log("ERRO: Timeout ao localizar barra de pesquisa do WhatsApp (Layout possivelmente alterado).")
            try:
                import pyautogui
                pyautogui.alert("O layout interno do WhatsApp da EMERGÊNCIA foi atualizado!\n\nO robô estourou o tempo limite de 2 minutos.\n\nContate a equipe Dev para manutenção.", "Aviso Crítico RPA")
            except: pass
            raise TimeoutError("Falha ao localizar campo de pesquisa (Layout alterado ou rede lenta)")

        # 3. Pesquisa do Grupo
        nome_grupo = "HSF - RECEPÇÃO - TEMPOS DA EMERGÊNCIA"
        campo_pesquisa.focus()
        campo_pesquisa.click(force=True)
        # Limpeza agressiva para despertar o React
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        campo_pesquisa.fill(nome_grupo)
        page.wait_for_timeout(2500)

        # 4. Seleção do Resultado
        xpath_resultado = f"//span[@title='{nome_grupo}'] | //span[text()='{nome_grupo}']"
        page.wait_for_selector(xpath_resultado, state="visible", timeout=10000)
        page.click(xpath_resultado)
        page.wait_for_timeout(1000)

        # 5. Envio da Mensagem
        page.wait_for_selector(WPP_MESSAGE_SELECTOR, state="visible", timeout=15000)
        campo_chat = page.locator(WPP_MESSAGE_SELECTOR).first
        
        # Limpeza de caracteres não-BMP (emojis problemáticos) mantendo acentos
        mensagem_limpa = re.sub(r'[^\x00-\x7F\u00C0-\u00FF\*\:\-\(\)\[\]\.\,\;\!\?\s\/]+', '', mensagem_texto)
        linhas = mensagem_limpa.split('\n')
        
        for i, linha in enumerate(linhas):
            if linha.strip():
                campo_chat.type(linha.strip(), delay=10)
            if i < len(linhas) - 1:
                page.keyboard.press("Shift+Enter")
                
        # 6. Botão Enviar com Fallbacks
        page.keyboard.press("Enter") # Playwright keyboard API é muito robusta
        registrar_log(f"Sucesso: Alerta disparado para o grupo {nome_grupo} (Enter pressionado).")
        
        page.wait_for_timeout(3000) # Cooldown reduzido
        
    except Exception as e:
        # Auditoria Visual Imediata
        try:
            temp_dir = os.path.join(os.getcwd(), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            screenshot_path = os.path.join(temp_dir, f"error_emergencia_{agora().replace(':', '-')}.png")
            page.screenshot(path=screenshot_path)
            registrar_log(f"Screenshot de erro salva em: {screenshot_path}")
        except: pass

        registrar_log(f"ERRO CRÍTICO em enviar_whatsapp_emergencia: {e}")

    registrar_log("enviar_whatsapp_emergencia - FIM")

def enviar_whatsapp_grupo(nome_grupo: str, mensagem_texto: str):
    """
    Função genérica e robusta para enviar mensagens via WhatsApp Web para qualquer grupo.
    Migrada para Playwright conforme GEMINI.md.
    """
    registrar_log(f"enviar_whatsapp_grupo({nome_grupo}) - INÍCIO")

    if not mensagem_texto or not mensagem_texto.strip():
        registrar_log("Nenhuma mensagem para enviar.")
        return

    page = get_wa_page("geral")
    
    try:
        # 1. Navegação
        if "web.whatsapp.com" not in page.url:
            page.goto("https://web.whatsapp.com")
            page.wait_for_load_state("networkidle")
        
        # 2. Pesquisa (Lexical Framework Support)
        try:
            esperar_e_diagnosticar_whatsapp(page)
            campo_pesquisa = page.locator(WPP_SEARCH_SELECTOR).first
        except Exception:
            try:
                path = os.path.join("temp", f"error_search_{nome_grupo}_{agora().replace(':','-')}.png")
                page.screenshot(path=path)
            except: pass

            registrar_log(f"ERRO: Timeout na pesquisa do grupo {nome_grupo}.")
            try:
                import pyautogui
                pyautogui.alert(f"O WhatsApp atualizou o layout de pesquisa!\n\nImpossível localizar a barra para: {nome_grupo}.", "Aviso Crítico RPA")
            except: pass
            raise TimeoutError("Falha ao localizar campo de pesquisa (Timeout 120s)")

        campo_pesquisa.focus()
        campo_pesquisa.click(force=True)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        campo_pesquisa.fill(nome_grupo)
        page.wait_for_timeout(2500)

        # 3. Seleção do Grupo
        xpath_resultado = f"//span[@title='{nome_grupo}'] | //span[text()='{nome_grupo}']"
        page.wait_for_selector(xpath_resultado, state="visible", timeout=8000)
        page.click(xpath_resultado)
        page.wait_for_timeout(1000)

        # 4. Envio
        page.wait_for_selector(WPP_MESSAGE_SELECTOR, state="visible", timeout=15000)
        campo_chat = page.locator(WPP_MESSAGE_SELECTOR).first
        
        mensagem_limpa = re.sub(r'[^\x00-\x7F\u00C0-\u00FF\*\:\-\(\)\[\]\.\,\;\!\?\s\/]+', '', mensagem_texto)
        linhas = mensagem_limpa.split('\n')
        
        for i, linha in enumerate(linhas):
            if linha.strip():
                campo_chat.type(linha.strip(), delay=10)
            if i < len(linhas) - 1:
                page.keyboard.press("Shift+Enter")
        
        # 5. Envio Final
        page.keyboard.press("Enter")
        registrar_log(f"Sucesso: Mensagem enviada para o grupo {nome_grupo} (Payload: {len(mensagem_texto)} caracteres).")
        page.wait_for_timeout(2000)

    except Exception as e:
        try:
            path = os.path.join("temp", f"error_{nome_grupo}_{agora().replace(':','-')}.png")
            page.screenshot(path=path)
            registrar_log(f"Screenshot de erro salva em: {path}")
        except: pass
        registrar_log(f"Erro em enviar_whatsapp_grupo({nome_grupo}): {e}")

    registrar_log(f"enviar_whatsapp_grupo({nome_grupo}) - FIM")

def enviar_whatsapp_laboratorio(lista_exames, modo_teste: bool = False):
    """
    Envia resultados críticos do laboratório via WhatsApp.
    Migrada para Playwright conforme GEMINI.md.
    """
    registrar_log("enviar_whatsapp_laboratorio - INÍCIO")
    
    if not lista_exames:
        registrar_log("Nenhum exame para enviar.")
        return

    if modo_teste:
        registrar_log(f"[MODO TESTE] Enviando {len(lista_exames)} exames para Laboratório")
        return

    page = get_wa_page()
    
    try:
        # 1. Navegação
        if "web.whatsapp.com" not in page.url:
            page.goto("https://web.whatsapp.com")
            page.wait_for_load_state("networkidle")
            
        # 2. Pesquisa (Lexical Framework Support)
        nome_grupo = "LAB - VALORES CRÍTICOS"
        try:
            esperar_e_diagnosticar_whatsapp(page)
            campo_pesq_lab = page.locator(WPP_SEARCH_SELECTOR).first
        except Exception:
            try:
                path = os.path.join("temp", f"error_search_lab_{agora().replace(':','-')}.png")
                page.screenshot(path=path)
            except: pass

            registrar_log("ERRO: Timeout na pesquisa do Laboratório.")
            try:
                import pyautogui
                pyautogui.alert("WhatsApp Lab report atualizou layout.\nBarra de pesquisa não encontrada no limite de 2 minutos.", "Falha Laboratório")
            except: pass
            raise TimeoutError("Timeout localizando busca do laboratório")
            
        campo_pesq_lab.focus()
        campo_pesq_lab.click(force=True)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        campo_pesq_lab.fill(nome_grupo)
        page.wait_for_timeout(2500)
        
        # 3. Seleção
        xpath_resultado = f"//span[@title='{nome_grupo}'] | //span[text()='{nome_grupo}']"
        page.wait_for_selector(xpath_resultado, state="visible", timeout=8000)
        page.click(xpath_resultado)
        
        # 4. Composição da Mensagem Complexa
        page.wait_for_selector(WPP_MESSAGE_SELECTOR, state="visible", timeout=15000)
        campo_chat_lab = page.locator(WPP_MESSAGE_SELECTOR).first
        
        agora_str = datetime.now().strftime("%d/%m/%Y às %Hh%Mm")
        cabecalho = f"*{agora_str}*\n\n*Analista Plantonista confirmar ciência do(s) resultado(s) crítico(s) encontrado(s):*\n"
        
        campo_chat_lab.type(cabecalho, delay=10)
        page.keyboard.press("Shift+Enter")
        
        for exame in lista_exames:
            for item in exame:
                if item.strip():
                    item_limpo = re.sub(r'[^\x00-\x7F\u00C0-\u00FF\*\:\-\(\)\[\]\.\,\;\!\?\s\/]+', '', item)
                    campo_chat_lab.type(item_limpo.strip(), delay=10)
                    page.keyboard.press("Shift+Enter")
            page.keyboard.press("Shift+Enter") # Separador entre exames
            
        # 5. Envio Final
        page.keyboard.press("Enter")
        registrar_log(f"Sucesso: {len(lista_exames)} resultados críticos enviados para o Laboratório.")
        page.wait_for_timeout(3000)

    except Exception as e:
        registrar_log(f"Erro em enviar_whatsapp_laboratorio: {e}")
        try:
            path = os.path.join("temp", f"error_lab_{agora().replace(':','-')}.png")
            page.screenshot(path=path)
        except: pass

    registrar_log("enviar_whatsapp_laboratorio - FIM")
    registrar_log("enviar_whatsapp_laboratorio - FIM")

def processar_coagulogramas_criticos(resultados_hemogramas_brutos):
    """
    Processa os resultados brutos de exames (incluindo RTF) para identificar
    coagulogramas com valores críticos de INR.
    Retorna uma lista de dicionários com os detalhes dos coagulogramas críticos.
    """
    registrar_log('processar_coagulogramas_criticos - INÍCIO')
    coagulogramas_criticos_encontrados = []

    if not resultados_hemogramas_brutos:
        registrar_log("Nenhum resultado bruto de hemogramas/exames para processar coagulogramas.")
        return coagulogramas_criticos_encontrados

    for linha_completa in resultados_hemogramas_brutos:
        if len(linha_completa) > 2:
            nr_prescricao = linha_completa[0]
            ds_resultado_valor_rtf = linha_completa[2]
            # NM_PACIENTE não está disponível diretamente aqui, então não será incluído
            # DT_EXAME também não está disponível

            if ds_resultado_valor_rtf and "COAGULOGRAMA" in str(ds_resultado_valor_rtf).upper():
                texto_limpo = limpar_rtf_para_texto(ds_resultado_valor_rtf)
                registrar_log(f'texto_limpo: {texto_limpo}')
                # Regex para extrair INR: Procura "INR", seguido por espaços/pontos e ":", depois o valor.
                match_inr = re.search(r"INR\s*\.*\s*:\s*([0-9,.]+)", texto_limpo, re.IGNORECASE)
                
                if match_inr:
                    try:
                        inr_str = match_inr.group(1).strip().replace(",", ".")
                        inr_val = float(inr_str)
                        
                        # Critério de criticidade para INR: > 6.00
                        if inr_val > 6.00:
                            coagulogramas_criticos_encontrados.append({
                                "prescricao": nr_prescricao,
                                # "paciente": nm_paciente, # Não disponível
                                "parametro": "INR",
                                "valor": inr_val,
                                "unidade": "", # INR não tem unidade explícita comum
                                "criterio": "> 6.00"
                            })
                            registrar_log(f"Coagulograma crítico encontrado: Prescrição {nr_prescricao}, INR: {inr_val}")
                            registrar_log(f"coagulogramas_criticos_encontrados: {coagulogramas_criticos_encontrados}\n")
                    except ValueError:
                        registrar_log(f"Prescricao {nr_prescricao} (Coagulograma): Valor de INR '{inr_str}' não é numérico.")

    registrar_log('processar_coagulogramas_criticos - FIM')
    return coagulogramas_criticos_encontrados

def processar_hepatogramas_criticos(resultados_exames_brutos):
    """
    Processa os resultados brutos de exames (incluindo RTF) para identificar
    hepatogramas com valores críticos de Plaquetas e Bilirrubina.
    Retorna uma lista de dicionários com os detalhes dos hepatogramas críticos.
    """
    registrar_log('processar_hepatogramas_criticos - INÍCIO')
    hepatogramas_criticos_encontrados = []

    if not resultados_exames_brutos:
        registrar_log("Nenhum resultado bruto de exames para processar hepatogramas.")
        return hepatogramas_criticos_encontrados

    for linha_completa in resultados_exames_brutos:
        if len(linha_completa) > 2:
            nr_prescricao = linha_completa[0]
            # nm_paciente = linha_completa[1] # Não usado no dicionário crítico, mas bom para log
            ds_resultado_valor_rtf = linha_completa[2]

            # Filtrar preliminarmente por RTFs que contêm "HEPATOGRAMA"
            if ds_resultado_valor_rtf and "HEPATOGRAMA" in str(ds_resultado_valor_rtf).upper():
                texto_limpo = limpar_rtf_para_texto(ds_resultado_valor_rtf)
                registrar_log(f'texto_limpo: {texto_limpo}')

                # Regex para extrair "Contagem de plaquetas"
                # Procura "Contagem de plaquetas" ou "Plaquetas", seguido por espaços/pontos e ":", depois o valor.
                # Captura opcionalmente "mil" para ajustar a escala.
                match_plaquetas = re.search(r"(?:Contagem de plaquetas|Plaquetas)\s*[:\s]*\s*([0-9,.]+)\s*(mil)?(?:/uL|/mm3|/\xb5L)?", texto_limpo, re.IGNORECASE)

                if match_plaquetas:
                    try:
                        plaquetas_str = match_plaquetas.group(1).strip().replace(",", ".")
                        plaquetas_val = float(plaquetas_str)
                        unidade_mil = match_plaquetas.group(2)
                        if unidade_mil and unidade_mil.lower() == 'mil':
                            plaquetas_val *= 1000 # Converte de "mil" para o valor absoluto

                        # Critério de criticidade: < 20.000/uL ou > 1.000.000/uL
                        if plaquetas_val < 20000.0 or plaquetas_val > 1000000.0:
                            hepatogramas_criticos_encontrados.append({
                                "prescricao": nr_prescricao,
                                "parametro": "Plaquetas (Hepatograma)",
                                "valor": plaquetas_val,
                                "unidade": "/uL"
                            })
                            registrar_log(f"Hepatograma crítico (Plaquetas) encontrado: Prescrição {nr_prescricao}, Valor: {plaquetas_val}")
                    except ValueError:
                        registrar_log(f"Prescricao {nr_prescricao} (Hepatograma): Valor de Plaquetas '{plaquetas_str}' não é numérico.")

                # Regex para extrair Bilirrubina (Total)
                # Procura "Bilirrubina Total" ou apenas "Bilirrubina", seguido por espaços/pontos e ":", depois o valor.
                match_bilirrubina = re.search(r"(Bilirrubina\s*(?:Total)?)\s*[:\s]*\s*([0-9,.]+)\s*(?:mg/dL)?", texto_limpo, re.IGNORECASE)

                if match_bilirrubina:
                    try:
                        bilirrubina_str = match_bilirrubina.group(2).strip().replace(",", ".")
                        bilirrubina_val = float(bilirrubina_str)

                        # Critério de criticidade: Bilirrubina > 15 mg/dL
                        if bilirrubina_val > 15.0:
                            hepatogramas_criticos_encontrados.append({
                                "prescricao": nr_prescricao,
                                "parametro": "Bilirrubina (Hepatograma)",
                                "valor": bilirrubina_val,
                                "unidade": "mg/dL"
                            })
                            registrar_log(f"Hepatograma crítico (Bilirrubina) encontrado: Prescrição {nr_prescricao}, Valor: {bilirrubina_val}")
                    except ValueError:
                        registrar_log(f"Prescricao {nr_prescricao} (Hepatograma): Valor de Bilirrubina '{bilirrubina_str}' não é numérico.")

    registrar_log('processar_hepatogramas_criticos - FIM')
    return hepatogramas_criticos_encontrados

def processar_lipidogramas_criticos(resultados_exames_brutos):
    """
    Processa os resultados brutos de exames (incluindo RTF) para identificar
    lipidogramas com valores críticos de Colesterol Total.
    Retorna uma lista de dicionários com os detalhes dos lipidogramas críticos.
    """
    registrar_log('processar_lipidogramas_criticos - INÍCIO')
    lipidogramas_criticos_encontrados = []

    if not resultados_exames_brutos:
        registrar_log("Nenhum resultado bruto de exames para processar lipidogramas.")
        return lipidogramas_criticos_encontrados

    for linha_completa in resultados_exames_brutos:
        if len(linha_completa) > 2:
            nr_prescricao = linha_completa[0]
            ds_resultado_valor_rtf = linha_completa[2]

            # Filtrar preliminarmente por RTFs que contêm "LIPIDOGRAMA" ou "COLESTEROL"
            if ds_resultado_valor_rtf and \
               ("LIPIDOGRAMA" in str(ds_resultado_valor_rtf).upper() or \
                "COLESTEROL" in str(ds_resultado_valor_rtf).upper()):
                
                texto_limpo = limpar_rtf_para_texto(ds_resultado_valor_rtf)
                registrar_log(f'texto_limpo: {texto_limpo}')
                
                # Regex para extrair "COLESTEROL TOTAL"
                # Procura "COLESTEROL TOTAL", seguido opcionalmente por espaços/pontos e ":", depois o valor.
                match_colesterol = re.search(r"COLESTEROL\s*TOTAL\s*\.*\s*:?\s*([0-9,.]+)", texto_limpo, re.IGNORECASE)
                
                if match_colesterol:
                    try:
                        colesterol_str = match_colesterol.group(1).strip().replace(",", ".")
                        colesterol_val = float(colesterol_str)
                        
                        # Critério de criticidade: Colesterol Total > 0 (conforme Valores Criticos.py)
                        if colesterol_val > 0:
                            lipidogramas_criticos_encontrados.append({
                                "prescricao": nr_prescricao,
                                "parametro": "Colesterol Total",
                                "valor": colesterol_val,
                                "unidade": "mg/dL"
                            })
                            registrar_log(f"Lipidograma crítico encontrado: Prescrição {nr_prescricao}, Colesterol Total: {colesterol_val}")
                    except ValueError:
                        registrar_log(f"Prescricao {nr_prescricao} (Lipidograma): Valor de Colesterol Total '{colesterol_str}' não é numérico.")

    registrar_log('processar_lipidogramas_criticos - FIM')
    return lipidogramas_criticos_encontrados

def processar_alertas_tempo_recepcao(df):
    """
    Processa e envia alertas para registros com Tempo Recepção > 10 minutos.
    
    Args:
        df (pandas.DataFrame): DataFrame com dados da emergência
    
    Returns:
        None
    """
    registrar_log("processar_alertas_tempo_recepcao - INÍCIO")
    
    try:
        # Filtra registros com Tempo Recepção > 10 minutos
        filtro_recepcao = df[df['TOTAL_RECEP'].apply(converter_tempo_para_minutos) > 10].copy()
        
        if filtro_recepcao.empty:
            registrar_log("Nenhum registro encontrado com Tempo Recepção > 10 minutos")
            mensagem = f"{datetime.now().strftime('%d/%m/%Y às %Hh%Mm')}\n\n"
            mensagem += "Prezados, informo que não foram identificados tempos críticos de atendimentos na Emergência para Tempo de Recepção.\n\n"
            mensagem += "✅ Situação Normal - Nenhum paciente com tempo de recepção superior a 10 minutos"
        else:
            registrar_log(f"Encontrados {len(filtro_recepcao)} registros com Tempo Recepção > 10 minutos")
            
            mensagem = f"{datetime.now().strftime('%d/%m/%Y às %Hh%Mm')}\n\n"
            mensagem += "Prezados, informo a identificação de tempo(s) crítico(s) de atendimento(s) na Emergência:\n"
            mensagem += "\n*--- TEMPOS ENCONTRADOS ---*\n"
            
            for index, row in filtro_recepcao.iterrows():
                tempo_recepcao_min = converter_tempo_para_minutos(row['TOTAL_RECEP'])
                mensagem += f"Paciente: {row['PACIENTE']}\n"
                mensagem += f"Triagem Classificação: {row['TRIAGEM_CLASSIFICACAO']}\n"
                mensagem += f"Tempo Recepção: {tempo_recepcao_min} minutos\n"
                if len(filtro_recepcao) > 1:
                    mensagem += "\n"
        
        # Envia mensagem via WhatsApp
        enviar_whatsapp_emergencia(mensagem)
        registrar_log("Alerta de Tempo Recepção processado e enviado")
        
    except Exception as e:
        registrar_log(f"Erro ao processar alertas de Tempo Recepção: {e}")
    
    registrar_log("processar_alertas_tempo_recepcao - FIM")

def processar_alertas_tempo_triagem(df):
    """
    Processa e envia alertas para registros com Tempo Triagem > 5 minutos.
    
    Args:
        df (pandas.DataFrame): DataFrame com dados da emergência
    
    Returns:
        None
    """
    registrar_log("processar_alertas_tempo_triagem - INÍCIO")
    
    try:
        # Calcular Tempo Triagem baseado em DT_INICIO_TRIAGEM e DT_FIM_TRIAGEM
        df_copia = df.copy()
        if 'DT_INICIO_TRIAGEM' in df_copia.columns and 'DT_FIM_TRIAGEM' in df_copia.columns:
            df_copia['DT_INICIO_TRIAGEM'] = pd.to_datetime(df_copia['DT_INICIO_TRIAGEM'], errors='coerce')
            df_copia['DT_FIM_TRIAGEM'] = pd.to_datetime(df_copia['DT_FIM_TRIAGEM'], errors='coerce')
            df_copia['TEMPO_TRIAGEM_MINUTOS'] = (df_copia['DT_FIM_TRIAGEM'] - df_copia['DT_INICIO_TRIAGEM']).dt.total_seconds() / 60
        else:
            registrar_log("Colunas de triagem não encontradas")
            return
        
        # Filtra registros com Tempo Triagem > 5 minutos
        filtro_triagem = df_copia[df_copia['TEMPO_TRIAGEM_MINUTOS'] > 5].copy()
        
        if filtro_triagem.empty:
            registrar_log("Nenhum registro encontrado com Tempo Triagem > 5 minutos")
            mensagem = f"{datetime.now().strftime('%d/%m/%Y às %Hh%Mm')}\n\n"
            mensagem += "Prezados, informo que não foram identificados tempos críticos de atendimentos na Emergência para Tempo de Triagem.\n\n"
            mensagem += "✅ Situação Normal - Nenhum paciente com tempo de triagem superior a 5 minutos"
        else:
            registrar_log(f"Encontrados {len(filtro_triagem)} registros com Tempo Triagem > 5 minutos")
            
            mensagem = f"{datetime.now().strftime('%d/%m/%Y às %Hh%Mm')}\n\n"
            mensagem += "Prezados, informo a identificação de tempo(s) crítico(s) de atendimento(s) na Emergência:\n\n"
            mensagem += "\n*--- TEMPOS ENCONTRADOS ---*\n"
            
            for index, row in filtro_triagem.iterrows():
                tempo_triagem_min = int(row['TEMPO_TRIAGEM_MINUTOS'])
                mensagem += f"Paciente: {row['PACIENTE']}\n"
                mensagem += f"Triagem Classificação: {row['TRIAGEM_CLASSIFICACAO']}\n"
                mensagem += f"Tempo Triagem: {tempo_triagem_min} minutos\n"
                if len(filtro_triagem) > 1:
                    mensagem += "\n"
        
        # Envia mensagem via WhatsApp
        enviar_whatsapp_emergencia(mensagem)
        registrar_log("Alerta de Tempo Triagem processado e enviado")
        
    except Exception as e:
        registrar_log(f"Erro ao processar alertas de Tempo Triagem: {e}")
    
    registrar_log("processar_alertas_tempo_triagem - FIM")

def processar_alertas_espera_medico(df):
    """
    Processa e envia alertas para registros com Espera por Médico > 5 minutos.
    
    Args:
        df (pandas.DataFrame): DataFrame com dados da emergência
    
    Returns:
        None
    """
    registrar_log("processar_alertas_espera_medico - INÍCIO")
    
    try:
        # Filtra registros com Espera por Médico > 5 minutos
        filtro_espera = df[df['TEMPO_ESPERA_ATEND'].apply(converter_tempo_para_minutos) > 5].copy()
        
        if filtro_espera.empty:
            registrar_log("Nenhum registro encontrado com Espera por Médico > 5 minutos")
            mensagem = f"{datetime.now().strftime('%d/%m/%Y às %Hh%Mm')}\n\n"
            mensagem += "Prezados, informo que não foram identificados tempos críticos de atendimentos na Emergência para Espera por Médico.\n\n"
            mensagem += "✅ Situação Normal - Nenhum paciente com espera por médico superior a 5 minutos"
        else:
            registrar_log(f"Encontrados {len(filtro_espera)} registros com Espera por Médico > 5 minutos")
            
            mensagem = f"{datetime.now().strftime('%d/%m/%Y às %Hh%Mm')}\n\n"
            mensagem += "Prezados, informo a identificação de tempo(s) crítico(s) de atendimento(s) na Emergência:\n\n"
            mensagem += "\n*--- TEMPOS ENCONTRADOS ---*\n"
            
            for index, row in filtro_espera.iterrows():
                tempo_espera_min = converter_tempo_para_minutos(row['TEMPO_ESPERA_ATEND'])
                mensagem += f"Paciente: {row['PACIENTE']}\n"
                mensagem += f"Triagem Classificação: {row['TRIAGEM_CLASSIFICACAO']}\n"
                mensagem += f"Espera por médico: {tempo_espera_min} minutos\n"
                if len(filtro_espera) > 1:
                    mensagem += "\n"
        
        # Envia mensagem via WhatsApp
        enviar_whatsapp_emergencia(mensagem)
        registrar_log("Alerta de Espera por Médico processado e enviado")
        
    except Exception as e:
        registrar_log(f"Erro ao processar alertas de Espera por Médico: {e}")
    
    registrar_log("processar_alertas_espera_medico - FIM")

def processar_alertas_tempo_final_fila(df):
    """
    Processa e envia alertas para registros com Tempo Final da Fila > 30 minutos.
    
    Args:
        df (pandas.DataFrame): DataFrame com dados da emergência
    
    Returns:
        None
    """
    registrar_log("processar_alertas_tempo_final_fila - INÍCIO")
    
    try:
        # Filtra registros com Tempo Final da Fila > 30 minutos
        filtro_fila = df[df['PACIENTE_SENHA_FILA_FIM'].apply(converter_tempo_para_minutos) > 30].copy()
        
        if filtro_fila.empty:
            registrar_log("Nenhum registro encontrado com Tempo Final da Fila > 30 minutos")
            mensagem = f"{datetime.now().strftime('%d/%m/%Y às %Hh%Mm')}\n\n"
            mensagem += "Prezados, informo que não foram identificados tempos críticos de atendimentos na Emergência para Tempo Final da Fila.\n\n"
            mensagem += "✅ Situação Normal - Nenhum paciente com tempo final da fila superior a 30 minutos"
        else:
            registrar_log(f"Encontrados {len(filtro_fila)} registros com Tempo Final da Fila > 30 minutos")
            
            mensagem = f"{datetime.now().strftime('%d/%m/%Y às %Hh%Mm')}\n\n"
            mensagem += "Prezados, informo a identificação de tempo(s) crítico(s) de atendimento(s) na Emergência:\n\n"
            mensagem += "\n*--- TEMPOS ENCONTRADOS ---*\n"
            
            for index, row in filtro_fila.iterrows():
                tempo_fila_min = converter_tempo_para_minutos(row['PACIENTE_SENHA_FILA_FIM'])
                mensagem += f"Paciente: {row['PACIENTE']}\n"
                mensagem += f"Triagem Classificação: {row['TRIAGEM_CLASSIFICACAO']}\n"
                mensagem += f"Tempo Final da Fila: {tempo_fila_min} minutos\n"
                if len(filtro_fila) > 1:
                    mensagem += "\n"
        
        # Envia mensagem via WhatsApp
        enviar_whatsapp_emergencia(mensagem)
        registrar_log("Alerta de Tempo Final da Fila processado e enviado")
        
    except Exception as e:
        registrar_log(f"Erro ao processar alertas de Tempo Final da Fila: {e}")
    
    registrar_log("processar_alertas_tempo_final_fila - FIM")

def processar_alertas_tempo_unificado(df):
    """
    Processa e envia alertas unificados agrupando todos os tempos críticos por paciente.
    
    Args:
        df (pandas.DataFrame): DataFrame com dados da emergência
    
    Returns:
        None
    """
    registrar_log("processar_alertas_tempo_unificado - INÍCIO")
    
    try:
        # Criar uma cópia do dataframe para trabalhar
        df_copia = df.copy()
        
        # Calcular Tempo Triagem baseado em DT_INICIO_TRIAGEM e DT_FIM_TRIAGEM
        if 'DT_INICIO_TRIAGEM' in df_copia.columns and 'DT_FIM_TRIAGEM' in df_copia.columns:
            df_copia['DT_INICIO_TRIAGEM'] = pd.to_datetime(df_copia['DT_INICIO_TRIAGEM'], errors='coerce')
            df_copia['DT_FIM_TRIAGEM'] = pd.to_datetime(df_copia['DT_FIM_TRIAGEM'], errors='coerce')
            df_copia['TEMPO_TRIAGEM_MINUTOS'] = (df_copia['DT_FIM_TRIAGEM'] - df_copia['DT_INICIO_TRIAGEM']).dt.total_seconds() / 60
            df_copia['TEMPO_TRIAGEM_MINUTOS'] = df_copia['TEMPO_TRIAGEM_MINUTOS'].apply(lambda x: int(x) if pd.notna(x) else 0)
        
        # Calcular tempos em minutos para cada tipo
        df_copia['TEMPO_RECEPCAO_MIN'] = df_copia['TOTAL_RECEP'].apply(converter_tempo_para_minutos)
        df_copia['TEMPO_ESPERA_MEDICO_MIN'] = df_copia['TEMPO_ESPERA_ATEND'].apply(converter_tempo_para_minutos)
        df_copia['TEMPO_FILA_MIN'] = df_copia['PACIENTE_SENHA_FILA_FIM'].apply(converter_tempo_para_minutos)
        
        # Dicionário para agrupar pacientes com tempos críticos
        pacientes_criticos = {}
        
        # Verificar cada paciente e seus tempos críticos
        for index, row in df_copia.iterrows():
            nr_atendimento = row['NR_ATENDIMENTO']
            paciente = row['PACIENTE']
            classificacao = row['TRIAGEM_CLASSIFICACAO']
            inicio_atendimento = row['ATENDIMENTO_PACIENTE_DT_INICIO']
            
            # Lista de tempos críticos para este paciente
            tempos_criticos = []
            
            # Verificar Tempo Recepção > 10 minutos
            if row['TEMPO_RECEPCAO_MIN'] > 10:
                tempos_criticos.append(f"⏰ *Tempo Recepção:* {row['TEMPO_RECEPCAO_MIN']} minutos")
            
            # Verificar Tempo Triagem > 5 minutos
            if 'TEMPO_TRIAGEM_MINUTOS' in row and row['TEMPO_TRIAGEM_MINUTOS'] > 5:
                tempos_criticos.append(f"⏰ *Tempo Triagem:* {row['TEMPO_TRIAGEM_MINUTOS']} minutos")
            
            # Verificar Espera por Médico > 5 minutos
            if row['TEMPO_ESPERA_MEDICO_MIN'] > 5:
                tempos_criticos.append(f"⏰ *Espera por médico:* {row['TEMPO_ESPERA_MEDICO_MIN']} minutos")
            
            # Verificar Tempo Final da Fila > 30 minutos
            if row['TEMPO_FILA_MIN'] > 30:
                tempos_criticos.append(f"⏰ *Tempo Final da Fila:* {row['TEMPO_FILA_MIN']} minutos")
            
            # Se há tempos críticos, adicionar ao dicionário
            if tempos_criticos:
                pacientes_criticos[nr_atendimento] = {
                    'paciente': paciente,
                    'classificacao': classificacao,
                    'inicio_atendimento': inicio_atendimento,
                    'fila': row.get('DS_FILA', 'N/A'),  # Adiciona informação da fila
                    'tempos_criticos': tempos_criticos
                }
        
        # Gerar mensagem unificada
        if not pacientes_criticos:
            registrar_log("Nenhum paciente encontrado com tempos críticos")
            mensagem = "🔴 *ALERTA TEMPO DE EMERGÊNCIA*\n\n"
            mensagem += "Prezados, informo que não foram identificados tempo(s) crítico(s) de atendimento(s) na EMERGÊNCIA\n\n"
            mensagem += f"{datetime.now().strftime('%d/%m/%Y às %Hh%Mm')}\n\n"
            mensagem += "✅ Situação Normal - Nenhum paciente com tempos críticos"
        else:
            registrar_log(f"Encontrados {len(pacientes_criticos)} pacientes com tempos críticos")
            
            mensagem = "🔴 *ALERTA TEMPO DE EMERGÊNCIA*\n\n"
            mensagem += "Prezados, informo a identificação de tempo(s) crítico(s) de atendimento(s) na EMERGÊNCIA\n\n"
            mensagem += f"{datetime.now().strftime('%d/%m/%Y às %Hh%Mm')}\n\n"
            mensagem += "\n*--- TEMPOS ENCONTRADOS ---*\n"
            
            for nr_atendimento, dados in pacientes_criticos.items():
                mensagem += f"🏥 *Atendimento:* {nr_atendimento}\n"
                mensagem += f"✅ *Paciente:* {dados['paciente']}\n"
                mensagem += f"🎯 *Fila:* {dados['fila']}\n"
                mensagem += f"📅 *Início Atendimento:* {dados['inicio_atendimento']}\n"
                mensagem += f"🔍 *Classificação:* {dados['classificacao']}\n"
                
                # Adicionar todos os tempos críticos deste paciente
                for tempo in dados['tempos_criticos']:
                    mensagem += f"{tempo}\n"
                
                # Separador entre pacientes (se houver mais de um)
                if len(pacientes_criticos) > 1:
                    mensagem += "\n" + "─" * 40 + "\n\n"
        
        # Envia mensagem via WhatsApp
        enviar_whatsapp_emergencia(mensagem)
        registrar_log("Alerta unificado de tempos críticos processado e enviado")
        
    except Exception as e:
        registrar_log(f"Erro ao processar alertas unificados: {e}")
    
    registrar_log("processar_alertas_tempo_unificado - FIM")

def logica_principal_exames():
    """Lógica principal que executa a verificação de todos os exames críticos."""
    registrar_log("logica_principal_background - INÍCIO")
    # Defina True para testar sem enviar mensagens reais, False para operação normal
    MODO_TESTE_WHATSAPP = False  
    
    registrar_log("Executando ciclo da lógica principal...")
    lista_de_resultados = resultados_exames_intervalo_58_min()
    registrar_log(f"lista_de_resultados: {lista_de_resultados}")        
    enviar_whatsapp_laboratorio(lista_de_resultados, modo_teste=MODO_TESTE_WHATSAPP)
    
    # --- INÍCIO DO PROCESSAMENTO DE HEMOGRAMAS CRÍTICOS ---
    registrar_log("Iniciando processamento de hemogramas críticos...")
    resultados_hemogramas = resultados_hemogramas_intervalo_58_min()
    if resultados_hemogramas:
        mensagens_hemogramas_criticos_whatsapp = []
        ###################################################################################################
        #VERIFICACOES DOS EXAMES DE DENTRO D HEMOGRAMA:
        if resultados_hemogramas is not None and resultados_hemogramas:
            hemogramas_criticos_encontrados = [] # Lista para dados brutos dos críticos
            for i, linha_completa in enumerate(resultados_hemogramas):
                if len(linha_completa) > 2:
                    nr_prescricao = linha_completa[0]
                    ds_resultado_valor_rtf = linha_completa[2]

                    if ds_resultado_valor_rtf and "HEMOGRAMA" in str(ds_resultado_valor_rtf).upper():
                        texto_limpo = limpar_rtf_para_texto(ds_resultado_valor_rtf)
                        
                        padroes_extracao = {
                            "Hemácias": r"Hemácias[\s\.]*:\s*([0-9,.]+)\s*Milhões/mmb3",
                            "Hemoglobina": r"Hemoglobina[\s\.]*:\s*([0-9,.]+)\s*g/dL",
                            "Hematocrito": r"Hematócrito[\s\.]*:\s*([0-9,.]+)\s*%",
                            "VCM": r"VCM[\s\.]*:\s*([0-9,.]+)\s*fl",
                            "HCM": r"HCM[\s\.]*:\s*([0-9,.]+)\s*pg",
                            "CHCM": r"CHCM[\s\.]*:\s*([0-9,.]+)\s*g/dL",
                            "RDW": r"RDW[\s\.]*:\s*([0-9,.]+)\s*%",
                            "Eritroblastos": r"Eritroblastos[\s\.]*:\s*([0-9,.]+)",
                            "Leucocitos": r"Leucócitos Totais[\s\.]*:\s*([0-9,.]+)\s*mmb3",
                            "Plaquetas": r"PLAQUETAS[\s\.]*:\s*([0-9,.]+)\s*mil/mmb3"
                        }
                        dados_extraidos = {}
                        for nome_campo, padrao in padroes_extracao.items():
                            match = re.search(padrao, texto_limpo, re.IGNORECASE)
                            if match:
                                dados_extraidos[nome_campo] = match.group(1).strip()
                            else:
                                dados_extraidos[nome_campo] = "Não encontrado"

                        # Verificar criticidade da Hemoglobina
                        hemoglobina_valor_str = dados_extraidos.get("Hemoglobina")
                        if hemoglobina_valor_str and hemoglobina_valor_str != "Não encontrado":
                            try:
                                hemoglobina_valor_float = float(hemoglobina_valor_str.replace(",", "."))
                                registrar_log(f"Prescricao {nr_prescricao} (Hemograma): Valor de Hemoglobina: {hemoglobina_valor_float}")   
                                if hemoglobina_valor_float < 6.6 or hemoglobina_valor_float > 19.9:
                                    hemogramas_criticos_encontrados.append({
                                        "prescricao": nr_prescricao,
                                        "parametro": "Hemoglobina",
                                        "valor": hemoglobina_valor_float,
                                        "unidade": "g/dL"
                                    })
                            except ValueError:
                                registrar_log(f"Prescricao {nr_prescricao} (Hemograma): Valor de Hemoglobina '{hemoglobina_valor_str}' não é numérico.")
                        
                        # Verificar criticidade do Hematócrito
                        hematocrito_valor_str = dados_extraidos.get("Hematocrito")
                        if hematocrito_valor_str and hematocrito_valor_str != "Não encontrado":
                            try:
                                hematocrito_valor_float = float(hematocrito_valor_str.replace(",", "."))
                                registrar_log(f"Prescricao {nr_prescricao} (Hemograma): Valor de Hematócrito: {hematocrito_valor_float}")
                                if hematocrito_valor_float < 18.0 or hematocrito_valor_float > 60.0: # vol%
                                    hemogramas_criticos_encontrados.append({
                                        "prescricao": nr_prescricao,
                                        "parametro": "Hematócrito",
                                        "valor": hematocrito_valor_float,
                                        "unidade": "vol%"
                                        # "todos_dados": dados_extraidos.copy() # Opcional
                                    })
                            except ValueError:
                                registrar_log(f"Prescricao {nr_prescricao} (Hemograma): Valor de Hematócrito '{hematocrito_valor_str}' não é numérico.")

                        # Verificar criticidade dos Leucócitos
                        leucocitos_valor_str = dados_extraidos.get("Leucocitos")
                        if leucocitos_valor_str and leucocitos_valor_str != "Não encontrado":
                            try:
                                # Se a regex captura "15,52" e a unidade é "mmb3" (que é /µL),
                                # e isso representa 15.520/µL, então multiplique por 1000.
                                # Se a regex já captura o valor na escala correta (ex: 15520), não multiplique.
                                leucocitos_valor_float = float(leucocitos_valor_str.replace(",", "."))
                                registrar_log(f"Prescricao {nr_prescricao} (Hemograma): Valor de Leucócitos: {leucocitos_valor_float}")
                                # leucocitos_valor_float = float(leucocitos_valor_str.replace(",", ".")) * 1000 # Ajuste se necessário

                                if leucocitos_valor_float > 2000.0 or leucocitos_valor_float > 50000.0: # /µL
                                    hemogramas_criticos_encontrados.append({
                                        "prescricao": nr_prescricao,
                                        "parametro": "Leucócitos",
                                        "valor": leucocitos_valor_float,
                                        "unidade": "/µL"
                                    })
                            except ValueError:
                                registrar_log(f"Prescricao {nr_prescricao} (Hemograma): Valor de Leucócitos '{leucocitos_valor_str}' não é numérico.")

                        # Verificar criticidade das Plaquetas
                        plaquetas_valor_str = dados_extraidos.get("Plaquetas")
                        if plaquetas_valor_str and plaquetas_valor_str != "Não encontrado":
                            try:
                                plaquetas_valor_float = float(plaquetas_valor_str.replace(",", ".")) * 1000 # Valor extraído é em "mil/mmb3"
                                registrar_log(f"Prescricao {nr_prescricao} (Hemograma): Valor de Plaquetas: {plaquetas_valor_float}")
                                if plaquetas_valor_float < 20000.0 or plaquetas_valor_float > 1000000.0: # /uL
                                    hemogramas_criticos_encontrados.append({
                                        "prescricao": nr_prescricao,
                                        "parametro": "Plaquetas",
                                        "valor": plaquetas_valor_float, # Armazena o valor já convertido para /uL
                                        "unidade": "/uL"
                                    })
                            except ValueError:
                                registrar_log(f"Prescricao {nr_prescricao} (Hemograma): Valor de Plaquetas '{plaquetas_valor_str}' não é numérico.")


            if hemogramas_criticos_encontrados:
                mensagens_hemogramas_criticos_whatsapp.append(["--- HEMOGRAMAS CRÍTICOS ENCONTRADOS ---"])
                for critico in hemogramas_criticos_encontrados:
                    linha_mensagem = f"Prescrição {critico['prescricao']}: {critico['parametro']} com valor crítico de {critico['valor']:.1f} {critico['unidade']}."
                    mensagens_hemogramas_criticos_whatsapp.append([linha_mensagem]) # Cada linha como uma lista de um item
                
                enviar_whatsapp_laboratorio(mensagens_hemogramas_criticos_whatsapp, modo_teste=MODO_TESTE_WHATSAPP)
            else:
                registrar_log("Nenhum hemograma crítico encontrado para enviar.")
        else:
            registrar_log("Nenhum resultado de hemograma encontrado na query para processamento.")

        # --- INÍCIO DO PROCESSAMENTO DE COAGULOGRAMAS CRÍTICOS ---
        registrar_log("Iniciando processamento de coagulogramas críticos...")
        coagulogramas_criticos = processar_coagulogramas_criticos(resultados_hemogramas) # Reutiliza os mesmos resultados brutos
        mensagens_coagulogramas_criticos_whatsapp = []

        if coagulogramas_criticos:
            mensagens_coagulogramas_criticos_whatsapp.append(["--- COAGULOGRAMAS CRÍTICOS ENCONTRADOS ---"])
            for critico in coagulogramas_criticos:
                linha_mensagem = f"Prescrição {critico['prescricao']}: {critico['parametro']} com valor crítico de {critico['valor']:.2f}."
                mensagens_coagulogramas_criticos_whatsapp.append([linha_mensagem])
            enviar_whatsapp_laboratorio(mensagens_coagulogramas_criticos_whatsapp, modo_teste=MODO_TESTE_WHATSAPP)
        else:
            registrar_log("Nenhum coagulograma crítico encontrado para enviar.")
        # --- FIM DO PROCESSAMENTO DE HEMOGRAMAS CRÍTICOS ---

        # --- INÍCIO DO PROCESSAMENTO DE HEPATOGRAMAS CRÍTICOS ---
        registrar_log("Iniciando processamento de hepatogramas críticos...")
        hepatogramas_criticos = processar_hepatogramas_criticos(resultados_hemogramas) # Reutiliza os mesmos resultados brutos
        mensagens_hepatogramas_criticos_whatsapp = []

        if hepatogramas_criticos:
            mensagens_hepatogramas_criticos_whatsapp.append(["--- HEPATOGRAMAS CRÍTICOS ENCONTRADOS ---"])
            for critico in hepatogramas_criticos:
                linha_mensagem = f"Prescrição {critico['prescricao']}: {critico['parametro']} com valor crítico de {critico['valor']:.2f} {critico['unidade']}."
                mensagens_hepatogramas_criticos_whatsapp.append([linha_mensagem])
            enviar_whatsapp_laboratorio(mensagens_hepatogramas_criticos_whatsapp, modo_teste=MODO_TESTE_WHATSAPP)
        else:
            registrar_log("Nenhum hepatograma crítico encontrado para enviar.")
        # --- FIM DO PROCESSAMENTO DE HEPATOGRAMAS CRÍTICOS ---

        # --- INÍCIO DO PROCESSAMENTO DE LIPIDOGRAMAS CRÍTICOS ---
        registrar_log("Iniciando processamento de lipidogramas críticos...")
        lipidogramas_criticos = processar_lipidogramas_criticos(resultados_hemogramas) # Reutiliza os mesmos resultados brutos
        mensagens_lipidogramas_criticos_whatsapp = []

        if lipidogramas_criticos:
            mensagens_lipidogramas_criticos_whatsapp.append(["--- LIPIDOGRAMAS CRÍTICOS ENCONTRADOS ---"])
            for critico in lipidogramas_criticos:
                linha_mensagem = f"Prescrição {critico['prescricao']}: {critico['parametro']} com valor crítico de {critico['valor']:.2f} {critico['unidade']}."
                mensagens_lipidogramas_criticos_whatsapp.append([linha_mensagem])
            enviar_whatsapp_laboratorio(mensagens_lipidogramas_criticos_whatsapp, modo_teste=MODO_TESTE_WHATSAPP)
        else:
            registrar_log("Nenhum lipidograma crítico encontrado para enviar.")
    else:
        registrar_log("Nenhum resultado de hemograma/exame bruto encontrado para processar.")
    registrar_log("logica_principal_background - FIM")

def tempo_espera_emergencia():
    """Executa a query HSF - TODOS - TEMPO DE ESPERA EMERGENCIA.sql e retorna o dataframe."""
    registrar_log("tempo_espera_emergencia - INICIO")
    
    try:
        # Inicialização do Oracle Client removida (agora é global)
        # diretorio_instantclient = encontrar_diretorio_instantclient()
        # if diretorio_instantclient:
        #     oracledb.init_oracle_client(lib_dir=diretorio_instantclient)
        #     registrar_log(f"tempo_espera_emergencia - Instant Client configurado: {diretorio_instantclient}")
        # else:
        #     registrar_log("tempo_espera_emergencia - ERRO: Diretório do Instant Client não encontrado")
        #     return None

        # Ler a query do arquivo SQL
        with open('HSF - TODOS - TEMPO DE ESPERA EMERGENCIA.sql', 'r', encoding='utf-8') as arquivo:
            query = arquivo.read()
        
        registrar_log("tempo_espera_emergencia - Query carregada do arquivo SQL")

        # Conectar ao banco de dados
        connection = oracledb.connect(user="TASY", password="aloisk", dsn="192.168.5.9:1521/TASYPRD")

        registrar_log("tempo_espera_emergencia - Conexão com banco estabelecida")

        # Executar a query e criar dataframe
        df = pd.read_sql(query, connection)
        registrar_log(f"tempo_espera_emergencia - Query executada. Linhas retornadas: {len(df)}")
        
        # Debug: Exibir colunas do DataFrame
        registrar_log(f"tempo_espera_emergencia - Colunas do DataFrame: {list(df.columns)}")

        # Fechar conexão
        connection.close()
        registrar_log("tempo_espera_emergencia - Conexão fechada")
        
        registrar_log("tempo_espera_emergencia - FIM")
        return df

    except Exception as e:
        registrar_log(f"tempo_espera_emergencia - ERRO: {str(e)}")
        return None

def exibir_dataframe_tempo_espera(df):
    """Exibe o dataframe completo de tempo de espera da emergência no console."""
    registrar_log("exibir_dataframe_tempo_espera - INICIO")
    
    if df is None or df.empty:
        registrar_log("exibir_dataframe_tempo_espera - DataFrame vazio ou None")
        print("DataFrame vazio ou não disponível")
        return
    
    try:
        print("\n" + "="*100)
        print("DATAFRAME COMPLETO - TEMPO DE ESPERA EMERGÊNCIA")
        print("="*100)
        print(f"Total de registros: {len(df)}")
        print(f"Colunas disponíveis: {list(df.columns)}")
        print("\n")
        print(df.to_string(index=False))
        print("="*100 + "\n")
        
        registrar_log(f"exibir_dataframe_tempo_espera - DataFrame exibido com {len(df)} registros")
        
    except Exception as e:
        registrar_log(f"exibir_dataframe_tempo_espera - ERRO: {str(e)}")
        print(f"Erro ao exibir dataframe: {str(e)}")
    
    registrar_log("exibir_dataframe_tempo_espera - FIM")

def formatar_minutos_para_hhmmss(minutos):
    """
    Converte minutos decimais para formato HH:MM:SS.
    
    Args:
        minutos (float): Tempo em minutos decimais
        
    Returns:
        str: Tempo formatado como HH:MM:SS ou "00:00:00" se None/inválido
        
    Exemplo:
        >>> formatar_minutos_para_hhmmss(65.5)
        "01:05:30"
        >>> formatar_minutos_para_hhmmss(3.18)
        "00:03:11"
    """
    if pd.isna(minutos) or minutos is None:
        return "00:00:00"
    
    try:
        # Converter para segundos totais
        segundos_totais = int(round(float(minutos) * 60))
        
        # Calcular horas, minutos e segundos
        horas = segundos_totais // 3600
        minutos_restantes = (segundos_totais % 3600) // 60
        segundos = segundos_totais % 60
        
        # Formatar como HH:MM:SS
        return f"{horas:02d}:{minutos_restantes:02d}:{segundos:02d}"
    except (ValueError, TypeError):
        return "00:00:00"

def converter_tempo_para_minutos(tempo_str):
    """
    Converte strings de tempo (HH:MM:SS ou HH:MM) para minutos inteiros.
    
    Args:
        tempo_str (str): String de tempo no formato HH:MM:SS ou HH:MM
        
    Returns:
        int: Tempo convertido em minutos inteiros, ou 0 se inválido/None
        
    Exemplo:
        >>> converter_tempo_para_minutos("01:05:30")
        66
        >>> converter_tempo_para_minutos("00:03:11")
        3
        >>> converter_tempo_para_minutos("02:30")
        150
    """
    if pd.isna(tempo_str) or tempo_str is None or tempo_str == '':
        return 0
    
    try:
        # Se já for um número, retorna como inteiro
        if isinstance(tempo_str, (int, float)):
            return int(round(float(tempo_str)))
        
        # Se for string no formato HH:MM:SS ou HH:MM
        tempo_str = str(tempo_str).strip()
        partes = tempo_str.split(':')
        
        if len(partes) == 3:  # HH:MM:SS
            horas, minutos, segundos = map(int, partes)
            # Converte tudo para minutos
            # Correção para arredondamento tradicional (0.5 arredonda para cima)
            # Python round() arredonda para o par mais próximo (bankers rounding)
            val_segundos = segundos / 60
            segundos_arredondados = int(val_segundos + 0.5)
            
            total_minutos = horas * 60 + minutos + segundos_arredondados
            return int(total_minutos)
        elif len(partes) == 2:  # HH:MM
            horas, minutos = map(int, partes)
            return int(horas * 60 + minutos)
        else:
            # Tentar converter diretamente para inteiro
            return int(round(float(tempo_str)))
    except (ValueError, TypeError):
        return 0

def exibir_registros_filtrados_tempo_espera(df):
    """
    Exibe registros que atendem a TODOS os critérios de filtro simultaneamente.
    
    Critérios aplicados:
    1) Atendimento > 0
    2) Triagem Classificacao <> null
    3) Tempo Recepcao maior do que 10 minutos
    4) Tempo Triagem maior do que 5 minutos
    5) Espera por Medico maior do que 5 minutos
    6) Tempo Final da Fila diferente de None e maior do que 30 minutos
    
    Args:
        df (pandas.DataFrame): DataFrame com dados de tempo de espera da emergência
        
    Returns:
        None: Exibe os resultados filtrados no console
    """
    registrar_log("exibir_registros_filtrados_tempo_espera - INICIO")
    
    if df is None or df.empty:
        registrar_log("exibir_registros_filtrados_tempo_espera - DataFrame vazio ou None")
        print("DataFrame vazio ou não disponível")
        return
    
    try:
        # Criar uma cópia do dataframe para não modificar o original
        df_copia = df.copy()
        
        # Calcular Tempo Triagem baseado em DT_INICIO_TRIAGEM e DT_FIM_TRIAGEM
        if 'DT_INICIO_TRIAGEM' in df_copia.columns and 'DT_FIM_TRIAGEM' in df_copia.columns:
            # Converter para datetime se necessário
            df_copia['DT_INICIO_TRIAGEM'] = pd.to_datetime(df_copia['DT_INICIO_TRIAGEM'], errors='coerce')
            df_copia['DT_FIM_TRIAGEM'] = pd.to_datetime(df_copia['DT_FIM_TRIAGEM'], errors='coerce')
            
            # Calcular diferença em minutos
            df_copia['TEMPO_TRIAGEM'] = (df_copia['DT_FIM_TRIAGEM'] - df_copia['DT_INICIO_TRIAGEM']).dt.total_seconds() / 60
            
            # Formatar Tempo Triagem para HH:MM:SS
            df_copia['TEMPO_TRIAGEM_FORMATADO'] = df_copia['TEMPO_TRIAGEM'].apply(formatar_minutos_para_hhmmss)
        
        # Aplicar filtros
        print("\n" + "="*120)
        print("APLICANDO FILTROS DE TEMPO DE ESPERA")
        print("="*120)
        
        total_inicial = len(df_copia)
        print(f"Total de registros inicial: {total_inicial}")
        
        # Filtro 1: Atendimento > 0
        if 'NR_ATENDIMENTO' in df_copia.columns:
            df_copia = df_copia[df_copia['NR_ATENDIMENTO'] > 0]
            print(f"Após filtro Atendimento > 0: {len(df_copia)} registros")
        
        # Filtro 2: Triagem Classificacao <> null
        if 'TRIAGEM_CLASSIFICACAO' in df_copia.columns:
            df_copia = df_copia[df_copia['TRIAGEM_CLASSIFICACAO'].notna()]
            df_copia = df_copia[df_copia['TRIAGEM_CLASSIFICACAO'] != '']
            print(f"Após filtro Triagem Classificacao não nula: {len(df_copia)} registros")
        
        # Filtro 3: Tempo Recepcao maior do que 10 minutos
        if 'TOTAL_RECEP' in df_copia.columns:
            df_copia['TOTAL_RECEP_MINUTOS'] = df_copia['TOTAL_RECEP'].apply(converter_tempo_para_minutos)
            df_copia = df_copia[df_copia['TOTAL_RECEP_MINUTOS'] > 10]
            print(f"Após filtro Tempo Recepcao > 10 min: {len(df_copia)} registros")
        
        # Filtro 4: Tempo Triagem maior do que 5 minutos
        if 'TEMPO_TRIAGEM' in df_copia.columns:
            df_copia = df_copia[df_copia['TEMPO_TRIAGEM'] > 5]
            print(f"Após filtro Tempo Triagem > 5 min: {len(df_copia)} registros")
        
        # Filtro 5: Espera por Medico maior do que 5 minutos
        if 'TEMPO_ESPERA_ATEND' in df_copia.columns:
            df_copia['TEMPO_ESPERA_ATEND_MINUTOS'] = df_copia['TEMPO_ESPERA_ATEND'].apply(converter_tempo_para_minutos)
            df_copia = df_copia[df_copia['TEMPO_ESPERA_ATEND_MINUTOS'] > 5]
            print(f"Após filtro Espera por Medico > 5 min: {len(df_copia)} registros")
        
        # Filtro 6: Tempo Final da Fila diferente de None e maior do que 30 minutos
        if 'PACIENTE_SENHA_FILA_FIM' in df_copia.columns:
            df_copia['PACIENTE_SENHA_FILA_FIM_MINUTOS'] = df_copia['PACIENTE_SENHA_FILA_FIM'].apply(converter_tempo_para_minutos)
            df_copia = df_copia[df_copia['PACIENTE_SENHA_FILA_FIM'].notna()]
            df_copia = df_copia[df_copia['PACIENTE_SENHA_FILA_FIM_MINUTOS'] > 30]
            print(f"Após filtro Tempo Final da Fila > 30 min: {len(df_copia)} registros")
        
        print("="*120)
        
        if df_copia.empty:
            print("NENHUM REGISTRO ATENDE A TODOS OS CRITÉRIOS DE FILTRO")
            print("="*120 + "\n")
            registrar_log("exibir_registros_filtrados_tempo_espera - Nenhum registro passou pelos filtros")
            return
        
        # Definir as colunas que queremos exibir
        colunas_desejadas = [
            'NR_ATENDIMENTO',  # Atendimento
            'TRIAGEM_CLASSIFICACAO',  # Triagem Classificacao
            'TOTAL_RECEP',  # Tempo Recepcao
            'PACIENTE_SENHA_FILA_FIM',  # Tempo Final da Fila
            'TEMPO_ESPERA_ATEND',  # Espera por medico
            'TEMPO_TRIAGEM_FORMATADO'  # Tempo Triagem (formatado como HH:MM:SS)
        ]
        
        # Verificar quais colunas existem no dataframe
        colunas_existentes = [col for col in colunas_desejadas if col in df_copia.columns]
        
        # Criar dataframe com as colunas disponíveis
        df_filtrado = df_copia[colunas_existentes]
        
        print("\n" + "="*120)
        print("REGISTROS FILTRADOS - TEMPO DE ESPERA EMERGÊNCIA")
        print("="*120)
        print(f"Total de registros que atendem aos critérios: {len(df_filtrado)}")
        print("Critérios aplicados:")
        print("1) Atendimento > 0")
        print("2) Triagem Classificacao não nula")
        print("3) Tempo Recepcao > 10 minutos")
        print("4) Tempo Triagem > 5 minutos")
        print("5) Espera por Medico > 5 minutos")
        print("6) Tempo Final da Fila não nulo e > 30 minutos")
        print("\n")
        
        # Renomear colunas para nomes mais amigáveis
        nomes_amigaveis = {
            'NR_ATENDIMENTO': 'Atendimento',
            'TRIAGEM_CLASSIFICACAO': 'Triagem Classificacao',
            'TOTAL_RECEP': 'Tempo Recepcao',
            'PACIENTE_SENHA_FILA_FIM': 'Tempo Final da Fila',
            'TEMPO_ESPERA_ATEND': 'Espera por medico',
            'TEMPO_TRIAGEM_FORMATADO': 'Tempo Triagem'
        }
        
        df_filtrado_renomeado = df_filtrado.rename(columns=nomes_amigaveis)
        print(df_filtrado_renomeado.to_string(index=False))
        print("="*120 + "\n")
        
        registrar_log(f"exibir_registros_filtrados_tempo_espera - {len(df_filtrado)} registros filtrados exibidos")
        
    except Exception as e:
        registrar_log(f"exibir_registros_filtrados_tempo_espera - ERRO: {str(e)}")
        print(f"Erro ao aplicar filtros: {str(e)}")
    
    registrar_log("exibir_registros_filtrados_tempo_espera - FIM")

def exibir_filtros_individuais_tempo_espera(df):
    """
    Exibe registros filtrados individualmente para cada critério de tempo,
    sempre incluindo as chaves únicas (Atendimento e Triagem Classificacao).
    """
    registrar_log("exibir_filtros_individuais_tempo_espera - INICIO")
    
    if df is None or df.empty:
        registrar_log("exibir_filtros_individuais_tempo_espera - DataFrame vazio ou None")
        print("DataFrame vazio ou não disponível")
        return
    
    try:
        # Criar uma cópia do dataframe para não modificar o original
        df_copia = df.copy()
        
        # Calcular Tempo Triagem baseado em DT_INICIO_TRIAGEM e DT_FIM_TRIAGEM
        if 'DT_INICIO_TRIAGEM' in df_copia.columns and 'DT_FIM_TRIAGEM' in df_copia.columns:
            # Converter para datetime se necessário
            df_copia['DT_INICIO_TRIAGEM'] = pd.to_datetime(df_copia['DT_INICIO_TRIAGEM'], errors='coerce')
            df_copia['DT_FIM_TRIAGEM'] = pd.to_datetime(df_copia['DT_FIM_TRIAGEM'], errors='coerce')
            
            # Calcular diferença em minutos
            df_copia['TEMPO_TRIAGEM'] = (df_copia['DT_FIM_TRIAGEM'] - df_copia['DT_INICIO_TRIAGEM']).dt.total_seconds() / 60
            
            # Formatar Tempo Triagem para HH:MM:SS
            df_copia['TEMPO_TRIAGEM_FORMATADO'] = df_copia['TEMPO_TRIAGEM'].apply(formatar_minutos_para_hhmmss)
        
        print("\n" + "="*120)
        print("FILTROS INDIVIDUAIS - TEMPO DE ESPERA EMERGÊNCIA")
        print("="*120)
        
        # Filtros básicos (sempre aplicados)
        df_base = df_copia.copy()
        if 'NR_ATENDIMENTO' in df_base.columns:
            df_base = df_base[df_base['NR_ATENDIMENTO'] > 0]
        if 'TRIAGEM_CLASSIFICACAO' in df_base.columns:
            df_base = df_base[df_base['TRIAGEM_CLASSIFICACAO'].notna()]
            df_base = df_base[df_base['TRIAGEM_CLASSIFICACAO'] != '']
        
        # 1. FILTRO: Tempo Recepcao > 10 minutos
        if 'TOTAL_RECEP' in df_base.columns:
            df_tempo_recepcao = df_base.copy()
            df_tempo_recepcao['TOTAL_RECEP_MINUTOS'] = df_tempo_recepcao['TOTAL_RECEP'].apply(converter_tempo_para_minutos)
            df_tempo_recepcao = df_tempo_recepcao[df_tempo_recepcao['TOTAL_RECEP_MINUTOS'] > 10]
            
            if not df_tempo_recepcao.empty:
                print(f"\n1) TEMPO RECEPCAO > 10 MINUTOS ({len(df_tempo_recepcao)} registros)")
                print("-" * 80)
                colunas_recepcao = ['NR_ATENDIMENTO', 'TRIAGEM_CLASSIFICACAO', 'TOTAL_RECEP']
                colunas_existentes = [col for col in colunas_recepcao if col in df_tempo_recepcao.columns]
                df_exibir = df_tempo_recepcao[colunas_existentes].rename(columns={
                    'NR_ATENDIMENTO': 'Atendimento',
                    'TRIAGEM_CLASSIFICACAO': 'Triagem Classificacao',
                    'TOTAL_RECEP': 'Tempo Recepcao'
                })
                print(df_exibir.to_string(index=False))
            else:
                print(f"\n1) TEMPO RECEPCAO > 10 MINUTOS (0 registros)")
        
        # 2. FILTRO: Tempo Triagem > 5 minutos
        if 'TEMPO_TRIAGEM' in df_base.columns:
            df_tempo_triagem = df_base.copy()
            df_tempo_triagem = df_tempo_triagem[df_tempo_triagem['TEMPO_TRIAGEM'] > 5]
            
            if not df_tempo_triagem.empty:
                print(f"\n2) TEMPO TRIAGEM > 5 MINUTOS ({len(df_tempo_triagem)} registros)")
                print("-" * 80)
                colunas_triagem = ['NR_ATENDIMENTO', 'TRIAGEM_CLASSIFICACAO', 'TEMPO_TRIAGEM_FORMATADO']
                colunas_existentes = [col for col in colunas_triagem if col in df_tempo_triagem.columns]
                df_exibir = df_tempo_triagem[colunas_existentes].rename(columns={
                    'NR_ATENDIMENTO': 'Atendimento',
                    'TRIAGEM_CLASSIFICACAO': 'Triagem Classificacao',
                    'TEMPO_TRIAGEM_FORMATADO': 'Tempo Triagem'
                })
                print(df_exibir.to_string(index=False))
            else:
                print(f"\n2) TEMPO TRIAGEM > 5 MINUTOS (0 registros)")
        
        # 3. FILTRO: Espera por Medico > 5 minutos
        if 'TEMPO_ESPERA_ATEND' in df_base.columns:
            df_espera_medico = df_base.copy()
            df_espera_medico['TEMPO_ESPERA_ATEND_MINUTOS'] = df_espera_medico['TEMPO_ESPERA_ATEND'].apply(converter_tempo_para_minutos)
            df_espera_medico = df_espera_medico[df_espera_medico['TEMPO_ESPERA_ATEND_MINUTOS'] > 5]
            
            if not df_espera_medico.empty:
                print(f"\n3) ESPERA POR MEDICO > 5 MINUTOS ({len(df_espera_medico)} registros)")
                print("-" * 80)
                colunas_espera = ['NR_ATENDIMENTO', 'TRIAGEM_CLASSIFICACAO', 'TEMPO_ESPERA_ATEND']
                colunas_existentes = [col for col in colunas_espera if col in df_espera_medico.columns]
                df_exibir = df_espera_medico[colunas_existentes].rename(columns={
                    'NR_ATENDIMENTO': 'Atendimento',
                    'TRIAGEM_CLASSIFICACAO': 'Triagem Classificacao',
                    'TEMPO_ESPERA_ATEND': 'Espera por Medico'
                })
                print(df_exibir.to_string(index=False))
            else:
                print(f"\n3) ESPERA POR MEDICO > 5 MINUTOS (0 registros)")
        
        # 4. FILTRO: Tempo Final da Fila > 30 minutos
        if 'PACIENTE_SENHA_FILA_FIM' in df_base.columns:
            df_fila_fim = df_base.copy()
            df_fila_fim['PACIENTE_SENHA_FILA_FIM_MINUTOS'] = df_fila_fim['PACIENTE_SENHA_FILA_FIM'].apply(converter_tempo_para_minutos)
            df_fila_fim = df_fila_fim[df_fila_fim['PACIENTE_SENHA_FILA_FIM'].notna()]
            df_fila_fim = df_fila_fim[df_fila_fim['PACIENTE_SENHA_FILA_FIM_MINUTOS'] > 30]
            
            if not df_fila_fim.empty:
                print(f"\n4) TEMPO FINAL DA FILA > 30 MINUTOS ({len(df_fila_fim)} registros)")
                print("-" * 80)
                colunas_fila = ['NR_ATENDIMENTO', 'TRIAGEM_CLASSIFICACAO', 'PACIENTE_SENHA_FILA_FIM']
                colunas_existentes = [col for col in colunas_fila if col in df_fila_fim.columns]
                df_exibir = df_fila_fim[colunas_existentes].rename(columns={
                    'NR_ATENDIMENTO': 'Atendimento',
                    'TRIAGEM_CLASSIFICACAO': 'Triagem Classificacao',
                    'PACIENTE_SENHA_FILA_FIM': 'Tempo Final da Fila'
                })
                print(df_exibir.to_string(index=False))
            else:
                print(f"\n4) TEMPO FINAL DA FILA > 30 MINUTOS (0 registros)")
        
        print("\n" + "="*120 + "\n")
        
        registrar_log("exibir_filtros_individuais_tempo_espera - Filtros individuais exibidos")
        
    except Exception as e:
        registrar_log(f"exibir_filtros_individuais_tempo_espera - ERRO: {str(e)}")
        print(f"Erro ao exibir filtros individuais: {str(e)}")
    
    registrar_log("exibir_filtros_individuais_tempo_espera - FIM")

def exibir_colunas_especificas_tempo_espera(df):
    """Exibe colunas específicas do dataframe e calcula Tempo Triagem."""
    registrar_log("exibir_colunas_especificas_tempo_espera - INICIO")
    
    if df is None or df.empty:
        registrar_log("exibir_colunas_especificas_tempo_espera - DataFrame vazio ou None")
        print("DataFrame vazio ou não disponível")
        return
    
    try:
        # Criar uma cópia do dataframe para não modificar o original
        df_copia = df.copy()
        
        # Calcular Tempo Triagem baseado em DT_INICIO_TRIAGEM e DT_FIM_TRIAGEM
        if 'DT_INICIO_TRIAGEM' in df_copia.columns and 'DT_FIM_TRIAGEM' in df_copia.columns:
            # Converter para datetime se necessário
            df_copia['DT_INICIO_TRIAGEM'] = pd.to_datetime(df_copia['DT_INICIO_TRIAGEM'], errors='coerce')
            df_copia['DT_FIM_TRIAGEM'] = pd.to_datetime(df_copia['DT_FIM_TRIAGEM'], errors='coerce')
            
            # Calcular diferença em minutos
            df_copia['TEMPO_TRIAGEM'] = (df_copia['DT_FIM_TRIAGEM'] - df_copia['DT_INICIO_TRIAGEM']).dt.total_seconds() / 60
            
            # Formatar Tempo Triagem para HH:MM:SS
            df_copia['TEMPO_TRIAGEM_FORMATADO'] = df_copia['TEMPO_TRIAGEM'].apply(formatar_minutos_para_hhmmss)
        
        # Definir as colunas que queremos exibir
        colunas_desejadas = [
            'NR_ATENDIMENTO',  # Atendimento
            'TRIAGEM_CLASSIFICACAO',  # Triagem Classificacao
            'TOTAL_RECEP',  # Tempo Recepcao
            'PACIENTE_SENHA_FILA_FIM',  # Tempo Final da Fila
            'TEMPO_ESPERA_ATEND',  # Espera por medico
            'TEMPO_TRIAGEM_FORMATADO'  # Tempo Triagem (formatado como HH:MM)
        ]
        
        # Verificar quais colunas existem no dataframe
        colunas_existentes = [col for col in colunas_desejadas if col in df_copia.columns]
        colunas_faltantes = [col for col in colunas_desejadas if col not in df_copia.columns]
        
        if colunas_faltantes:
            registrar_log(f"exibir_colunas_especificas_tempo_espera - Colunas não encontradas: {colunas_faltantes}")
        
        # Criar dataframe com as colunas disponíveis
        df_filtrado = df_copia[colunas_existentes]
        
        print("\n" + "="*120)
        print("COLUNAS ESPECÍFICAS - TEMPO DE ESPERA EMERGÊNCIA")
        print("="*120)
        print(f"Total de registros: {len(df_filtrado)}")
        print(f"Colunas exibidas: {colunas_existentes}")
        if colunas_faltantes:
            print(f"Colunas não encontradas: {colunas_faltantes}")
        print("\n")
        
        # Renomear colunas para nomes mais amigáveis
        nomes_amigaveis = {
            'NR_ATENDIMENTO': 'Atendimento',
            'TRIAGEM_CLASSIFICACAO': 'Triagem Classificacao',
            'TOTAL_RECEP': 'Tempo Recepcao',
            'PACIENTE_SENHA_FILA_FIM': 'Tempo Final da Fila',
            'TEMPO_ESPERA_ATEND': 'Espera por medico',
            'TEMPO_TRIAGEM_FORMATADO': 'Tempo Triagem'
        }
        
        df_filtrado_renomeado = df_filtrado.rename(columns=nomes_amigaveis)
        print(df_filtrado_renomeado.to_string(index=False))
        print("="*120 + "\n")
        
        registrar_log(f"exibir_colunas_especificas_tempo_espera - Colunas específicas exibidas com {len(df_filtrado)} registros")
        
    except Exception as e:
        registrar_log(f"exibir_colunas_especificas_tempo_espera - ERRO: {str(e)}")
        print(f"Erro ao exibir colunas específicas: {str(e)}")
    
    registrar_log("exibir_colunas_especificas_tempo_espera - FIM")

def fetch_ordens_servico_ti() -> pd.DataFrame:
    """Busca as ordens de serviço não encerradas da TI no Oracle DB."""
    registrar_log("fetch_ordens_servico_ti - INÍCIO")
    connection = None
    try:
        # Credenciais conforme padrão estabelecido em main.py
        connection = oracledb.connect(user="TASY", password="aloisk", dsn="192.168.5.9:1521/TASYPRD")
        
        with connection:
            sql_file = 'HSF - ORDENS DE SERVICO NAO ENCERRADAS PARA A TI.sql'
            sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), sql_file)
            
            if not os.path.exists(sql_path):
                registrar_log(f"Erro: SQL não encontrado em {sql_path}")
                return pd.DataFrame()
            
            with open(sql_path, 'r', encoding='utf-8') as f:
                query = f.read()
            
            df = pd.read_sql(query, connection)
            registrar_log(f"Fetch OS TI concluído: {len(df)} registros.")
            registrar_log(f"df:{df.sample}")
            return df
    except Exception as e:
        registrar_log(f"Erro ao buscar OS TI: {e}")
        return pd.DataFrame()

def fetch_ordens_servico_fechadas_hoje():
    """Busca as ordens de serviço encerradas hoje para a TI no Oracle DB."""
    registrar_log("fetch_ordens_servico_fechadas_hoje - INÍCIO")
    connection = None
    try:
        connection = oracledb.connect(user="TASY", password="aloisk", dsn="192.168.5.9:1521/TASYPRD")
        
        with connection:
            sql_file = 'HSF - ORDENS DE SERVICO ENCERRADAS HOJE PARA A TI.sql'
            sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), sql_file)
            
            if not os.path.exists(sql_path):
                registrar_log(f"Erro: SQL não encontrado em {sql_path}")
                return pd.DataFrame()
            
            with open(sql_path, 'r', encoding='utf-8') as f:
                query = f.read()
            
            df = pd.read_sql(query, connection)
            registrar_log(f"Fetch OS Encerradas Hoje concluído: {len(df)} registros.")
            return df
    except Exception as e:
        registrar_log(f"Erro ao buscar OS encerradas hoje: {e}")
        return pd.DataFrame()

def ordens_de_servico_com_mais_de_2_dias():
    """
    Processa ordens de serviço atrasadas e envia indicadores para o grupo de WhatsApp da TI.
    """
    registrar_log("ordens_de_servico_com_mais_de_2_dias - INÍCIO")
    
    try:
        df = fetch_ordens_servico_ti()
        if df.empty:
            registrar_log("Nenhuma OS pendente encontrada.")
            return

        # Agrupamento por ANALISTA
        analistas_raw = df['ANALISTA'].unique()
        analistas = sorted([str(a) for a in analistas_raw if pd.notna(a) and str(a).strip() != ""])
        registrar_log(f"Identificados {len(analistas)} analistas com OS pendentes.")
        
        msg_corpo = "📊 *HSF - MONITORAMENTO O.S. TI*\n\n"
        detalhes = []

        registrar_log("Calculando indicadores de atraso (>2 dias) por analista...")
        for analista in analistas:
            df_analista = df[df['ANALISTA'] == analista].copy()
            total = len(df_analista)
            df_analista.loc[:, 'IDADE_DA_OS'] = pd.to_numeric(df_analista['IDADE_DA_OS'], errors='coerce').fillna(0)
            atrasadas = len(df_analista[df_analista['IDADE_DA_OS'].astype(float) > 2])
            
            msg_analista = f"👨‍💻 *{analista}*: {total} OS ({atrasadas} em atraso ⚠️)\n" if atrasadas > 0 else f"👨‍💻 *{analista}*: {total} OS\n"
            
            # Listar apenas as OS que estão efetivamente em atraso (v3.2.3)
            os_list = []
            if atrasadas > 0:
                df_atrasadas = df_analista[df_analista['IDADE_DA_OS'].astype(float) > 2]
                for _, row in df_atrasadas.iterrows():
                    os_num = row['ORDEM_SERVICO']
                    desc = str(row['DESCRICAO']).strip()
                    desc_curta = (desc[:60] + '...') if len(desc) > 60 else desc
                    os_list.append(f" OS {os_num}: {desc_curta}")
                
                msg_analista += "\n".join(os_list)
            
            detalhes.append(msg_analista)
            registrar_log(f"Analista {analista}: {total} OS (Atrasadas: {atrasadas})")

        # Adicionar "Sem Analista" (Solicitado v3.1.7 / v3.2.2 / v3.2.4)
        df_sem = df[df['ANALISTA'].isna() | (df['ANALISTA'].astype(str).str.strip() == "")]
        if not df_sem.empty:
            total_sem = len(df_sem)
            df_sem.loc[:, 'IDADE_DA_OS'] = pd.to_numeric(df_sem['IDADE_DA_OS'], errors='coerce').fillna(0)
            atrasadas_sem = len(df_sem[df_sem['IDADE_DA_OS'].astype(float) > 2])
            
            msg_sem = f"❓ *Sem Analista*: {total_sem} OS ({atrasadas_sem} em atraso ⚠️)\n" if atrasadas_sem > 0 else f"❓ *Sem Analista*: {total_sem} OS\n"
            
            # Listar apenas as OS sem analista que estão em atraso (v3.2.3)
            os_list_sem = []
            if atrasadas_sem > 0:
                df_sem_atrasadas = df_sem[df_sem['IDADE_DA_OS'].astype(float) > 2]
                for _, row in df_sem_atrasadas.iterrows():
                    os_num = row['ORDEM_SERVICO']
                    desc = str(row['DESCRICAO']).strip()
                    desc_curta = (desc[:60] + '...') if len(desc) > 60 else desc
                    os_list_sem.append(f" OS {os_num}: {desc_curta}")
                
                msg_sem += "\n".join(os_list_sem)
            
            detalhes.append(msg_sem)
            registrar_log(f"Sem Analista: {total_sem} OS (Atrasadas: {atrasadas_sem})")

        if not detalhes:
            msg_corpo += "Nenhuma OS vinculada a analistas conhecidos."
        else:
            msg_corpo += "\n".join(detalhes)
            
        msg_corpo += f"\n\n*Total Geral:* {len(df)} OS pendentes."
        
        registrar_log("Corpo da mensagem TI gerado com sucesso.")

        # Envio via WhatsApp (Playwright)
        registrar_log("Iniciando interface Playwright para disparo TI...")
        enviar_whatsapp_grupo("HSF - O.S. TI", msg_corpo)
        
        registrar_log("ordens_de_servico_com_mais_de_2_dias - FIM")
    except Exception as e:
        registrar_log(f"Erro no processamento de OS TI: {e}")

def ordens_de_servico_fechadas_hoje():
    """
    Processa as OS encerradas hoje e envia para o grupo de WhatsApp da TI.
    Agrupado por analista em ordem alfabética.
    """
    registrar_log("ordens_de_servico_fechadas_hoje - INÍCIO")
    
    try:
        df = fetch_ordens_servico_fechadas_hoje()
        if df.empty:
            registrar_log("Nenhuma OS encerrada hoje encontrada.")
            return

        # Agrupamento por ANALISTA
        analistas_raw = df['ANALISTA'].unique()
        # Filtrar nulos/vazios e ordenar alfabeticamente
        analistas = sorted([str(a) for a in analistas_raw if pd.notna(a) and str(a).strip() != ""])
        
        msg_corpo = "✅ *HSF - O.S. ENCERRADAS HOJE*\n"
        msg_corpo += "───────────────────\n\n"
        detalhes = []

        for analista in analistas:
            df_analista = df[df['ANALISTA'] == analista].copy()
            total_analista = len(df_analista)
            
            msg_analista = f"👨‍💻 *{analista}* ({total_analista} encerradas)\n"
            os_list = []
            for _, row in df_analista.iterrows():
                os_num = row['ORDEM_SERVICO']
                desc = str(row['DESCRICAO']).strip()
                desc_curta = (desc[:65] + '...') if len(desc) > 65 else desc
                os_list.append(f" 🔹 {os_num}: {desc_curta}")
            
            msg_analista += "\n".join(os_list)
            detalhes.append(msg_analista)
            registrar_log(f"Analista {analista}: {total_analista} OS encerradas.")

        # Verificar se há registros sem analista
        df_sem = df[df['ANALISTA'].isna() | (df['ANALISTA'].astype(str).str.strip() == "")]
        if not df_sem.empty:
            total_sem = len(df_sem)
            msg_sem = f"❓ *Sem Analista Atribuído* ({total_sem})\n"
            os_list_sem = []
            for _, row in df_sem.iterrows():
                os_list_sem.append(f" 🔹 {row['ORDEM_SERVICO']}: {str(row['DESCRICAO'])[:65]}")
            msg_sem += "\n".join(os_list_sem)
            detalhes.append(msg_sem)

        msg_corpo += "\n\n".join(detalhes)
        msg_corpo += "\n\n" + "─" * 20
        msg_corpo += f"\n🏆 *Total Encerradas Hoje:* {len(df)}"

        # Envio via WhatsApp
        registrar_log("Iniciando disparo do relatório de OS encerradas...")
        enviar_whatsapp_grupo("HSF - O.S. TI", msg_corpo)
        
        registrar_log("ordens_de_servico_fechadas_hoje - FIM")
    except Exception as e:
        registrar_log(f"Erro no processamento de OS encerradas hoje: {e}")
    

# Classe AppGUI removida - não precisamos mais da interface gráfica
# A execução agora é automática através da função main()

def executar_ciclo_completo():
    """
    Executa um ciclo completo de monitoramento usando Playwright.
    Gerencia o ciclo de vida do browser conforme GEMINI.md.
    """
    registrar_log("--- INICIANDO CICLO PLAYWRIGHT ---")
    
    try:
        # 1. TI - Pendências (Prioridade Máxima)
        registrar_log("Processando O.S. TI (Pendências)...")
        ordens_de_servico_com_mais_de_2_dias()

        # 1.1 TI - Encerradas Hoje
        registrar_log("Processando O.S. TI (Encerradas Hoje)...")
        ordens_de_servico_fechadas_hoje()

        # 2. Emergência
        registrar_log("Processando Alertas Emergência...")
        df_emergencia = tempo_espera_emergencia()
        if df_emergencia is not None:
            processar_alertas_tempo_unificado(df_emergencia)
            
        # 3. Laboratório
        registrar_log("Processando Exames Laboratório...")
        lista_exames = logica_principal_exames()
        if not lista_exames:
            registrar_log("Monitoramento Lab: Nenhum exame crítico detectado no banco.")
        
        return True
    except Exception as e:
        registrar_log(f"Erro crítico no ciclo Playwright: {e}")
        return False
    finally:
        # Padrão GEMINI.md: Fechar e recriar entre ciclos críticos
        fechar_playwright()
        registrar_log("--- CICLO FINALIZADO E PLAYWRIGHT LIMPO ---")

def main():
    """Loop principal de execução automática (HSF Olho de Deus v3.0)."""
    registrar_log("INICIANDO SISTEMA - OLHO DE DEUS V3.0 (PLAYWRIGHT ENGINE)")
    
    if not inicializar_oracle_client_global():
        registrar_log("ERRO FATAL: Oracle Client indisponível. Encerrando.")
        return

    while True:
        try:
            sucesso = executar_ciclo_completo()
            
            # Cálculo de intervalo (1 hora cheia)
            agora = datetime.now()
            proxima_hora = (agora + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            segundos_espera = (proxima_hora - agora).total_seconds()
            
            if segundos_espera <= 0: segundos_espera = 3600
            
            registrar_log(f"Aguardando {int(segundos_espera)}s até a próxima execução às {proxima_hora.strftime('%H:%M:%S')}")
            time.sleep(segundos_espera)
            
        except KeyboardInterrupt:
            registrar_log("Encerrado pelo usuário.")
            fechar_playwright()
            break
        except Exception as e:
            registrar_log(f"Erro no loop principal: {e}")
            time.sleep(300) # Espera 5 min em caso de erro genérico

if __name__ == "__main__":
    """
    Ponto de entrada do sistema HSF Olho de Deus.
    
    MUDANÇA IMPORTANTE - EXECUÇÃO AUTOMÁTICA:
    - Sistema convertido de interface gráfica para execução automática
    - Não há mais botões ou janelas - tudo roda automaticamente
    - Execução contínua em background com ciclos de 1 hora
    - Para interromper: use Ctrl+C no terminal
    - Logs detalhados salvos em log.txt para monitoramento
    
    Funcionalidades executadas automaticamente:
    1. Monitoramento de tempos de espera da emergência
    2. Monitoramento de exames críticos do laboratório
    3. Envio automático de alertas via WhatsApp
    """
    # Este bloco é crucial para o multiprocessing funcionar corretamente no Windows.
    # Ele garante que o código de criação de processos só seja executado
    # quando o script é o principal, e não quando é importado por um processo filho.
    main()

    # Exemplo de uso (comentado para usar a GUI):
    # df = tempo_espera_emergencia()
    # if df is not None:
    #     exibir_dataframe_tempo_espera(df)
    #     exibir_colunas_especificas_tempo_espera(df)
    #     exibir_registros_filtrados_tempo_espera(df)
    #     exibir_filtros_individuais_tempo_espera(df)
