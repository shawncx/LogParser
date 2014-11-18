from tkinter import *  
  
def btn_click():  
    b2['text'] = 'clicked'  
    evalue = e.get()  
    print('btn Click and Entry value is %s' % evalue)   
  
def btn_click_bind(event):  
    print('enter b2')  
  
def show_toplevel():  
    top = Toplevel()  
    top.title('no.2 window')  
    Label(top, text='this no.2 window').pack()  
  
root = Tk()  
root.title('no.1 window')  
# x = Label(root, bitmap='warning')  
l = Label(root, fg='red', bg='blue',text='wangwei', width=34, height=10)  
l.pack()  
  
b = Button(root, text='clickme', command=btn_click)  
b['width'] = 10  
b['height'] = 2  
b.pack()  
b2 = Button(root, text = 'clickme2')  
b2.configure(width = 10, height = 2, state = 'disabled')  
b2.bind("<Enter>", btn_click_bind)  
b2.pack()  
b3 = Button(root, text = 'showToplevel', command=show_toplevel)  
b3.pack()  
  
e = Entry(root, text = 'input your name')  
e.pack()  
epwd = Entry(root, text = 'input your pwd', show = '*')  
epwd.pack()  
  
def menu_click():  
    print('I am menu') 
  
xmenu = Menu(root)  
submenu = Menu(xmenu, tearoff = 0)  
for item in ['java', 'cpp', 'c', 'php']:  
    xmenu.add_command(label = item, command = menu_click)  
      
for item in ['think in java', 'java web', 'android']:  
    submenu.add_command(label = item, command = menu_click)  
xmenu.add_cascade(label = 'progame', menu = submenu)  
  
def pop(event):  
    submenu.post(event.x_root, event.y_root)  
  
def get_clickpoint(event):  
    print(event.x, event.y) 
  
for x in ['red', 'blue', 'yellow']:  
    Frame(height = 20, width = 20, bg = x).pack()  
  
root['menu'] = xmenu  
root.bind('<Button-3>', pop)  
root.bind('<Button-1>', get_clickpoint)  
root.mainloop()  