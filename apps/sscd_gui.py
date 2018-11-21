import logging
from equipment import LIA, PEM, Stepper, StepperCmd
from logzero import logger
from pathlib import Path
from tkinter import Tk, BOTH, TOP, LEFT, X
from tkinter.ttk import Frame, Label, Entry


class App(Frame):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.master.title("MHz Steady State CD")
        self.pack(fill=BOTH, expand=1)
        port_frame = Frame(self, borderwidth=1)
        # PEM port
        pem_port_frame = Frame(port_frame)
        pem_port_frame.pack(fill=X)
        pem_port_label = Label(pem_port_frame, text="PEM Port", width=12)
        pem_port_label.pack(side=LEFT, padx=5, pady=5)
        pem_port_entry = Entry(pem_port_frame)
        pem_port_entry.pack(fill=X, padx=5, expand=True)
        # Stepper port
        stepper_port_frame = Frame(port_frame)
        stepper_port_frame.pack(fill=X)
        stepper_port_label = Label(stepper_port_frame, text="Stepper Port", width=12)
        stepper_port_label.pack(side=LEFT, padx=5, pady=5)
        stepper_port_entry = Entry(stepper_port_frame)
        stepper_port_entry.pack(fill=X, padx=5, expand=True)
        # LIA port
        lia_port_frame = Frame(port_frame)
        lia_port_frame.pack(fill=X)
        lia_port_label = Label(lia_port_frame, text="LIA Port", width=12)
        lia_port_label.pack(side=LEFT, padx=5, pady=5)
        lia_port_entry = Entry(lia_port_frame)
        lia_port_entry.pack(fill=X, padx=5, expand=True)

        port_frame.pack(fill=BOTH, expand=True)



def main():
    root = Tk()
    root.geometry("250x150+300+300")
    app = App()
    root.mainloop()


if __name__ == "__main__":
    main()
