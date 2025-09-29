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
import time
from datetime import datetime
import tkinter as tk
from multiprocessing import Process, Event # Importar Event
import oracledb
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options # Para configurar opções do navegador
from webdriver_manager.chrome import ChromeDriverManager # Para gerenciar o ChromeDriver
# Imports para WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import pandas as pd

def agora():
    agora = datetime.now()
    agora = agora.strftime("%Y-%m-%d %H-%M-%S")
    return str(agora)

def registrar_log(texto):
    """Função para registrar um texto em um arquivo de log."""
    diretorio_atual = os.getcwd()
    caminho_arquivo = os.path.join(diretorio_atual, 'log.txt')
    print(f"{agora()} - {texto}")

    # Abre o arquivo em modo de append (adiciona texto ao final)
    with open(caminho_arquivo, 'a', encoding='utf-8') as arquivo:  # Especifica a codificação UTF-8
        arquivo.write(f"{agora()} - {texto}\n")

def encontrar_diretorio_instantclient(nome_pasta="instantclient-basiclite-windows.x64-23.6.0.24.10\\instantclient_23_6"):
  registrar_log(f'encontrar_diretorio_instantclient - Inicio')
  # Obtém o diretório do script atual
  diretorio_atual = os.path.dirname(os.path.abspath(__file__))

  # Constrói o caminho completo para a pasta do Instant Client
  caminho_instantclient = os.path.join(diretorio_atual, nome_pasta)

  # Verifica se a pasta existe
  if os.path.exists(caminho_instantclient):
    registrar_log(f'encontrar_diretorio_instantclient - FIM')
    return caminho_instantclient
  else:
    registrar_log(f"A pasta '{nome_pasta}' não foi encontrada na raiz do aplicativo.")
    registrar_log(f'encontrar_diretorio_instantclient - FIM')
    return None
  
def resultados_exames_intervalo_58_min():
    try:
        registrar_log(f'resultados_exames_intervalo_58_min - INICIO')

        # Chamar a função para obter o caminho do Instant Client
        caminho_instantclient = encontrar_diretorio_instantclient()
        if caminho_instantclient:
            oracledb.init_oracle_client(lib_dir=caminho_instantclient)
        else:
            registrar_log("Erro ao localizar o Instant Client. Verifique o nome da pasta e o caminho.")

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

        # Chamar a função para obter o caminho do Instant Client
        caminho_instantclient = encontrar_diretorio_instantclient()
        if caminho_instantclient:
            oracledb.init_oracle_client(lib_dir=caminho_instantclient)
        else:
            registrar_log("Erro ao localizar o Instant Client. Verifique o nome da pasta e o caminho.")

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
    text = re.sub(r' +', ' ', text) # Substitui múltiplos espaços por um único espaço
    text = re.sub(r'(\r\n|\r|\n){2,}', '\n', text).strip() # Remove linhas em branco excessivas

    return text

def enviar_whatsapp_emergencia(mensagem_texto, modo_teste=False):
    """
    Envia mensagem via WhatsApp para o grupo HSF - RECEPÇÃO - TEMPOS DA EMERGÊNCIA.
    
    Args:
        mensagem_texto (str): Texto da mensagem a ser enviada
        modo_teste (bool): Se True, apenas registra no log sem enviar
    
    Returns:
        None
    """
    registrar_log("enviar_whatsapp_emergencia - INÍCIO")
    
    if not mensagem_texto or not mensagem_texto.strip():
        registrar_log("Nenhuma mensagem para enviar via WhatsApp.")
        registrar_log("enviar_whatsapp_emergencia - FIM")
        return

    if modo_teste:
        registrar_log("[MODO DE TESTE] Simulação de envio de mensagem para WhatsApp Emergência:")
        registrar_log(f"[MODO DE TESTE] Grupo: HSF - RECEPÇÃO - TEMPOS DA EMERGÊNCIA")
        registrar_log(f"[MODO DE TESTE] Mensagem: {mensagem_texto}")
        registrar_log("enviar_whatsapp_emergencia - FIM")
        return
    
    driver = None
    
    try:        
        # Configurações do Chrome
        options = Options()
        
        # Configurar o perfil de usuário para manter o login
        dir_path = os.path.dirname(os.path.abspath(__file__))
        profile_path = os.path.join(dir_path, "profile", "wpp")
        options.add_argument(f"user-data-dir={profile_path}")

        # Inicializa o driver
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        registrar_log('driver.get("https://web.whatsapp.com")')
        driver.get("https://web.whatsapp.com")

        registrar_log("time.sleep(15)")
        time.sleep(15) 

        registrar_log("WhatsApp Web aberto. Aguardando o campo de pesquisa...")

        # Espera explícita para o campo de pesquisa
        xpath_campo_pesquisa = '//*[@id="side"]/div[1]/div/div[2]/div/div/div[1]/p'
        
        try:
            wait = WebDriverWait(driver, 30)
            registrar_log("time.sleep(3)")
            time.sleep(3)
            campo_pesquisa_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_campo_pesquisa)))
            registrar_log("Campo de pesquisa encontrado e clicável.")
            campo_pesquisa_element.click()
            registrar_log("Clicado no campo de pesquisa.")

            # Localiza o campo de input de texto ativo para a pesquisa
            xpath_input_pesquisa_ativo = "//div[@id='side']//div[@contenteditable='true'][@role='textbox']"
            input_pesquisa_ativo = wait.until(EC.presence_of_element_located((By.XPATH, xpath_input_pesquisa_ativo)))
            registrar_log("Campo de input de pesquisa ativo encontrado.")
            
            nome_grupo = "HSF - RECEPÇÃO - TEMPOS DA EMERGÊNCIA"
            input_pesquisa_ativo.send_keys(nome_grupo)
            registrar_log(f"Texto '{nome_grupo}' enviado para o campo de pesquisa.")
            registrar_log("time.sleep(0.5)")
            time.sleep(0.5) 

            # Espera e clica no resultado da pesquisa correspondente ao nome do grupo
            xpath_resultado_grupo = f"//span[@class='matched-text _ao3e' and text()='{nome_grupo}']"
            registrar_log("time.sleep(0.5)")
            time.sleep(0.5) 

            resultado_grupo_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_resultado_grupo)))
            registrar_log(f"Resultado da pesquisa para '{nome_grupo}' encontrado e clicável.")
            resultado_grupo_element.click()
            registrar_log(f"Clicado no grupo '{nome_grupo}' na lista de resultados.")
            registrar_log("time.sleep(0.5)")
            time.sleep(0.5)

            # Localiza a caixa de texto do chat
            registrar_log('Localizando a caixa de texto do chat...')
            xpath_chat_caixa_de_texto = '//div[@id="main"]//div[@contenteditable="true"][@role="textbox"]'

            try:
                chat_caixa_de_texto_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_chat_caixa_de_texto)))
                registrar_log('Caixa de texto localizada e clicável com sucesso!')
                
                # Envia a mensagem
                chat_caixa_de_texto_element.send_keys(mensagem_texto)
                registrar_log(f"Mensagem enviada para a caixa de texto: {mensagem_texto}")
                registrar_log("time.sleep(0.5)")
                time.sleep(0.5)

                # Localiza e clica no botão de enviar
                registrar_log('Localizando e clicando no botão de enviar...')
                xpath_botao_enviar = "//button[@aria-label='Enviar']"
                botao_enviar_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_botao_enviar)))

                registrar_log('botao_enviar_element.click()')
                botao_enviar_element.click()
                registrar_log("Processo de envio de mensagem concluído.")
                registrar_log('time.sleep(5)')
                time.sleep(5)
                
            except Exception as e_chatbox:
                registrar_log(f"Erro ao localizar ou interagir com a caixa de texto do chat: {e_chatbox}")                
                registrar_log("time.sleep(5)")
                time.sleep(5)

            # Pausa breve para garantir que a mensagem seja processada
            time.sleep(5)

        except Exception as e_search:
            registrar_log(f"Erro ao tentar clicar no campo de pesquisa: {e_search}")
        
        # Fechar o navegador após o envio
        if driver:
            registrar_log("time.sleep(60)")
            time.sleep(60)            
            registrar_log("driver.quit()")
            driver.quit() 
        registrar_log("driver.quit() - Navegador fechado.")

    except Exception as e:
        registrar_log(f"Erro ao tentar enviar mensagem pelo WhatsApp Emergência: {e}")
    
    registrar_log("enviar_whatsapp_emergencia - FIM")


def enviar_whatsapp(lista_exames, modo_teste=False):
    """Abre o WhatsApp Web usando Selenium com perfil de usuário."""
    registrar_log("enviar_whatsapp - INÍCIO")
    if not lista_exames:
        registrar_log("Nenhum exame crítico para enviar via WhatsApp.")
        registrar_log("enviar_whatsapp - FIM")
        return

    if modo_teste:
        registrar_log("[MODO DE TESTE] Simulação de envio de mensagens para o WhatsApp:")
        if isinstance(lista_exames, list) and all(isinstance(sublist, list) for sublist in lista_exames):
            for sublist in lista_exames:
                for item_exame in sublist:
                    registrar_log(f"[MODO DE TESTE] Linha a ser enviada: {item_exame}")
        else:
            registrar_log(f"[MODO DE TESTE] Dados a serem enviados (formato não esperado para iteração linha a linha): {lista_exames}")
        return
    
    driver = None # Inicializa driver como None

    try:        
        # Configurações do Chrome
        options = Options()
        # Manter o navegador aberto após a execução do script (útil para depuração)
        # options.add_experimental_option("detach", True)

        # Configurar o perfil de usuário para manter o login
        # O diretório "profile/wpp" será criado na pasta do seu projeto
        dir_path = os.path.dirname(os.path.abspath(__file__))
        profile_path = os.path.join(dir_path, "profile", "wpp")
        options.add_argument(f"user-data-dir={profile_path}")

        # Inicializa o driver usando ChromeDriverManager
        # Isso baixa e gerencia o chromedriver automaticamente
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        registrar_log('driver.get("https://web.whatsapp.com")')
        driver.get("https://web.whatsapp.com")

        registrar_log("time.sleep(15)")
        time.sleep(15) 

        registrar_log("WhatsApp Web aberto. Aguardando o campo de pesquisa...")

        # Espera explícita para o campo de pesquisa (ou o contêiner dele)
        # O XPath fornecido parece ser para o placeholder do campo de pesquisa
        xpath_campo_pesquisa = '//*[@id="side"]/div[1]/div/div[2]/div/div/div[1]/p'
        # Um XPath mais robusto para o input de pesquisa pode ser: //div[@id='side']//div[@contenteditable='true'][@role='textbox']
        # Por enquanto, usaremos o XPath fornecido.
        
        try:
            wait = WebDriverWait(driver, 30) # Espera até 30 segundos
            registrar_log("time.sleep(3)")
            time.sleep(3)
            campo_pesquisa_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_campo_pesquisa)))
            registrar_log("Campo de pesquisa encontrado e clicável.")
            campo_pesquisa_element.click()
            registrar_log("Clicado no campo de pesquisa.")

            # Após clicar, o campo de pesquisa (ou um novo input) estará ativo.
            # Localiza o campo de input de texto ativo para a pesquisa.
            # Este XPath é comum para o campo de texto de pesquisa do WhatsApp Web.
            xpath_input_pesquisa_ativo = "//div[@id='side']//div[@contenteditable='true'][@role='textbox']"
            input_pesquisa_ativo = wait.until(EC.presence_of_element_located((By.XPATH, xpath_input_pesquisa_ativo)))
            registrar_log("Campo de input de pesquisa ativo encontrado.")
            
            nome_grupo = "LAB - VALORES CRÍTICOS"
            input_pesquisa_ativo.send_keys(nome_grupo)
            registrar_log(f"Texto '{nome_grupo}' enviado para o campo de pesquisa.")
            registrar_log("time.sleep(0.5)")
            time.sleep(0.5) 

            # Espera e clica no resultado da pesquisa correspondente ao nome do grupo
            xpath_resultado_grupo = f"//span[@class='matched-text _ao3e' and text()='{nome_grupo}']"
            registrar_log("time.sleep(0.5)")
            time.sleep(0.5) 

            resultado_grupo_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_resultado_grupo)))
            registrar_log(f"Resultado da pesquisa para '{nome_grupo}' encontrado e clicável.")
            resultado_grupo_element.click()
            registrar_log(f"Clicado no grupo '{nome_grupo}' na lista de resultados.")
            registrar_log("time.sleep(0.5)")
            time.sleep(0.5)

            # Agora que a conversa está aberta, localize a caixa de texto do chat.
            registrar_log('Localizando a caixa de texto do chat...')
            # Usamos WebDriverWait para esperar que a caixa de texto esteja presente e clicável.

            # O seletor abaixo é mais robusto para encontrar a caixa de texto do chat.
            # Ele busca por um elemento <div> que seja editável (contenteditable="true")
            # e tenha a função de uma caixa de texto (role="textbox"), dentro da área principal do chat (div com id="main").
            # Este tipo de seletor é muito mais estável que um "Full XPath", pois não depende da estrutura exata da página.
            # A linha que você adicionou com `driver.find_element` foi removida, pois o `wait.until` já faz a busca
            # e precisa receber a string do XPath, não o elemento já encontrado.
            xpath_chat_caixa_de_texto = '//div[@id="main"]//div[@contenteditable="true"][@role="textbox"]'

            try:
                chat_caixa_de_texto_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_chat_caixa_de_texto)))
                registrar_log('Caixa de texto localizada e clicável com sucesso!')
                
                # Opcional: Clicar na caixa de texto para garantir o foco (geralmente não é estritamente necessário para send_keys)
                # chat_caixa_de_texto_element.click()
                # registrar_log('Clicado na caixa de texto.')
                
                # Re-localiza a caixa de texto antes de cada envio principal
                def get_chat_box():
                    return wait.until(EC.element_to_be_clickable((By.XPATH, xpath_chat_caixa_de_texto)))

                # Envia cada detalhe de cada exame como uma mensagem separada
                if lista_exames:
                    # Envia um cabeçalho inicial
                    chat_caixa_de_texto_element.send_keys(" ")
                    chat_caixa_de_texto_element.send_keys(Keys.ENTER)
                    registrar_log("Cabeçalho da mensagem enviado.")
                    time.sleep(0.5) # Pequena pausa

                    registrar_log("Separador entre exames enviado.")
                    current_chat_box = get_chat_box()

                    agora_atual = datetime.now()
                    data_hora_formatada = '*' + agora_atual.strftime("%d/%m/%Y às %Hh%Mm") + '*'
                    registrar_log(f'data_hora_formatada: {data_hora_formatada}')

                    textinho = f'{data_hora_formatada}'
                    registrar_log(f'textinho: {textinho}')
                    current_chat_box.send_keys(textinho)
                    time.sleep(0.5)
                    current_chat_box.send_keys(Keys.CONTROL, Keys.ENTER)
                    time.sleep(0.5)

                    textinho2 = '*Analista Plantonista confirmar ciência do(s) resultado(s) crítico(s) encontrado(s):*'
                    current_chat_box.send_keys(textinho2)
                    time.sleep(0.5)
                    current_chat_box.send_keys(Keys.CONTROL, Keys.ENTER)
                    time.sleep(0.5)

                    current_chat_box.send_keys(Keys.CONTROL, Keys.ENTER)
                    time.sleep(0.5)

                    for i, exame in enumerate(lista_exames):
                        if i > 0: # Adiciona uma linha em branco (enviando um Enter) entre exames
                            registrar_log('Envia uma "mensagem em branco" como separador')
                            #get_chat_box().send_keys(Keys.ENTER) 
                            current_chat_box.send_keys(Keys.CONTROL, Keys.ENTER)

                            registrar_log('time.sleep(0.5)')
                            time.sleep(0.5) # Pequena pausa

                        for item_exame in exame: # item_exame é uma string como 'PRESCRICAO: 5977045'
                            if item_exame.strip(): # Garante que não estamos enviando strings vazias
                                current_chat_box = get_chat_box()
                                current_chat_box.send_keys(item_exame)
                                current_chat_box.send_keys(Keys.CONTROL, Keys.ENTER)
                                registrar_log(f"Linha enviada: {item_exame}")
                                time.sleep(1) # Pequena pausa para não sobrecarregar
                    
                else:
                    get_chat_box().send_keys("Nenhum exame crítico encontrado para reportar.")
                    get_chat_box().send_keys(Keys.ENTER)
                    registrar_log("Mensagem de 'nenhum exame' enviada.")
                
                registrar_log('time.sleep(0.5)')
                time.sleep(0.5)

                registrar_log('Localizando e clicando no botão de enviar...')
                # O seletor abaixo é mais robusto para encontrar o botão de enviar.
                # Ele busca pelo atributo 'aria-label', que descreve a função do botão ("Enviar").
                # Isso é muito mais estável do que um XPath completo ou um seletor de classe.
                # A espera explícita (wait.until) já aguarda o botão ficar clicável,
                # tornando pausas com time.sleep() desnecessárias e ineficientes.
                xpath_botao_enviar = "//button[@aria-label='Enviar']"
                botao_enviar_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_botao_enviar)))

                registrar_log('botao_enviar_element.click()')
                botao_enviar_element.click()
                registrar_log("Processo de envio de mensagens concluído.")
                registrar_log('time.sleep(5)')
                time.sleep(5)
            except Exception as e_chatbox:
                registrar_log(f"Erro ao localizar ou interagir com a caixa de texto do chat: {e_chatbox}")                
                registrar_log("time.sleep(5)")
                time.sleep(5)



            # Pausa breve para garantir que a mensagem seja processada antes de fechar o navegador
            time.sleep(5) # Ajuste conforme necessário para garantir o envio


        except Exception as e_search:
            registrar_log(f"Erro ao tentar clicar no campo de pesquisa: {e_search}")
        
        # Fechar o navegador após o envio para liberar recursos
        if driver: # Garante que o driver foi inicializado antes de tentar fechar
            registrar_log("time.sleep(60)")
            time.sleep(60)            
            registrar_log("driver.quit()")
            driver.quit() 
        registrar_log(" driver.quit() - Navegador fechado.")

    except Exception as e:
        registrar_log(f"Erro ao tentar enviar mensagem pelo WhatsApp: {e}")
    
    registrar_log("enviar_whatsapp - FIM")

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
            mensagem += "Prezados, informo a identificação de tempo(s) crítico(s) de atendimento(s) na Emergência:\n\n"
            mensagem += "--- TEMPOS ENCONTRADOS ---\n"
            
            for index, row in filtro_recepcao.iterrows():
                tempo_recepcao_min = converter_tempo_para_minutos(row['TOTAL_RECEP'])
                mensagem += f"Paciente: {row['PACIENTE']}\n"
                mensagem += f"Triagem Classificação: {row['TRIAGEM_CLASSIFICACAO']}\n"
                mensagem += f"Tempo Recepção: {tempo_recepcao_min} minutos\n"
                if len(filtro_recepcao) > 1:
                    mensagem += "\n"
        
        # Envia mensagem via WhatsApp (modo teste por enquanto)
        enviar_whatsapp_emergencia(mensagem, modo_teste=True)
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
            mensagem += "--- TEMPOS ENCONTRADOS ---\n"
            
            for index, row in filtro_triagem.iterrows():
                tempo_triagem_min = int(row['TEMPO_TRIAGEM_MINUTOS'])
                mensagem += f"Paciente: {row['PACIENTE']}\n"
                mensagem += f"Triagem Classificação: {row['TRIAGEM_CLASSIFICACAO']}\n"
                mensagem += f"Tempo Triagem: {tempo_triagem_min} minutos\n"
                if len(filtro_triagem) > 1:
                    mensagem += "\n"
        
        # Envia mensagem via WhatsApp (modo teste por enquanto)
        enviar_whatsapp_emergencia(mensagem, modo_teste=True)
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
            mensagem += "--- TEMPOS ENCONTRADOS ---\n"
            
            for index, row in filtro_espera.iterrows():
                tempo_espera_min = converter_tempo_para_minutos(row['TEMPO_ESPERA_ATEND'])
                mensagem += f"Paciente: {row['PACIENTE']}\n"
                mensagem += f"Triagem Classificação: {row['TRIAGEM_CLASSIFICACAO']}\n"
                mensagem += f"Espera por médico: {tempo_espera_min} minutos\n"
                if len(filtro_espera) > 1:
                    mensagem += "\n"
        
        # Envia mensagem via WhatsApp (modo teste por enquanto)
        enviar_whatsapp_emergencia(mensagem, modo_teste=True)
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
            mensagem += "--- TEMPOS ENCONTRADOS ---\n"
            
            for index, row in filtro_fila.iterrows():
                tempo_fila_min = converter_tempo_para_minutos(row['PACIENTE_SENHA_FILA_FIM'])
                mensagem += f"Paciente: {row['PACIENTE']}\n"
                mensagem += f"Triagem Classificação: {row['TRIAGEM_CLASSIFICACAO']}\n"
                mensagem += f"Tempo Final da Fila: {tempo_fila_min} minutos\n"
                if len(filtro_fila) > 1:
                    mensagem += "\n"
        
        # Envia mensagem via WhatsApp (modo teste por enquanto)
        enviar_whatsapp_emergencia(mensagem, modo_teste=True)
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
            mensagem += "⚠️ TEMPOS ENCONTRADOS ⚠️\n"
            
            for nr_atendimento, dados in pacientes_criticos.items():
                mensagem += f"🏥 *Atendimento:* {nr_atendimento}\n"
                mensagem += f"✅ *Paciente:* {dados['paciente']}\n"
                mensagem += f"📅 *Início Atendimento:* {dados['inicio_atendimento']}\n"
                mensagem += f"🔍 *Classificação:* {dados['classificacao']}\n"
                
                # Adicionar todos os tempos críticos deste paciente
                for tempo in dados['tempos_criticos']:
                    mensagem += f"{tempo}\n"
                
                # Separador entre pacientes (se houver mais de um)
                if len(pacientes_criticos) > 1:
                    mensagem += "\n" + "─" * 40 + "\n\n"
        
        # Envia mensagem via WhatsApp (modo teste por enquanto)
        enviar_whatsapp_emergencia(mensagem, modo_teste=True)
        registrar_log("Alerta unificado de tempos críticos processado e enviado")
        
    except Exception as e:
        registrar_log(f"Erro ao processar alertas unificados: {e}")
    
    registrar_log("processar_alertas_tempo_unificado - FIM")


def logica_principal_background(stop_event):
    """Lógica principal que será executada em um processo separado, repetidamente."""
    registrar_log("logica_principal_background - INÍCIO")
    # Defina True para testar sem enviar mensagens reais, False para operação normal
    MODO_TESTE_WHATSAPP = False  
    
    while not stop_event.is_set():
        registrar_log("Executando ciclo da lógica principal...")
        lista_de_resultados = resultados_exames_intervalo_58_min()
        registrar_log(f"lista_de_resultados: {lista_de_resultados}")        
        enviar_whatsapp(lista_de_resultados, modo_teste=MODO_TESTE_WHATSAPP)
        
        # --- INÍCIO DO PROCESSAMENTO DE HEMOGRAMAS CRÍTICOS ---
        registrar_log("Iniciando processamento de hemogramas críticos...")
        resultados_hemogramas = resultados_hemogramas_intervalo_58_min()
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
                
                enviar_whatsapp(mensagens_hemogramas_criticos_whatsapp, modo_teste=MODO_TESTE_WHATSAPP)
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
            enviar_whatsapp(mensagens_coagulogramas_criticos_whatsapp, modo_teste=MODO_TESTE_WHATSAPP)
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
            enviar_whatsapp(mensagens_hepatogramas_criticos_whatsapp, modo_teste=MODO_TESTE_WHATSAPP)
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
            enviar_whatsapp(mensagens_lipidogramas_criticos_whatsapp, modo_teste=MODO_TESTE_WHATSAPP)
        else:
            registrar_log("Nenhum lipidograma crítico encontrado para enviar.")
        # --- FIM DO PROCESSAMENTO DE LIPIDOGRAMAS CRÍTICOS ---
        
        # Espera 5 minutos (300 segundos) ou até o evento de parada ser setado
        registrar_log("Aguardando 60 minutos para o próximo ciclo...")
        registrar_log('stop_event.wait(3480) - Espera por 3480 segundos ou até stop_event ser setado')
        stop_event.wait(3480)

    registrar_log("logica_principal_background - FIM")
    print("Processo em background concluído.") # Feedback no console

def tempo_espera_emergencia():
    """Executa a query HSF - TODOS - TEMPO DE ESPERA EMERGENCIA.sql e retorna o dataframe."""
    registrar_log("tempo_espera_emergencia - INICIO")
    
    try:
        # Configurar o diretório do Instant Client
        diretorio_instantclient = encontrar_diretorio_instantclient()
        if diretorio_instantclient:
            oracledb.init_oracle_client(lib_dir=diretorio_instantclient)
            registrar_log(f"tempo_espera_emergencia - Instant Client configurado: {diretorio_instantclient}")
        else:
            registrar_log("tempo_espera_emergencia - ERRO: Diretório do Instant Client não encontrado")
            return None

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
            # Converte tudo para minutos e arredonda para inteiro
            total_minutos = horas * 60 + minutos + round(segundos / 60)
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

class AppGUI:
    def __init__(self, master):
        registrar_log("def __init__ GUI - INICIO")
        self.master = master
        master.title("HSF Olho de Deus")
        master.geometry("600x400") # Define o tamanho inicial da janela para 600x400
        master.resizable(False, False) # Impede que o usuário redimensione a janela

        self.process = None # Para armazenar a referência do processo
        self.stop_event = None # Para armazenar o evento de parada
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing) # Captura o evento de fechar janela

        self.label = tk.Label(master, text="Clique para começar...")
        self.label.pack(pady=100)

        self.start_button = tk.Button(master, text="LAB - Valores Críticos", command=self.iniciar_processo)
        self.start_button.pack(pady=10)
        
        self.emergencia_button = tk.Button(master, text="EMERGÊNCIA - Tempos de Espera", command=self.iniciar_alertas_emergencia)
        self.emergencia_button.pack(pady=10)
        
        registrar_log("def __init__ GUI - FIM")

    def iniciar_alertas_emergencia(self):
        """Inicia o processo de análise e envio de alertas de tempo da emergência."""
        registrar_log("iniciar_alertas_emergencia - Botão Emergência clicado")
        
        # Desabilita o botão para evitar múltiplos cliques
        self.emergencia_button.config(state=tk.DISABLED)
        self.label.config(text="Processando alertas de emergência...")
        
        try:
            # Executa a análise dos tempos da emergência
            registrar_log("Iniciando análise dos tempos da emergência")
            df = tempo_espera_emergencia()
            
            if df is not None:
                registrar_log("DataFrame obtido com sucesso, processando alertas unificados")
                
                # Processa alertas unificados (nova função que agrupa todos os tempos por paciente)
                processar_alertas_tempo_unificado(df)
                
                self.label.config(text="Alertas de emergência processados com sucesso!")
                registrar_log("Alertas de emergência unificados processados com sucesso")
            else:
                self.label.config(text="Erro ao obter dados da emergência")
                registrar_log("Erro: DataFrame da emergência retornou None")
                
        except Exception as e:
            registrar_log(f"Erro ao processar alertas de emergência: {e}")
            self.label.config(text="Erro ao processar alertas de emergência")
        
        finally:
            # Reabilita o botão após o processamento
            self.emergencia_button.config(state=tk.NORMAL)
            registrar_log("iniciar_alertas_emergencia - FIM")

    def iniciar_processo(self):
        registrar_log("iniciar_processo - Botão Iniciar clicado")
        # Desabilita o botão para evitar múltiplos cliques enquanto o processo está rodando
        if self.process is None or not self.process.is_alive():
            self.start_button.config(state=tk.DISABLED)
            self.label.config(text="Processo em execução ...")

            # Cria o evento de parada
            registrar_log('Cria o evento de parada')
            self.stop_event = Event()

            # Cria e inicia o processo, passando o evento de parada
            self.process = Process(target=logica_principal_background, args=(self.stop_event,))
            registrar_log('self.process.start()')
            self.process.start()
            registrar_log(f"Processo background iniciado com PID: {self.process.pid}")
        else:
            registrar_log("Processo background já está rodando.")

    def on_closing(self):
        """Lida com o fechamento da janela, sinalizando o processo background para parar."""
        registrar_log("Fechando janela. Sinalizando processo background para parar...")
        if self.process and self.process.is_alive():
        # Exemplo simples para reabilitar após um tempo (não ideal para processos longos):
        # self.master.after(6000, self.reabilitar_botao) # 6000 ms = 6s

    # def reabilitar_botao(self): # Exemplo de como poderia ser
    #     self.start_button.config(state=tk.NORMAL)
    #     self.label.config(text="Processo concluído. Clique para iniciar novamente.")

            self.stop_event.set() # Sinaliza o evento de parada
            self.process.join(timeout=5) # Espera o processo terminar por até 5 segundos
            if self.process.is_alive():
                registrar_log("Processo background não terminou, encerrando...")
                self.process.terminate() # Encerra o processo se ele não terminar sozinho
        registrar_log('self.master.destroy()')
        self.master.destroy() # Adicionar esta linha para fechar a janela

def main():
    """Função principal que configura e inicia a GUI."""
    registrar_log("MAIN - INICIO")
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()
    registrar_log("MAIN - FIM")

if __name__ == "__main__":
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

