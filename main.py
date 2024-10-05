import os  # Para pegar o diretório atual
from PIL import Image, ImageTk
import ttkbootstrap as tb  # Importa ttkbootstrap no lugar do Tkinter
from ttkbootstrap.constants import *
from tkinter import filedialog

# Função para criar a janela principal
def criar_janela():
    # Usando o theme 'darkly' como exemplo. Você pode escolher qualquer tema.
    janela = tb.Window(themename="darkly")  
    janela.title("📷 PROCESSAMENTO DE IMAGENS 📷")
    janela.geometry("1000x600")
    janela.minsize(1000, 600)

    # Criando o frame principal que irá dividir a tela em três partes
    frame_principal = tb.Frame(janela)
    frame_principal.pack(fill=BOTH, expand=True)

    # Criando o menu lateral
    frame_menu_lateral = tb.Frame(frame_principal, bootstyle="secondary", width=200)
    frame_menu_lateral.pack(side=LEFT, fill=Y)

    # Criando o frame superior para os botões e colunas (a área principal)
    frame_superior = tb.Frame(frame_principal)
    frame_superior.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=5)

    # Criando o frame para exibir a imagem selecionada acima da tabela
    frame_imagem = tb.Frame(frame_superior)
    frame_imagem.pack(side=TOP, fill=BOTH, padx=10, pady=5)

    # Criando o label de imagem no frame superior
    label_imagem = tb.Label(frame_imagem)
    label_imagem.pack(fill=BOTH, expand=True)

    # Criando o frame inferior para os dados da tabela
    frame_tabela = tb.Frame(frame_superior)
    frame_tabela.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=5)

    # Criando a tabela de status (usando Treeview) na área principal
    colunas = ("Nome", "Estado", "Última Modificação", "Última Execução", "Tamanho")
    tree = tb.Treeview(frame_tabela, columns=colunas, show='headings', height=10)

    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    tree.pack(fill=BOTH, expand=True)

    # Inserindo dados fictícios na tabela
    data = [
        ("sample_file_20.txt", "Backup Up", "13.12.2021 14:03", "13.12.2021 14:03", "6 MB"),
        ("sample_file_21.txt", "Missed", "13.12.2021 14:03", "13.12.2021 14:03", "7 MB"),
        ("sample_file_22.txt", "Missed", "13.12.2021 14:03", "13.12.2021 14:03", "7 MB"),
    ]
    
    for item in data:
        tree.insert('', 'end', values=item)

    # Função para carregar uma imagem
    def carregar_imagem():
        # Pega o diretório atual onde o programa está rodando
        diretorio_atual = os.getcwd()
        
        caminho_imagem = filedialog.askopenfilename(
            initialdir=diretorio_atual,  # Define o diretório atual como inicial
            filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.bmp"), ("Todos os arquivos", "*.*")]
        )
        if caminho_imagem:
            img = Image.open(caminho_imagem)
            img = img.resize((400, 300))  # Redimensiona a imagem
            img_tk = ImageTk.PhotoImage(img)
            label_imagem.config(image=img_tk)
            label_imagem.image = img_tk  # Salva a referência para não ser coletada pelo garbage collector

    # Função para calcular o HI (Exemplo fictício)
    def calcular_hi():
        print("Cálculo do Índice Hepatorenal (HI)")
    
    # Adicionando botões no menu lateral para funcionalidades
    btn_carregar_imagem = tb.Button(frame_menu_lateral, text="Carregar Imagem", command=carregar_imagem, bootstyle="primary")
    btn_carregar_imagem.pack(fill=X, padx=10, pady=10)

    btn_recortar_roi = tb.Button(frame_menu_lateral, text="Recortar ROI", command=lambda: print("ROI Recortada"), bootstyle="warning")
    btn_recortar_roi.pack(fill=X, padx=10, pady=10)

    btn_calcular_hi = tb.Button(frame_menu_lateral, text="Calcular HI", command=calcular_hi, bootstyle="success")
    btn_calcular_hi.pack(fill=X, padx=10, pady=10)

    btn_salvar_resultados = tb.Button(frame_menu_lateral, text="Salvar Resultados", command=lambda: print("Resultados Salvos"), bootstyle="danger")
    btn_salvar_resultados.pack(fill=X, padx=10, pady=10)

    # Executando a janela
    janela.mainloop()

# Iniciar a aplicação
criar_janela()
