import os
from PIL import Image, ImageTk
import ttkbootstrap as tb
from skimage.measure import moments
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, StringVar, Menu
from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cv2
from skimage.feature import graycomatrix, graycoprops
from skimage import exposure

# Variável global para armazenar o arquivo .mat carregado e a imagem atual
data = None
img = None

# Função para limpar o histograma no frame_histograma
def limpar_histograma():
    for widget in frame_histograma.winfo_children():
        widget.destroy()

# Função para exibir histograma no frame_histograma
def exibir_histograma():
    global img
    if img is None:
        messagebox.showerror("Erro", "Nenhuma imagem carregada!")
        return

    # Converte a imagem para tons de cinza se estiver em outro modo
    gray_img = img.convert('L')

    # Calcula o histograma da imagem em tons de cinza
    hist = gray_img.histogram()

    # Limpa o frame_histograma antes de plotar um novo histograma
    limpar_histograma()

    # Cria e exibe o gráfico do histograma
    fig, ax = plt.subplots()
    ax.plot(hist, color='black')
    ax.set_title("Histograma da Imagem")
    ax.set_xlabel("Intensidade de pixels")
    ax.set_ylabel("Número de pixels")
    canvas = FigureCanvasTkAgg(fig, master=frame_histograma)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Função para carregar arquivo .mat e exibir opções de paciente e imagem
def carregar_arquivo_mat():
    global data
    diretorio_atual = os.getcwd()
    caminho_mat = filedialog.askopenfilename(
        initialdir=diretorio_atual,
        filetypes=[("Arquivos MAT", "*.mat"), ("Todos os arquivos", "*.*")]
    )
    if caminho_mat:
        try:
            data = loadmat(caminho_mat)['data'][0]  # Carrega a lista de pacientes
            pacientes = [f"Paciente {i}" for i in range(len(data))]
            combo_paciente['values'] = pacientes
            combo_imagem['values'] = [f"Imagem {i}" for i in range(10)]  # 10 imagens por paciente
            combo_paciente.current(0)
            combo_imagem.current(0)
            messagebox.showinfo("Sucesso", "Arquivo .mat carregado com sucesso!")
            ocultar_opcoes_imagem()  # Oculta as opções da imagem comum
            mostrar_opcoes_mat()  # Mostra as opções específicas para arquivo .mat
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar o arquivo .mat: {e}")

# Função para carregar e exibir a imagem selecionada do .mat
def carregar_imagem_selecionada():
    global img
    try:
        indice_paciente = int(selected_patient.get().split()[-1])
        indice_imagem = int(selected_image.get().split()[-1])
        img_data = data[indice_paciente]['images'][indice_imagem]

        # Convertendo a imagem do .mat para PIL
        img = Image.fromarray(img_data)
        img = img.resize((400, 300))
        img_tk = ImageTk.PhotoImage(img)

        # Limpa o histograma e atualiza a exibição no frame de imagem
        limpar_histograma()
        label_imagem.config(image=img_tk)
        label_imagem.image = img_tk
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar a imagem: {e}")

# Função para calcular a GLCM e extrair os descritores de textura
def calcular_glcm(img_array):
    # Converte a imagem para tons de cinza (se necessário)
    if len(img_array.shape) == 3:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

    # Ajuste o contraste da imagem para melhorar a visualização da GLCM
    img_array = exposure.rescale_intensity(img_array, in_range='image', out_range=(0, 255))

    # Converte a imagem para uint8, pois o graycomatrix não suporta imagens float
    img_array = img_array.astype(np.uint8)

    # Calcula a matriz de co-ocorrência para distâncias e ângulos específicos
    glcm = graycomatrix(img_array, distances=[1, 2, 3], angles=[0, np.pi / 4, np.pi / 2, 3 * np.pi / 4], levels=256,
                        symmetric=True, normed=True)
    img_array = cv2.equalizeHist(img_array)

    # Extrai os descritores de textura
    contraste = graycoprops(glcm, 'contrast')[0, 0]
    homogeneidade = graycoprops(glcm, 'homogeneity')[0, 0]
    energia = graycoprops(glcm, 'energy')[0, 0]
    correlacao = graycoprops(glcm, 'correlation')[0, 0]

    # Exibe os valores calculados em uma janela de diálogo
    messagebox.showinfo("Descritores de Textura",
                        f"Contraste: {contraste}\n"
                        f"Homogeneidade: {homogeneidade}\n"
                        f"Energia: {energia}\n"
                        f"Correlação: {correlacao}")

    # Exibir a GLCM como uma imagem (matriz)
    exibir_glcm(glcm)

def exibir_glcm(glcm):
    # Limpar o frame do histograma antes de exibir a GLCM
    limpar_histograma()

    # Exibir a GLCM usando matplotlib
    fig, ax = plt.subplots()
    ax.imshow(glcm[:, :, 0, 0], cmap='gray')  # Mostra a primeira matriz da GLCM
    ax.set_title("Matriz de Co-ocorrência (GLCM)")
    ax.set_xlabel("Nível de Cinza (i)")
    ax.set_ylabel("Nível de Cinza (j)")

    # Adiciona o gráfico ao frame de histograma usando FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=frame_histograma)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Função para carregar e exibir a imagem
def carregar_imagem():
    global img
    diretorio_atual = os.getcwd()
    caminho_imagem = filedialog.askopenfilename(
        initialdir=diretorio_atual,
        filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.bmp"), ("Todos os arquivos", "*.*")]
    )
    if caminho_imagem:
        img = Image.open(caminho_imagem)
        img = img.resize((400, 300))
        img_tk = ImageTk.PhotoImage(img)

        # Limpa o histograma e atualiza a exibição no frame de imagem
        limpar_histograma()
        label_imagem.config(image=img_tk)
        label_imagem.image = img_tk

        ocultar_opcoes_mat()  # Oculta as opções do .mat
        mostrar_opcoes_imagem()  # Mostra as opções específicas para imagem comum

# Função para selecionar ROI (Região de Interesse)
def selecionar_roi(imagem):
    roi = cv2.selectROI("Selecione a ROI", imagem, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()
    return roi

# Função para recortar a ROI e atualizar a imagem
def recortar_roi():
    global img
    if img is None:
        messagebox.showerror("Erro", "Nenhuma imagem carregada!")
        return

    # Converter a imagem PIL para um array do OpenCV (BGR)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # Chamar a função para selecionar a ROI
    roi_coords = selecionar_roi(img_cv)
    x, y, w, h = roi_coords

    # Verificar se a ROI selecionada é válida
    if w == 0 or h == 0:
        messagebox.showerror("Erro", "Nenhuma ROI selecionada ou seleção inválida!")
        return

    # Recortar a imagem com base na ROI selecionada
    roi_cropped = img_cv[int(y):int(y + h), int(x):int(x + w)]

    # Atualizar a exibição da imagem na interface
    img_cropped = Image.fromarray(cv2.cvtColor(roi_cropped, cv2.COLOR_BGR2RGB))
    img_resized = img_cropped.resize((400, 300))
    img = img_resized  # Atualizar a imagem global
    img_tk = ImageTk.PhotoImage(img)
    label_imagem.config(image=img_tk)
    label_imagem.image = img_tk

    # Limpar o histograma já que a imagem mudou
    limpar_histograma()

    # Calcular a GLCM e os descritores de textura para a ROI
    calcular_glcm(roi_cropped)

# Função para mostrar as opções no menu lateral para arquivos .mat
def mostrar_opcoes_mat():
    # Exibe as opções de paciente e imagem, além das opções padrão
    combo_paciente.pack(fill=X, padx=10, pady=5)
    combo_imagem.pack(fill=X, padx=10, pady=5)
    btn_carregar_imagem_selecionada.pack(fill=X, padx=10, pady=10)
    btn_calcular_histograma.pack(fill=X, padx=10, pady=10)
    btn_recortar_roi.pack(fill=X, padx=10, pady=10)
    btn_binarizar_imagem.pack(fill=X, padx=10, pady=10)


# Função para calcular o centróide
def centroid(moment):
    if moment['m00'] != 0:
        x_centroid = round(moment['m10'] / moment['m00'])
        y_centroid = round(moment['m01'] / moment['m00'])
        print(f"Centróide: ({x_centroid}, {y_centroid})")
    else:
        x_centroid, y_centroid = 0, 0
        print("Centróide: (0, 0)")
    return x_centroid, y_centroid

# Função para binarizar a imagem
def binaryImage():
    global img
    if img is None:
        messagebox.showerror("Erro", "Nenhuma imagem carregada!")
        return

    # Verificar o tipo de imagem carregada e converter para grayscale
    if img.mode != 'L':  # Se a imagem não estiver em tons de cinza, converte
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    else:
        img_cv = np.array(img)  # Se já estiver em grayscale, usa diretamente

    # Aplicar adaptive threshold para binarização adaptativa
    adaptive_bw_img = cv2.adaptiveThreshold(img_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)
    momentos = cv2.moments(adaptive_bw_img)
    momentos_hu = cv2.HuMoments(momentos)
    print("Momentos Invariantes de Hu:")
    for i, hu in enumerate(momentos_hu):
        print(f"Hu[{i + 1}] = {hu[0]}")
    # Converter de volta para PIL para exibir na interface
    bw_img_pil = Image.fromarray(adaptive_bw_img)
    img_resized = bw_img_pil.resize((400, 300))
    img_tk = ImageTk.PhotoImage(img_resized)

    # Atualizar a imagem binária na interface
    label_imagem.config(image=img_tk)
    label_imagem.image = img_tk
    momentos_hu_str = "\n".join([f"Hu[{i + 1}]: {momento[0]}" for i, momento in enumerate(momentos_hu)])
    messagebox.showinfo("Momentos Invariantes de Hu", momentos_hu_str)
    # Limpar o histograma, já que a imagem foi alterada
    return momentos_hu
    limpar_histograma()


# Função para mostrar as opções no menu lateral para imagens comuns
def mostrar_opcoes_imagem():
    # Exibe as opções padrão e o novo botão "Selecionar Nova Imagem"
    btn_selecionar_nova_imagem.pack(fill=X, padx=10, pady=10)
    btn_calcular_histograma.pack(fill=X, padx=10, pady=10)
    btn_recortar_roi.pack(fill=X, padx=10, pady=10)
    btn_binarizar_imagem.pack(fill=X, padx=10, pady=10)
    btn_momentos_hu.pack(fill=X, padx=10, pady=10)

# Função para ocultar as opções do arquivo .mat
def ocultar_opcoes_mat():
    combo_paciente.pack_forget()
    combo_imagem.pack_forget()
    btn_carregar_imagem_selecionada.pack_forget()


# Função para ocultar as opções da imagem comum
def ocultar_opcoes_imagem():
    btn_selecionar_nova_imagem.pack_forget()
    btn_calcular_histograma.pack_forget()
    btn_recortar_roi.pack_forget()

# Função para criar a janela principal
def criar_janela():
    global frame_imagem, frame_histograma, label_imagem
    global combo_paciente, combo_imagem
    global btn_carregar_imagem_selecionada, btn_calcular_histograma, btn_recortar_roi, btn_selecionar_nova_imagem,btn_binarizar_imagem,btn_momentos_hu
    global selected_patient, selected_image

    # Configurações iniciais
    janela = tb.Window(themename="cerculean")
    janela.title("📷 PROCESSAMENTO DE IMAGENS 📷")
    janela.geometry("1000x600")
    janela.minsize(1000, 600)

    # Inicialização de StringVars após a criação da janela
    selected_patient = StringVar(janela)
    selected_image = StringVar(janela)

    # Menu superior
    menu = Menu(janela)
    janela.config(menu=menu)

    arquivo_menu = Menu(menu, tearoff=0)
    menu.add_cascade(label="Arquivo", menu=arquivo_menu)
    arquivo_menu.add_command(label="Carregar Imagem", command=carregar_imagem)
    arquivo_menu.add_command(label="Carregar Arquivo .mat", command=carregar_arquivo_mat)

    # Frame principal
    frame_principal = tb.Frame(janela)
    frame_principal.pack(fill=BOTH, expand=True)

    # Menu lateral
    frame_menu_lateral = tb.Frame(frame_principal, bootstyle="secondary", width=200)
    frame_menu_lateral.pack(side=LEFT, fill=Y)

    # Frame superior para botões e colunas
    frame_superior = tb.Frame(frame_principal)
    frame_superior.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=5)

    # Frame para exibir a imagem
    frame_imagem = tb.Frame(frame_superior, width=400, height=300)
    frame_imagem.pack(side=TOP, fill=X, padx=10, pady=5)

    # Frame para exibir o histograma
    frame_histograma = tb.Frame(frame_superior, width=400, height=300)
    frame_histograma.pack(side=TOP, fill=X, padx=10, pady=5)

    # Label de imagem
    label_imagem = tb.Label(frame_imagem)
    label_imagem.pack(fill=BOTH, expand=True)

    # Combobox para seleção de paciente e imagem
    combo_paciente = tb.Combobox(frame_menu_lateral, textvariable=selected_patient)
    combo_imagem = tb.Combobox(frame_menu_lateral, textvariable=selected_image)

    # Botão para carregar imagem selecionada
    btn_carregar_imagem_selecionada = tb.Button(frame_menu_lateral, text="Carregar Imagem Selecionada",
                                                command=carregar_imagem_selecionada, bootstyle="primary")

    # Botão para calcular histograma
    btn_calcular_histograma = tb.Button(frame_menu_lateral, text="Calcular Histograma", command=exibir_histograma,
                                        bootstyle="info")

    # Botão para recortar ROI
    btn_recortar_roi = tb.Button(frame_menu_lateral, text="Recortar ROI", command=recortar_roi, bootstyle="warning")

    # Novo botão para selecionar uma nova imagem
    btn_selecionar_nova_imagem = tb.Button(frame_menu_lateral, text="Selecionar Nova Imagem", command=carregar_imagem,
                                           bootstyle="primary")

    # Chamar a função de binarizar a imagem, você pode fazer isso no botão ou em outro ponto após carregar a imagem
    btn_binarizar_imagem = tb.Button(frame_menu_lateral, text="Binarizar Imagem", command=binaryImage,
                                     bootstyle="primary")

    # Executando a janela
    janela.mainloop()

# Iniciar a aplicação
criar_janela()
