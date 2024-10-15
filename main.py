import os
import numpy as np
import tkinter as tk
import ttkbootstrap as ttk
import matplotlib as mpl
import matplotlib.pyplot as plt
import cv2
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox
from scipy.io import loadmat
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import RectangleSelector

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.title("Processamento e Análise de Imagens")
        self.geometry("1224x800")
        self.imagem_atual = None
        self.roi_size = 28  # Tamanho fixo da ROI de 28x28 pixels
        self.roi = None

        # Label superior
        self.label = ttk.Label(self, text="Image Processing", font=("Helvetica", 14))
        self.label.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=20)
        
        # Separador horizontal
        self.separator = ttk.Separator(self, orient='horizontal')
        self.separator.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=10)
        
        # Frame superior à esquerda
        self.label_frame = ttk.Labelframe(self, text="Opções", bootstyle="dark", padding=10, width=400 , height=200)
        self.label_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nw")

        # Botões no frame superior
        self.button_carregar_img = ttk.Button(self.label_frame, text="Carregar Imagem", command=self.carregar_imagem, bootstyle="dark", width=15)
        self.button_carregar_img.grid(row=0, column=0, padx=10, pady=5)
        
        self.button_carregar_roi = ttk.Button(self.label_frame, text="Carregar ROI", command=self.carregar_roi, bootstyle="dark", width=15)
        self.button_carregar_roi.grid(row=0, column=1, padx=10, pady=5)
        
        self.button_exibir_histograma = ttk.Button(self.label_frame, text="Exibir Histograma", command=lambda:self.exibir_histograma(self.imagem_atual), bootstyle="dark", width=15)
        self.button_exibir_histograma.grid(row=0, column=2, padx=10, pady=5)
        
        self.button_recortar_roi = ttk.Button(self.label_frame, text="Recortar Roi", command=self.recortar_roi, bootstyle="dark", width=15)
        self.button_recortar_roi.grid(row=0, column=3, padx=10, pady=5)

        # Frame de imagem abaixo do frame superior
        self.imagem_frame = ttk.Labelframe(self, text="Exibir Imagens", bootstyle="dark", width=500, height=500)
        self.imagem_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        self.imagem_frame.grid_propagate(False)        

        # Frame para exibir as rois
        self.menu_roi_frame = ttk.Labelframe(self, text="Menu Roi", bootstyle="dark", width=500, height=500)
        self.menu_roi_frame.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")
        self.menu_roi_frame.grid_propagate(False)
    
        self.menu_roi_frame.columnconfigure(0, weight=1)
        self.menu_roi_frame.rowconfigure(0, weight=1)  

        self.roi_frame = ttk.Frame(self.menu_roi_frame)
        self.roi_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew", columnspan=3)

        
        # Controle de Tamanho para ajustar o figsize
        self.figsize_scale = tk.Scale(self.menu_roi_frame, from_=1, to=6, resolution=0.8, orient=tk.HORIZONTAL)
        self.figsize_scale.set(1) 
        self.figsize_scale.grid(row=1, column=0, padx=10, pady=10, sticky="ew",columnspan=3)

        # Botão para aplicar o tamanho de visualização
        self.button_aplicar_tamanho = ttk.Button(self.menu_roi_frame, text="Aplicar Zoom", command=self.atualizar_tamanho, bootstyle="dark", width=15)
        self.button_aplicar_tamanho.grid(row=2, column=0, padx=10, pady=10,columnspan=3)
        
        # Botão para calcular HI
        self.button_salvar_roi = ttk.Button(self.menu_roi_frame, text="Calcular HI", command=self.calcular_indice_hepatorenal, bootstyle="dark", width=15)
        self.button_salvar_roi.grid(row=3, column=0, padx=10, pady=10, columnspan=1)
        
        # Botão para salvar a ROI do fígado
        self.button_salvar_roi = ttk.Button(self.menu_roi_frame, text="Salvar ROI", command=self.salvar_roi_figado_selecionado, bootstyle="dark", width=15)
        self.button_salvar_roi.grid(row=3, column=1, padx=10, pady=10,columnspan=2)
        
        
        # Frame à direita para operações
        self.label_frame_direita = ttk.Labelframe(self, text="Operações", bootstyle="dark", padding=20)
        self.label_frame_direita.grid(row=3, column=2, padx=10, pady=5, sticky="ne")        
        
        # Botões no frame direito

        self.button_carregar_mat = ttk.Button(self.label_frame_direita, text="Carregar .Mat", command=self.carregar_dataset, bootstyle="dark", width=15)
        self.button_carregar_mat.grid(row=0, column=0, padx=10, pady=5)
        
        # Frame combobox
        self.combo_frame = ttk.Labelframe(self.label_frame_direita, text="Pacientes", bootstyle="dark", padding=5)
        self.combo_frame.grid(row=2, column=0, padx=10, pady=(25,10), sticky="nw")
        
        self.combo_paciente = ttk.Combobox(self.combo_frame, bootstyle="primary", state="readonly")
        self.combo_paciente.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.combo_paciente.bind("<<ComboboxSelected>>", self.carregar_imagens_paciente)
        
        self.combo_imagens = ttk.Combobox(self.combo_frame, bootstyle="primary", state="readonly")
        self.combo_imagens.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.combo_imagens.bind("<<ComboboxSelected>>", self.exibir_imagem_paciente)
        
        # Dicionário para armazenar as imagens dos pacientes
        self.imagens_pacientes = {}

        # Configuração de redimensionamento das colunas
        self.columnconfigure(0, weight=1)  # O frame de imagem ocupa mais espaço
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        
    def carregar_imagem(self):
        atual_dir = os.getcwd()
        caminho_imagem = filedialog.askopenfilename(
            initialdir=atual_dir,
            title="Selecione uma imagem",
            filetypes=[("Imagens", ".jpg .png")]
        )
        if caminho_imagem:
            self.imagem_atual = np.array(Image.open(caminho_imagem).convert("L"))
            self.exibir_imagem_no_frame()
             
    def binarizar_imagem(self):
        if self.roi is not None:
            #Aplicar adaptive threshold para binarização adaptativa
            adaptive_bw_img = cv2.adaptiveThreshold(self.roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                    cv2.THRESH_BINARY, 11, 2)
            bw_img_pil = Image.fromarray(adaptive_bw_img)
            img_tk = ImageTk.PhotoImage(bw_img_pil)
            self.roi_binarizada.config(image=img_tk)
            self.roi_binarizada.image = img_tk
            
            return adaptive_bw_img

        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada")
    
    def momento_hu(self):
        imagem_binarizada = self.binarizar_imagem()

        if imagem_binarizada is not None:
            momentos = cv2.moments(imagem_binarizada)
            momentos_hu = cv2.HuMoments(momentos)
            
            for i, hu in enumerate(momentos_hu):
                momentos_hu_str = "\n".join([f"Hu[{i + 1}]: {momento[0]}" for i, momento in enumerate(momentos_hu)])
                messagebox.showinfo("Momentos Invariantes de Hu", momentos_hu_str)
                return momentos_hu
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada")
        
    def carregar_dataset(self):
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo .mat",
            filetypes=[("Mat files", ".mat")]
        )
        
        if caminho_arquivo:
            mat = loadmat(caminho_arquivo)
            data = mat.get("data")
            
            if data is not None:
                for i in range(data.shape[1]):  # Iterar pacientes
                    paciente_id = f"Paciente {i + 1}"
                    imagens = []
                    
                    for j in range(10):  # Iterar sobre as 10 imagens de cada paciente
                        img_array = data['images'][0][i][j]
                        imagens.append(img_array)
                    
                    self.imagens_pacientes[paciente_id] = imagens
                
                self.combo_paciente['values'] = list(self.imagens_pacientes.keys())
                self.combo_paciente.current(0)
                self.carregar_imagens_paciente()
            
            else:
                print("Coluna 'data' não encontrada!")
                
                
    def carregar_imagens_paciente(self, event=None):
        paciente_id = self.combo_paciente.get()        
        imagens = self.imagens_pacientes.get(paciente_id, [])
        
        self.combo_imagens['values'] = [f"Imagem {i + 1}" for i in range(len(imagens))]
        self.combo_imagens.current(0)
        
        self.exibir_imagem_paciente()
    
    def exibir_imagem_paciente(self, event=None):
        paciente_id = self.combo_paciente.get()
        imagem_index = self.combo_imagens.current()
        
        imagem_array = self.imagens_pacientes.get(paciente_id)[imagem_index]
        
        if imagem_array is not None:
            self.imagem_atual = imagem_array
            self.exibir_imagem_no_frame()
            
    
    def exibir_imagem_no_frame(self):
        # Limpa o frame de qualquer gráfico anterior
        for widget in self.imagem_frame.winfo_children():
            widget.destroy()
        
        # Cria a figura do Matplotlib e insere a imagem
        fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
        ax.imshow(self.imagem_atual, cmap="gray")
        ax.axis('off')  # Esconde os eixos

        # Adiciona a figura ao canvas do Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.imagem_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        
        # Adiciona a barra de ferramentas de navegação
        toolbar = NavigationToolbar2Tk(canvas, self.imagem_frame)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        plt.close(fig)



    def recortar_roi(self):
        
        self.rois = []
        # Função de callback para a seleção de ROI com tamanho fixo de 28x28
        def onselect(eclick, erelease):
            x_center = int(eclick.xdata)
            y_center = int(eclick.ydata)
            
            x_start = max(x_center - self.roi_size // 2, 0)
            y_start = max(y_center - self.roi_size // 2, 0)
            x_end = x_start + self.roi_size
            y_end = y_start + self.roi_size
            
            x_end = min(x_end, self.imagem_atual.shape[1])
            y_end = min(y_end, self.imagem_atual.shape[0])
            x_start = max(0, x_end - self.roi_size)
            y_start = max(0, y_end - self.roi_size)

            # Recorta a ROI e habilita o botão de salvar
            roi = self.imagem_atual[y_start:y_end, x_start:x_end]
            self.rois.append(roi)

    
            if len(self.rois) == 2:
                self.exibir_rois()
                

        # Exibe a imagem para seleção de ROI
        fig, ax = plt.subplots()
        ax.imshow(self.imagem_atual, cmap='gray')
        rect_selector = RectangleSelector(
            ax, onselect, interactive=False, button=[1], 
            props=dict(facecolor='green', edgecolor='green', alpha=0.5, fill=True)
        )
        plt.show()


    def atualizar_tamanho(self):
        # Obtém o valor do slider e exibe as ROIs com o novo tamanho
        novo_tamanho = self.figsize_scale.get()
        self.exibir_rois(figsize=(novo_tamanho, novo_tamanho))
        
    def exibir_rois(self, figsize=(1, 1)):
        # Limpa o conteúdo anterior do roi_frame antes de exibir as novas ROIs
        for widget in self.roi_frame.winfo_children():
            widget.destroy()
            
        # Configura o layout do frame de ROIs para centralizar
        self.roi_frame.grid_columnconfigure(0, weight=1)
        self.roi_frame.grid_columnconfigure(1, weight=1)
        
        # Exibe as duas ROIs no Tkinter com figsize ajustável
        for i, roi in enumerate(self.rois):
            frame = ttk.Labelframe(self.roi_frame, text=f"ROI {i + 1}", bootstyle="dark")
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

            # Exibe a ROI com o figsize ajustado
            fig, ax = plt.subplots(figsize=figsize, dpi=24)
            ax.imshow(roi, cmap='gray')
            ax.axis('off')
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

            # Adiciona ao canvas do Tkinter
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            plt.close(fig)


    def calcular_indice_hepatorenal(self):
        if len(self.rois) < 2:
            messagebox.showerror("Erro", "Por favor, selecione as ROIs do fígado e do rim.")
            return

        roi_figado = self.rois[0]
        roi_rim = self.rois[1]

        # Calcula as médias de tons de cinza
        media_figado = np.mean(roi_figado)
        media_rim = np.mean(roi_rim)

        # Calcula o índice hepatorenal (HI)
        if media_rim != 0:
            indice_hepatorenal = media_figado / media_rim
            messagebox.showinfo("Índice Hepatorenal", f"HI = {indice_hepatorenal:.2f}")
            return indice_hepatorenal
        else:
            messagebox.showerror("Erro", "A média da ROI do rim é zero, não é possível calcular o índice.")
            return None

            
    def salvar_roi_figado_selecionado(self):
        try:
            numero_paciente = int(self.combo_paciente.get().split()[-1]) - 1  # Ajuste para o índice do paciente
            numero_imagem = int(self.combo_imagens.get().split()[-1]) - 1  # Ajuste para o índice da imagem
        except ValueError:
            messagebox.showerror("Erro", "Por favor, selecione um paciente e uma imagem válidos.")
            return

        # Chama a função para ajustar e salvar a ROI do fígado
        self.ajustar_e_salvar_roi_figado(numero_paciente, numero_imagem)
    
    def ajustar_e_salvar_roi_figado(self, numero_paciente, numero_imagem):
        
        indice_hepatorenal = self.calcular_indice_hepatorenal()
        
        if indice_hepatorenal is None:
            messagebox.showerror("Erro", "Não foi possivel calcular o HI")
            
        roi_figado = self.rois[0]

        #print("Matriz original da ROI do fígado:")
        #print(roi_figado)
            
        # Ajusta os tons de cinza da ROI do fígado
        roi_ajustada = roi_figado * indice_hepatorenal
        roi_ajustada = np.clip(roi_ajustada, 0, 255)  # Garante que os valores estejam entre 0 e 255
        roi_ajustada = np.round(roi_ajustada).astype(np.uint8)  # Arredonda e converte para uint8

        # Imprime a matriz ajustada da ROI do fígado
        #print("Matriz ajustada da ROI do fígado:")
        #print(roi_ajustada)

        # Define o caminho e o nome do arquivo
        nome_arquivo = f"ROI_{numero_paciente:02d}_{numero_imagem}.png"
        caminho_arquivo = os.path.join("pasta_rois", nome_arquivo)  # Substitua 'diretorio_destino' pelo seu diretório de destino
        # Salva a imagem
        Image.fromarray(roi_ajustada).save(caminho_arquivo)
        messagebox.showinfo("Salvo", f"Imagem salva como {nome_arquivo} em {caminho_arquivo}")            
              

    def carregar_roi(self):
        atual_dir = os.getcwd()
        caminho_imagem = filedialog.askopenfilename(
            initialdir=atual_dir,
            title="Selecione uma imagem",
            filetypes=[("Imagens", ".jpg .png")]
        )
        if caminho_imagem:
            self.imagem_atual = np.array(Image.open(caminho_imagem).convert("L"))
            self.exibir_roi_no_frame()



    def exibir_histograma(self, imagem):
        if imagem is not None:
            
            imagem_array = np.array(imagem)
            
            fig, ax = plt.subplots(figsize=(6, 4))
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
            ax.hist(imagem_array.ravel(), bins=256, range=(0, 256), color='gray')
            ax.set_title("Histograma da Imagem Exibida")
            ax.set_xlabel("Intensidade de Pixel", labelpad=5)
            ax.set_ylabel("Frequência", labelpad=5)
            plt.show(block=False)
 
        else:
            print("Nenhuma imagem para exibir o histograma")

    def on_close(self):
        self.destroy()  # Fecha a janela do Tkinter
        plt.close('all')  # Fecha todos os gráficos abertos do Matplotlib
        self.quit()  # Encerra o loop principal
        os._exit(0)  # Garante que o processo termine
    
if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close) 
    app.mainloop()
