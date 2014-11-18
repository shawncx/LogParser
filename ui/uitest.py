'''
'''

from tkinter import Tk, Text, BOTH, W, N, E, S, Frame, Label, Button, \
    PanedWindow, Entry
from tkinter.constants import VERTICAL
from tkinter.ttk import Style


class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent
        
        self.files = ["file1", "file2"]
        
        self.initUI()
        
    def initUI(self):
      
        self.parent.title("Windows")
        self.style = Style()
        self.style.theme_use("default")
        self.pack()
        
        self.filelistpanel = self.createfilelistpanel(self)
        self.filelistpanel.grid(row=0, column=0, rowspan=4, columnspan=2, padx=5, pady=5, sticky=N)
        
        self.console = self.createconsole(self)
        self.console.grid(row=0, column=2, columnspan=4, rowspan=4, padx=5, sticky=E + W + S + N)
        
        newfilebtn = Button(self, text="New File", command=self.addfile)
        newfilebtn.grid(row=4, column=0, padx=5, pady=5)
        
        resbtn = Button(self, text="Get Result")
        resbtn.grid(row=4, column=1, padx=5, pady=5)
        
        
#         buttonpanel.add(resbtn)

#         self.columnconfigure(1, weight=1)
#         self.columnconfigure(3, pad=7)
#         self.rowconfigure(3, weight=1)
#         self.rowconfigure(5, pad=7)
        
        
        
#         lbl = Label(self, text="Windows")
#         lbl.grid(sticky=E, pady=4, column=1)
        
#         area = Text(self)
#         area.grid(row=1, column=1, columnspan=2, rowspan=4,
#             padx=5, sticky=E + W + S + N)
        
#         abtn = Button(self, text="Activate")
#         abtn.grid(row=1, column=0)
# 
#         cbtn = Button(self, text="Close")
#         cbtn.grid(row=2, column=0, pady=4)
        
#         hbtn = Button(self, text="Help")
#         hbtn.grid(row=5, column=2, padx=5)

#         obtn = Button(self, text="OK")
#         obtn.grid(row=5, column=0)

    def createconsole(self, parent):
        console = Text(parent)
        return console
        
    def createfilelistpanel(self, parent):
        panel = PanedWindow(parent, orient=VERTICAL)
        for file in self.files:
            panel.add(self.createfilepanel(panel, file))
        return panel
        
    def createfilepanel(self, parent, file):
        panel = PanedWindow(parent)
        
        filelabel = Label(panel, text="File: ")
        filelabel.grid(row=0, column=0, padx=5, pady=5)
        
        fileentry = Entry(panel)
        fileentry.insert(0, file)
        fileentry.grid(row=0, column=1, pady=5, columnspan=3)
        
        condbtn = Button(panel, text="Condition", command=lambda: self.setcondition(file))
        condbtn.grid(row=1, column=0, padx=5, pady=5)
        
        delbtn = Button(panel, text="Delete")
        delbtn.grid(row=1, column=1, pady=5)
        
        upbtn = Button(panel, text="Up")
        upbtn.grid(row=1, column=2, pady=5)
        
        downbtn = Button(panel, text="Down")
        downbtn.grid(row=1, column=3, pady=5)
        
        return panel
    
    def setcondition(self, file):
        pass
    
    def addfile(self):
        print("dd")
        newfile = "new-file"
        
        self.files.append(newfile)
        newfilepanel = self.createfilepanel(self.filelistpanel, newfile)
        
        self.filelistpanel.add(newfilepanel)

def main():
  
    root = Tk()
#     root.geometry("350x300+300+300")
    Example(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  
