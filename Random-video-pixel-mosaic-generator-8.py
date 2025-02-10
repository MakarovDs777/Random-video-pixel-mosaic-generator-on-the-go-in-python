import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
import random
import os
import cv2  # Импортируем OpenCV

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
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg;*.png;*.jpeg;*.mp4;*.avi")])
    if file_paths:
        for fp in file_paths:
            if fp.endswith(('.jpg', '.png', '.jpeg')):
                img = np.array(Image.open(fp).resize((canvas_width, canvas_height)).convert("RGB"))
                image_data.append(img)
                image_listbox.insert(tk.END, fp)  # Добавляем изображение в Listbox
            elif fp.endswith(('.mp4', '.avi')):
                # Извлечение случайных кадров из видео
                video_frames = extract_random_frames(fp)
                image_data.extend(video_frames)
                image_listbox.insert(tk.END, fp)  # Добавляем видео в Listbox

def extract_random_frames(video_path, num_frames=10):
    frames = []
    cap = cv2.VideoCapture(video_path)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indices = random.sample(range(total_frames), min(num_frames, total_frames))  # Случайные индексы кадров

    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)  # Установка на индекс кадра
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (canvas_width, canvas_height))  # Изменение размера кадра
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # Конвертация цвета
    cap.release()
    return frames

def split_image(image, min_size=20):
    height, width, _ = image.shape
    blocks = []

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

    flat_mosaic = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)  # Черный фон

    # Генерация случайных блоков для фона
    for _ in range(10):  # Установите количество слоев фона
        img = random.choice(images)
        blocks = split_image(img)
        for block in blocks:
            block_height, block_width, _ = block.shape
            
            # Поиск места для размещения блока
            x = random.randint(0, canvas_width - block_width)
            y = random.randint(0, canvas_height - block_height)

            # Размещение блока
            flat_mosaic[y:y + block_height, x:x + block_width] = block

    total_blocks = []
    for img in images:
        blocks = split_image(img)
        total_blocks.extend(blocks)

    current_x = 0
    current_y = 0
    
    for block in total_blocks:
        block_height, block_width, _ = block.shape
        
        if current_y + block_height > canvas_height:
            break

        if current_x + block_width > canvas_width:
            current_x = 0
            current_y += block_height
            if current_y + block_height > canvas_height:
                break

        # Наложение блока на готовую мозаику
        flat_mosaic[current_y:current_y + block_height, current_x:current_x + block_width] = block
        
        current_x += block_width  # Переход на следующую позицию по горизонтали

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

load_image_button = tk.Button(root, text="Загрузить изображения/видео", command=load_images)
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
