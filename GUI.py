import tkinter as tk
from tkinter import ttk, messagebox
import threading
from PIL import Image, ImageTk
import method
# 在method的基础上创建用户界面，简易使用

class WeiboAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文本情感分析")
        self.root.geometry("800x400")

        # 设置背景图片
        self.canvas = tk.Canvas(root, height=400, width=800)
        self.background_image = ImageTk.PhotoImage(Image.open("background.png"))
        self.background_label = tk.Label(root, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)
        self.canvas.pack()

        # 设置框架
        self.frame = tk.Frame(root, bg='#f0f0f0', bd=5)
        self.frame.place(relx=0.5, rely=0.1, relwidth=0.75, relheight=0.5, anchor='n')

        # 存储cookie历史记录
        self.cookie_history = []
        self.load_cookie_history()

        # 添加菜单
        self.create_menu()

        # 添加输入字段和按钮
        self.create_widgets()

        # 初始化进度条
        self.progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="indeterminate")
        self.progress.place(relx=0.5, rely=0.75, anchor='center')

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="操作方式", command=self.show_help)

    def show_help(self):
        messagebox.showinfo("操作方式", "请输入微博Cookie和话题关键词，然后点击“开始分析”按钮。"
                                        "\n微博Cookie获取方法：打开微博网页，点击F12进入控制台，选择“网络”并刷新，在其中找到Cookie进行复制即可")

    def create_widgets(self):
        ttk.Label(self.frame, text="微博Cookie:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10,
                                                                               sticky=tk.W)
        self.entry_cookie = ttk.Combobox(self.frame, width=47, font=("Helvetica", 12))
        self.entry_cookie.grid(row=0, column=1, padx=10, pady=10)

        # 加载历史cookie到下拉菜单
        self.entry_cookie['values'] = self.cookie_history

        ttk.Label(self.frame, text="话题关键词:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10,
                                                                               sticky=tk.W)
        self.entry_topic = ttk.Entry(self.frame, width=50, font=("Helvetica", 12))
        self.entry_topic.grid(row=1, column=1, padx=10, pady=10)

        self.button_start = ttk.Button(self.frame, text="开始分析", command=self.start_analysis, style="TButton")
        self.button_start.grid(row=2, column=1, pady=20)

        # 配置按钮样式
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12, "bold"), background="#4CAF50", foreground="black")

    def load_cookie_history(self):
        # 从文件加载历史记录
        try:
            with open('cookie_history.txt', 'r') as file:
                self.cookie_history = file.read().splitlines()
        except FileNotFoundError:
            pass

    def save_cookie_history(self):
        # 保存历史记录到文件
        with open('cookie_history.txt', 'w') as file:
            for cookie in self.cookie_history:
                file.write(cookie + '\n')

    def start_analysis(self):
        cookie = self.entry_cookie.get()
        topic = self.entry_topic.get()

        if not cookie or not topic:
            messagebox.showwarning("输入错误", "请提供微博Cookie和话题关键词.")
            return

        # 添加cookie到历史记录
        if cookie not in self.cookie_history:
            self.cookie_history.append(cookie)
            self.save_cookie_history()
            self.entry_cookie['values'] = self.cookie_history

        def run_analysis():
            try:
                method.crawComments(cookie, topic)
                self.progress.stop()
                self.root.after(0, self.progress.place_forget)
                method.drawWordsCloud(topic)
                self.root.after(0, self.show_info_message, "分析完成", "可喜可贺，可喜可贺.")
            except Exception as e:
                self.progress.stop()
                self.root.after(0, self.progress.place_forget)
                self.root.after(0, self.show_error_message, "Error", str(e))

        self.progress.start()
        self.progress.place(relx=0.5, rely=0.75, anchor='center')
        analysis_thread = threading.Thread(target=run_analysis)
        analysis_thread.start()
        self.show_wait_message()

    def show_wait_message(self):
        self.root.after(0, lambda: messagebox.showinfo("操作成功", "操作成功，请耐心等待"))

    def show_info_message(self, title, message):
        messagebox.showinfo(title, message)

    def show_error_message(self, title, message):
        messagebox.showerror(title, message)


def mainPasswordKeeper():
    root = tk.Tk()
    app = WeiboAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = WeiboAnalyzerApp(root)
    root.mainloop()
