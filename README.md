# <img src="logo.png" width="40" height="40" valign="middle"> Variant Cover Manager

**Variant Cover Manager** is a high-performance desktop utility for digital comic collectors. It streamlines the "remastering" of `.cbz` and `.zip` archives by allowing you to inject variant art, prune unwanted pages, and re-index gallery sequences through a clean, surgical interface.

---

## ✨ Features

* **Visual Lightbox:** Preview your entire archive in a 4-column grid.
* **Surgical Injection:** Toggle each new cover to the **Front [F]** or **Back [B]** of the book.
* **Manual Reordering:** Use **▲/▼ arrows** to perfectly sequence your variant gallery.
* **Individual Pruning:** Remove specific items from your queue or archive with a single click.
* **Zero-Asset Build:** Clean UI that compiles into a single, portable `.exe`.

---

## 📂 The Remastering Process

The app follows a non-destructive workflow to ensure archive integrity:

1.  **Smart Extraction:** The app flattens the internal directory of the `.cbz`, ensuring even nested folders are brought to the surface.
2.  **Page Pruning:** Unchecked pages in the grid are permanently excluded from the new build (ideal for removing ads).
3.  **Variant Positioning:**
    * **[F] Front:** Prefixed with `000_v_` to force the image before Page 1.
    * **[B] Back:** Prefixed with `zzz_v_` to append the image to the end.
4.  **Re-Indexing:** The app performs a lexicographical sort using 3-digit padding to prevent "page jumping" in comic reader apps.

---

## 📖 User Manual

### 1. Loading the Source

Click **LOAD SOURCE COMIC** to open a `.cbz` or `.zip`. The app extracts images to a temporary workspace and displays them in the **Archive Content** grid.

### 2. Adding Variants

Click **ADD NEW COVERS** to select your artwork. Each item appears in the **Variant Queue**:
* **Placement:** Toggle **[F]** for the start or **[B]** for the gallery at the end.
* **Reordering:** Use the arrows to arrange your covers (e.g., placing the 1:100 incentive before the standard B cover).

### 3. Processing

Click **PROCESS & SAVE CBZ**. The app builds a fresh archive.
* **Note:** Your original file is never touched; the app always saves a **new** version to protect your data.

---

## 🔍 Troubleshooting

| Scenario | Solution |
| :--- | :--- |
| **.CBR Files** | Rename `.cbr` to `.rar`, extract the images, and "Add" them to the app to save as a new `.cbz`. |
| **Images Missing** | Ensure files are in `.jpg`, `.png`, or `.webp` format. |
| **UI Cut Off** | The window is fully resizable; drag the corners to expand your workspace. |

---


## 🛠 Installation:
**Bash** - **pip install customtkinter Pillow**

## 🚀 Running the App
**Bash** - **python variant_manager.py**

## 📦 Compiling to EXE
**Bash** - **pyinstaller --noconsole --onefile --collect-all customtkinter variant_manager.py**