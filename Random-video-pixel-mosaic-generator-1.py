import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import random
import time
from tkinter import filedialog

# Параметры
image_data = None  # Хранение данных изображения
mosaic_arrays = []  # Массив мозаик
canvas = None  # Canvas для отображения изображения

# Функция для загрузки изображений
def load_image():
    global image_data, canvas
    file_path = filedialog.askopenfilename()
    if file_path:
        image = Image.open(file_path).convert("RGB")
        image_data = np.array(image)  # Сохранение данных изображения как массива
        generate_mosaics(image_data)  # Генерация мозайки из загруженного изображения

def generate_mosaics(image):
    global mosaic_arrays
    height, width, _ = image.shape
    mosaic_arrays = []
    remaining_pixels = height * width

    # Пример объединений в мозаики
    while remaining_pixels > 0:
        # Генерация случайного числа для количества пикселей в мозаике
        num_pixels = random.randint(1, remaining_pixels)  
        mosaic = []

        for _ in range(num_pixels):
            if remaining_pixels > 0:
                x_coord = random.randint(0, height - 1)
                y_coord = random.randint(0, width - 1)
                mosaic.append(image[x_coord, y_coord])  # Добавляем цвет пикселя в мозаику
                remaining_pixels -= 1
        
        mosaic_arrays.append(mosaic)

    random.shuffle(mosaic_arrays)  # Перемешивание мозайки

    # Преобразование мозайки в массив
    flat_mosaic = [color for mosaic in mosaic_arrays for color in mosaic]

    # Отображение результирующей мозайки
    update_canvas(flat_mosaic, width)

def update_canvas(flat_mosaic, width):
    """Отображает мозаику на Canvas."""
    global canvas
    if canvas is None:
        # Создаем новое окно для отображения
        canvas_window = tk.Toplevel()
        canvas = tk.Canvas(canvas_window, width=640, height=480)
        canvas.pack()

    mosaic_image = np.array(flat_mosaic).reshape((-1, width, 3))  # Формируем изображение из массива
    mosaic_image = Image.fromarray(np.uint8(mosaic_image))

    # Отображение изображения мозайки в Canvas
    mosaic_image_tk = ImageTk.PhotoImage(mosaic_image)
    canvas.delete('all')
    canvas.create_image(0, 0, anchor=tk.NW, image=mosaic_image_tk)
    canvas.image = mosaic_image_tk  # Сохраняем ссылку для предотвращения сборки мусора

# Создание основного окна
root = tk.Tk()
root.title("Procedural Mosaic Generator")
root.geometry("320x250")

# Кнопка для загрузки изображения
load_image_button = tk.Button(root, text="Загрузить изображение", command=load_image)
load_image_button.pack()

# Запуск основного цикла интерфейса
root.mainloop()
