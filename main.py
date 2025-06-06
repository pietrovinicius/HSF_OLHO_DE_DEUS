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
  
def resultados_exames_intervalo_5_min():
    try:
        registrar_log(f'resultados_exames_intervalo_5_min - INICIO')

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
                sql_file_name = 'HSF - RESULTADOS EXAMES COM INTERVALO DE 5 MINUTOS.sql'
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

        registrar_log(f'resultados_exames_intervalo_5_min - FIM')
        return resultados # Retorna a lista de resultados

    except oracledb.Error as erro:
        registrar_log(f"resultados_exames_intervalo_5_min - Erro no Oracle DB: {erro}")
        return None # Retorna None em caso de erro
    except Exception as erro: # Captura outros erros que não sejam do DB
        registrar_log(f"resultados_exames_intervalo_5_min - Erro geral: {erro}")
        return None # Retorna None em caso de erro

def enviar_whatsapp(lista_exames):
    """Abre o WhatsApp Web usando Selenium com perfil de usuário."""
    registrar_log("enviar_whatsapp - INÍCIO")
    if not lista_exames:
        registrar_log("Nenhum exame crítico para enviar via WhatsApp.")
        registrar_log("enviar_whatsapp - FIM")
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

        registrar_log("time.sleep(5)")
        time.sleep(5) 

        registrar_log("WhatsApp Web aberto. Aguardando o campo de pesquisa...")

        # Espera explícita para o campo de pesquisa (ou o contêiner dele)
        # O XPath fornecido parece ser para o placeholder do campo de pesquisa
        xpath_campo_pesquisa = '//*[@id="side"]/div[1]/div/div[2]/div/div/div[1]/p'
        # Um XPath mais robusto para o input de pesquisa pode ser: //div[@id='side']//div[@contenteditable='true'][@role='textbox']
        # Por enquanto, usaremos o XPath fornecido.
        
        try:
            wait = WebDriverWait(driver, 30) # Espera até 30 segundos
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
            xpath_chat_caixa_de_texto = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div[2]/div[1]/p'
            
            try:
                chat_caixa_de_texto_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_chat_caixa_de_texto)))
                registrar_log('Caixa de texto inicial localizada e clicável com sucesso!')
                
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

                registrar_log('Localiza e clica no botão de enviar')
                time.sleep(0.5)
                # Localiza e clica no botão de enviar
                xpath_botao_enviar = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[2]/button/span'
                botao_enviar_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_botao_enviar)))
                
                # Comentado pois cada linha é enviada com Keys.ENTER
                # Se Keys.ENTER não funcionar para a última linha ou em geral, descomente.
                registrar_log('time.sleep(0.5)')
                time.sleep(0.5)

                registrar_log('botao_enviar_element.click()')
                botao_enviar_element.click()
                # registrar_log("Botão de enviar clicado. Mensagem enviada.")
                registrar_log("Processo de envio de mensagens concluído.")
            except Exception as e_chatbox:
                registrar_log(f"Erro ao localizar ou interagir com a caixa de texto do chat: {e_chatbox}")


            # Removida a longa pausa daqui. Se precisar de uma pausa para observar,
            # adicione-a intencionalmente e por um período menor.


        except Exception as e_search:
            registrar_log(f"Erro ao tentar clicar no campo de pesquisa: {e_search}")
        
        registrar_log('time.sleep(60)')
        time.sleep(60)
        driver.quit() # Comentado para manter o navegador aberto para desenvolvimento/interação
        registrar_log(" driver.quit() - Navegador fechado.")

    except Exception as e:
        registrar_log(f"Erro ao tentar enviar mensagem pelo WhatsApp: {e}")
    
    registrar_log("enviar_whatsapp - FIM")


def logica_principal_background(stop_event):
    """Lógica principal que será executada em um processo separado, repetidamente."""
    registrar_log("logica_principal_background - INÍCIO")
    
    while not stop_event.is_set():
        registrar_log("Executando ciclo da lógica principal...")
        lista_de_resultados = resultados_exames_intervalo_5_min()
        registrar_log(f"lista_de_resultados: {lista_de_resultados}")        
        enviar_whatsapp(lista_de_resultados)
        
        # Espera 5 minutos (300 segundos) ou até o evento de parada ser setado
        registrar_log("Aguardando 58 minutos para o próximo ciclo...")
        registrar_log('stop_event.wait(3480) - Espera por 3480 segundos ou até stop_event ser setado')
        stop_event.wait(3480)

    registrar_log("logica_principal_background - FIM")
    print("Processo em background concluído.") # Feedback no console

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
        registrar_log("def __init__ GUI - FIM")

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
