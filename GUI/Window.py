from tkinter import *



class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    #Creation of init_window
    def init_window(self):

        # changing the title of our master widget
        self.master.title("eBoat Simulation")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=5)

        # creating a button instance
        quitButton = Button(self, text="Quit")

        # placing the button on my window
        quitButton.place(x=0, y=0)


if __name__ == "__main__":
    root = Tk()

    # size of the window
    root.geometry("300x500")

    app = Window(root)
    root.mainloop()
