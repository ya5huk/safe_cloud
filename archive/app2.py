import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title('SafeCloud Login')
        
        container = tk.Frame(self,)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Initializing all frames in the app
        self.frames = {}
        for F in (LoginPage, RegisterPage):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            
            # frame.grid(row=0, column=0)

        self.show_frame(LoginPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class RegisterPage(tk.Frame):

    def __init__(self, parent: tk.Frame, controller: App):
        print('reg')
        tk.Frame.__init__(self, parent)
        
        l = tk.Label(parent, text='Register')
        l.pack(padx=10, pady=10)

        nav_button = tk.Button(self, text='To login', command=lambda: controller.show_frame('LoginPage'))
        nav_button.pack()

class LoginPage(tk.Frame):

    def __init__(self, parent: tk.Frame, controller: App):
        tk.Frame.__init__(self, parent)
        print('log')
        l = tk.Label(parent, text='Login')
        l.pack(padx=10, pady=10)

        nav_button = tk.Button(self, text='To register', command=lambda: controller.show_frame('RegisterPage'))
        nav_button.pack()
    

def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()