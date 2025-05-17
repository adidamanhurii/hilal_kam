import cv2 # type: ignore
import numpy as np # type: ignore
import time
from datetime import datetime
import pytz # type: ignore
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk # type: ignore
import threading
import os

class HilalObserverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Pengamatan Hilal")
        
        # Variabel pengaturan
        self.greyscale = False
        self.equalize = False
        self.stack_frames = False
        self.stack_size = 10
        self.frames_to_stack = []
        self.last_saved_frame = None
        
        # Setup kamera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Kamera tidak dapat diakses")
            exit()
            
        # Setup GUI
        self.setup_gui()
        
        # Thread untuk update frame
        self.running = True
        self.thread = threading.Thread(target=self.update_frame)
        self.thread.daemon = True
        self.thread.start()
        
        # Update lokasi dan waktu
        self.update_datetime()
        
    def setup_gui(self):
        # Frame utama
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame untuk video dan histogram
        self.video_frame = ttk.Frame(self.main_frame)
        self.video_frame.pack(side=tk.LEFT, padx=10, pady=0, fill=tk.BOTH, expand=True)
        
        # Canvas untuk video
        self.canvas = tk.Canvas(self.video_frame, width=640, height=480)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Canvas untuk histogram
        self.hist_canvas = tk.Canvas(self.video_frame, height=120)
        self.hist_canvas.pack(fill=tk.BOTH, expand=True)
        
        
        
        # Frame untuk kontrol
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)
        
        # Tombol kontrol
        ttk.Button(self.control_frame, text="Greyscale (Skala Abu-abu)", command=self.toggle_greyscale).pack(fill=tk.X, pady=5)
        ttk.Button(self.control_frame, text="Equalize Histogram (Perataan Histogram)", command=self.toggle_equalize).pack(fill=tk.X, pady=5)
        ttk.Button(self.control_frame, text="Stack Frames (Tumpuk Frame)", command=self.toggle_stack).pack(fill=tk.X, pady=5)
        
        # Input jumlah frame untuk stacking
        ttk.Label(self.control_frame, text="Jumlah Frame Stacking:").pack(pady=(10,0))
        self.stack_entry = ttk.Entry(self.control_frame)
        self.stack_entry.insert(0, "10")
        self.stack_entry.pack(pady=5)
        ttk.Button(self.control_frame, text="Set Stack Size", command=self.set_stack_size).pack(fill=tk.X, pady=5)
        
        # Progress bar untuk stacking
        self.stack_progress_label = ttk.Label(self.control_frame, text="Stack Progress: 0/0")
        self.stack_progress_label.pack(pady=(10,0))
        self.stack_progress = ttk.Progressbar(self.control_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.stack_progress.pack(pady=5)
        
        # Informasi lokasi dan waktu
        self.info_frame = ttk.LabelFrame(self.control_frame, text="Informasi")
        self.info_frame.pack(fill=tk.X, pady=10)
        
        self.local_time_label = ttk.Label(self.info_frame, text="Waktu Lokal: ")
        self.local_time_label.pack(anchor=tk.W)
        
        self.utc_time_label = ttk.Label(self.info_frame, text="Waktu UTC: ")
        self.utc_time_label.pack(anchor=tk.W)
        
        self.location_label = ttk.Label(self.info_frame, text="Lokasi: di Tempat Bang AdiDam")
        self.location_label.pack(anchor=tk.W)
        
        # Tombol keluar
        ttk.Button(self.control_frame, text="Keluar", command=self.close_app).pack(fill=tk.X, pady=10)

        # Panel status menu
        self.status_frame = ttk.LabelFrame(self.video_frame, text="Status Menu")
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        self.greyscale_status = ttk.Label(self.status_frame, text="Greyscale: OFF")
        self.greyscale_status.pack(side=tk.LEFT, anchor=tk.NE)
        
        self.equalize_status = ttk.Label(self.status_frame, text="Equalize Histogram: OFF")
        self.equalize_status.pack(side=tk.LEFT, anchor=tk.NE)
        
        self.stack_status = ttk.Label(self.status_frame, text="Stack Frames: OFF")
        self.stack_status.pack(side=tk.LEFT, anchor=tk.NE)
    
    def toggle_greyscale(self):
        self.greyscale = not self.greyscale
        status = "ON" if self.greyscale else "OFF"
        self.greyscale_status.config(text=f"Greyscale: {status}")
        print(f"Greyscale: {status}")
    
    def toggle_equalize(self):
        self.equalize = not self.equalize
        status = "ON" if self.equalize else "OFF"
        self.equalize_status.config(text=f"Equalize Histogram: {status}")
        print(f"Equalize Histogram: {status}")
    
    def toggle_stack(self):
        self.stack_frames = not self.stack_frames
        status = "ON" if self.stack_frames else "OFF"
        self.stack_status.config(text=f"Stack Frames: {status}")
        if self.stack_frames:
            self.frames_to_stack = []
        print(f"Stack Frames: {status}")
    
    def set_stack_size(self):
        try:
            self.stack_size = int(self.stack_entry.get())
            print(f"Stack size diatur ke: {self.stack_size}")
            self.update_stack_progress()
        except ValueError:
            print("Masukkan angka yang valid")
    
    def update_datetime(self):
        # Mendapatkan waktu lokal dan UTC
        local_time = datetime.now()
        utc_time = datetime.now(pytz.utc)
        
        # Format waktu
        local_str = local_time.strftime("%Y-%m-%d %H:%M:%S")
        utc_str = utc_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Update label
        self.local_time_label.config(text=f"Waktu Lokal: {local_str}")
        self.utc_time_label.config(text=f"Waktu UTC: {utc_str}")
        
        # Update lokasi (contoh sederhana)
        self.location_label.config(text="Lokasi: di Tempat Bang AdiDam")
        
        # Jadwalkan update berikutnya dalam 1 detik
        self.root.after(1000, self.update_datetime)
    
    def update_stack_progress(self):
        if self.stack_frames:
            current = len(self.frames_to_stack)
            total = self.stack_size
            self.stack_progress_label.config(text=f"Stack Progress: {current}/{total}")
            self.stack_progress['maximum'] = total
            self.stack_progress['value'] = current
        else:
            self.stack_progress_label.config(text="Stack Progress: 0/0")
            self.stack_progress['value'] = 0
    
    def draw_histogram(self, frame):
        # Buat histogram dari frame
        if self.greyscale:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        else:
            hist_b = cv2.calcHist([frame], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([frame], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([frame], [2], None, [256], [0, 256])
        
        # Normalisasi histogram
        hist_h = 100  # tinggi histogram
        if self.greyscale:
            cv2.normalize(hist, hist, 0, hist_h, cv2.NORM_MINMAX)
        else:
            cv2.normalize(hist_b, hist_b, 0, hist_h, cv2.NORM_MINMAX)
            cv2.normalize(hist_g, hist_g, 0, hist_h, cv2.NORM_MINMAX)
            cv2.normalize(hist_r, hist_r, 0, hist_h, cv2.NORM_MINMAX)
        
        # Buat gambar histogram
        hist_img = np.zeros((hist_h, 256, 3), dtype=np.uint8)
        
        if self.greyscale:
            for i in range(1, 256):
                cv2.line(hist_img, (i-1, hist_h - int(hist[i-1])), 
                         (i, hist_h - int(hist[i])), 
                         (255, 255, 255), 1)
        else:
            for i in range(1, 256):
                cv2.line(hist_img, (i-1, hist_h - int(hist_b[i-1])), 
                         (i, hist_h - int(hist_b[i])), 
                         (255, 0, 0), 1)
                cv2.line(hist_img, (i-1, hist_h - int(hist_g[i-1])), 
                         (i, hist_h - int(hist_g[i])), 
                         (0, 255, 0), 1)
                cv2.line(hist_img, (i-1, hist_h - int(hist_r[i-1])), 
                         (i, hist_h - int(hist_r[i])), 
                         (0, 0, 255), 1)
        
        return hist_img
    
    def save_last_frame(self, frame):
        # Buat folder jika belum ada
        if not os.path.exists("saved_frames"):
            os.makedirs("saved_frames")
        
        local_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Example: "2023-03-15_14-30-45"

        # Format nama file tetap
        filename = os.path.join("saved_frames", f"{local_str}.png")
        #filename=f"{local_str}.png"
        
        # Simpan frame
        cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        print(f"Frame disimpan sebagai: {filename}")
        self.last_saved_frame = frame
    
    def process_frame(self, frame):
        # Greyscale
        if self.greyscale:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)  # Konversi kembali ke BGR untuk konsistensi
        
        # Equalize histogram (hanya jika greyscale)
        if self.equalize and self.greyscale:
            # Konversi ke YUV dan equalize channel Y (luminance)
            yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
            yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
            frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        
        # Stacking frames
        if self.stack_frames:
            # Tambahkan frame ke daftar
            if len(self.frames_to_stack) < self.stack_size:
                self.frames_to_stack.append(frame)
            else:
                self.frames_to_stack.pop(0)
                self.frames_to_stack.append(frame)
            
            # Update progress bar
            self.root.after(0, self.update_stack_progress)
            
            # Hitung rata-rata jika sudah ada cukup frame
            if len(self.frames_to_stack) > 0:
                stacked_frame = np.zeros_like(self.frames_to_stack[0], dtype=np.float32)
                for f in self.frames_to_stack:
                    stacked_frame += f.astype(np.float32)
                stacked_frame /= len(self.frames_to_stack)
                frame = stacked_frame.astype(np.uint8)
                
                # Simpan frame terakhir saat stack selesai
                if len(self.frames_to_stack) == self.stack_size:
                    self.save_last_frame(frame)
        
        return frame
    
    def resize_image(self, img, target_width, target_height):
        original_width, original_height = img.size
        if original_width == 0 or original_height == 0:
            return img
        ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def update_frame(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = self.process_frame(frame)
                
                # Konversi ke format yang bisa ditampilkan di Tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                hist_img = self.draw_histogram(frame)
                hist_img_pil = Image.fromarray(hist_img)
                
                # Update GUI di thread utama
                self.root.after(0, self.update_canvas, img, hist_img_pil)
    
    def update_canvas(self, img_pil, hist_img_pil):
        # Update gambar utama
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 0 or canvas_height <= 0:
            canvas_width = 640
            canvas_height = 480
        resized_img = self.resize_image(img_pil, canvas_width, canvas_height)
        imgtk = ImageTk.PhotoImage(image=resized_img)
        
        self.canvas.imgtk = imgtk
        self.canvas.create_image(
            (canvas_width - resized_img.width) // 2,
            (canvas_height - resized_img.height) // 2,
            anchor=tk.NW,
            image=imgtk
        )
        
        # Update histogram
        hist_width = self.hist_canvas.winfo_width()
        hist_height = self.hist_canvas.winfo_height()
        if hist_width <= 0 or hist_height <= 0:
            hist_width = 640
            hist_height = 120
        hist_resized = hist_img_pil.resize((hist_width, hist_height))
        hist_imgtk = ImageTk.PhotoImage(image=hist_resized)
        
        self.hist_canvas.imgtk = hist_imgtk
        self.hist_canvas.create_image(0, 0, anchor=tk.NW, image=hist_imgtk)
    
    def close_app(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        self.cap.release()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HilalObserverApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close_app)
    root.mainloop()
