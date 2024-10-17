import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from skimage.metrics import structural_similarity as ssim
import cv2
import numpy as np

# Função para abrir um diálogo de seleção de arquivos
def upload_image(image_num):
    file_path = filedialog.askopenfilename()
    if file_path:  # Verifica se o caminho não está vazio
        file_path = os.path.normpath(file_path)  # Converte o caminho para um formato adequado
        if image_num == 1:
            global img1_path
            img1_path = file_path
            label_img1.config(text=f"Imagem 1: {os.path.basename(file_path)}")
        elif image_num == 2:
            global img2_path
            img2_path = file_path
            label_img2.config(text=f"Imagem 2: {os.path.basename(file_path)}")
    return file_path

# Função para comparar as imagens
def compare_images():
    if not img1_path or not img2_path:
        messagebox.showerror("Erro", "Por favor, selecione ambas as imagens.")
        return

    print(f"Carregando Imagem 1: {img1_path}")
    print(f"Carregando Imagem 2: {img2_path}")

    # Tente salvar em um diretório mais simples
    output_dir = "C:/imagens"
    
    # Cria a pasta se não existir
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Pasta '{output_dir}' criada com sucesso.")
        except Exception as e:
            print(f"Erro ao criar a pasta '{output_dir}': {e}")
            messagebox.showerror("Erro", f"Erro ao criar a pasta '{output_dir}'.")
            return

    # Carrega as imagens
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    # Verificação para garantir que as imagens foram carregadas
    if img1 is None:
        print(f"Falha ao carregar a imagem 1: {img1_path}")
        messagebox.showerror("Erro", f"Erro ao carregar a imagem 1: {img1_path}")
        return
    if img2 is None:
        print(f"Falha ao carregar a imagem 2: {img2_path}")
        messagebox.showerror("Erro", f"Erro ao carregar a imagem 2: {img2_path}")
        return

    # Converte para cinza
    gray_img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray_img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Calcula SSIM
    score, diff = ssim(gray_img1, gray_img2, full=True)
    diff = (diff * 255).astype("uint8")

    # Encontra as diferenças
    _, thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    output_image = img1.copy()
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(output_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Salva a imagem resultante em formato JPG para testar
    highlighted_diff_path = os.path.join(output_dir, "highlighted.jpg")
    try:
        if cv2.imwrite(highlighted_diff_path, output_image):
            print(f"Imagem com diferenças destacadas salva em: {highlighted_diff_path}")
        else:
            print(f"Falha ao salvar a imagem: {highlighted_diff_path}")
            messagebox.showerror("Erro", f"Falha ao salvar a imagem: {highlighted_diff_path}")
            return
    except Exception as e:
        print(f"Erro ao salvar a imagem destacada: {e}")
        messagebox.showerror("Erro", f"Erro ao salvar a imagem destacada: {e}")
        return

    # Exibe a imagem com diferenças na interface
    show_result(highlighted_diff_path)

def show_result(image_path):
    # Verifica se o arquivo foi realmente criado
    if not os.path.exists(image_path):
        print(f"Imagem resultante não encontrada: {image_path}")
        messagebox.showerror("Erro", f"Imagem resultante não encontrada: {image_path}")
        return

    # Carrega a imagem resultante no Tkinter
    try:
        result_img = Image.open(image_path)
        result_img = result_img.resize((400, 300))  # Redimensiona a imagem para caber na interface
        result_img_tk = ImageTk.PhotoImage(result_img)
        result_label.config(image=result_img_tk)
        result_label.image = result_img_tk
        result_label.config(text="")
    except Exception as e:
        print(f"Erro ao carregar a imagem resultante: {e}")
        messagebox.showerror("Erro", f"Erro ao carregar a imagem resultante: {e}")

# Configura a interface com Tkinter
root = tk.Tk()
root.title("Comparador de Imagens")

img1_path = None
img2_path = None

# Layout da interface
label_img1 = tk.Label(root, text="Imagem 1: Nenhuma imagem selecionada", padx=10, pady=10)
label_img1.pack()

btn_img1 = tk.Button(root, text="Carregar Imagem 1", command=lambda: upload_image(1))
btn_img1.pack()

label_img2 = tk.Label(root, text="Imagem 2: Nenhuma imagem selecionada", padx=10, pady=10)
label_img2.pack()

btn_img2 = tk.Button(root, text="Carregar Imagem 2", command=lambda: upload_image(2))
btn_img2.pack()

btn_compare = tk.Button(root, text="Comparar Imagens", command=compare_images, pady=10, padx=20)
btn_compare.pack()

# Local onde será exibida a imagem resultante
result_label = tk.Label(root, text="Resultado será exibido aqui.", padx=10, pady=10)
result_label.pack()

root.mainloop()
