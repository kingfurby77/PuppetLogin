import json
import time
import requests
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar


class Application(tk.Frame):
    # Setup
    def __init__(self, master=None):
        super().__init__(master)

        # File
        self.file = None
        self.saved = True

        # Menu
        self.menu = tk.Menu()

        self.file_menu = tk.Menu(self.menu)
        self.file_menu.add_command(label="New", command=self.new, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Save", command=self.save, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As", command=self.save_as, accelerator="Ctrl+Shift+S")
        self.file_menu.add_command(label="Open", command=self.open, accelerator="Ctrl+O")

        self.list_menu = tk.Menu(self.menu)
        self.list_menu.add_command(label="Insert Above", command=self.insert_above)
        self.list_menu.add_command(label="Append", command=self.append)
        self.list_menu.add_command(label="Replace", command=self.replace)
        self.list_menu.add_command(label="Remove", command=self.remove)

        self.tools_menu = tk.Menu(self.menu)
        self.tools_menu.add_command(label="Login Selected", command=self.login_selected)
        self.tools_menu.add_command(label="Login All", command=self.login_all)

        # Nation and password box
        self.nation_box = tk.Entry()
        self.password_box = tk.Entry()

        # Scrollbar and lists
        self.scrollbar_vertical = tk.Scrollbar(orient="vertical")
        self.scrollbar_horizontal = tk.Scrollbar(orient="horizontal")
        self.list_box = tk.Listbox(yscrollcommand=self.scrollbar_vertical.set,
                                   xscrollcommand=self.scrollbar_horizontal.set)
        self.scrollbar_vertical.config(command=self.yview())
        self.scrollbar_horizontal.config(command=self.xview())

        self.create_widgets()

    def create_widgets(self):
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.menu.add_cascade(label="List", menu=self.list_menu)
        self.menu.add_cascade(label="Tools", menu=self.tools_menu)
        root.config(menu=self.menu)

        tk.Label(text="Nation Name:").grid(row=0, sticky=tk.E)
        tk.Label(text="Password:").grid(row=1, sticky=tk.E)
        self.nation_box.grid(row=0, column=1)
        self.password_box.grid(row=1, column=1)

        self.list_box.grid(row=2, columnspan=2, sticky=tk.N+tk.E+tk.S+tk.W)
        self.scrollbar_vertical.grid(row=2, column=2, sticky=tk.N+tk.E+tk.S+tk.W)
        self.scrollbar_horizontal.grid(row=3, columnspan=2, sticky=tk.N+tk.E+tk.S+tk.W)

    # Util
    def yview(self, *args):
        self.list_box.yview(*args)

    def xview(self, *args):
        self.list_box.xview(*args)

    @staticmethod
    def login(name, password):
        url_beginning = "https://www.nationstates.net/cgi-bin/api.cgi?nation="
        url_end = "&q=ping"
        response = str(requests.get(url_beginning+name+url_end, headers={"X-Password": password}))
        if response == "<Response [200]>":
            return "Login successful"
        elif response == "<Response [403]>":
            return "Error 403 - incorrect password"
        elif response == "<Response [404]>":
            return "Error 404 - nation not found"
        elif response == "<Response [409]>":
            return "Error 409 - previous successful login too recent"
        elif response == "<Response [429]>":
            return "Error 429 - API limit reached"
        else:
            return "Something went wrong"

    def listbox_to_pil(self):
        puppets = {}
        for i in range(self.list_box.size()):
            puppets[self.list_box.get(i)[0]] = self.list_box.get(i)[1]
        return puppets

    # Menu
    def new(self):
        if not self.saved:
            answer = messagebox.askyesnocancel(title="Unsaved changes", message="Do you want to save unsaved changes?")
            if answer:
                self.save()
            elif answer is None:
                return
        self.list_box.delete(0, tk.END)
        self.file = None
        self.saved = True

    def save(self):
        if self.file is None:
            file = filedialog.asksaveasfile(mode="w+", defaultextension=".pil", filetypes=(
                ("Puppet information list", "*.pil"), ("JSON", "*.json"), ("All files", "*.*")))
            json.dump(self.listbox_to_pil(), file)
            self.file = file
            self.saved = True
        else:
            self.file.truncate(0)
            self.file.seek(0, 0)
            json.dump(self.listbox_to_pil(), self.file)
            self.saved = True

    def save_as(self):
        file = filedialog.asksaveasfile(mode="w+", defaultextension=".pil", filetypes=(
            ("Puppet information list", "*.pil"), ("JSON", "*.json"), ("All files", "*.*")))
        json.dump(self.listbox_to_pil(), file)
        self.file = file
        self.saved = True

    def open(self):
        if not self.saved:
            answer = messagebox.askyesnocancel(title="Unsaved changes", message="Do you want to save unsaved changes?")
            if answer:
                self.save()
            elif answer is None:
                return
        self.list_box.delete(0, tk.END)
        file = filedialog.askopenfile(mode="r+", filetypes=(("Puppet information list", "*.pil"), ("JSON", "*.json"),
                                                            ("All files", "*.*")))
        puppets = json.load(file)
        for name in puppets:
            self.list_box.insert(tk.END, (name, puppets[name]))
        self.file = file
        self.saved = True

    def insert_above(self):
        self.list_box.insert(tk.ACTIVE, (self.nation_box.get(), self.password_box.get()))
        self.nation_box.delete(0, tk.END)
        self.password_box.delete(0, tk.END)
        self.saved = False

    def append(self):
        self.list_box.insert(tk.END, (self.nation_box.get(), self.password_box.get()))
        self.nation_box.delete(0, tk.END)
        self.password_box.delete(0, tk.END)
        self.saved = False

    def replace(self):
        self.list_box.delete(tk.ACTIVE)
        self.list_box.insert(tk.ACTIVE, (self.nation_box.get(), self.password_box.get()))
        self.nation_box.delete(0, tk.END)
        self.password_box.delete(0, tk.END)
        self.saved = False

    def remove(self):
        self.list_box.delete(tk.ACTIVE)
        self.saved = False

    def login_selected(self):
        puppet = self.list_box.get(tk.ACTIVE)
        error_message = self.login(puppet[0], puppet[1])
        messagebox.showinfo(title="Information", message=error_message)

    def login_all(self):
        progress_bar = Progressbar(orient=tk.HORIZONTAL, length=100, mode='determinate')
        progress_bar.grid(row=4, columnspan=2, sticky=tk.N+tk.E+tk.S+tk.W)
        errors = ""
        for i in range(self.list_box.size()):
            puppet = self.list_box.get(i)
            error_message = self.login(puppet[0], puppet[1])
            if error_message != "Login successful":
                errors += (puppet[0]+": "+error_message+"\n")
            time.sleep(0.6)
            progress_bar['value'] += (100/self.list_box.size())
            root.update_idletasks()
        progress_bar.grid_forget()
        if errors == "":
            messagebox.showinfo(title="Information", message="All logins successful")
        else:
            messagebox.showinfo(title="Information", message=errors)


root = tk.Tk()
root.title("Puppet Login")
root.geometry("225x250")

Application(root).mainloop()
