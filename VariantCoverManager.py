import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os, zipfile, shutil, tempfile

class VariantLightboxManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Variant Cover Manager")
        self.geometry("1300x950")
        
        self.selected_archive = None
        self.temp_dir = None
        self.new_cover_items = [] 
        self.existing_pages = [] 
        self.image_refs = [] 

        self.setup_ui()

    def setup_ui(self):
        # --- Header ---
        self.header = ctk.CTkFrame(self)
        self.header.pack(fill="x", padx=10, pady=10)
        
        # Title Branding (Text Only)
        self.brand_row = ctk.CTkFrame(self.header, fg_color="transparent")
        self.brand_row.pack(fill="x", padx=10, pady=(10, 5))
        self.title_label = ctk.CTkLabel(self.brand_row, text="Variant Cover Manager", font=("Arial", 28, "bold"))
        self.title_label.pack(side="left")

        # Action Row
        self.action_row = ctk.CTkFrame(self.header, fg_color="transparent")
        self.action_row.pack(fill="x", padx=10, pady=(5, 10))
        self.load_btn = ctk.CTkButton(self.action_row, text="LOAD SOURCE COMIC", width=180, command=self.load_archive)
        self.load_btn.pack(side="left")
        self.file_label = ctk.CTkLabel(self.action_row, text="No Book Loaded", font=("Arial", 12, "italic"), text_color="gray")
        self.file_label.pack(side="left", padx=20)
        
        # --- Main Layout ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_container.grid_columnconfigure(0, weight=3)
        self.main_container.grid_columnconfigure(1, weight=2)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Left Panel (Archive Content)
        self.left_frame = ctk.CTkFrame(self.main_container)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5)
        self.left_controls = ctk.CTkFrame(self.left_frame, height=40)
        self.left_controls.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(self.left_controls, text="Select All", width=80, command=lambda: self.toggle_all(True)).pack(side="right", padx=5)
        ctk.CTkButton(self.left_controls, text="Unselect All", width=80, command=lambda: self.toggle_all(False)).pack(side="right", padx=5)
        self.archive_scroll = ctk.CTkScrollableFrame(self.left_frame, label_text="ARCHIVE CONTENT")
        self.archive_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Right Panel (Variant Queue)
        self.right_frame = ctk.CTkFrame(self.main_container)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        self.right_controls = ctk.CTkFrame(self.right_frame, height=40)
        self.right_controls.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(self.right_controls, text="ADD NEW COVERS", command=self.load_new_covers).pack(side="left", padx=5)
        self.queue_scroll = ctk.CTkScrollableFrame(self.right_frame, label_text="VARIANT QUEUE")
        self.queue_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Footer
        self.footer = ctk.CTkFrame(self, height=60)
        self.footer.pack(fill="x", padx=10, pady=10)
        self.save_btn = ctk.CTkButton(self.footer, text="PROCESS & SAVE CBZ", font=("Arial", 14, "bold"), fg_color="green", height=45, command=self.process_archive)
        self.save_btn.pack(side="right", padx=20)

    # --- CORE LOGIC ---
    def load_archive(self):
        path = filedialog.askopenfilename(filetypes=[("Comic Archives", "*.cbz *.zip")])
        if not path: return
        self.selected_archive = path
        self.file_label.configure(text=os.path.basename(path))
        if self.temp_dir: shutil.rmtree(self.temp_dir)
        self.temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(path, 'r') as z:
            for member in z.namelist():
                if not member.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')): continue
                fn = os.path.basename(member)
                with z.open(member) as s, open(os.path.join(self.temp_dir, fn), "wb") as t:
                    shutil.copyfileobj(s, t)
        self.refresh_existing_grid()

    def refresh_existing_grid(self):
        for widget in self.archive_scroll.winfo_children(): widget.destroy()
        self.existing_pages = []
        files = sorted(os.listdir(self.temp_dir))
        for i, f in enumerate(files):
            var = ctk.BooleanVar(value=True)
            card = ctk.CTkFrame(self.archive_scroll)
            card.grid(row=i//4, column=i%4, padx=5, pady=5)
            try:
                img = Image.open(os.path.join(self.temp_dir, f))
                img.thumbnail((120, 160))
                tk_img = ImageTk.PhotoImage(img)
                self.image_refs.append(tk_img)
                ctk.CTkLabel(card, image=tk_img, text="").pack(pady=2)
            except: pass
            ctk.CTkCheckBox(card, text=f[:12], variable=var, font=("Arial", 10)).pack(pady=2)
            self.existing_pages.append({'name': f, 'var': var})

    def load_new_covers(self):
        paths = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        for p in paths:
            self.new_cover_items.append({'path': p, 'pos': ctk.StringVar(value="end")})
        self.refresh_new_covers_grid()

    def refresh_new_covers_grid(self):
        for widget in self.queue_scroll.winfo_children(): widget.destroy()
        # Clean up refs while keeping archive thumbnails
        self.image_refs = [ref for ref in self.image_refs if hasattr(ref, 'is_archive')]
        for i, item in enumerate(self.new_cover_items):
            card = ctk.CTkFrame(self.queue_scroll)
            card.pack(pady=5, fill="x", padx=5)
            
            # Reordering buttons
            move_f = ctk.CTkFrame(card, fg_color="transparent")
            move_f.pack(side="left", padx=2)
            ctk.CTkButton(move_f, text="▲", width=20, height=20, command=lambda idx=i: self.move_item(idx, -1)).pack(pady=1)
            ctk.CTkButton(move_f, text="▼", width=20, height=20, command=lambda idx=i: self.move_item(idx, 1)).pack(pady=1)
            
            try:
                img = Image.open(item['path'])
                img.thumbnail((65, 90))
                tk_img = ImageTk.PhotoImage(img)
                self.image_refs.append(tk_img) 
                ctk.CTkLabel(card, image=tk_img, text="").pack(side="left", padx=5)
            except: pass

            info_f = ctk.CTkFrame(card, fg_color="transparent")
            info_f.pack(side="left", fill="both", expand=True, padx=5)
            ctk.CTkLabel(info_f, text=os.path.basename(item['path']), font=("Arial", 11, "bold"), wraplength=130).pack(anchor="w")
            
            radio_f = ctk.CTkFrame(info_f, fg_color="transparent")
            radio_f.pack(anchor="w")
            ctk.CTkRadioButton(radio_f, text="F", variable=item['pos'], value="beginning", width=45).pack(side="left")
            ctk.CTkRadioButton(radio_f, text="B", variable=item['pos'], value="end", width=45).pack(side="left")
            
            ctk.CTkButton(card, text="✕", width=25, height=25, fg_color="gray", command=lambda idx=i: self.remove_item(idx)).pack(side="right", padx=5)

    def move_item(self, index, direction):
        new_index = index + direction
        if 0 <= new_index < len(self.new_cover_items):
            self.new_cover_items[index], self.new_cover_items[new_index] = self.new_cover_items[new_index], self.new_cover_items[index]
            self.refresh_new_covers_grid()

    def remove_item(self, index):
        self.new_cover_items.pop(index)
        self.refresh_new_covers_grid()

    def toggle_all(self, state):
        for item in self.existing_pages: item['var'].set(state)

    def process_archive(self):
        if not self.selected_archive: return
        out = filedialog.asksaveasfilename(defaultextension=".cbz", filetypes=[("Comic Archive", "*.cbz")])
        if not out: return
        try:
            ws = tempfile.mkdtemp()
            for item in self.existing_pages:
                if item['var'].get():
                    shutil.copy2(os.path.join(self.temp_dir, item['name']), os.path.join(ws, item['name']))
            for i, item in enumerate(self.new_cover_items):
                prefix = "000_v_" if item['pos'].get() == "beginning" else "zzz_v_"
                ext = os.path.splitext(item['path'])[1]
                shutil.copy2(item['path'], os.path.join(ws, f"{prefix}{i:03}{ext}"))
            with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as new_z:
                for f in sorted(os.listdir(ws)):
                    new_z.write(os.path.join(ws, f), arcname=f)
            messagebox.showinfo("Success", "Archive Remastered Successfully!")
            self.new_cover_items = []
            self.refresh_new_covers_grid()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

if __name__ == "__main__":
    app = VariantLightboxManager()
    app.mainloop()
