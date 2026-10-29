import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import time
import webbrowser
import logging
import schedule
from main import runMonitor, stopMonitoring, startAiAnalysis

bgColor = "#121212"
textColor = "#e0e0e0"
subTextColor = "#9aa0a6"
logBg = "#252526"

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
        self.root.title("Система мониторинга")
        self.root.geometry("850x680")
        self.root.configure(bg=bgColor)

        tk.Label(root, text="Система мониторинга", font=("Segoe UI", 18, "bold"),
                 bg=bgColor, fg=textColor).pack(pady=(25, 10))

        self.statusLabel = tk.Label(root, text="Статус: Остановлен", font=("Segoe UI", 13),
                                    fg="#ff6b6b", bg=bgColor)
        self.statusLabel.pack(pady=8)

        btnFrame = tk.Frame(root, bg=bgColor)
        btnFrame.pack(pady=15)

        # ✅ Убрали disabledbackground/disabledforeground (их нет в tk.Button)
        btn_opts = {
            "font": ("Segoe UI", 11, "bold"), "fg": "white", "width": 24,
            "relief": "flat", "bd": 0, "cursor": "hand2",
            "activebackground": "#333333", "activeforeground": "white"
        }

        self.startBtn = tk.Button(btnFrame, text="▶ Запустить мониторинг", bg="#4caf50",
                                  command=self.start_monitoring, **btn_opts)
        self.startBtn.pack(side="left", padx=12)

        self.stopBtn = tk.Button(btnFrame, text=" Остановить мониторинг", bg="#f44336",
                                 command=self.stopMonitoring, state="disabled", **btn_opts)
        self.stopBtn.pack(side="left", padx=12)

        tk.Button(root, text="⚠ Показать последний риск", font=("Segoe UI", 11),
                  bg="#ff9800", fg="white", relief="flat", bd=0, cursor="hand2",
                  activebackground="#333333", activeforeground="white",
                  command=self.openAnalysis).pack(pady=12)

        tk.Label(root, text="📋 Логи событий:", font=("Segoe UI", 11, "bold"),
                 bg=bgColor, fg=subTextColor).pack(anchor="w", padx=35, pady=(5, 0))

        self.logText = scrolledtext.ScrolledText(root, height=24, font=("Consolas", 10),
                                                  bg=logBg, fg=textColor,
                                                  insertbackground="white", relief="solid", bd=1,
                                                  highlightthickness=0, padx=8, pady=5)
        self.logText.pack(padx=25, pady=10, fill="both", expand=True)

        logging.getLogger().handlers.clear()
        handler = GuiLogHandler(self)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

        self.running = False

    def log(self, message):
        self.logText.config(state="normal")
        self.logText.insert(tk.END, message + "\n")
        self.logText.see(tk.END)
        self.logText.config(state="disabled")

    def start_monitoring(self):
        if self.running: return
        self.running = True
        self.statusLabel.config(text="Статус: Работает ✅", fg="#69f0ae")
        # ✅ Явно задаём цвета при переключении состояния
        self.startBtn.config(state="disabled", bg="#3a3a3a", fg="#999999")
        self.stopBtn.config(state="normal", bg="#f44336", fg="white")
        self.log("🚀 Мониторинг запущен...")
        threading.Thread(target=self.backgroundLoop, daemon=True).start()

    def stopMonitoring(self):
        self.running = False
        stopMonitoring()
        self.statusLabel.config(text="Статус: Остановлен", fg="#ff6b6b")
        # ✅ Возвращаем исходные цвета при активации
        self.startBtn.config(state="normal", bg="#4caf50", fg="white")
        self.stopBtn.config(state="disabled", bg="#3a3a3a", fg="#999999")
        self.log(" Мониторинг остановлен.")

    def backgroundLoop(self):
        import schedule
        schedule.every(1).minutes.do(runMonitor)
        schedule.every(4).minutes.do(startAiAnalysis)
        logging.info("Мониторинг раз в минуту, анализ раз в 4 минуты")
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def openAnalysis(self):
        try:
            webbrowser.open("analysis.txt")
            self.log("Открыт analysis.txt")
        except:
            messagebox.showerror("Ошибка", "Файл analysis.txt не найден")

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg=bgColor)
    app = MonitorApp(root)
    root.mainloop()