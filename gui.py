import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import time
import webbrowser
import logging
import schedule
from main import run_monitor, stop_monitoring

class GuiLogHandler(logging.Handler):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def emit(self, record):
        msg = self.format(record)
        self.app.log(msg)

class MonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Мониторинг ИБ — Диплом")
        self.root.geometry("800x650")

        tk.Label(root, text="Система мониторинга информационной безопасности", font=("Arial", 16, "bold")).pack(pady=15)

        self.status_label = tk.Label(root, text="Статус: Остановлен", font=("Arial", 14), fg="red")
        self.status_label.pack(pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="▶ Запустить мониторинг", font=("Arial", 12), bg="#4CAF50", fg="white", width=22, command=self.start_monitoring)
        self.start_btn.pack(side="left", padx=15)

        self.stop_btn = tk.Button(btn_frame, text="⏹ Остановить мониторинг", font=("Arial", 12), bg="#f44336", fg="white", width=22, command=self.stop_monitoring, state="disabled")
        self.stop_btn.pack(side="left", padx=15)

        tk.Button(root, text="⚠ Показать последний риск", font=("Arial", 11), bg="#FF9800", fg="white", command=self.open_analysis).pack(pady=8)

        tk.Label(root, text="Живой лог:").pack(anchor="w", padx=20)
        self.log_text = scrolledtext.ScrolledText(root, height=22, font=("Consolas", 10))
        self.log_text.pack(padx=20, pady=10, fill="both", expand=True)

        # Логирование в окно
        logging.getLogger().handlers.clear()
        handler = GuiLogHandler(self)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

        self.running = False

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def start_monitoring(self):
        if self.running: return
        self.running = True
        self.status_label.config(text="Статус: Работает ✅", fg="green")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.log("🚀 Мониторинг запущен...")

        threading.Thread(target=self.background_loop, daemon=True).start()

    def stop_monitoring(self):
        self.running = False
        stop_monitoring()
        self.status_label.config(text="Статус: Остановлен", fg="red")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.log("⏹ Мониторинг остановлен.")

    def background_loop(self):
        schedule.every(1).minutes.do(run_monitor)  # 1 минута для теста
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def open_analysis(self):
        try:
            webbrowser.open("analysis.txt")
            self.log("Открыт analysis.txt")
        except:
            messagebox.showerror("Ошибка", "Файл analysis.txt не найден")

if __name__ == "__main__":
    root = tk.Tk()
    app = MonitorApp(root)
    root.mainloop()