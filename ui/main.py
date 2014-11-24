'''
Created on 2014/11/12

@author: chen_xi
'''
from csv import DictReader
from tkinter import Tk, Listbox, Frame, Text, Button, Scrollbar, \
    Toplevel, Label, Entry, IntVar, Radiobutton, StringVar
from tkinter.constants import END, N, E, W, S, HORIZONTAL, VERTICAL, DISABLED, \
    NORMAL
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Combobox, Separator
import traceback

from handler import csvhandler
from handler.csvhandler import ValueSearchCondition, RangeSearchCondition, \
    JoinSearchCondition, SingleFileSearch, JoinFileSearch, Search
from model.filemodel import FileModel


class LogUI(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        
        self.filemodels = []
#         filemodel1 = FileModel("C:/Users/chen_xi/test1.csv", searchconds=[], relation="and", joincondtuples=[])
#         filemodel2 = FileModel("C:/Users/chen_xi/test2.csv", searchconds=[], relation="and", joincondtuples=[])
#         self.filemodels = [filemodel1, filemodel2]
        
        self._initUI()
        self.selectedfileindex = -1
        
        
    def _initUI(self):
        self.parent.title("Log Processor")
        self.pack()
        
        self._initfilepanel()
        self._initsearchcondpanel()
        self._initjoincondpanel()
        self._initfieldspanel()
        self._initconsole()
        
        self._inflatefilelist()
        
        
    def _initfilepanel(self):
        frame = Frame(self)
        frame.grid(row=0, column=0, sticky=E + W + S + N)
        
        label = Label(frame, text="File List: ")
        label.grid(sticky=N + W)
        
        self.filelist = Listbox(frame, width=40)
        self.filelist.grid(row=1, column=0, rowspan=2, columnspan=3)
        
        vsl = Scrollbar(frame, orient=VERTICAL)
        vsl.grid(row=1, column=3, rowspan=2, sticky=N + S + W)
        
        hsl = Scrollbar(frame, orient=HORIZONTAL)
        hsl.grid(row=3, column=0, columnspan=3, sticky=W + E + N)
        
        self.filelist.config(yscrollcommand=vsl.set, xscrollcommand=hsl.set)
        self.filelist.bind('<<ListboxSelect>>', self._onfilelistselection)
        
        hsl.config(command=self.filelist.xview)
        vsl.config(command=self.filelist.yview)
        
        upbtn = Button(frame, text="Up", width=7, command=self._upfile)
        upbtn.grid(row=1, column=4, padx=5, pady=5, sticky=S)
        
        downbtn = Button(frame, text="Down", width=7, command=self._downfile)
        downbtn.grid(row=2, column=4, padx=5, pady=5, sticky=N)
        
        newbtn = Button(frame, text="New", width=7, command=self._addfile)
        newbtn.grid(row=4, column=1, pady=5, sticky=E + S)
        
        delbtn = Button(frame, text="Delete", width=7, command=self._deletefile)
        delbtn.grid(row=4, column=2, padx=5, pady=5, sticky=W + S)
        
            
    def _inflatefilelist(self):
        self.filelist.delete(0, END)
        for filemodel in self.filemodels:
            self.filelist.insert(END, filemodel.filename)
            
        
    def _initsearchcondpanel(self):
        frame = Frame(self)
        frame.grid(row=0, column=1, sticky=E + W + S + N, padx=5)
        
        label = Label(frame, text="Search Condition: ")
        label.grid(row=0, column=0, columnspan=1, sticky=W)
        
        relationlable = Label(frame, text="Relation")
        relationlable.grid(row=0, column=1, columnspan=1, sticky=E)
        
        self.condrelationvar = StringVar(frame)
        relationinput = Combobox(frame, textvariable=self.condrelationvar, values=["and", "or"])
        relationinput.grid(row=0, column=2, padx=5, sticky=E)
        relationinput.bind('<<ComboboxSelected>>', self._onrelationchange)
        
        self.searchcondlist = Listbox(frame)
        self.searchcondlist.grid(row=1, rowspan=1, columnspan=3, sticky=E + W + S + N)
        
        vsl = Scrollbar(frame, orient=VERTICAL)
        vsl.grid(row=1, column=3, rowspan=1, sticky=N + S + W)
        
        hsl = Scrollbar(frame, orient=HORIZONTAL)
        hsl.grid(row=2, column=0, columnspan=3, sticky=W + E + N)
        
        self.searchcondlist.config(yscrollcommand=vsl.set, xscrollcommand=hsl.set)
        
        hsl.config(command=self.searchcondlist.xview)
        vsl.config(command=self.searchcondlist.yview)
        
        newbtn = Button(frame, text="New", width=7, command=self._addsearchcondition)
        newbtn.grid(row=3, column=0, padx=5, pady=5, sticky=E)
        
        delbtn = Button(frame, text="Delete", width=7, command=self._deletesearchcondition)
        delbtn.grid(row=3, column=1, sticky=E)
        
        modbtn = Button(frame, text="Update", width=7, command=self._modifysearchcondition)
        modbtn.grid(row=3, column=2, padx=5, pady=5, sticky=W)
        
    
    def _onrelationchange(self, evt):
        selectedmodel = self._getselectedfile()
        selectedmodel.relation = self.condrelationvar.get()
    
            
    def _inflatesearchcondlist(self, filemodel):
        self.condrelationvar.set(filemodel.relation)
        conds = filemodel.searchconds
        self.searchcondlist.delete(0, END)
        for cond in conds:
            self.searchcondlist.insert(END, cond.tostring())
        
        
    def _initjoincondpanel(self):
        frame = Frame(self)
        frame.grid(row=0, column=2, sticky=E + W + S + N, padx=5)
        
        label = Label(frame, text="Join Condition: ")
        label.grid(sticky=N + W)
        
        self.joincondlist = Listbox(frame)
        self.joincondlist.grid(row=1, rowspan=1, columnspan=3, sticky=E + W + S + N)
        
        vsl = Scrollbar(frame, orient=VERTICAL)
        vsl.grid(row=1, column=3, rowspan=1, sticky=N + S + W)
        
        hsl = Scrollbar(frame, orient=HORIZONTAL)
        hsl.grid(row=2, column=0, columnspan=3, sticky=W + E + N)
        
        self.joincondlist.config(yscrollcommand=vsl.set, xscrollcommand=hsl.set)
        
        hsl.config(command=self.joincondlist.xview)
        vsl.config(command=self.joincondlist.yview)
        
        newbtn = Button(frame, text="New", width=7, command=self._addjoincondition)
        newbtn.grid(row=3, column=0, padx=5, pady=5, sticky=E)
        
        delbtn = Button(frame, text="Delete", width=7, command=self._deletejoincondition)
        delbtn.grid(row=3, column=1, sticky=E)
        
        modbtn = Button(frame, text="Update", width=7, command=self._modifyjoincondition)
        modbtn.grid(row=3, column=2, padx=5, pady=5, sticky=W)
        
    
    def _inflatejoincondlist(self, condtuples):
        self.joincondlist.delete(0, END)
        for condtuple in condtuples:
            cond = condtuple[0]
            tofilename = condtuple[1]
            self.joincondlist.insert(END, cond.tostring() + " in " + tofilename)
            
            
    def _addfieldToDisplay(self):
        selectedfile = self._getselectedfile()
        index = self._getselectednodisplayfieldIndex()
        if index >= 0:
            selectedfile.displayfields.append(self._getselectednodisplayfield())
            self._inflatefieldpanel(selectedfile)
    
    
    def _removefieldFromDisplay(self):
        selectedfile = self._getselectedfile()
        index = self._getselecteddisplayfieldIndex()
        if index >= 0:
            del selectedfile.displayfields[index]
            self._inflatefieldpanel(selectedfile)
            
    
    def _initfieldspanel(self):
        frame = Frame(self)
        frame.grid(row=0, column=3, sticky=E + W + S + N)
        
        label = Label(frame, text="Display Fields List: ")
        label.grid(row=0, column=0, sticky=N + W)
        
        self.displayfieldlist = Listbox(frame)
        self.displayfieldlist.grid(row=1, column=0, rowspan=2)
        
        vsl = Scrollbar(frame, orient=VERTICAL)
        vsl.grid(row=1, column=1, rowspan=2, sticky=N + S + W)
        
        hsl = Scrollbar(frame, orient=HORIZONTAL)
        hsl.grid(row=3, column=0, sticky=W + E + N)
        
        self.displayfieldlist.config(yscrollcommand=vsl.set, xscrollcommand=hsl.set)
        
        hsl.config(command=self.displayfieldlist.xview)
        vsl.config(command=self.displayfieldlist.yview)
        
        addbtn = Button(frame, text="Add", width=7, command=self._addfieldToDisplay)
        addbtn.grid(row=1, column=2, padx=5, pady=5, sticky=S)
        
        removebtn = Button(frame, text="Remove", width=7, command=self._removefieldFromDisplay)
        removebtn.grid(row=2, column=2, padx=5, pady=5, sticky=N)
        
        label = Label(frame, text="No Display Fields List: ")
        label.grid(row=0, column=3, sticky=N + W)
        
        self.nodisplayfieldlist = Listbox(frame)
        self.nodisplayfieldlist.grid(row=1, column=3, rowspan=2)
        
        vsl = Scrollbar(frame, orient=VERTICAL)
        vsl.grid(row=1, column=4, rowspan=2, sticky=N + S + W)
        
        hsl = Scrollbar(frame, orient=HORIZONTAL)
        hsl.grid(row=3, column=3, sticky=W + E + N)
        
        self.nodisplayfieldlist.config(yscrollcommand=vsl.set, xscrollcommand=hsl.set)
        
        hsl.config(command=self.nodisplayfieldlist.xview)
        vsl.config(command=self.nodisplayfieldlist.yview)
        
        
    def _inflatefieldpanel(self, filemodel):
        filename = filemodel.filename
        fields = csvhandler.getfields(filename)
        displayfields = filemodel.displayfields
        displayfielddict = set(displayfields)
        
        self.nodisplayfieldlist.delete(0, END)
        self.displayfieldlist.delete(0, END)
        for field in fields:
            if field in displayfielddict:
                self.displayfieldlist.insert(END, field)
            else:
                self.nodisplayfieldlist.insert(END, field)
        
    
    def _initconsole(self):
        
        separator = Separator(self, orient=HORIZONTAL)
        separator.grid(row=1, columnspan=4, sticky=W + E, padx=5, pady=5)
        
        self.console = Text(self)
        self.console.grid(row=2, columnspan=4, sticky=W + E, padx=5, pady=5)
        
        vsl = Scrollbar(self, orient=VERTICAL)
        vsl.grid(row=2, column=4, sticky=N + S + W)
        
        hsl = Scrollbar(self, orient=HORIZONTAL)
        hsl.grid(row=3, column=0, columnspan=4, sticky=W + E + N)
        
        hsl.config(command=self.console.xview)
        vsl.config(command=self.console.yview)
        
        resbtn = Button(self, text="Search", width=7, command=self._showsearchresult)
        resbtn.grid(row=4, column=3, padx=5, pady=5, sticky=E)
        
    
    def _showsearchresult(self):
        try:
            res = self._searchresult()
            formatres = self._formatsearchresult(res)
        except Exception:
            formatres = "Error!\r\n" + traceback.format_exc()
        
        self.console.delete("0.0", END)
        self.console.insert("0.0", formatres)
    
    
    def _searchresult(self):
        filesearchs = []
        joinsearchs = []
        for filemodel in self.filemodels:
            filename = filemodel.filename
            
            singlesearch = SingleFileSearch(filename, DictReader(open(filename)), filemodel.searchconds, filemodel.relation)
            filesearchs.append(singlesearch)
            
            joindict = {}
            for joincondtuple in filemodel.joincondtuples:
                tofilename = joincondtuple[1]
                joincond = joincondtuple[0]
                if tofilename not in joindict:
                    joindict[tofilename] = []
                joindict[tofilename].append(joincond)
            
            for tofilename in joindict:
                joinsearch = JoinFileSearch(filename, DictReader(open(filename)), tofilename, DictReader(open(tofilename)), joindict[tofilename])
                joinsearchs.append(joinsearch)
                
        search = Search(filesearchs, joinsearchs)
        return search.process()
    
    
    def _formatsearchresult(self, searchresult):
        formatres = self._formatsummary(searchresult) + "\r\n"
        fileresults = searchresult.results
        for filemodel in self.filemodels:
            filename = filemodel.filename
            fileresult = fileresults[filename]
            displayfields = filemodel.displayfields
            formatres += self._formatfileresult(fileresult, displayfields)
            formatres += "\r\n"
        return formatres
    
    
    def _formatsummary(self, searchresult):
        res = "Summary\r\n"
        res += "Time Cost: " + str(searchresult.timecost) + " Seconds\r\n"
        fileresults = searchresult.results
        for filemodel in self.filemodels:
            filename = filemodel.filename
            fileresult = fileresults[filename]
            res += filename + "    Size: " + str(len(fileresult.result)) + "\r\n"
        return res
        
    
    def _formatfileresult(self, fileresult, displayfields):
        res = ""
        filename = fileresult.filename
        res += filename + "    Size: " + str(len(fileresult.result)) + "\r\n"
        
        for (i, field) in enumerate(displayfields):
            res += field
            if i < (len(displayfields) - 1):
                res += ","
            else:
                res += "\r\n"
                
        for rowdict in fileresult.result:
            for (i, field) in enumerate(displayfields):
                res += rowdict[field]
                if i < (len(displayfields) - 1):
                    res += ","
                else:
                    res += "\r\n"
        return res
                
             
        
    def _addfile(self):
        filetypes = [('csv files', '*.csv'), ('All files', '*')]
        
        selectedfile = askopenfilename(filetypes=filetypes)
        if selectedfile is not None:
            newmodel = FileModel(selectedfile, searchconds=[], relation="and", joincondtuples=[], displayfields=csvhandler.getfields(selectedfile))
            self.filemodels.append(newmodel)
            self.filelist.insert(END, newmodel.filename)
            self._setselectedfileindex(len(self.filemodels) - 1)
        
        
    def _deletefile(self):
        index = self._getselectedfileindex()
        if index >= 0:
            self.filelist.delete(index)
            del self.filemodels[index]
            self._setselectedfileindex(-1)
        
        
    def _upfile(self):
        if self._getselectedfileindex() <= 0:
            return
        index = self._getselectedfileindex()
        selectedfilename = self._getselectedfile().filename
        
        if index > 0:
            self.filelist.insert((index - 1), selectedfilename)
            self.filelist.delete(index + 1)
            
            self.filemodels[index - 1], self.filemodels[index] = self.filemodels[index], self.filemodels[index - 1]
            self._setselectedfileindex(index - 1)
            
            
    def _downfile(self):
        if self._getselectedfileindex() < 0:
            return
        index = self._getselectedfileindex()
        selectedfilename = self._getselectedfile().filename
        
        if index < (len(self.filemodels) - 1):
            self.filelist.insert((index + 2), selectedfilename)
            self.filelist.delete(index)
            
            self.filemodels[index], self.filemodels[index + 1] = self.filemodels[index + 1], self.filemodels[index]
            self._setselectedfileindex(index + 1)
         
         
    def _onfilelistselection(self, evt):
        if len(self.filelist.curselection()) == 0:
            return
        
        self._setselectedfileindex(self.filelist.curselection()[0])
        selectedfile = self._getselectedfile()
        
        self._inflatesearchcondlist(selectedfile)
        
        joincondtuples = selectedfile.joincondtuples
        self._inflatejoincondlist(joincondtuples)
        
        self._inflatefieldpanel(selectedfile)
        
    def _addsearchcondition(self):
        if self._getselectedfileindex() < 0:
            return
        
        self._popupsearchcondwindow()
        
    
    def _deletesearchcondition(self):
        index = self._getselectedsearchcondindex()
        if index < 0:
            return
        
        selectedfile = self._getselectedfile()
        del selectedfile.searchconds[index]
        self.searchcondlist.delete(index)
    
    
    def _modifysearchcondition(self):
        if self._getselectedsearchcondindex() < 0:
            return
        
        self._popupsearchcondwindow(self._getselectedsearchcondindex())
        
    
    def _addjoincondition(self):
        if self._getselectedfileindex() < 0:
            return
        
        self._popupjoincondwindow()
        
    
    def _deletejoincondition(self):
        index = self._getselectedjoincondindex()
        if index < 0:
            return
        
        selectedfile = self._getselectedfile()
        del selectedfile.joincondtuples[index]
        self.joincondlist.delete(index)
    
    
    def _modifyjoincondition(self):
        if self._getselectedjoincondindex() < 0:
            return
        
        self._popupjoincondwindow(self._getselectedjoincondindex())
         
         
    def _popupsearchcondwindow(self, index=-1):
        if index < 0:
            cond = ValueSearchCondition("", "")
        else:
            cond = self._getselectedfile().searchconds[index]
        
        window = Toplevel(self)
        
        title = Label(window, text="New Search Condition")
        title.grid(row=0, column=0, padx=5, pady=5, sticky=W + N)
        
        fieldlabel = Label(window, text="Field Name: ")
        fieldlabel.grid(row=1, column=0, padx=5, pady=5, sticky=W)
        
        fields = csvhandler.getfields(self._getselectedfile().filename)
        fieldvar = StringVar(window)
        fieldinput = Combobox(window, textvariable=fieldvar, values=fields, width=20)
        fieldinput.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        valuelabel = Label(window, text="Value: ")
        valuelabel.grid(row=3, column=0, padx=5, pady=5, sticky=W)
        
        valueinput = Entry(window)
        valueinput.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        minlabel = Label(window, text="Min Value: ")
        minlabel.grid(row=4, column=0, padx=5, pady=5, sticky=W)
        
        mininput = Entry(window)
        mininput.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        maxlabel = Label(window, text="Max Value: ")
        maxlabel.grid(row=5, column=0, padx=5, pady=5, sticky=W)
        
        maxinput = Entry(window)
        maxinput.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        sarchkind = IntVar()
        
        def _enablesingle():
            valueinput.config(state=NORMAL)
            mininput.config(state=DISABLED)
            maxinput.config(state=DISABLED)
            singlebutton.select()
            
        def _enablejoin():
            valueinput.config(state=DISABLED)
            mininput.config(state=NORMAL)
            maxinput.config(state=NORMAL)
            joinbutton.select()
            
        typelabel = Label(window, text="Search Type: ")
        typelabel.grid(row=2, column=0, padx=5, pady=5, sticky=W)
        
        singlebutton = Radiobutton(window, text="Single", variable=sarchkind, value=1, command=_enablesingle)
        singlebutton.grid(row=2, column=1, columnspan=1, padx=5, pady=5, sticky=W)
        
        joinbutton = Radiobutton(window, text="Range", variable=sarchkind, value=2, command=_enablejoin)
        joinbutton.grid(row=2, column=2, columnspan=1, padx=5, pady=5, sticky=W)
        
        # init value
        fieldvar.set(cond.field)
        if isinstance(cond, ValueSearchCondition):
            valueinput.insert(0, cond.val)
            _enablesingle()
        elif isinstance(cond, RangeSearchCondition):
            mininput.insert(0, cond.valmin)
            maxinput.insert(0, cond.valmax)
            _enablejoin()
            
        def _newcond():
            '''create new condition
            '''
            if sarchkind.get() == 1:
                cond = ValueSearchCondition(fieldvar.get(), valueinput.get())
            else:
                cond = RangeSearchCondition(fieldvar.get(), mininput.get(), maxinput.get())
            selectedfile = self._getselectedfile()
            if index < 0:
                selectedfile.searchconds.append(cond)
                
            else:
                del selectedfile.searchconds[index]
                selectedfile.searchconds[index:index] = [cond]
                
            self._inflatesearchcondlist(selectedfile)
            
            window.destroy()
        
        okbtn = Button(window, text="Confirm", width=7, command=_newcond)
        okbtn.grid(row=6, column=1, rowspan=1, columnspan=1, sticky=E, padx=5, pady=5)
        
        clsbtn = Button(window, text="Close", width=7, command=lambda: window.destroy())
        clsbtn.grid(row=6, column=2, rowspan=1, columnspan=1, sticky=E, padx=5, pady=5)
        
        
    def _popupjoincondwindow(self, index=-1):
        if index < 0:
            cond = JoinSearchCondition(("", ""))
            tofilename = ""
        else:
            condtuple = self._getselectedfile().joincondtuples[index]
            cond = condtuple[0]
            tofilename = condtuple[1]
            
        window = Toplevel(self)
        
        title = Label(window, text="New Search Condition")
        title.grid(row=0, column=0, padx=5, pady=5, sticky=W + N)
        
        filenamelabel = Label(window, text="Target Field Name: ")
        filenamelabel.grid(row=1, column=0, padx=5, pady=5, sticky=W)
        
        filevar = StringVar(window)
        filenameinput = Combobox(window, textvariable=filevar, values=self.filelist.get(0, END), width=30)
        filenameinput.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        fromfieldlabel = Label(window, text="Field in From File: ")
        fromfieldlabel.grid(row=3, column=0, padx=5, pady=5, sticky=W)
        
        fromfields = csvhandler.getfields(self._getselectedfile().filename)
        fromfieldvar = StringVar(window)
        fieldinput = Combobox(window, textvariable=fromfieldvar, values=fromfields, width=20)
        fieldinput.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        tofieldlabel = Label(window, text="Field in Target File: ")
        tofieldlabel.grid(row=4, column=0, padx=5, pady=5, sticky=W)
        
        tofields = []
        tofieldvar = StringVar(window)
        tofieldinput = Combobox(window, textvariable=tofieldvar, values=tofields, width=20)
        tofieldinput.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        def updatetofieldinput(evt):
            if filevar.get() is not None and len(filevar.get()) > 0:
                tofields = csvhandler.getfields(filevar.get())
                window.grid_slaves(4, 1)[0].grid_forget()
                tofieldinput = Combobox(window, textvariable=tofieldvar, values=tofields, width=20)
                tofieldinput.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        filenameinput.bind('<<ComboboxSelected>>', updatetofieldinput)
        
        # init value
        filevar.set(tofilename)
        fromfieldvar.set(cond.fieldtuple[0])
        updatetofieldinput(None)
        tofieldvar.set(cond.fieldtuple[1])
        
        def _newcond():
            '''create new condition
            '''
            cond = JoinSearchCondition((fromfieldvar.get(), tofieldvar.get()))
            tofilename = filevar.get()
            
            selectedfile = self._getselectedfile()
            if index < 0:
                selectedfile.joincondtuples.append((cond, tofilename))
                
            else:
                del selectedfile.joincondtuples[index]
                selectedfile.joincondtuples[index:index] = [(cond, tofilename)]
                
            self._inflatejoincondlist(selectedfile.joincondtuples)
            
            window.destroy()
        
        okbtn = Button(window, text="Confirm", width=7, command=_newcond)
        okbtn.grid(row=6, column=1, rowspan=1, columnspan=1, sticky=E, padx=5, pady=5)
        
        clsbtn = Button(window, text="Close", width=7, command=lambda: window.destroy())
        clsbtn.grid(row=6, column=2, rowspan=1, columnspan=1, sticky=W, padx=5, pady=5)
        
        
    def _getselectedfile(self):
        if self._getselectedfileindex() < 0:
            return None
        return self.filemodels[self._getselectedfileindex()]
    
    
    def _getselectedfileindex(self):
        return self.selectedfileindex
    
    
    def _setselectedfileindex(self, index):
        self.selectedfileindex = index
        if index >= 0:
            self.filelist.selection_set(index)
            
    def _getselectedsearchcondindex(self):
        if len(self.searchcondlist.curselection()) > 0:
            return self.searchcondlist.curselection()[0]
        return -1
    
    def _getselectedjoincondindex(self):
        if len(self.joincondlist.curselection()) > 0:
            return self.joincondlist.curselection()[0]
        return -1
    
    def _getselecteddisplayfieldIndex(self):
        if len(self.displayfieldlist.curselection()) > 0:
            return self.displayfieldlist.curselection()[0]
        return -1
    
    def _getselectednodisplayfieldIndex(self):
        if len(self.nodisplayfieldlist.curselection()) > 0:
            return self.nodisplayfieldlist.curselection()[0]
        return -1
    
    def _getselectednodisplayfield(self):
        if len(self.nodisplayfieldlist.curselection()) > 0:
            return self.nodisplayfieldlist.get(self.nodisplayfieldlist.curselection()[0])
        return None

if __name__ == "__main__":
    root = Tk()
    
    ui = LogUI(root)
    
    ui.mainloop() 
