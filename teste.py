import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import ttkbootstrap as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import RectangleSelector

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.title("Recortar e Salvar ROI")
        self.geometry("600x400")
        self.imagem_atual = np.random.randint(0, 255, (100, 100), dtype=np.uint8)  # Imagem de teste
        self.roi_size = 28
        self.roi = None

        # Botão para recortar a ROI
        self.button_roi = ttk.Button(self, text="Recortar ROI", command=self.recortar_roi)
        self.button_roi.pack(pady=10)
        
        # Botão para salvar a ROI
        self.button_save = ttk.Button(self, text="Salvar ROI", command=self.salvar_roi, state="disabled")
        self.button_save.pack(pady=10)

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
            self.button_save.config(state="normal")  # Habilita o botão de salvar

            # Mostra a ROI no Tkinter sem a barra de ferramentas
            fig, ax = plt.subplots(figsize=(1, 1), dpi=28)
            ax.imshow(self.roi, cmap='gray', interpolation='nearest')
            ax.axis('off')  # Remove os eixos
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

            # Integrar com Tkinter sem a barra de ferramentas
            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()
            canvas.get_tk_widget().pack()

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
            # Define o caminho completo para salvar a imagem
            output_path = "roi_image.png"
            
            fig, ax = plt.subplots(figsize=(1, 1), dpi=28)
            ax.imshow(self.roi, cmap='gray', interpolation='nearest')
            ax.axis('off')
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
            fig.savefig(output_path, dpi=28, bbox_inches='tight', pad_inches=0)
            plt.close(fig)
            print(f"Imagem da ROI salva com sucesso como '{output_path}'")

if __name__ == "__main__":
    app = App()
    app.mainloop()
