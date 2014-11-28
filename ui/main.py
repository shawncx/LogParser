'''
Created on 2014/11/12

@author: chen_xi
'''
from tkinter import Tk, Listbox, Frame, Text, Button, Scrollbar, \
    Toplevel, Label, Entry, IntVar, Radiobutton, StringVar
from tkinter.constants import END, N, E, W, S, HORIZONTAL, VERTICAL, DISABLED, \
    NORMAL
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Combobox, Separator
import traceback

from handler import loghandler
from handler.loghandler import SingleFileSearch, JoinFileSearch, Search, \
    EqualSearchCondition, RangeSearchCondition, JoinSearchCondition, \
    ContainSearchCondition
from model.filemodel import FileModel


class LogUI(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        
        self.fileModels = []
#         fileModel1 = FileModel("C:/Users/chen_xi/test1.csv", searchConds=[], relation="and", joinCondTuples=[])
#         fileModel2 = FileModel("C:/Users/chen_xi/test2.csv", searchConds=[], relation="and", joinCondTuples=[])
#         self.fileModels = [fileModel1, fileModel2]
        
        self._initUI()
        self.selectedFileIndex = -1
        
        
    def _initUI(self):
        self.parent.title("Log Parser")
        self.pack()
        
        self._initFilePanel()
        self._initSearchCondPanel()
        self._initJoinCondPanel()
        self._initFieldsPanel()
        self._initConsole()
        
        self._inflateFileList()
        
        
    def _initFilePanel(self):
        frame = Frame(self)
        frame.grid(row=0, column=0, sticky=E + W + S + N)
        
        label = Label(frame, text="File List: ")
        label.grid(sticky=N + W)
        
        self.fileList = Listbox(frame, width=40)
        self.fileList.grid(row=1, column=0, rowspan=2, columnspan=3)
        
        vsl = Scrollbar(frame, orient=VERTICAL)
        vsl.grid(row=1, column=3, rowspan=2, sticky=N + S + W)
        
        hsl = Scrollbar(frame, orient=HORIZONTAL)
        hsl.grid(row=3, column=0, columnspan=3, sticky=W + E + N)
        
        self.fileList.config(yscrollcommand=vsl.set, xscrollcommand=hsl.set)
        self.fileList.bind('<<ListboxSelect>>', self._onFileListSelection)
        
        hsl.config(command=self.fileList.xview)
        vsl.config(command=self.fileList.yview)
        
        upBtn = Button(frame, text="Up", width=7, command=self._upFile)
        upBtn.grid(row=1, column=4, padx=5, pady=5, sticky=S)
        
        downBtn = Button(frame, text="Down", width=7, command=self._downFile)
        downBtn.grid(row=2, column=4, padx=5, pady=5, sticky=N)
        
        newBtn = Button(frame, text="New", width=7, command=self._addFile)
        newBtn.grid(row=4, column=1, pady=5, sticky=E + S)
        
        delBtn = Button(frame, text="Delete", width=7, command=self._deleteFile)
        delBtn.grid(row=4, column=2, padx=5, pady=5, sticky=W + S)
        
            
    def _inflateFileList(self):
        self.fileList.delete(0, END)
        for fileModel in self.fileModels:
            self.fileList.insert(END, fileModel.fileName)
            
        
    def _initSearchCondPanel(self):
        frame = Frame(self)
        frame.grid(row=0, column=1, sticky=E + W + S + N, padx=5)
        
        label = Label(frame, text="Search Condition: ")
        label.grid(row=0, column=0, columnspan=1, sticky=W)
        
        relationLable = Label(frame, text="Relation")
        relationLable.grid(row=0, column=1, columnspan=1, sticky=E)
        
        self.condRelationVar = StringVar(frame)
        relationInput = Combobox(frame, textvariable=self.condRelationVar, values=["and", "or"])
        relationInput.grid(row=0, column=2, padx=5, sticky=E)
        relationInput.bind('<<ComboboxSelected>>', self._onRelationChange)
        
        self.searchCondList = Listbox(frame)
        self.searchCondList.grid(row=1, rowspan=1, columnspan=3, sticky=E + W + S + N)
        
        vsl = Scrollbar(frame, orient=VERTICAL)
        vsl.grid(row=1, column=3, rowspan=1, sticky=N + S + W)
        
        hsl = Scrollbar(frame, orient=HORIZONTAL)
        hsl.grid(row=2, column=0, columnspan=3, sticky=W + E + N)
        
        self.searchCondList.config(yscrollcommand=vsl.set, xscrollcommand=hsl.set)
        
        hsl.config(command=self.searchCondList.xview)
        vsl.config(command=self.searchCondList.yview)
        
        newBtn = Button(frame, text="New", width=7, command=self._addSearchCondition)
        newBtn.grid(row=3, column=0, padx=5, pady=5, sticky=E)
        
        delBtn = Button(frame, text="Delete", width=7, command=self._deleteSearchCondition)
        delBtn.grid(row=3, column=1, sticky=E)
        
        modBtn = Button(frame, text="Update", width=7, command=self._modifySearchCondition)
        modBtn.grid(row=3, column=2, padx=5, pady=5, sticky=W)
        
    
    def _onRelationChange(self, evt):
        selectedModel = self._getSelectedFile()
        selectedModel.relation = self.condRelationVar.get()
    
            
    def _inflateSearchCondList(self, fileModel):
        self.condRelationVar.set(fileModel.relation)
        conds = fileModel.searchConds
        self.searchCondList.delete(0, END)
        for cond in conds:
            self.searchCondList.insert(END, cond.toString())
        
        
    def _initJoinCondPanel(self):
        frame = Frame(self)
        frame.grid(row=0, column=2, sticky=E + W + S + N, padx=5)
        
        label = Label(frame, text="Join Condition: ")
        label.grid(sticky=N + W)
        
        self.joinCondList = Listbox(frame)
        self.joinCondList.grid(row=1, rowspan=1, columnspan=3, sticky=E + W + S + N)
        
        vsl = Scrollbar(frame, orient=VERTICAL)
        vsl.grid(row=1, column=3, rowspan=1, sticky=N + S + W)
        
        hsl = Scrollbar(frame, orient=HORIZONTAL)
        hsl.grid(row=2, column=0, columnspan=3, sticky=W + E + N)
        
        self.joinCondList.config(yscrollcommand=vsl.set, xscrollcommand=hsl.set)
        
        hsl.config(command=self.joinCondList.xview)
        vsl.config(command=self.joinCondList.yview)
        
        newBtn = Button(frame, text="New", width=7, command=self._addJoinCondition)
        newBtn.grid(row=3, column=0, padx=5, pady=5, sticky=E)
        
        delBtn = Button(frame, text="Delete", width=7, command=self._deleteJoinCondition)
        delBtn.grid(row=3, column=1, sticky=E)
        
        modBtn = Button(frame, text="Update", width=7, command=self._modifyJoinCondition)
        modBtn.grid(row=3, column=2, padx=5, pady=5, sticky=W)
        
    
    def _inflateJoinCondList(self, condTuples):
        self.joinCondList.delete(0, END)
        for condTuple in condTuples:
            cond = condTuple[0]
            toFileName = condTuple[1]
            self.joinCondList.insert(END, cond.toString() + " in " + toFileName)
            
            
    def _addFieldToDisplay(self):
        selectedFile = self._getSelectedFile()
        index = self._getSelectedNoDisplayFieldIndex()
        if index >= 0:
            selectedFile.displayFields.append(self._getSelectedNoDisplayField())
            self._inflateFieldPanel(selectedFile)
    
    
    def _removeFieldFromDisplay(self):
        selectedFile = self._getSelectedFile()
        index = self._getSelectedDisplayFieldIndex()
        if index >= 0:
            del selectedFile.displayFields[index]
            self._inflateFieldPanel(selectedFile)
            
    
    def _initFieldsPanel(self):
        frame = Frame(self)
        frame.grid(row=0, column=3, sticky=E + W + S + N)
        
        label = Label(frame, text="Display Fields List: ")
        label.grid(row=0, column=0, sticky=N + W)
        
        self.displayFieldList = Listbox(frame)
        self.displayFieldList.grid(row=1, column=0, rowspan=2)
        
        vsl = Scrollbar(frame, orient=VERTICAL)
        vsl.grid(row=1, column=1, rowspan=2, sticky=N + S + W)
        
        hsl = Scrollbar(frame, orient=HORIZONTAL)
        hsl.grid(row=3, column=0, sticky=W + E + N)
        
        self.displayFieldList.config(yscrollcommand=vsl.set, xscrollcommand=hsl.set)
        
        hsl.config(command=self.displayFieldList.xview)
        vsl.config(command=self.displayFieldList.yview)
        
        addBtn = Button(frame, text="Add", width=7, command=self._addFieldToDisplay)
        addBtn.grid(row=1, column=2, padx=5, pady=5, sticky=S)
        
        removeBtn = Button(frame, text="Remove", width=7, command=self._removeFieldFromDisplay)
        removeBtn.grid(row=2, column=2, padx=5, pady=5, sticky=N)
        
        label = Label(frame, text="No Display Fields List: ")
        label.grid(row=0, column=3, sticky=N + W)
        
        self.noDisplayFieldList = Listbox(frame)
        self.noDisplayFieldList.grid(row=1, column=3, rowspan=2)
        
        vsl = Scrollbar(frame, orient=VERTICAL)
        vsl.grid(row=1, column=4, rowspan=2, sticky=N + S + W)
        
        hsl = Scrollbar(frame, orient=HORIZONTAL)
        hsl.grid(row=3, column=3, sticky=W + E + N)
        
        self.noDisplayFieldList.config(yscrollcommand=vsl.set, xscrollcommand=hsl.set)
        
        hsl.config(command=self.noDisplayFieldList.xview)
        vsl.config(command=self.noDisplayFieldList.yview)
        
        
    def _inflateFieldPanel(self, fileModel):
        fileName = fileModel.fileName
        reader = loghandler.createReader(fileName)
        fields = reader.getFields()
        displayFields = fileModel.displayFields
        displayFieldDict = set(displayFields)
        
        self.noDisplayFieldList.delete(0, END)
        self.displayFieldList.delete(0, END)
        for field in fields:
            if field in displayFieldDict:
                self.displayFieldList.insert(END, field)
            else:
                self.noDisplayFieldList.insert(END, field)
                
    
    def _initConsole(self):
        
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
        
        resBtn = Button(self, text="Search", width=7, command=self._showSearchResult)
        resBtn.grid(row=4, column=3, padx=5, pady=5, sticky=E)
        
    
    def _showSearchResult(self):
        try:
            res = self._searchResult()
            formatRes = self._formatSearchResult(res)
        except Exception:
            formatRes = "Error!\r\n" + traceback.format_exc()
        
        self.console.delete("0.0", END)
        self.console.insert("0.0", formatRes)
    
    
    def _searchResult(self):
        fileSearchs = []
        joinSearchs = []
        for fileModel in self.fileModels:
            fileName = fileModel.fileName
            
            reader = loghandler.createReader(fileName)
            singleSearch = SingleFileSearch(fileName, reader.getRecords(), \
                                            fileModel.searchConds, fileModel.relation)
            fileSearchs.append(singleSearch)
            
            joinDict = {}
            for joinCondTuple in fileModel.joinCondTuples:
                toFileName = joinCondTuple[1]
                joinCond = joinCondTuple[0]
                if toFileName not in joinDict:
                    joinDict[toFileName] = []
                joinDict[toFileName].append(joinCond)
            
            for toFileName in joinDict:
                toReader = loghandler.createReader(toFileName)
                joinSearch = JoinFileSearch(fileName, reader.getRecords(), toFileName, \
                                            toReader.getRecords(), joinDict[toFileName])
                joinSearchs.append(joinSearch)
                
        search = Search(fileSearchs, joinSearchs)
        return search.process()
    
    
    def _formatSearchResult(self, searchResult):
        formatRes = self._formatSummary(searchResult) + "\r\n"
        fileResults = searchResult.results
        for fileModel in self.fileModels:
            fileName = fileModel.fileName
            fileResult = fileResults[fileName]
            displayFields = fileModel.displayFields
            formatRes += self._formatFileResult(fileResult, displayFields)
            formatRes += "\r\n"
        return formatRes
    
    
    def _formatSummary(self, searchResult):
        res = "Summary\r\n"
        res += "Time Cost: " + str(searchResult.timeCost) + " Seconds\r\n"
        fileResults = searchResult.results
        for fileModel in self.fileModels:
            fileName = fileModel.fileName
            fileResult = fileResults[fileName]
            res += fileName + "    Size: " + str(len(fileResult.result)) + "\r\n"
        return res
        
    
    def _formatFileResult(self, fileResult, displayFields):
        res = ""
        fileName = fileResult.fileName
        res += fileName + "    Size: " + str(len(fileResult.result)) + "\r\n"
        
        for (i, field) in enumerate(displayFields):
            res += field
            if i < (len(displayFields) - 1):
                res += ","
            else:
                res += "\r\n"
                
        for rowdict in fileResult.result:
            for (i, field) in enumerate(displayFields):
                res += rowdict[field]
                if i < (len(displayFields) - 1):
                    res += ","
                else:
                    res += "\r\n"
        return res
                
             
        
    def _addFile(self):
        fileTypes = [('csv files', '*.csv'), ('log files', '*.log'), ('All files', '*')]
        
        selectedFile = askopenfilename(filetypes=fileTypes)
        if selectedFile is not None and len(selectedFile.strip(" ")) > 0:
            reader = loghandler.createReader(selectedFile)
            newModel = FileModel(selectedFile, searchConds=[], relation="and", \
                                 joinCondTuples=[], displayFields=reader.getFields())
            self.fileModels.append(newModel)
            self.fileList.insert(END, newModel.fileName)
            self._setSelectedFileIndex(len(self.fileModels) - 1)
        
        
    def _deleteFile(self):
        index = self._getSelectedFileIndex()
        if index >= 0:
            self.fileList.delete(index)
            del self.fileModels[index]
            self._setSelectedFileIndex(-1)
        
        
    def _upFile(self):
        if self._getSelectedFileIndex() <= 0:
            return
        index = self._getSelectedFileIndex()
        selectedFileName = self._getSelectedFile().fileName
        
        if index > 0:
            self.fileList.insert((index - 1), selectedFileName)
            self.fileList.delete(index + 1)
            
            self.fileModels[index - 1], self.fileModels[index] = self.fileModels[index], self.fileModels[index - 1]
            self._setSelectedFileIndex(index - 1)
            
            
    def _downFile(self):
        if self._getSelectedFileIndex() < 0:
            return
        index = self._getSelectedFileIndex()
        selectedFileName = self._getSelectedFile().fileName
        
        if index < (len(self.fileModels) - 1):
            self.fileList.insert((index + 2), selectedFileName)
            self.fileList.delete(index)
            
            self.fileModels[index], self.fileModels[index + 1] = self.fileModels[index + 1], self.fileModels[index]
            self._setSelectedFileIndex(index + 1)
         
         
    def _onFileListSelection(self, evt):
        if len(self.fileList.curselection()) == 0:
            return
        
        self._setSelectedFileIndex(self.fileList.curselection()[0])
        selectedFile = self._getSelectedFile()
        
        self._inflateSearchCondList(selectedFile)
        
        joinCondTuples = selectedFile.joinCondTuples
        self._inflateJoinCondList(joinCondTuples)
        
        self._inflateFieldPanel(selectedFile)
        
    def _addSearchCondition(self):
        if self._getSelectedFileIndex() < 0:
            return
        
        self._popupSearchCondWindow()
        
    
    def _deleteSearchCondition(self):
        index = self._getSelectedSearchCondIndex()
        if index < 0:
            return
        
        selectedFile = self._getSelectedFile()
        del selectedFile.searchConds[index]
        self.searchCondList.delete(index)
    
    
    def _modifySearchCondition(self):
        if self._getSelectedSearchCondIndex() < 0:
            return
        
        self._popupSearchCondWindow(self._getSelectedSearchCondIndex())
        
    
    def _addJoinCondition(self):
        if self._getSelectedFileIndex() < 0:
            return
        
        self._popupJoinCondWindow()
        
    
    def _deleteJoinCondition(self):
        index = self._getSelectedJoinCondIndex()
        if index < 0:
            return
        
        selectedFile = self._getSelectedFile()
        del selectedFile.joinCondTuples[index]
        self.joinCondList.delete(index)
    
    
    def _modifyJoinCondition(self):
        if self._getSelectedJoinCondIndex() < 0:
            return
        
        self._popupJoinCondWindow(self._getSelectedJoinCondIndex())
         
         
    def _popupSearchCondWindow(self, index=-1):
        if index < 0:
            cond = EqualSearchCondition("", "")
        else:
            cond = self._getSelectedFile().searchConds[index]
        
        window = Toplevel(self)
        
        title = Label(window, text="New Search Condition")
        title.grid(row=0, column=0, padx=5, pady=5, sticky=W + N)
        
        fieldLabel = Label(window, text="Field Name: ")
        fieldLabel.grid(row=1, column=0, padx=5, pady=5, sticky=W)
        
        reader = loghandler.createReader(self._getSelectedFile().fileName)
        fields = reader.getFields()
        fieldVar = StringVar(window)
        fieldInput = Combobox(window, textvariable=fieldVar, values=fields, width=20)
        fieldInput.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        valueLabel = Label(window, text="Value: ")
        valueLabel.grid(row=5, column=0, padx=5, pady=5, sticky=W)
        
        valueInput = Entry(window)
        valueInput.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        minLabel = Label(window, text="Min Value: ")
        minLabel.grid(row=6, column=0, padx=5, pady=5, sticky=W)
        
        minInput = Entry(window)
        minInput.grid(row=6, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        maxLabel = Label(window, text="Max Value: ")
        maxLabel.grid(row=7, column=0, padx=5, pady=5, sticky=W)
        
        maxInput = Entry(window)
        maxInput.grid(row=7, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        sarchKind = IntVar()
        
        def _enableEqual():
            valueInput.config(state=NORMAL)
            minInput.config(state=DISABLED)
            maxInput.config(state=DISABLED)
            equalBtn.select()
        
        def _enableContain():
            valueInput.config(state=NORMAL)
            minInput.config(state=DISABLED)
            maxInput.config(state=DISABLED)
            containBtn.select()
            
        def _enableRange():
            valueInput.config(state=DISABLED)
            minInput.config(state=NORMAL)
            maxInput.config(state=NORMAL)
            rangeBtn.select()
            
        typeLabel = Label(window, text="Search Type: ")
        typeLabel.grid(row=2, column=0, padx=5, pady=5, sticky=W)
        
        equalBtn = Radiobutton(window, text="Equal", variable=sarchKind, value=1, command=_enableEqual)
        equalBtn.grid(row=2, column=1, columnspan=1, padx=5, pady=5, sticky=W)
        
        containBtn = Radiobutton(window, text="Contain", variable=sarchKind, value=2, command=_enableContain)
        containBtn.grid(row=3, column=1, columnspan=1, padx=5, pady=5, sticky=W)
        
        rangeBtn = Radiobutton(window, text="Range", variable=sarchKind, value=3, command=_enableRange)
        rangeBtn.grid(row=4, column=1, columnspan=1, padx=5, pady=5, sticky=W)
        
        # init value
        fieldVar.set(cond.field)
        if isinstance(cond, EqualSearchCondition):
            valueInput.insert(0, cond.val)
            _enableEqual()
        elif isinstance(cond, ContainSearchCondition):
            valueInput.insert(0, cond.val)
            _enableContain()
        elif isinstance(cond, RangeSearchCondition):
            minInput.insert(0, cond.valMin)
            maxInput.insert(0, cond.valMax)
            _enableRange()
            
        def _newCond():
            '''
            create new condition
            '''
            if sarchKind.get() == 1:
                cond = EqualSearchCondition(fieldVar.get(), valueInput.get())
            elif sarchKind.get() == 2:
                cond = ContainSearchCondition(fieldVar.get(), valueInput.get())
            elif sarchKind.get() == 3:
                cond = RangeSearchCondition(fieldVar.get(), minInput.get(), maxInput.get())
                
            selectedFile = self._getSelectedFile()
            
            if index < 0:
                selectedFile.searchConds.append(cond)
            else:
                del selectedFile.searchConds[index]
                selectedFile.searchConds[index:index] = [cond]
                
            self._inflateSearchCondList(selectedFile)
            
            window.destroy()
        
        okBtn = Button(window, text="Confirm", width=7, command=_newCond)
        okBtn.grid(row=8, column=1, rowspan=1, columnspan=1, sticky=E, padx=5, pady=5)
        
        clsBtn = Button(window, text="Close", width=7, command=lambda: window.destroy())
        clsBtn.grid(row=8, column=2, rowspan=1, columnspan=1, sticky=E, padx=5, pady=5)
        
        
    def _popupJoinCondWindow(self, index=-1):
        if index < 0:
            cond = JoinSearchCondition("", "")
            toFileName = ""
        else:
            condTuple = self._getSelectedFile().joinCondTuples[index]
            cond = condTuple[0]
            toFileName = condTuple[1]
            
        window = Toplevel(self)
        
        title = Label(window, text="New Search Condition")
        title.grid(row=0, column=0, padx=5, pady=5, sticky=W + N)
        
        fileNamelabel = Label(window, text="Target Field Name: ")
        fileNamelabel.grid(row=1, column=0, padx=5, pady=5, sticky=W)
        
        fileVar = StringVar(window)
        fileNameinput = Combobox(window, textvariable=fileVar, values=self.fileList.get(0, END), width=30)
        fileNameinput.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        fromfieldLabel = Label(window, text="Field in From File: ")
        fromfieldLabel.grid(row=3, column=0, padx=5, pady=5, sticky=W)
        
        reader = loghandler.createReader(self._getSelectedFile().fileName)
        fromFields = reader.getFields()
        fromFieldVar = StringVar(window)
        fieldInput = Combobox(window, textvariable=fromFieldVar, values=fromFields, width=20)
        fieldInput.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        toFieldLabel = Label(window, text="Field in Target File: ")
        toFieldLabel.grid(row=4, column=0, padx=5, pady=5, sticky=W)
        
        toFields = []
        toFieldVar = StringVar(window)
        toFieldInput = Combobox(window, textvariable=toFieldVar, values=toFields, width=20)
        toFieldInput.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        def updateToFieldInput(evt):
            if fileVar.get() is not None and len(fileVar.get()) > 0:
                reader = loghandler.createReader(fileVar.get())
                toFields = reader.getFields()
                window.grid_slaves(4, 1)[0].grid_forget()
                toFieldInput = Combobox(window, textvariable=toFieldVar, values=toFields, width=20)
                toFieldInput.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky=W)
        
        fileNameinput.bind('<<ComboboxSelected>>', updateToFieldInput)
        
        # init value
        fileVar.set(toFileName)
        fromFieldVar.set(cond.fromField)
        updateToFieldInput(None)
        toFieldVar.set(cond.toField)
        
        def _newCond():
            '''create new condition
            '''
            cond = JoinSearchCondition(fromFieldVar.get(), toFieldVar.get())
            toFileName = fileVar.get()
            
            selectedFile = self._getSelectedFile()
            if index < 0:
                selectedFile.joinCondTuples.append((cond, toFileName))
                
            else:
                del selectedFile.joinCondTuples[index]
                selectedFile.joinCondTuples[index:index] = [(cond, toFileName)]
                
            self._inflateJoinCondList(selectedFile.joinCondTuples)
            
            window.destroy()
        
        okBtn = Button(window, text="Confirm", width=7, command=_newCond)
        okBtn.grid(row=6, column=1, rowspan=1, columnspan=1, sticky=E, padx=5, pady=5)
        
        clsBtn = Button(window, text="Close", width=7, command=lambda: window.destroy())
        clsBtn.grid(row=6, column=2, rowspan=1, columnspan=1, sticky=W, padx=5, pady=5)
        
        
    def _getSelectedFile(self):
        if self._getSelectedFileIndex() < 0:
            return None
        return self.fileModels[self._getSelectedFileIndex()]
    
    
    def _getSelectedFileIndex(self):
        return self.selectedFileIndex
    
    
    def _setSelectedFileIndex(self, index):
        self.selectedFileIndex = index
        if index >= 0:
            self.fileList.selection_set(index)
            
    def _getSelectedSearchCondIndex(self):
        if len(self.searchCondList.curselection()) > 0:
            return self.searchCondList.curselection()[0]
        return -1
    
    def _getSelectedJoinCondIndex(self):
        if len(self.joinCondList.curselection()) > 0:
            return self.joinCondList.curselection()[0]
        return -1
    
    def _getSelectedDisplayFieldIndex(self):
        if len(self.displayFieldList.curselection()) > 0:
            return self.displayFieldList.curselection()[0]
        return -1
    
    def _getSelectedNoDisplayFieldIndex(self):
        if len(self.noDisplayFieldList.curselection()) > 0:
            return self.noDisplayFieldList.curselection()[0]
        return -1
    
    def _getSelectedNoDisplayField(self):
        if len(self.noDisplayFieldList.curselection()) > 0:
            return self.noDisplayFieldList.get(self.noDisplayFieldList.curselection()[0])
        return None

if __name__ == "__main__":
    root = Tk()
    
    ui = LogUI(root)
    
    ui.mainloop() 
