import os
import shutil
import zipfile
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class VariantCoverManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Variant Cover Manager 2.0")
        self.geometry("1300x850")

        # --- Data State ---
        self.temp_dir = None
        self.source_filename = ""
        self.archive_images = []
        self.variant_queue = []
        self.view_mode = "Standard Grid"
        self.thumb_size = 140 

        # --- UI Layout ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.header_frame.pack(side="top", fill="x", padx=20, pady=(20, 10))
        
        self.header_label = ctk.CTkLabel(self.header_frame, text="Variant Cover Manager 2.0", font=("Arial", 28, "bold"))
        self.header_label.pack(side="left")

        self.toolbar = ctk.CTkFrame(self, height=50, corner_radius=8)
        self.toolbar.pack(side="top", fill="x", padx=20, pady=(0, 15))

        self.btn_load = ctk.CTkButton(self.toolbar, text="LOAD SOURCE COMIC", width=180, command=self.load_archive)
        self.btn_load.pack(side="left", padx=15, pady=10)

        ctk.CTkLabel(self.toolbar, text="VIEW:", font=("Arial", 12, "bold")).pack(side="left", padx=(10, 5))
        self.view_menu = ctk.CTkOptionMenu(self.toolbar, values=["Standard Grid", "Vertical List"], command=self.update_view_settings)
        self.view_menu.pack(side="left", padx=5)

        ctk.CTkLabel(self.toolbar, text="THEME:", font=("Arial", 12, "bold")).pack(side="left", padx=(10, 5))
        self.theme_menu = ctk.CTkOptionMenu(self.toolbar, values=["Dark", "Light"], width=100, command=self.change_theme)
        self.theme_menu.set("Dark")
        self.theme_menu.pack(side="left", padx=5)

        # Main Workspace with Draggable Divider
        self.paned_window = tk.PanedWindow(self, orient="horizontal", sashwidth=6, bg="#1a1a1a", bd=0)
        self.paned_window.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.left_container = ctk.CTkFrame(self.paned_window, fg_color="transparent")
        self.scroll_frame = ctk.CTkScrollableFrame(self.left_container, label_text="Archive Content")
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.sidebar = ctk.CTkFrame(self.paned_window, width=380)
        self.sidebar.pack_propagate(False)
        
        self.paned_window.add(self.left_container, stretch="always")
        self.paned_window.add(self.sidebar, stretch="never")

        # Sidebar Elements
        self.btn_add_variants = ctk.CTkButton(self.sidebar, text="+ ADD NEW COVERS", fg_color="#3d5a80", height=40, font=("Arial", 13, "bold"), command=self.add_variants)
        self.btn_add_variants.pack(side="top", fill="x", padx=10, pady=10)

        queue_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        queue_header.pack(side="top", fill="x", padx=10)
        ctk.CTkLabel(queue_header, text="Injection Queue", font=("Arial", 12, "bold")).pack(side="left")
        ctk.CTkButton(queue_header, text="Clear All", width=60, height=20, fg_color="transparent", text_color="#9e2a2b", hover_color=("#e0e0e0", "#2b2b2b"), command=self.clear_queue).pack(side="right")

        self.variant_frame = ctk.CTkScrollableFrame(self.sidebar)
        self.variant_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        self.btn_save = ctk.CTkButton(self.sidebar, text="PROCESS & SAVE CBZ", fg_color="#2b9348", hover_color="#007200", height=55, font=("Arial", 15, "bold"), command=self.save_archive)
        self.btn_save.pack(side="bottom", fill="x", padx=10, pady=10)

        self.bind("<Configure>", self.on_window_resize)

    def clear_queue(self):
        if self.variant_queue and messagebox.askyesno("Confirm", "Remove all covers from the injection queue?"):
            self.variant_queue = []
            self.refresh_variant_display()

    def change_theme(self, choice):
        ctk.set_appearance_mode(choice)
        sash_color = "#1a1a1a" if choice == "Dark" else "#c0c0c0"
        self.paned_window.configure(bg=sash_color)

    def on_window_resize(self, event=None):
        self.after(10, self.recalculate_layout)

    def recalculate_layout(self):
        if not self.archive_images: return
        width = self.scroll_frame._parent_canvas.winfo_width() - 40
        cols = 1 if self.view_mode == "Vertical List" else max(1, width // (self.thumb_size + 20))
        if not hasattr(self, 'current_cols') or self.current_cols != cols:
            self.current_cols = cols
            self.refresh_archive_display(cols)

    def refresh_archive_display(self, cols=4):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        for i in range(cols): self.scroll_frame.columnconfigure(i, weight=1)

        for index, item in enumerate(self.archive_images):
            row, col = index // cols, index % cols
            f = ctk.CTkFrame(self.scroll_frame, corner_radius=4)
            f.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            img = Image.open(item["path"])
            ratio = img.height / img.width
            h = int(self.thumb_size * ratio)
            img = img.resize((self.thumb_size, h), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(self.thumb_size, h))
            ctk.CTkLabel(f, image=ctk_img, text="").pack(pady=5)
            ctk.CTkCheckBox(f, text=item["name"][:12], variable=item["keep"], font=("Arial", 10)).pack(pady=2)

        self.scroll_frame._parent_canvas.configure(scrollregion=self.scroll_frame._parent_canvas.bbox("all"))
        self.update_idletasks()

    def refresh_variant_display(self):
        for widget in self.variant_frame.winfo_children(): widget.destroy()
        for i, item in enumerate(self.variant_queue):
            f = ctk.CTkFrame(self.variant_frame)
            f.pack(fill="x", pady=5, padx=5)
            move_frame = ctk.CTkFrame(f, fg_color="transparent")
            move_frame.pack(side="left", padx=2)
            ctk.CTkButton(move_frame, text="▲", width=25, height=20, command=lambda idx=i: self.move_variant(idx, "up")).pack(pady=1)
            ctk.CTkButton(move_frame, text="▼", width=25, height=20, command=lambda idx=i: self.move_variant(idx, "down")).pack(pady=1)
            img = Image.open(item["path"])
            img.thumbnail((50, 50))
            ctk_img = ctk.CTkImage(light_image=img, size=img.size)
            ctk.CTkLabel(f, image=ctk_img, text="").pack(side="left", padx=10)
            pos_frame = ctk.CTkFrame(f, fg_color="transparent")
            pos_frame.pack(side="left", expand=True, fill="x")
            f_color = ("#1f538d", "#1f538d") if item["pos"] == "Front" else ("gray70", "gray30")
            b_color = ("#1f538d", "#1f538d") if item["pos"] == "Back" else ("gray70", "gray30")
            ctk.CTkButton(pos_frame, text="FRONT", height=22, font=("Arial", 10, "bold"), fg_color=f_color, command=lambda idx=i: self.set_variant_pos(idx, "Front")).pack(fill="x", pady=1)
            ctk.CTkButton(pos_frame, text="BACK", height=22, font=("Arial", 10, "bold"), fg_color=b_color, command=lambda idx=i: self.set_variant_pos(idx, "Back")).pack(fill="x", pady=1)
            ctk.CTkButton(f, text="X", width=25, height=46, fg_color="#9e2a2b", command=lambda idx=i: self.remove_variant(idx)).pack(side="right", padx=5)

    def set_variant_pos(self, index, pos):
        self.variant_queue[index]["pos"] = pos
        self.refresh_variant_display()

    def update_view_settings(self, choice):
        self.view_mode = choice
        self.recalculate_layout()

    def load_archive(self):
        file_path = filedialog.askopenfilename(filetypes=[("Comic Archives", "*.cbz *.zip")])
        if not file_path: return
        self.source_filename = os.path.splitext(os.path.basename(file_path))[0]
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        self.temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        self.archive_images = []
        valid_exts = (".jpg", ".jpeg", ".png", ".webp")
        for root, _, files in os.walk(self.temp_dir):
            for file in sorted(files):
                if file.lower().endswith(valid_exts):
                    self.archive_images.append({"path": os.path.join(root, file), "name": file, "keep": tk.BooleanVar(value=True)})
        self.recalculate_layout()

    def add_variants(self):
        files = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")])
        for f in files:
            self.variant_queue.append({"path": f, "name": os.path.basename(f), "pos": "Front"})
        self.refresh_variant_display()

    def move_variant(self, index, direction):
        if direction == "up" and index > 0:
            self.variant_queue[index], self.variant_queue[index-1] = self.variant_queue[index-1], self.variant_queue[index]
        elif direction == "down" and index < len(self.variant_queue) - 1:
            self.variant_queue[index], self.variant_queue[index+1] = self.variant_queue[index+1], self.variant_queue[index]
        self.refresh_variant_display()

    def remove_variant(self, index):
        self.variant_queue.pop(index)
        self.refresh_variant_display()

    def save_archive(self):
        if not self.archive_images and not self.variant_queue: return
        suggested_name = f"{self.source_filename}_v2" if self.source_filename else "new_comic"
        save_path = filedialog.asksaveasfilename(initialfile=suggested_name, defaultextension=".cbz", filetypes=[("CBZ file", "*.cbz")])
        if not save_path: return
        try:
            target_size = (1800, 2750)
            for item in self.archive_images:
                if item["keep"].get():
                    with Image.open(item["path"]) as reference:
                        target_size = reference.size
                    break
            with zipfile.ZipFile(save_path, 'w') as zip_out:
                def process_and_resize(img_path, output_name):
                    with Image.open(img_path) as img:
                        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                        resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
                        temp_img_path = os.path.join(self.temp_dir, f"proc_{output_name}")
                        resized_img.save(temp_img_path, "JPEG", quality=95)
                        zip_out.write(temp_img_path, arcname=output_name)
                f_idx = 0
                for v in self.variant_queue:
                    if v["pos"] == "Front":
                        process_and_resize(v["path"], f"000_var_{f_idx:02d}.jpg"); f_idx += 1
                p_idx = 1
                for item in self.archive_images:
                    if item["keep"].get():
                        zip_out.write(item["path"], arcname=f"{p_idx:03d}_page.jpg"); p_idx += 1
                b_idx = 0
                for v in self.variant_queue:
                    if v["pos"] == "Back":
                        process_and_resize(v["path"], f"zzz_var_{b_idx:02d}.jpg"); b_idx += 1
            messagebox.showinfo("Success", "Archive Saved and Scaled!")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")

    def on_closing(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        self.destroy()

if __name__ == "__main__":
    app = VariantCoverManager()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
