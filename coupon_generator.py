import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
from PIL import Image, ImageOps, ImageColor
import barcode
from barcode.writer import ImageWriter
import io
import os
import sys

# Define input window parammeters
def ask_larger_string(title, prompt):
    
    def center_window(win):
        win.update_idletasks()  # Make sure the window size is calculated
        width = win.winfo_width()
        height = win.winfo_height()
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        win.geometry(f"+{x}+{y}")
    
    def on_ok():
        nonlocal result
        result = entry.get()
        dialog.destroy()

    def on_cancel():
        nonlocal result
        result = None
        dialog.destroy()

    result = None
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.geometry("400x150")
    dialog.resizable(False, False)
    dialog.grab_set()  # Make modal

    center_window(dialog)

    label = tk.Label(dialog, text=prompt, font=("Segoe UI", 12))
    label.pack(pady=10)

    entry = tk.Entry(dialog, font=("Segoe UI", 14))
    entry.pack(pady=5, padx=20, fill='x')
    entry.focus_set()
    entry.bind("<Return>", lambda event: on_ok())
    dialog.bind("<Escape>", lambda event: on_cancel())

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=10)

    ok_btn = tk.Button(btn_frame, text="Vytvořit", width=10, command=on_ok)
    ok_btn.pack(side='left', padx=5)

 #   cancel_btn = tk.Button(btn_frame, text="Zrušit", width=10, command=on_cancel)
 #   cancel_btn.pack(side='left', padx=5)

    dialog.wait_window()
    return result

# Load bundled image from relative path or PyInstaller temp dir
def get_resource_path(relative_path):
    try:
        # PyInstaller temp dir
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def generate_barcode_image(data, size=(500, 145), bar_color="white", bg_color=(0, 255, 0, 255), transparent=False):
    # Create barcode in memory
    code128 = barcode.get("code128", data, writer=ImageWriter())
    buffer = io.BytesIO()
    code128.write(buffer, {"module_height": 15, "write_text": False})
    buffer.seek(0)
    
    # Open with PIL
    barcode_img = Image.open(buffer).convert("RGBA")

    # Resize
    barcode_img = barcode_img.resize(size, Image.Resampling.LANCZOS)

    # Recolor
    datas = barcode_img.getdata()
    new_data = []
    for item in datas:
        if item[0] < 128:  # black bar
            new_data.append((*ImageColor.getrgb(bar_color), 255))
        else:  # white background
            if transparent:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(bg_color)
    barcode_img.putdata(new_data)

    # Rotate to vertical
    return barcode_img.rotate(90, expand=True)

def main():
    # Init GUI
    root = tk.Tk()
    root.withdraw()

    # Prompt for data
    data = ask_larger_string("Generátor kupónů", "Zadej kód kupónu:")
    if not data:
        messagebox.showinfo("Zrušeno", "Nebyl zadán vstup.")
        return

    try:
        # Load coupon background image (embedded)
        background_path = get_resource_path("grafika.png")
        background = Image.open(background_path).convert("RGBA")

        # Generate barcode image
        barcode_img = generate_barcode_image(
            data,
            size=(500, 145),
            bar_color="white",
            bg_color=(0, 0, 0, 0),
            transparent=True
        )

        # Position barcode on the coupon
        position = (255, 79)  # X, Y pixel coordinates
        background.paste(barcode_img, position, barcode_img)

        # Ask where to save
        default_name = f"{data}.png"
        save_path = filedialog.asksaveasfilename(
            title="Uložit výslednou grafiku",
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[("PNG Image", "*.png")]
        )
        if save_path:
            background.save(save_path)
            messagebox.showinfo("Uloženo", f"Obrázek uložen do:\n{save_path}")
        else:
            messagebox.showinfo("Zrušeno", "Sobour nebyl uložen")

    except Exception as e:
        messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    main()
