# overlay_manager.py
import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
import os

class SystemOverlay:
    def __init__(self):
        self.root = None # Henüz oluşturmuyoruz
        self.active = False
        self.message_queue = [] # Mesajları sıraya alalım

    def setup_gui(self):
        """Tkinter objelerini SADECE kendi thread'i içinde oluşturur."""
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.config(bg='black')
        
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_w}x{screen_h}+0+0")
        
        self.label = tk.Label(self.root, bg='black', fg='#00FFFF', font=("Helvetica", 40, "bold"))
        self.label.pack(expand=True)
        
        # Başlangıçta gizli tut
        self.root.withdraw()

    def show_message(self, message, duration=1.5):
        """Dışarıdan çağrılan güvenli mesaj gösterme metodu."""
        if self.root:
            # Tkinter thread'ine komut gönder (after kullanmak thread-safe'dir)
            self.root.after(0, self._trigger_show, message, duration)

    def _trigger_show(self, message, duration):
        if not self.active:
            self.active = True
            self.label.config(text=message)
            self.root.deiconify() # Pencereyi göster
            threading.Timer(duration, self._hide).start()

    def _hide(self):
        if self.root:
            # Yine ana thread üzerinden gizle
            self.root.after(0, self.root.withdraw)
            self.active = False

    def run(self):
        """Bu metod threading.Thread tarafından çağrılacak."""
        self.setup_gui()
        self.root.mainloop()

# Singleton başlatma
overlay = SystemOverlay()
# Thread'i hemen başlatıyoruz
overlay_thread = threading.Thread(target=overlay.run, daemon=True)
overlay_thread.start()