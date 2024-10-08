import os
from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, StringVar, Menu
from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
    #limpar_histograma()
    
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

# Função para carregar imagem comum
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

# Função para mostrar as opções no menu lateral para arquivos .mat
def mostrar_opcoes_mat():
    # Exibe as opções de paciente e imagem, além das opções padrão
    combo_paciente.pack(fill=X, padx=10, pady=5)
    combo_imagem.pack(fill=X, padx=10, pady=5)
    btn_carregar_imagem_selecionada.pack(fill=X, padx=10, pady=10)
    btn_calcular_histograma.pack(fill=X, padx=10, pady=10)
    btn_recortar_roi.pack(fill=X, padx=10, pady=10)

# Função para mostrar as opções no menu lateral para imagens comuns
def mostrar_opcoes_imagem():
    # Exibe as opções padrão e o novo botão "Selecionar Nova Imagem"
    btn_selecionar_nova_imagem.pack(fill=X, padx=10, pady=10)
    btn_calcular_histograma.pack(fill=X, padx=10, pady=10)
    btn_recortar_roi.pack(fill=X, padx=10, pady=10)

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
    global btn_carregar_imagem_selecionada, btn_calcular_histograma, btn_recortar_roi, btn_selecionar_nova_imagem
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
    btn_carregar_imagem_selecionada = tb.Button(frame_menu_lateral, text="Carregar Imagem Selecionada", command=carregar_imagem_selecionada, bootstyle="primary")
    
    # Botão para calcular histograma
    btn_calcular_histograma = tb.Button(frame_menu_lateral, text="Calcular Histograma", command=exibir_histograma, bootstyle="info")
    
    # Botão para recortar ROI
    btn_recortar_roi = tb.Button(frame_menu_lateral, text="Recortar ROI", command=lambda: print("Recorte de ROI"), bootstyle="warning")
    
    # Novo botão para selecionar uma nova imagem
    btn_selecionar_nova_imagem = tb.Button(frame_menu_lateral, text="Selecionar Nova Imagem", command=carregar_imagem, bootstyle="primary")

    # Executando a janela
    janela.mainloop()

# Iniciar a aplicação
criar_janela()
