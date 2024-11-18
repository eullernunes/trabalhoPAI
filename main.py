import os
import cv2
import csv
import numpy as np
import tkinter as tk
import ttkbootstrap as ttk
import locale
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import shutil
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score
from skimage.feature import graycomatrix, graycoprops
from skimage.measure import shannon_entropy
from skimage.io import imread
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox
from scipy.io import loadmat
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import RectangleSelector

locale.setlocale(locale.LC_NUMERIC,'C')

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Processamento e Análise de Imagens")
        self.geometry("1310x880")
        self.imagem_atual = None
        self.roi_binarizada = None
        self.roi_ajustada = None
        self.teste_atualiza = 0
        self.roi_size = 28  
        self.coordenadas_rois = []
        self.rois = []  

        
        self.frame_superior = ttk.Frame(self, padding=10)
        self.frame_superior.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="nw")
        
        self.button_carregar_img = ttk.Button(self.frame_superior, text="Carregar Imagem", command=self.carregar_imagem, bootstyle="secondary", width=20)
        self.button_carregar_img.grid(row=0, column=0, padx=10, pady=5)
        
        self.button_exibir_histograma = ttk.Button(self.frame_superior, text="Exibir Histograma", command=lambda: self.exibir_histograma(self.imagem_atual), bootstyle="secondary", width=20)
        self.button_exibir_histograma.grid(row=0, column=2, padx=10, pady=5)
        
        self.button_recortar_roi = ttk.Button(self.frame_superior, text="Recortar ROI", command=self.recortar_roi, bootstyle="secondary", width=20)
        self.button_recortar_roi.grid(row=0, column=3, padx=10, pady=5)
        
        self.separator = ttk.Separator(self, orient='horizontal')
        self.separator.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=10)
        
        self.frame_esquerdo = ttk.Labelframe(self, text="Imagens", bootstyle="light", width=500, height=500)
        self.frame_esquerdo.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        self.frame_esquerdo.grid_propagate(False)
             
        self.menu_roi_frame = ttk.Labelframe(self, text="Menu ROI", bootstyle="light", width=500, height=500)
        self.menu_roi_frame.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")
        self.menu_roi_frame.grid_propagate(False)

        self.roi_frame = ttk.Frame(self.menu_roi_frame)
        self.roi_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew", columnspan=3)

        self.menu_roi_frame.columnconfigure(0, weight=1)
        self.menu_roi_frame.columnconfigure(1, weight=1)
        self.menu_roi_frame.columnconfigure(2, weight=1)

        self.menu_roi_frame.rowconfigure(0, weight=1)  
        self.menu_roi_frame.rowconfigure(1, weight=0)  

        self.figsize_scale = tk.Scale(self.menu_roi_frame, from_=1, to=6, resolution=0.8, orient=tk.HORIZONTAL)
        self.figsize_scale.set(1)
        self.figsize_scale.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="ew", columnspan=3)

        self.button_aplicar_tamanho = ttk.Button(self.menu_roi_frame, text="Aplicar Zoom", command=self.atualizar_tamanho, bootstyle="secondary")
        self.button_aplicar_tamanho.grid(row=2, column=1, padx=10, pady=5, sticky="ew", columnspan=1)

        self.button_calcular_hi = ttk.Button(self.menu_roi_frame, text="Calcular HI", command=lambda: self.calcular_indice_hepatorenal(1), bootstyle="secondary")
        self.button_calcular_hi.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.button_ajustar_roi = ttk.Button(self.menu_roi_frame, text="Ajustar ROI", command=lambda:self.ajusta_roi_figado(0), bootstyle="secondary")
        self.button_ajustar_roi.grid(row=2, column=2, padx=10, pady=5, sticky="ew")

        self.button_salvar_roi = ttk.Button(self.menu_roi_frame, text="Salvar ROI", command=self.salvar_roi_figado_selecionado, bootstyle="secondary")
        self.button_salvar_roi.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.button_calcular_hu = ttk.Button(self.menu_roi_frame, text="Calcular Hu", command=self.momento_hu, bootstyle="secondary")
        self.button_calcular_hu.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        
        self.button_exibir_histograma = ttk.Button(self.menu_roi_frame, text="Exibir Histograma", command=lambda:self.exibir_histograma(self.roi_ajustada), bootstyle="secondary")
        self.button_exibir_histograma.grid(row=3, column=2, padx=10, pady=5, sticky="ew")
        
        self.label_frame_direita = ttk.Labelframe(self, text="Pacientes", bootstyle="light", padding=20)
        self.label_frame_direita.grid(row=3, column=2, padx=10, pady=10, sticky="ne")        
        
        self.button_carregar_mat = ttk.Button(self.label_frame_direita, text="Carregar .Mat", command=self.carregar_dataset, bootstyle="light")
        self.button_carregar_mat.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.combo_frame = ttk.Labelframe(self.label_frame_direita, text="Pacientes", bootstyle="light", padding=5)
        self.combo_frame.grid(row=0, column=0, padx=10, pady=(25,10), sticky="nw")
        
        self.combo_paciente = ttk.Combobox(self.combo_frame, bootstyle="secondary", state="readonly")
        self.combo_paciente.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.combo_paciente.bind("<<ComboboxSelected>>", self.exibir_imagens_pacientes)
        
        self.combo_imagens = ttk.Combobox(self.combo_frame, bootstyle="secondary", state="readonly")
        self.combo_imagens.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.combo_imagens.bind("<<ComboboxSelected>>", self.exibir_imagem_paciente)
        
        self.imagens_pacientes = {}

        self.columnconfigure(0, weight=1)  
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
            
    def carregar_dataset(self):
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo .mat",
            filetypes=[("Mat files", ".mat")]
        )
        
        if caminho_arquivo:
            mat = loadmat(caminho_arquivo)
            data = mat.get("data")
            
            if data is not None:
                for i in range(data.shape[1]):
                    paciente_id = f"Paciente {i + 1}"
                    imagens = []
                    
                    for j in range(10):  
                        img_array = data['images'][0][i][j]
                        imagens.append(img_array)
                    
                    self.imagens_pacientes[paciente_id] = imagens
                
                self.combo_paciente['values'] = list(self.imagens_pacientes.keys())
                self.combo_paciente.current(0)
                self.exibir_imagens_pacientes()
            
            else:
                print("Coluna 'data' não encontrada!")
                 
    def exibir_imagens_pacientes(self, event=None):
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
        for widget in self.frame_esquerdo.winfo_children():
            widget.destroy()
        
        fig, ax = plt.subplots(figsize=(6, 5), dpi=100, facecolor='none')
        ax.imshow(self.imagem_atual, cmap="gray")
        ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self.frame_esquerdo)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self.frame_esquerdo)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        plt.close(fig)

    def binarizar_imagem(self):
            if self.roi_ajustada is not None:
                self.roi_binarizada = cv2.adaptiveThreshold(self.roi_ajustada, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
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
        
        for widget in self.roi_frame.winfo_children():
            widget.destroy()
            
        self.rois = []
        self.teste_atualiza = 0

        def onmove(event):
            [p.remove() for p in reversed(ax.patches)]  
            if event.inaxes:
                x, y = int(event.xdata), int(event.ydata)

                if x + self.roi_size > self.imagem_atual.shape[1]:
                    x = self.imagem_atual.shape[1] - self.roi_size
                if y + self.roi_size > self.imagem_atual.shape[0]:
                    y = self.imagem_atual.shape[0] - self.roi_size

                rect = plt.Rectangle((x, y), self.roi_size, self.roi_size, linewidth=1, edgecolor='green', facecolor='none')
                ax.add_patch(rect)
                plt.draw()

        def onclick(event):
            if event.button == 1 and event.inaxes:
                x_center = int(event.xdata)
                y_center = int(event.ydata)

                x_start = max(x_center - self.roi_size // 2, 0)
                y_start = max(y_center - self.roi_size // 2, 0)
                x_end = min(x_start + self.roi_size, self.imagem_atual.shape[1])
                y_end = min(y_start + self.roi_size, self.imagem_atual.shape[0])

                roi = self.imagem_atual[y_start:y_end, x_start:x_end]

                if len(self.rois) >= 2:
                    self.rois.clear()
                    self.coordenadas_rois.clear()

                self.rois.append(roi)
                self.coordenadas_rois.append((x_start))
                self.coordenadas_rois.append((y_start))
                

                self.exibir_rois()
                plt.draw()

        fig, ax = plt.subplots()
        ax.imshow(self.imagem_atual, cmap='gray')

        fig.canvas.mpl_connect('motion_notify_event', onmove)
        fig.canvas.mpl_connect('button_press_event', onclick)

        plt.show()

    def atualizar_tamanho(self):
        novo_tamanho = float(self.figsize_scale.get())

        self.exibir_rois(figsize=(novo_tamanho, novo_tamanho))

        if self.teste_atualiza == 1:
            self.ajusta_roi_figado(0, figsize=(novo_tamanho, novo_tamanho))

    def exibir_rois(self, figsize=(1, 1)):

        for widget in self.roi_frame.winfo_children():
            widget.destroy()

        self.roi_frame.grid_columnconfigure(0, weight=1)
        self.roi_frame.grid_columnconfigure(1, weight=1)


        for i, roi in enumerate(self.rois):
            frame = ttk.Labelframe(self.roi_frame, text=f"ROI {i + 1}", bootstyle="light")
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")


            fig, ax = plt.subplots(figsize=figsize, dpi=24, facecolor = 'none')
            ax.imshow(roi, cmap='gray')
            ax.axis('off')
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

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


        media_figado = np.mean(roi_figado)
        media_rim = np.mean(roi_rim)

        if media_rim != 0:
            indice_hepatorenal = media_figado / media_rim
            
            if selecao == 1:
                messagebox.showinfo("Índice Hepatorenal", f"HI = {indice_hepatorenal:.2f}")
                
            return indice_hepatorenal
        else:
            messagebox.showerror("Erro", "A média da ROI do rim é zero, não é possível calcular o índice.")
            return None

    def calcular_glcm(self, distancias=[1, 2, 4, 8], angulos=[0, np.pi / 2, np.pi, 3 * np.pi / 2]):
        if self.roi_ajustada.dtype != np.uint8:
            self.roi_ajustada = (self.roi_ajustada * 255).astype(np.uint8)

        glcm_results = {}
        for distancia in distancias:
            for angulo in angulos:
                glcm = graycomatrix(self.roi_ajustada, [distancia], [angulo], symmetric=True, normed=True)

                glcm_props = {
                    'homogeneity': graycoprops(glcm, 'homogeneity')[0, 0],
                    'energy': graycoprops(glcm, 'energy')[0, 0],
                }
         
                angulo_graus = angulo * (180 / np.pi)
                glcm_normalized = glcm[:, :, 0] 
                glcm_normalized = glcm_normalized / np.sum(glcm_normalized) 
                entropy_value = -np.sum(glcm_normalized * np.log(glcm_normalized + 1e-10))  
                angulo_graus = angulo * (180 / np.pi)

                # Imprime as características com distância, ângulo, homogeneidade e entropia
                #print(f'Distância: {distancia}, Ângulo: {angulo_graus:.2f}° - '
                #      f'Homogeneidade: {glcm_props["homogeneity"]:.4f}, '
                #      f'Entropia: {entropy_value:.4f}')

                key = f'Distância: {distancia}, Ângulo: {angulo_graus:.2f}°'
                glcm_results[key] = (glcm, glcm_props)

        return glcm_results
   
    def ajusta_roi_figado(self, selecao, figsize=(1,1)):
        indice_hepatorenal = self.calcular_indice_hepatorenal(selecao)
        self.teste_atualiza = 1

        if indice_hepatorenal is None:
            messagebox.showerror("Erro", "Não foi possível calcular o HI")
            return
        
        roi_figado = self.rois[0]

        self.roi_ajustada = roi_figado * indice_hepatorenal
        self.roi_ajustada = np.clip(self.roi_ajustada, 0, 255)
        self.roi_ajustada = np.round(self.roi_ajustada).astype(np.uint8)
        
        
        frame = ttk.Labelframe(self.roi_frame, text=f"Roi Ajustada", bootstyle="light")
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)
        
        fig, ax = plt.subplots(figsize=figsize, dpi=24, facecolor='none')
        ax.imshow(self.roi_ajustada, cmap='gray')
        ax.axis('off')
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    def executar_calculos_e_salvar(self):
        momentos_hu = self.momento_hu()
        indice_hepatorenal = self.calcular_indice_hepatorenal(1)
        
        glcm_results = self.calcular_glcm()

        numero_paciente = int(self.combo_paciente.get().split()[-1]) - 1 
        numero_imagem = int(self.combo_imagens.get().split()[-1]) - 1 
        nome_imagem = f"Paciente_{numero_paciente+1}Imagem{numero_imagem+1}"
        coordenadas_figado_x = self.coordenadas_rois[0]
        coordenadas_figado_y = self.coordenadas_rois[1]
        coordenadas_rim_x = self.coordenadas_rois[2]
        coordenadas_rim_y = self.coordenadas_rois[3]
        
        # Extraindo apenas os valores numéricos
        momentos_hu_str = [momento[0] for momento in momentos_hu]  # Agora momentos_hu_str será uma lista de valores

        glcm_data = []
        for key, (glcm, props) in glcm_results.items():
            distancia, angulo = key.split(", ")
            glcm_data.extend([f"{props['homogeneity']:.6f}", f"{props['energy']:.6f}"])

        dados_csv = [
            nome_imagem,  
            indice_hepatorenal,  
            *momentos_hu_str,  # Agora isso incluirá os números corretos
            *glcm_data, 
            coordenadas_figado_x,
            coordenadas_figado_y,
            coordenadas_rim_x,
            coordenadas_rim_y
        ]

        nome_arquivo_csv = "resultados_processamento_imagens.csv"
        salvar_novo_csv = not os.path.exists(nome_arquivo_csv) 

        with open(nome_arquivo_csv, mode='a', newline='') as file:
            writer = csv.writer(file)

            if salvar_novo_csv:
                writer.writerow([
                    "Nome da Imagem", "Índice Hepatorenal",
                    "Hu1", "Hu2", "Hu3", "Hu4", "Hu5", "Hu6", "Hu7",
                    "GLCM_Homogeneidade_1", "GLCM_Entropia_1", "GLCM_Homogeneidade_2", "GLCM_Entropia_2",
                    "GLCM_Homogeneidade_3", "GLCM_Entropia_3", "GLCM_Homogeneidade_4", "GLCM_Entropia_4",
                    "GLCM_Homogeneidade_5", "GLCM_Entropia_5", "GLCM_Homogeneidade_6", "GLCM_Entropia_6",
                    "GLCM_Homogeneidade_7", "GLCM_Entropia_7", "GLCM_Homogeneidade_8", "GLCM_Entropia_8",
                    "Coordenadas_Figado_X", "Coordenadas_Figado_Y", "Coordenadas_Rim_X", "Coordenadas_Rim_Y"
                ])

            writer.writerow(dados_csv)

        messagebox.showinfo("Sucesso", f"Dados salvos no arquivo {nome_arquivo_csv}")
  
    def salvar_roi_figado_selecionado(self):
        try:
            numero_paciente = int(self.combo_paciente.get().split()[-1]) - 1  
            numero_imagem = int(self.combo_imagens.get().split()[-1]) - 1  
        except ValueError:
            messagebox.showerror("Erro", "Por favor, selecione um paciente e uma imagem válidos.")
            return

        self.salvar_roi_figado(numero_paciente, numero_imagem)
        
    def salvar_roi_figado(self, numero_paciente, numero_imagem):


        nome_arquivo = f"ROI_{numero_paciente:02d}_{numero_imagem}.png"
        caminho_arquivo = os.path.join("pasta_rois", nome_arquivo)  

        Image.fromarray(self.roi_ajustada).save(caminho_arquivo)
        messagebox.showinfo("Salvo", f"Imagem salva como {nome_arquivo} em {caminho_arquivo}")            
        self.executar_calculos_e_salvar()

    def carregar_imagens(self, pasta_base):
        X = []
        y = []
        grupos = []
        pacientes = sorted(os.listdir(pasta_base))
        for paciente in pacientes:
            pasta_paciente = os.path.join(pasta_base, paciente)
            if os.path.isdir(pasta_paciente):
                imagens = os.listdir(pasta_paciente)
                for imagem_nome in imagens:
                    if imagem_nome.endswith('.png'):
                        caminho_imagem = os.path.join(pasta_paciente, imagem_nome)
                        imagem = imread(caminho_imagem, as_gray=True)  
                        imagem = imagem.flatten() 
                        X.append(imagem)
                        
                        paciente_id = int(paciente.split('_')[1])
                        y.append(paciente_id)
                        grupos.append(paciente_id)
        return np.array(X), np.array(y), np.array(grupos)

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
        self.destroy()  
        plt.close('all')  
        self.quit()  
        os._exit(0) 
    
if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close) 
    pasta_base = './pacientes_organizados'
    X, y, grupos = app.carregar_imagens(pasta_base)
    print("X", X)
    print("y", y)
    print("grupos", grupos)
    
    from sklearn.model_selection import LeaveOneGroupOut
    logo = LeaveOneGroupOut()

    resultados = []
    for train_index, test_index in logo.split(X, y, grupos):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
    
        # Treinar o SVM
        svm = SVC(kernel='linear', C=1.0)
        svm.fit(X_train, y_train)

        # Testar o SVM
        y_pred = svm.predict(X_test)
    
        # Avaliar o desempenho
        acuracia = accuracy_score(y_test, y_pred)
        resultados.append(acuracia)

    acuracia_media = np.mean(resultados)
    print(f"Acurácia média: {acuracia_media * 100:.2f}%")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    app.mainloop()