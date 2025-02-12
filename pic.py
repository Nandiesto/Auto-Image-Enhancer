import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os

def analyze_image(img):
    brightness = np.mean(img)
    contrast = np.std(img)
    saturation = np.mean(cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 1])
    sharpness = cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
    return brightness, contrast, saturation, sharpness

def dynamic_gamma_correction(img, brightness):
    gamma = 1.0 + (100 - brightness) / 200
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(img, table)

def adjust_saturation(img, saturation):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    saturation_adjustment = (100 - saturation) * 0.5
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] + saturation_adjustment, 0, 255)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def smooth_image(img, sharpness):
    if sharpness < 100:
        return cv2.bilateralFilter(img, 10, 50, 50)
    return img

def adjust_contrast(img, contrast):
    factor = 1.0 + (contrast - 50) / 100
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    lab[:, :, 0] = cv2.convertScaleAbs(lab[:, :, 0], alpha=factor)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

def apply_white_balance(img):
    result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    avg_a = np.mean(result[:, :, 1])
    avg_b = np.mean(result[:, :, 2])
    result[:, :, 1] = np.clip(result[:, :, 1] - (avg_a - 128) * 0.5, 0, 255).astype(np.uint8)
    result[:, :, 2] = np.clip(result[:, :, 2] - (avg_b - 128) * 0.5, 0, 255).astype(np.uint8)
    return cv2.cvtColor(result, cv2.COLOR_LAB2BGR)

def sharpen_image(img, sharpness):
    if sharpness < 50:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        return cv2.filter2D(img, -1, kernel)
    return img

def process_image(img):
    brightness, contrast, saturation, sharpness = analyze_image(img)
    processed_img = img.copy()
    processed_img = dynamic_gamma_correction(processed_img, brightness)
    processed_img = adjust_contrast(processed_img, contrast)
    processed_img = adjust_saturation(processed_img, saturation)
    processed_img = smooth_image(processed_img, sharpness)
    processed_img = apply_white_balance(processed_img)
    processed_img = sharpen_image(processed_img, sharpness)
    return processed_img

def select_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    if not file_path:
        return
    
    progress_bar.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    progress_bar.start()
    root.update()
    
    original_img = cv2.imread(file_path)
    edited_img = process_image(original_img)
    
    progress_bar.stop()
    progress_bar.place_forget()
    display_images(original_img, edited_img, file_path)

def display_images(original, edited, path):
    global img1, img2, edited_cv_img
    edited_cv_img = edited
    original = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    edited = cv2.cvtColor(edited, cv2.COLOR_BGR2RGB)
    original = Image.fromarray(original)
    edited = Image.fromarray(edited)
    
    max_size = (350, 350)
    original.thumbnail(max_size, Image.LANCZOS)
    edited.thumbnail(max_size, Image.LANCZOS)
    
    img1 = ImageTk.PhotoImage(original)
    img2 = ImageTk.PhotoImage(edited)
    label1.config(image=img1)
    label2.config(image=img2)
    save_button.config(state=tk.NORMAL)
    save_button.image_path = path

def save_image():
    file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
    if file_path:
        cv2.imwrite(file_path, edited_cv_img)

def close_app():
    root.destroy()

root = tk.Tk()
root.title("Auto Image Enhancer")
root.geometry("800x500")
root.configure(bg="#2C2C2C")

frame = tk.Frame(root, bg="#2C2C2C")
frame.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

title_label = tk.Label(root, text="Auto Image Enhancer", fg="white", bg="#2C2C2C", font=("Arial", 16))
title_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

label1 = tk.Label(frame, bg="#2C2C2C")
label1.grid(row=0, column=0, padx=10)

label2 = tk.Label(frame, bg="#2C2C2C")
label2.grid(row=0, column=1, padx=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="indeterminate")
progress_bar.place_forget()

btn_frame = tk.Frame(root, bg="#2C2C2C")
btn_frame.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

select_button = tk.Button(btn_frame, text="Select Image", command=select_image, fg="white", bg="#444", padx=10, pady=5)
select_button.pack(side=tk.LEFT, padx=10)

save_button = tk.Button(btn_frame, text="Save Image", command=save_image, fg="white", bg="#444", padx=10, pady=5, state=tk.DISABLED)
save_button.pack(side=tk.LEFT, padx=10)

close_button = tk.Button(btn_frame, text="Close", command=close_app, fg="white", bg="#444", padx=10, pady=5)
close_button.pack(side=tk.LEFT, padx=10)

root.mainloop()
