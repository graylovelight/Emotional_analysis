import sqlite3

import Start_project_Init
import Cryptography_Init
from tkinter import *
from tkinter import messagebox, ttk
import os
from PIL import Image, ImageTk
import tkinter as tk
from GUI import WeiboAnalyzerApp
# 建立登录机制，登录成功后进入GUI

root = Tk()
root.title("登录界面")
root.iconbitmap("background.png")
width = 700
height = 600
root.geometry(f"{width}x{height}")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = int((screen_width / 2) - (width / 2))
y_coordinate = int((screen_height / 2) - (height / 2))
root.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

canvas = Canvas(root, height=height, width=width)
background_image = ImageTk.PhotoImage(Image.open("background.png"))
background_label = Label(root, image=background_image)
background_label.place(relwidth=1, relheight=1)
canvas.pack()

frame = Frame(root, bg='#f0f0f0', bd=5, relief='raised')
frame.place(relx=0.5, rely=0.1, relwidth=0.75, relheight=0.5, anchor='n')

welcome_label = Label(frame, text="文本情感分析应用", font=("楷体", 30))
welcome_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
username_label = Label(frame, text="用户名:", font=("楷体", 15))
username_label.grid(row=1, column=0, padx=3, pady=10, sticky=W)
password_label = Label(frame, text="密码:", font=("楷体", 15))
password_label.grid(row=2, column=0, padx=3, pady=10, sticky=W)

username_entry = ttk.Combobox(frame, width=30)
username_entry.grid(row=1, column=1, padx=3, pady=10)
password_entry = Entry(frame, width=33, show="*")
password_entry.grid(row=2, column=1, padx=3, pady=10)


def load_username_history():
    if os.path.exists('username_history.txt'):
        with open('username_history.txt', 'r') as file:
            usernames = file.read().splitlines()
            return usernames
    return []



username_history = load_username_history()
username_entry['values'] = username_history


def save_username_to_history(username):
    with open('username_history.txt', 'a') as file:
        file.write(username + '\n')


def login():
    if (username_entry.get() == "" or password_entry.get()== ""):
        messagebox.showwarning("警告", "用户名与密码皆不可为空!")
    else:
        username = username_entry.get()
        password = password_entry.get()

        try:
            key = Cryptography_Init.get_key(username)
            if Start_project_Init.searchUser(key, username, password):
                root.destroy()
                root1 = tk.Tk()
                app = WeiboAnalyzerApp(root1)
                root1.mainloop()
            else:
                messagebox.showerror("发生错误", "用户名或密码错误！请再次尝试")
        except Exception as error:
            messagebox.showerror("Error", error)


def signup():
    if (username_entry.get() == "" or password_entry.get() == ""):
        messagebox.showwarning("警告", "用户名与密码皆不可为空!!")
    else:
        username = username_entry.get()
        password = password_entry.get()

        try:
            conn = sqlite3.connect("PM.db")
            c = conn.cursor()

            try:
                Start_project_Init.tableCreate()
            except sqlite3.OperationalError as error:
                messagebox.showwarning("Error", error)

            c.execute("SELECT * FROM users WHERE username=?", (username,))
            existing_user = c.fetchone()

            if existing_user:
                messagebox.showwarning("Error", "该用户名已经存在")
                return

            Cryptography_Init.set_key(username)
            encrypted_user = Cryptography_Init.encrypt_some(username, password)
            encrypted_password = encrypted_user[1]
            Start_project_Init.signup(username, encrypted_password)
            save_username_to_history(username)
            root.destroy()
        except sqlite3.OperationalError as error:
            messagebox.showwarning("Error", error)
        except Exception as error:
            messagebox.showwarning("Error", error)
        finally:
            conn.close()


def info():
    os.system('方案.txt')


login_button = Button(frame, text="登录", font=("楷体", 13), command=login)
login_button.grid(row=4, column=0, pady=15)
signup_button = Button(frame, text="注册", font=("楷体", 13), command=signup)
signup_button.grid(row=4, column=1, pady=15)
info_button = Button(root, text="帮助", font=("楷体", 13), command=info)
info_button.place(relx=0.9, rely=0.02, anchor='ne')

root.mainloop()
