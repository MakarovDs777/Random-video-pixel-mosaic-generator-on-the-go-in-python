import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
import random
import os

# Параметры
image_data = []
canvas = None
current_flat_mosaic = None
canvas_width = 640
canvas_height = 480
update_interval = 100
is_running = False

def load_images():
    global image_data
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
    if file_paths:
        for fp in file_paths:
            img = np.array(Image.open(fp).resize((canvas_width, canvas_height)).convert("RGB"))
            image_data.append(img)
            image_listbox.insert(tk.END, fp)

def split_image(image, min_size=20):
    height, width, _ = image.shape
    blocks = []

    # Генерация блоков, пока размеры позволяют
    while height >= min_size and width >= min_size:
        block_width = random.randint(min_size, min(width, 100))
        block_height = random.randint(min_size, min(height, 100))

        start_x = random.randint(0, width - block_width)
        start_y = random.randint(0, height - block_height)

        block = image[start_y:start_y + block_height, start_x:start_x + block_width]
        blocks.append(block)

        if len(blocks) >= 50:
            break

    return blocks

def generate_random_mosaic(images):
    if len(images) == 0:
        return np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)

    flat_mosaic = np.full((canvas_height, canvas_width, 3), (255, 255, 255), dtype=np.uint8)  # Белый фон

    # Список всех блоков для формирования мозаики
    total_blocks = []
    for img in images:
        blocks = split_image(img)
        total_blocks.extend(blocks)

    # Перемешиваем блоки для случайных добавлений
    random.shuffle(total_blocks)

    # Заполнение мозаики
    for block in total_blocks:
        block_height, block_width, _ = block.shape
        
        # Поиск первого доступного места на холсте, чтобы установить блок
        placed = False
        for _ in range(100):  # Попыток разместить блок
            x = random.randint(0, canvas_width - block_width)
            y = random.randint(0, canvas_height - block_height)

            # Накладываем блок на холст, перезаписывая
            if np.all(flat_mosaic[y:y + block_height, x:x + block_width] == (255, 255, 255)):
                flat_mosaic[y:y + block_height, x:x + block_width] = block
                placed = True
                break

    return flat_mosaic

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
    global is_running
    if image_data and not is_running:
        is_running = True
        run_mosaic_animation()

def run_mosaic_animation():
    global current_flat_mosaic, is_running
    if is_running:
        current_flat_mosaic = generate_random_mosaic(image_data)
        update_canvas(current_flat_mosaic)
        root.after(update_interval, run_mosaic_animation)

def stop_mosaic():
    global is_running
    is_running = False

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

stop_button = tk.Button(root, text="Остановить мозаику", command=stop_mosaic)
stop_button.pack()

save_image_button = tk.Button(root, text="Сохранить мозаику", command=save_image)
save_image_button.pack()

image_listbox = tk.Listbox(root, width=60, height=15)
image_listbox.pack()

root.mainloop()
