import os
import numpy as np
import tkinter as tk
import ttkbootstrap as ttk
import matplotlib as mpl
import matplotlib.pyplot as plt
from ttkbootstrap.constants import *
from PIL import Image
from tkinter import filedialog
from scipy.io import loadmat
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import RectangleSelector

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.title("Frame com Borda")
        self.geometry("1224x800")
        self.imagem_atual = None
        self.roi_size = 28  # Tamanho fixo da ROI de 28x28 pixels
        self.roi = None

        # Label superior
        self.label = ttk.Label(self, text="Image Processing", font=("Helvetica", 14))
        self.label.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=20)
        
        # Separador horizontal
        self.separator = ttk.Separator(self, orient=HORIZONTAL)
        self.separator.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=10)
        
        # Frame superior à esquerda
        self.label_frame = ttk.Labelframe(self, text="Opções", bootstyle="dark", padding=10, width=400 , height=200)
        self.label_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nw")

        # Botões no frame superior
        self.button_carregar_img = ttk.Button(self.label_frame, text="Carregar Imagem", command=self.carregar_imagem, bootstyle="dark", width=15)
        self.button_carregar_img.grid(row=0, column=0, padx=10, pady=5)
        
        self.button_carregar_roi = ttk.Button(self.label_frame, text="Carregar ROI", command=self.carregar_roi, bootstyle="dark", width=15)
        self.button_carregar_roi.grid(row=0, column=1, padx=10, pady=5)
        
        self.button_exibir_histograma = ttk.Button(self.label_frame, text="Exibir Histograma", command=self.exibir_histograma, bootstyle="dark", width=15)
        self.button_exibir_histograma.grid(row=0, column=2, padx=10, pady=5)
        
        self.button_recortar_roi = ttk.Button(self.label_frame, text="Recortar Roi", command=self.recortar_roi, bootstyle="dark", width=15)
        self.button_recortar_roi.grid(row=0, column=3, padx=10, pady=5)
        
        self.button_binarizar = ttk.Button(self.label_frame, text="Binarizar", command=self.on_click, bootstyle="dark", width=15)
        self.button_binarizar.grid(row=0, column=4, padx=10, pady=5)
        
        # Frame de imagem abaixo do frame superior
        self.imagem_frame = ttk.Labelframe(self, text="Exibir Imagens", bootstyle="dark", padding=5, width=500, height=500)
        self.imagem_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        self.imagem_frame.grid_propagate(False)  # Desativa o redimensionamento automático
        

        # Frame para exibir as rois
        self.novo_frame = ttk.Labelframe(self, text="Menu Roi", bootstyle="dark", padding=20, width= 500, height=500)
        self.novo_frame.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")
        self.novo_frame.grid_propagate(False)  # Desativa o redimensionamento automático

        self.roi_frame = ttk.Labelframe(self.novo_frame, text="Roi", bootstyle="dark", width=500, height=500)
        self.roi_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Conteúdo dentro do roi_frame, centralizado
        self.label_roi = ttk.Label(self.roi_frame, text="Conteúdo da ROI")  # Exemplo de conteúdo
        self.label_roi.pack(expand=True)  # Expande o conteúdo para centralizar
        
        self.button_teste = ttk.Button(self.novo_frame, text="Histograma Roi", command=lambda:print("teste"))
        self.button_teste.grid(row=2, column=0, padx=5, pady=5)
        
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
        self.columnconfigure(0, weight=2)  # O frame de imagem ocupa mais espaço
        self.columnconfigure(1, weight=1)
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



    def recortar_roi(self):
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
            self.roi = self.imagem_atual[y_start:y_end, x_start:x_end]

            # Limpa o frame de qualquer gráfico anterior
            for widget in self.roi_frame.winfo_children():
                widget.destroy()

            # Mostra a ROI no Matplotlib dentro do frame_roi
            fig, ax = plt.subplots(figsize=(1, 1), dpi=28)
            ax.imshow(self.roi, cmap='gray', interpolation='nearest')
            ax.axis('off')
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

            # Adiciona o gráfico ao canvas do Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.roi_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Exibe a imagem para seleção de ROI
        fig, ax = plt.subplots()
        ax.imshow(self.imagem_atual, cmap='gray')
        rect_selector = RectangleSelector(
            ax, onselect, interactive=False, button=[1], 
            props=dict(facecolor='green', edgecolor='green', alpha=0.5, fill=True)
        )
        plt.show()




    def salvar_roi(self):
        if self.roi is not None:
            #Caminho para salvar a roi
            output_path = "roi_image.png"
            fig, ax = plt.subplots(figsize=(1,1), dpi=28)
            ax.imshow(self.roi, cmap='gray',interpolation='nearest')
            ax.axis('off')
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
            fig.savefig(output_path, dpi=28, bbox_inches='tight', pad_inches=0)
            plt.close(fig)

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
            
    def exibir_roi_no_frame(self):
        # Limpa o frame de qualquer gráfico anterior
        for widget in self.label_roi.winfo_children():
            widget.destroy()
        
        # Cria a figura do Matplotlib e insere a imagem
        fig, ax = plt.subplots(figsize=(1, 1), dpi=100)
        ax.imshow(self.imagem_atual, cmap="gray")
        ax.axis('off')  # Esconde os eixos

        # Adiciona a figura ao canvas do Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.label_roi)
        canvas.draw()
        canvas.get_tk_widget().pack()


    def exibir_histograma(self):
        if self.imagem_atual is not None:
            imagem_array = np.array(self.imagem_atual)
            
            fig, ax = plt.subplots(figsize=(6, 4))
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
            ax.hist(imagem_array.ravel(), bins=256, range=(0, 256), color='gray')
            ax.set_title("Histograma da Imagem Exibida")
            ax.set_xlabel("Intensidade de Pixel", labelpad=5)
            ax.set_ylabel("Frequência", labelpad=5)
            plt.show()
        
        else:
            print("Nenhuma imagem para exibir o histograma")

    def on_click(self):
        self.label.config(text="Botão Clicado!")

if __name__ == "__main__":
    app = App()
    app.mainloop()
