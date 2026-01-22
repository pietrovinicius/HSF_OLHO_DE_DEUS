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
from datetime import datetime
from main import (
    executar_ciclo_completo,
    set_log_callback,
    driver_emergencia_global,
    driver_whatsapp_global,
    driver_is_alive,
    inicializar_oracle_client_global
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
        
        # Botão Executar Ciclo Completo
        self.btn_executar = ctk.CTkButton(
            self.botoes_frame,
            text="▶️ Executar Ciclo Completo",
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
        self.atualizar_status("Rodando", "#ffaa00")
        
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
        """Lógica executada na thread."""
        try:
            # Executa a função refatorada do main.py
            # Isso garante que a GUI faça EXATAMENTE o mesmo que o CLI
            from main import executar_ciclo_completo
            
            executar_ciclo_completo()
            
        except Exception as e:
            self.adicionar_log(f"❌ Erro crítico lançado para a GUI: {e}")
            
        finally:
            # Ao terminar (seja sucesso ou erro), reseta a interface
            # Nota: Em um sistema de loop real, aqui poderíamos ter um loop while not self.parar_loop
            # Mas como o pedido foi "botão executa UMA das tarefas" (ou ciclo), vamos manter execução única.
            # Se o usuário quiser loop, ele pode clicar de novo ou implementamos um loop aqui.
            # O main.py tem loop. Aqui, o botão chama "Executar Ciclo Completo" (singular).
            
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
            self.adicionar_log("⚠️ Nenhuma execução em andamento!")
            return
            
        self.adicionar_log("⏹️ Solicitando parada...")
        self.parar_loop = True
        
        # Tentar fechar drivers imediatamente (forçar parada)
        # Atenção: Isso pode gerar exceções na thread de execução, que serão capturadas
        self._fechar_drivers_forca()
        
        # O reset dos botões acontecerá no finally da thread ou aqui?
        # É mais seguro deixar a thread morrer naturalmente ou forçar o reset se ela travar.
        # Vamos forçar o reset visual.
        self._resetar_botoes()
        
    def _fechar_drivers_forca(self):
        """Fecha os drivers do WhatsApp Web globalmente."""
        # Importar globais para fechar
        from main import driver_emergencia_global, driver_whatsapp_global, driver_is_alive
        
        try:
            if driver_emergencia_global and driver_is_alive(driver_emergencia_global):
                driver_emergencia_global.quit()
                self.adicionar_log("🔒 Driver de emergência fechado forçosamente")
                
            if driver_whatsapp_global and driver_is_alive(driver_whatsapp_global):
                driver_whatsapp_global.quit()
                self.adicionar_log("🔒 Driver de laboratório fechado forçosamente")
                
        except Exception as e:
            self.adicionar_log(f"⚠️ Erro ao fechar drivers: {e}")


def main():
    """Função principal para executar a aplicação."""
    app = HSFApp()
    app.mainloop()


if __name__ == "__main__":
    main()
