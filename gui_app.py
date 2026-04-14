"""
Interface Gráfica para HSF Olho de Deus.

Sistema de monitoramento automatizado com interface CustomTkinter.
Permite executar ciclos de monitoramento sob demanda e visualizar logs em tempo real.

Autor: @PLima
Data: 22/01/2026
"""

import customtkinter as ctk
import threading
import sys
import io
from datetime import datetime, timedelta
from version import __version__
from main import (
    executar_ciclo_completo,
    set_log_callback,
    inicializar_oracle_client_global,
    ordens_de_servico_com_mais_de_2_dias,
    fechar_playwright
)


class HSFApp(ctk.CTk):
    """Aplicação principal da interface gráfica HSF Olho de Deus."""

    def __init__(self):
        """Inicializa a aplicação."""
        super().__init__()

        # Configurações da janela
        self.title("HSF Olho de Deus - Sistema de Monitoramento")
        self.geometry("900x700")
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Estado da aplicação
        self.executando = False
        self.thread_execucao = None
        self.parar_loop = False
        
        
        # Inicializar Oracle Client Globalmente
        inicializar_oracle_client_global()
        
        # Resetar arquivo de log ao abrir o app
        try:
            with open('log.txt', 'w', encoding='utf-8') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H-%M-%S')} - Log resetado na inicializacao\n")
        except Exception as e:
            print(f"Erro ao resetar log: {e}")
        
        # Evento para controlar parada
        self.stop_event = threading.Event()
        
        # Configurar callback de logos (conectar com main.py)
        set_log_callback(self.adicionar_log_callback)
        
        # Criar interface
        self._criar_interface()
        
    def _criar_interface(self):
        """Cria os elementos da interface gráfica."""
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        self.titulo = ctk.CTkLabel(
            self.main_frame,
            text="🏥 HSF Olho de Deus",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.titulo.pack(pady=(10, 5))
        
        # Subtítulo
        self.subtitulo = ctk.CTkLabel(
            self.main_frame,
            text="Sistema de Monitoramento Hospitalar",
            font=ctk.CTkFont(size=14)
        )
        self.subtitulo.pack(pady=(0, 20))
        
        # Frame de status
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.pack(fill="x", pady=(0, 20))
        
        # Label de status
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Status: Parado",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00ff00"
        )
        self.status_label.pack(pady=10)
        
        # Frame de botões
        self.botoes_frame = ctk.CTkFrame(self.main_frame)
        self.botoes_frame.pack(fill="x", pady=(0, 20))
        
        # Botão Executar Ciclo Completo (MOMENTANEAMENTE: VALIDAR OS TI)
        self.btn_executar = ctk.CTkButton(
            self.botoes_frame,
            text="🧪 Validar Fluxo O.S. TI",
            command=self.executar_ciclo,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color="#1f6aa5",
            hover_color="#144870"
        )
        self.btn_executar.pack(side="left", expand=True, padx=(10, 5))
        
        # Botão Parar Execução
        self.btn_parar = ctk.CTkButton(
            self.botoes_frame,
            text="⏹️ Parar Execução",
            command=self.parar_execucao,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color="#c42b1c",
            hover_color="#8b1f15",
            state="disabled"
        )
        self.btn_parar.pack(side="right", expand=True, padx=(5, 10))
        
        # Label para área de logs
        self.log_titulo = ctk.CTkLabel(
            self.main_frame,
            text="📋 Logs de Execução",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.log_titulo.pack(pady=(0, 10))
        
        # Área de logs (Text widget)
        self.log_text = ctk.CTkTextbox(
            self.main_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True)
        
        # Botão Limpar Logs
        self.btn_limpar = ctk.CTkButton(
            self.main_frame,
            text="🗑️ Limpar Logs",
            command=self.limpar_logs,
            font=ctk.CTkFont(size=12),
            height=30,
            fg_color="#555555",
            hover_color="#333333"
        )
        self.btn_limpar.pack(pady=(10, 0))
        
        # Versão no rodapé (lado direito)
        self.version_label = ctk.CTkLabel(
            self.main_frame,
            text=f"v{__version__}",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#555555"
        )
        self.version_label.pack(side="bottom", anchor="e", pady=(5, 0))
        
        # Auto-start: Apenas TI (conforme solicitado v3.1.6)
        self.after(1000, self.auto_start_ti_only)
    
    def adicionar_log_callback(self, mensagem):
        """Callback chamada pelo main.py quando um log é gerado."""
        # Agendar atualização da GUI na main thread
        self.after(0, lambda: self.adicionar_log(mensagem, from_callback=True))

    def adicionar_log(self, mensagem, from_callback=False):
        """
        Adiciona mensagem à área de logs.
        
        Args:
            mensagem (str): Mensagem a ser adicionada
            from_callback (bool): Se veio do callback (já tem timestamp em alguns casos, mas aqui garantimos padronizacao)
        """
        if not from_callback:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_formatado = f"[{timestamp}] {mensagem}\n"
        else:
            # Se veio do callback, assumimos que é texto puro do registrar_log
            # O registrar_log do main.py não manda timestamp no callback, então adicionamos aqui
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_formatado = f"[{timestamp}] {mensagem}\n"
        
        # Inserir no widget de texto
        self.log_text.insert("end", log_formatado)
        self.log_text.see("end")  # Auto-scroll para o final
        
    def limpar_logs(self):
        """Limpa a área de logs."""
        self.log_text.delete("1.0", "end")
        self.adicionar_log("Logs limpos")
        
    def atualizar_status(self, status, cor="#00ff00"):
        """
        Atualiza o label de status.
        
        Args:
            status (str): Texto do status
            cor (str): Cor do texto (hex)
        """
        self.status_label.configure(text=f"Status: {status}", text_color=cor)
        
    def executar_ciclo(self):
        """Inicia a execução em thread separada."""
        if self.executando:
            self.adicionar_log("⚠️ Já existe uma execução em andamento!")
            return
            
        # Marcar como executando
        self.executando = True
        self.parar_loop = False
        self.stop_event.clear() # Limpa evento de parada
        self.atualizar_status("Rodando - Monitoramento Contínuo", "#ffaa00")
        
        # Desabilitar botão executar e habilitar botão parar
        self.btn_executar.configure(state="disabled")
        self.btn_parar.configure(state="normal")
        
        # Executar em thread separada
        self.thread_execucao = threading.Thread(
            target=self._executar_logica,
            daemon=True
        )
        self.thread_execucao.start()
        
    def _executar_logica(self):
        """Lógica executada na thread com loop contínuo."""
        try:
            from main import executar_ciclo_completo
            
            self.adicionar_log("🔄 Iniciando ciclo de monitoramento contínuo...")
            
            while not self.stop_event.is_set():
                # Data/hora inicio do ciclo
                inicio_ciclo = datetime.now()
                
                # Executa o ciclo completo
                try:
                    executar_ciclo_completo()
                except Exception as e_ciclo:
                     self.adicionar_log(f"⚠️ Erro ao executar ciclo completo: {e_ciclo}")
                
                if self.stop_event.is_set():
                    self.adicionar_log("🛑 Execução interrompida pelo usuário.")
                    break
                
                # Calcular tempo para a próxima hora cheia
                agora = datetime.now()
                proxima_hora = (agora + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
                
                # Se já passou da hora (ex: demorou muito), ajusta
                if proxima_hora <= agora:
                     proxima_hora += timedelta(hours=1)
                
                segundos_espera = (proxima_hora - agora).total_seconds()
                
                # Log de espera
                self.adicionar_log(f"⏳ Aguardando {int(segundos_espera)}s até a próxima execução ({proxima_hora.strftime('%H:%M:%S')})...")
                
                # Espera interruptível
                # wait() retorna True se a flag for setada (interrupção), False se der timeout (continuar)
                if self.stop_event.wait(timeout=segundos_espera):
                    self.adicionar_log("🛑 Espera interrompida pelo usuário.")
                    break
            
        except Exception as e:
            self.adicionar_log(f"❌ Erro crítico na thread: {e}")
            
        finally:
            # Resetar estado na main thread
            self.after(0, self._resetar_botoes)

    def _resetar_botoes(self):
        self.executando = False
        self.atualizar_status("Parado", "#00ff00")
        self.btn_executar.configure(state="normal")
        self.btn_parar.configure(state="disabled")
        self.adicionar_log("ℹ️ Execução finalizada (aguardando novo comando)")

            
    def parar_execucao(self):
        """Para a execução atual."""
        if not self.executando:
            return
            
        self.adicionar_log("⏹️ Solicitando parada...")
        self.parar_loop = True
        self.stop_event.set() # Sinaliza parada para sair do wait() imediatamente
        
        # Tentar fechar drivers
        self._fechar_drivers_forca()
        
        # O reset dos botões acontecerá no finally da thread ou aqui?
        # É mais seguro deixar a thread morrer naturalmente ou forçar o reset se ela travar.
        # Vamos forçar o reset visual.
        self._resetar_botoes()
        
    def _fechar_drivers_forca(self):
        """Fecha os drivers do WhatsApp Web globalmente."""
        self.adicionar_log("🔒 Sinal de parada enviado ao Loop Principal.")
        self.adicionar_log("⚠️ O ciclo será finalizado e o navegador limpo com segurança pela thread nativa.")

    def auto_start_ti_only(self):
        """Inicia apenas o envio de OS da TI automaticamente na inicialização."""
        if self.executando:
            return
            
        self.executando = True
        self.atualizar_status("Auto-start: O.S. TI...", "#ffaa00")
        
        def _task():
            try:
                from main import ordens_de_servico_com_mais_de_2_dias, ordens_de_servico_fechadas_hoje, fechar_playwright
                self.adicionar_log("🚀 [AUTO-START] Iniciando Processamento de O.S. TI (Geral)...")
                
                # 1. Fechadas Hoje
                self.adicionar_log("📥 Processando O.S. Encerradas Hoje...")
                ordens_de_servico_fechadas_hoje()
                
                # 2. Atrasadas (>2 dias)
                self.adicionar_log("⚠️ Processando O.S. Atrasadas (>2 dias)...")
                ordens_de_servico_com_mais_de_2_dias()
                
                self.adicionar_log("✅ [AUTO-START] Concluído com sucesso.")
            except Exception as e:
                self.adicionar_log(f"❌ [AUTO-START] Falha no fluxo TI: {e}")
            finally:
                fechar_playwright() # Limpa recursos do browser
                self.executando = False
                self.after(0, lambda: self.atualizar_status("Pronto", "#00ff00"))
                self.after(0, lambda: self.btn_executar.configure(state="normal"))
                self.after(0, lambda: self.btn_parar.configure(state="disabled"))

        self.thread_execucao = threading.Thread(target=_task, daemon=True)
        self.btn_executar.configure(state="disabled")
        self.btn_parar.configure(state="normal")
        self.thread_execucao.start()


def main():
    """Função principal para executar a aplicação."""
    app = HSFApp()
    app.mainloop()


if __name__ == "__main__":
    main()
