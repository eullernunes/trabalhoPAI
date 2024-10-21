import os
import cv2
import numpy as np
import tkinter as tk
import ttkbootstrap as ttk
import locale
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from skimage.feature import graycomatrix, graycoprops
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox
from scipy.io import loadmat
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import RectangleSelector

locale.setlocale(locale.LC_NUMERIC,'C')

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.title("Processamento e Análise de Imagens")
        self.geometry("1220x980")
        self.imagem_atual = None
        self.roi_binarizada = None
        self.roi = None
        self.roi_size = 28  # Tamanho fixo da ROI de 28x28 pixels
        self.rois = []  # Lista para armazenar as ROIs

        # Label superior
        self.label = ttk.Label(self, text="Image Processing", font=("Helvetica", 14))
        self.label.grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=20)
        
        # Separador horizontal
        self.separator = ttk.Separator(self, orient='horizontal')
        self.separator.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=10)
        
        # Frame superior à esquerda
        self.label_frame = ttk.Labelframe(self, text="Opções", bootstyle="dark", padding=10)
        self.label_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nw")

        # Botões no frame superior
        self.button_carregar_img = ttk.Button(self.label_frame, text="Carregar Imagem", command=self.carregar_imagem, bootstyle="dark", width=15)
        self.button_carregar_img.grid(row=0, column=0, padx=10, pady=5)
        
        self.button_carregar_roi = ttk.Button(self.label_frame, text="Carregar ROI", command=self.carregar_roi, bootstyle="dark", width=15)
        self.button_carregar_roi.grid(row=0, column=1, padx=10, pady=5)
        
        self.button_exibir_histograma = ttk.Button(self.label_frame, text="Exibir Histograma", command=lambda: self.exibir_histograma(self.imagem_atual), bootstyle="dark", width=15)
        self.button_exibir_histograma.grid(row=0, column=2, padx=10, pady=5)
        
        self.button_recortar_roi = ttk.Button(self.label_frame, text="Recortar ROI", command=self.recortar_roi, bootstyle="dark", width=15)
        self.button_recortar_roi.grid(row=0, column=3, padx=10, pady=5)

        # Frame de imagem abaixo do frame superior
        self.imagem_frame = ttk.Labelframe(self, text="Exibir Imagens", bootstyle="dark", width=500, height=500)
        self.imagem_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        self.imagem_frame.grid_propagate(False)        

        # Frame para exibir as ROIs
        self.menu_roi_frame = ttk.Labelframe(self, text="Menu ROI", bootstyle="dark", width=450, height=450)
        self.menu_roi_frame.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")
        self.menu_roi_frame.grid_propagate(False)

        # Novo frame para exibir as ROIs
        self.roi_frame = ttk.Frame(self.menu_roi_frame)
        self.roi_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew", columnspan=3)

        self.menu_roi_frame.columnconfigure(0, weight=1)
        self.menu_roi_frame.columnconfigure(1, weight=1)
        self.menu_roi_frame.columnconfigure(2, weight=1)

        self.menu_roi_frame.rowconfigure(0, weight=1)  # Permite que a linha das ROIs se expanda
        self.menu_roi_frame.rowconfigure(1, weight=0)  # Linha para os botões não precisa se expandir

        # Controle de Tamanho para ajustar o figsize
        self.figsize_scale = tk.Scale(self.menu_roi_frame, from_=1, to=6, resolution=0.8, orient=tk.HORIZONTAL)
        self.figsize_scale.set(1)
        self.figsize_scale.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="ew", columnspan=3)

        # Botões na linha abaixo do controle de tamanho
        self.button_aplicar_tamanho = ttk.Button(self.menu_roi_frame, text="Aplicar Zoom", command=self.atualizar_tamanho, bootstyle="dark")
        self.button_aplicar_tamanho.grid(row=2, column=1, padx=10, pady=(5, 15), sticky="ew", columnspan=1)

        # Botões para calcular HI e ajustar ROI
        self.button_calcular_hi = ttk.Button(self.menu_roi_frame, text="Calcular HI", command=lambda: self.calcular_indice_hepatorenal(1), bootstyle="dark")
        self.button_calcular_hi.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.button_ajustar_roi = ttk.Button(self.menu_roi_frame, text="Ajustar ROI", command=lambda:self.ajusta_roi_figado(0), bootstyle="dark")
        self.button_ajustar_roi.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        self.button_salvar_roi = ttk.Button(self.menu_roi_frame, text="Salvar ROI", command=self.salvar_roi_figado_selecionado, bootstyle="dark")
        self.button_salvar_roi.grid(row=3, column=2, padx=10, pady=5, sticky="ew")

        # Botões para calcular Hu, matriz e exibir histograma, ocultos inicialmente
        self.button_calcular_hu = ttk.Button(self.menu_roi_frame, text="Calcular Hu", command=self.momento_hu, bootstyle="dark")
        self.button_calcular_hu.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        self.button_calcular_hu.grid_forget()

        self.button_calcular_glcm = ttk.Button(self.menu_roi_frame, text="Calcular GLCM", command=self.processar_roi, bootstyle="dark")
        self.button_calcular_glcm.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        self.button_calcular_glcm.grid_forget()
        
        self.button_exibir_histograma = ttk.Button(self.menu_roi_frame, text="Exibir Histograma", command=lambda:self.exibir_histograma(self.roi), bootstyle="dark")
        self.button_exibir_histograma.grid(row=4, column=2, padx=10, pady=5, sticky="ew")
        self.button_exibir_histograma.grid_forget()
        
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
             
    def carregar_roi(self):
        
        atual_dir = os.getcwd()
        caminho_imagem = filedialog.askopenfilename(
            initialdir=atual_dir,
            title="Selecione uma imagem",
            filetypes=[("Imagens", ".jpg .png")]
        )
        
        if caminho_imagem:
            self.roi = np.array(Image.open(caminho_imagem))
            
            # Limpa as ROIs anteriores e adiciona nova ROI
            self.rois.clear()
            self.rois.append(self.roi)
            
            for widget in self.imagem_frame.winfo_children():
                widget.destroy()
                
            # Atualiza a exibição das ROIs no frame
            self.exibir_rois(figsize=(1, 1))  # Use o tamanho que deseja para a exibição
            
            self.remove_botoes_antigos()
        
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

    def binarizar_imagem(self):
            if self.roi is not None:
                print("entrou")
                # Aplicar adaptive threshold para binarização adaptativa
                self.roi_binarizada = cv2.adaptiveThreshold(self.roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                        cv2.THRESH_BINARY, 11, 2)
            else:
                messagebox.showerror("Erro", "Nenhuma imagem carregada")
                
    def momento_hu(self):

        self.binarizar_imagem()

        if self.roi_binarizada is not None:
            momentos = cv2.moments(self.roi_binarizada)
            momentos_hu = cv2.HuMoments(momentos)
            
            for i, hu in enumerate(momentos_hu):
                momentos_hu_str = "\n".join([f"Hu[{i + 1}]: {momento[0]}" for i, momento in enumerate(momentos_hu)])
                messagebox.showinfo("Momentos Invariantes de Hu", momentos_hu_str)
                return momentos_hu
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada")

    def recortar_roi(self):
        
        self.remove_botoes_novos()
         
        for widget in self.roi_frame.winfo_children():
            widget.destroy()
            
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

            if len(self.rois) >= 2:
                self.rois.clear()

            self.rois.append(roi)
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
        novo_tamanho = float(self.figsize_scale.get())

        # Atualiza as ROIs exibidas
        self.exibir_rois(figsize=(novo_tamanho, novo_tamanho))

        # Atualiza a ROI ajustada, se ela já tiver sido criada
        if hasattr(self, 'roi_ajustada'):
            # Chama a função de ajuste de ROI para atualizar a ROI ajustada
            self.ajusta_roi_figado(0, figsize=(novo_tamanho, novo_tamanho))

    def exibir_rois(self, figsize=(1, 1)):
        # Limpa o conteúdo anterior do roi_frame antes de exibir as novas ROIs
        for widget in self.roi_frame.winfo_children():
            widget.destroy()
            
        # Configura o layout do frame de ROIs para centralizar
        self.roi_frame.grid_columnconfigure(0, weight=1)
        self.roi_frame.grid_columnconfigure(1, weight=1)

        # Exibe as ROIs no Tkinter com figsize ajustável
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

    def calcular_indice_hepatorenal(self, selecao):
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
            
            if selecao == 1:
                messagebox.showinfo("Índice Hepatorenal", f"HI = {indice_hepatorenal:.2f}")
                
            return indice_hepatorenal
        else:
            messagebox.showerror("Erro", "A média da ROI do rim é zero, não é possível calcular o índice.")
            return None
    
    def calcular_glcm(self, distancias=[1, 2, 4, 8], angulos=[0, np.pi/2, np.pi, 3*np.pi/2]):
         # Verifica se a ROI é binarizada
        if self.roi.dtype != np.uint8:
            self.roi = (self.roi * 255).astype(np.uint8)

        # GLCM e características
        glcm_results = {}
        for distancia in distancias:
            for angulo in angulos:
                # Calcule a GLCM
                glcm = graycomatrix(self.roi, [distancia], [angulo],  symmetric=True, normed=True)

                # Calcule propriedades da GLCM
                glcm_props = {
                    'contrast': graycoprops(glcm, 'contrast')[0, 0],
                    'dissimilarity': graycoprops(glcm, 'dissimilarity')[0, 0],
                    'homogeneity': graycoprops(glcm, 'homogeneity')[0, 0],
                    'energy': graycoprops(glcm, 'energy')[0, 0],
                    'correlation': graycoprops(glcm, 'correlation')[0, 0],
                    'ASM': graycoprops(glcm, 'ASM')[0, 0]  # Angular Second Moment
                }

                # Armazena os resultados
                key = f'Distância: {distancia}, Ângulo: {angulo * (180/np.pi)}°'
                glcm_results[key] = (glcm, glcm_props)

        return glcm_results

    def processar_roi(self):
        if self.roi is not None:
            glcm_results = self.calcular_glcm()
            
            # Exibir ou processar os resultados conforme necessário
            for key, (glcm, props) in glcm_results.items():
                print(f"{key}: {props}")

                # Extraindo distância e ângulo da chave
                distancia = int(key.split(",")[0].split(":")[1].strip())
                angulo = float(key.split(",")[1].split(":")[1].strip().replace('°', '')) * (np.pi / 180)  # Convertendo para radianos

                # Plotar a GLCM
                self.plot_glcm(glcm[:, :, 0], distancia, angulo)  # glcm[:, :, 0] para pegar a primeira GLCM calculada
        else:
            messagebox.showerror("Erro", "Nenhuma ROI carregada.")
   
    def ajusta_roi_figado(self, selecao, figsize=(1,1)):
        
        #Calcula o HI e seleciona a roi do indice 0 (que é a do figado)
        indice_hepatorenal = self.calcular_indice_hepatorenal(selecao)
        
        if indice_hepatorenal is None:
            messagebox.showerror("Erro", "Não foi possivel calcular o HI")
            
        roi_figado = self.rois[0]

        print("Matriz original da ROI do fígado:")
        print(roi_figado)
        print(indice_hepatorenal)
        
        # Ajusta os tons de cinza da ROI do fígado
        self.roi_ajustada = roi_figado * indice_hepatorenal
        self.roi_ajustada = np.clip(self.roi_ajustada, 0, 255)  # Garante que os valores estejam entre 0 e 255
        self.roi_ajustada = np.round(self.roi_ajustada).astype(np.uint8)  # Arredonda e converte para uint8
        
        frame = ttk.Labelframe(self.roi_frame, text=f"Roi Ajustada", bootstyle="dark")
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)
        
        # Exibe a ROI ajustada
        fig, ax = plt.subplots(figsize=figsize, dpi=24)
        ax.imshow(self.roi_ajustada, cmap='gray')
        ax.axis('off')
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)
        
        # Imprime a matriz ajustada da ROI do fígado
        print("Matriz ajustada da ROI do fígado:")
        print(self.roi_ajustada)
        
    def salvar_roi_figado_selecionado(self):
        try:
            numero_paciente = int(self.combo_paciente.get().split()[-1]) - 1  # Ajuste para o índice do paciente
            numero_imagem = int(self.combo_imagens.get().split()[-1]) - 1  # Ajuste para o índice da imagem
        except ValueError:
            messagebox.showerror("Erro", "Por favor, selecione um paciente e uma imagem válidos.")
            return

        # Chama a função para ajustar e salvar a ROI do fígado
        self.salvar_roi_figado(numero_paciente, numero_imagem)
        
    def salvar_roi_figado(self, numero_paciente, numero_imagem):

        # Define o caminho e o nome do arquivo
        nome_arquivo = f"ROI_{numero_paciente:02d}_{numero_imagem}.png"
        caminho_arquivo = os.path.join("pasta_rois", nome_arquivo)  # Substitua 'diretorio_destino' pelo seu diretório de destino
        # Salva a imagem
        Image.fromarray(self.roi_ajustada).save(caminho_arquivo)
        messagebox.showinfo("Salvo", f"Imagem salva como {nome_arquivo} em {caminho_arquivo}")            
   
    def remove_botoes_antigos(self):
        # Remove os botões antigos
        self.button_ajustar_roi.grid_forget()
        self.button_calcular_hi.grid_forget()
        self.button_salvar_roi.grid_forget()
            
        # Exibe os novos botões
        self.button_calcular_hu.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        self.button_calcular_glcm.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        self.button_exibir_histograma.grid(row=4, column=2, padx=10, pady=5, sticky="ew")
            
    def remove_botoes_novos(self):
        # Remove os botões antigos
        self.button_ajustar_roi.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.button_calcular_hi.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.button_salvar_roi.grid(row=3, column=2, padx=10, pady=5, sticky="ew")
            
        # Exibe os novos botões
        self.button_calcular_hu.grid_forget()
        self.button_exibir_histograma.grid_forget()
        self.button_calcular_glcm.grid_forget()

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