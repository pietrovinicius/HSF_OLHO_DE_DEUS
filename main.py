#03/06/2025
#@PLima
#arquivo principal para execução do projeto

#cd c:\Pietro\Projetos\HSF_OLHO_DE_DEUS
#python -m venv .venv
#.venv\Scripts\activate
#pip install -r requirements.txt
#python main.py


import os
import time
from datetime import datetime
import tkinter as tk
from multiprocessing import Process
import oracledb

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

                # Exibir resultados no console
                for row in resultados:
                    print(row) # Imprime cada linha retornada pela query

        registrar_log(f'resultados_exames_intervalo_5_min - FIM')

    except oracledb.Error as erro:
        registrar_log(f"resultados_exames_intervalo_5_min - Erro no Oracle DB: {erro}")
    except Exception as erro: # Captura outros erros que não sejam do DB
        registrar_log(f"resultados_exames_intervalo_5_min - Erro geral: {erro}")


def logica_principal_background():
    """Lógica principal que será executada em um processo separado."""
    registrar_log("MAIN - INÍCIO")

    #TODO: executar todo o projeto no bloco abaixo

    resultados_exames_intervalo_5_min()

    registrar_log("time.sleep(5)")
    time.sleep(5) # Simula uma tarefa demorada

    registrar_log("MAIN - FIM")
    print("Processo em background concluído.") # Feedback no console

class AppGUI:
    def __init__(self, master):
        registrar_log("def __init__ GUI - INICIO")
        self.master = master
        master.title("HSF Olho de Deus")
        master.geometry("600x400") # Define o tamanho inicial da janela para 600x400
        master.resizable(False, False) # Impede que o usuário redimensione a janela

        self.label = tk.Label(master, text="Clique para começar...")
        self.label.pack(pady=10)

        self.start_button = tk.Button(master, text="Valores críticos", command=self.iniciar_processo)
        self.start_button.pack(pady=10)
        registrar_log("def __init__ GUI - FIM")

    def iniciar_processo(self):
        registrar_log("iniciar_processo - Botão Iniciar clicado")
        # Desabilita o botão para evitar múltiplos cliques enquanto o processo está rodando
        self.start_button.config(state=tk.DISABLED)
        self.label.config(text="Processo em execução...")

        # Cria e inicia o processo
        # É importante que o processo filho não tente modificar diretamente a GUI
        # pois Tkinter não é thread-safe/process-safe entre processos diferentes.
        processo = Process(target=logica_principal_background)
        processo.start()
        # Para reabilitar o botão, precisaríamos de um mecanismo de comunicação
        # (ex: polling, Queue) para saber quando o processo terminou.
        # Por simplicidade, ele permanecerá desabilitado nesta versão.
        # Uma forma de reabilitar seria o processo filho sinalizar o FIM,
        # ou a GUI verificar periodicamente se o processo ainda está vivo.
        # Exemplo simples para reabilitar após um tempo (não ideal para processos longos):
        # self.master.after(6000, self.reabilitar_botao) # 6000 ms = 6s

    # def reabilitar_botao(self): # Exemplo de como poderia ser
    #     self.start_button.config(state=tk.NORMAL)
    #     self.label.config(text="Processo concluído. Clique para iniciar novamente.")


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
