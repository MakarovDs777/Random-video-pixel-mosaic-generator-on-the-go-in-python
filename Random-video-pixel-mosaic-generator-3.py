import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk
import random
import os

# Параметры
image_data = []  # Хранение данных изображений
canvas = None  # Canvas для отображения
current_flat_mosaic = None  # Хранить текущую плоскую мозаику для сохранения
canvas_width = 640  # Ширина холста
canvas_height = 480  # Высота холста
update_interval = 100  # Интервал обновления в миллисекундах
iterations = 10  # Количество итераций (10 обновлений за 1 секунду)

def load_images():
    global image_data
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
    if file_paths:
        for fp in file_paths:
            img = Image.open(fp)
            img = img.resize((canvas_width, canvas_height))  # Устанавливаем фиксированный размер
            image_data.append(np.array(img.convert("RGB")))
            image_listbox.insert(tk.END, fp)  # Добавление каждого пути к списку (отображение на новой строке)

def generate_random_mosaic(images):
    if len(images) < 1:
        return np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)  # Возвращаем пустое изображение
    
    flat_mosaic = []
    total_pixels = canvas_width * canvas_height

    for _ in range(total_pixels):
        idx = random.randint(0, len(images) - 1)  # Случайный индекс изображения
        img_pixels = images[idx].reshape(-1, 3)  # Преобразуем в одномерный массив пикселей
        random_pixel = random.choice(img_pixels)  # Случайный пиксель
        flat_mosaic.append(random_pixel)

    return np.array(flat_mosaic).reshape((canvas_height, canvas_width, 3))

def update_canvas(flat_mosaic):
    global canvas
    if canvas is None:
        canvas_window = tk.Toplevel()
        canvas = tk.Canvas(canvas_window, width=canvas_width, height=canvas_height)
        canvas.pack()

    mosaic_image = Image.fromarray(np.uint8(flat_mosaic))
    mosaic_image_tk = ImageTk.PhotoImage(mosaic_image)
    canvas.delete('all')
    canvas.create_image(0, 0, anchor=tk.NW, image=mosaic_image_tk)
    canvas.image = mosaic_image_tk

def start_mosaic():
    if image_data:
        run_mosaic_animation(iterations)  # Запускаем анимацию
    else:
        messagebox.showwarning("Предупреждение", "Сначала загрузите хотя бы одно изображение.")

def run_mosaic_animation(remaining_iterations):
    if remaining_iterations > 0:
        flat_mosaic = generate_random_mosaic(image_data)
        update_canvas(flat_mosaic)
        root.after(update_interval, run_mosaic_animation, remaining_iterations - 1)  # Запланировать следующую итерацию
    else:
        print("Воспроизведение завершено.")

def save_image():
    global current_flat_mosaic
    if current_flat_mosaic is not None and current_flat_mosaic.size > 0:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        save_path = os.path.join(desktop_path, "mosaic_image.png")
        mosaic_image = Image.fromarray(np.uint8(current_flat_mosaic))
        mosaic_image.save(save_path)
        print(f"Изображение сохранено по: {save_path}")

# Создание основного окна
root = tk.Tk()
root.title("Генератор мозаики")
root.geometry("400x500")

load_image_button = tk.Button(root, text="Загрузить изображения", command=load_images)
load_image_button.pack()

start_button = tk.Button(root, text="Запустить мозаику", command=start_mosaic)
start_button.pack()

save_image_button = tk.Button(root, text="Сохранить мозаику", command=save_image)
save_image_button.pack()

image_listbox = tk.Listbox(root, width=60, height=15)
image_listbox.pack()

root.mainloop()
