from tkinter import *
from tkinter.ttk import *

master = Tk()
 
variable = StringVar(master)
variable.set("one") # default value
 
w = Combobox(master, textvariable=variable, values=["one", "two", "three"])
w.pack()
btn = Button(master, text="test", command=lambda: print(variable.get()))
btn.pack()

 
master.mainloop()