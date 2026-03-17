# launcher.py
import webview
from app import app # Flask uygulamamız
import threading
import sys

def start_flask():
    # Flask'ı arka planda sessiz modda başlat
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # 1. Flask'ı ayrı bir thread'de (iş parçacığı) başlat
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()

    # 2. Masaüstü penceresini oluştur ve Flask adresine yönlendir
    webview.create_window(
        title='🐺 Wolf Hand Controller v1.0', 
        url='http://127.0.0.1:5000',
        width=1000, 
        height=800,
        resizable=True,
        confirm_close=True # Kapatırken sor
    )
    
    # 3. GUI'yi başlat
    webview.start()
    sys.exit()