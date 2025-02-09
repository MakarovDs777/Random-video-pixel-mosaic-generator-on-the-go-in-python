import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import random
from tkinter import filedialog
import os

# Параметры
image_data = None  # Хранение данных изображения
mosaic_arrays = []  # Массив мозаик
canvas = None  # Canvas для отображения
current_flat_mosaic = None  # Хранить текущую плоскую мозаику для сохранения
update_interval = 1000  # Интервал обновления в миллисекундах (1000 мс = 1 секунда)

def load_image():
    global image_data, current_flat_mosaic
    file_path = filedialog.askopenfilename()
    if file_path:
        image = Image.open(file_path).convert("RGB")
        image_data = np.array(image)  # Сохранение данных изображения как массива
        current_flat_mosaic = generate_mosaics(image_data)  # Генерация мозаики из загруженного изображения
        update_canvas(current_flat_mosaic, image_data.shape[1])  # Обновляем canvas с начальной мозаикой
        update_mosaic()  # Начинаем обновление мозаики

def generate_mosaics(image):
    global mosaic_arrays
    height, width, _ = image.shape
    mosaic_arrays = []
    remaining_pixels = height * width

    # Генерация мозайки
    while remaining_pixels > 0:
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

    # Преобразование мозаики в массив
    flat_mosaic = [color for mosaic in mosaic_arrays for color in mosaic]
    
    return flat_mosaic  # Возвращаем плоскую мозаику для дальнейшего использования

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

def update_mosaic():
    global image_data, current_flat_mosaic
    if image_data is not None:
        current_flat_mosaic = generate_mosaics(image_data)  # Генерация новой мозаики
        update_canvas(current_flat_mosaic, image_data.shape[1])  # Обновляем canvas
    root.after(update_interval, update_mosaic)  # Запланировать следующую перезагрузку

def save_image():
    global current_flat_mosaic
    if current_flat_mosaic is not None:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        save_path = os.path.join(desktop_path, "mosaic_image.png")

        # Определяем количество пикселей
        num_pixels = len(current_flat_mosaic) // 3

        # Убедимся, что количество пикселей делится на 3
        if len(current_flat_mosaic) % 3 != 0:
            print("Ошибка: размер мозаики не кратен 3.")
            return

        # Вычисляем размер для ресайза
        width = int(np.sqrt(num_pixels))  # Примерная ширина
        height = num_pixels // width  # Высота

        # Если кто-то (например, ширина) не может быть равным нулю, используем максимально возможный размер
        if width * height < num_pixels:
            height += 1
        
        mosaic_image = np.array(current_flat_mosaic).reshape((height, width, 3))  # Формируем изображение
        mosaic_image = Image.fromarray(np.uint8(mosaic_image))
        mosaic_image.save(save_path)  # Сохранение изображения на рабочий стол
        print(f"Изображение сохранено по: {save_path}")

# Создание основного окна
root = tk.Tk()
root.title("Procedural Mosaic Generator")
root.geometry("320x250")

# Кнопка для загрузки изображения
load_image_button = tk.Button(root, text="Загрузить изображение", command=load_image)
load_image_button.pack()

# Кнопка для сохранения изображения
save_image_button = tk.Button(root, text="Сохранить мозаику", command=save_image)
save_image_button.pack()

# Запуск основного цикла интерфейса
root.mainloop()
