from tkinter import *
import tkinter.ttk as ttk
import threading
from tkinter.filedialog import askopenfilename
import ControlUtil
from tkinter import messagebox
#from tkFileDialog import askopenfilename

class VendChannelEventsGUI:

    def __init__(self, callback, root=None):
        """
            Constructor for the GUI. The delete function passed is the entry
            function in the calling class/module to bind to the delete button.
        """
        self.TEXT_BOXES = []
        self.BUTTONS = []
        self.__callback = callback
        self.root = root
        self.title = "Vend Channel Events"
        if self.root is None:
            self.root = Tk()
            self.root.geometry("1420x700")
            self.root.call('tk','scaling', 2.0)
        #self.root.geometry("650x450")
            self.root.minsize(650,450)
        #self.root.resizable(0,0)
            self.root.title(self.title)
            self.root.pack_propagate(0)

        header = Label(self.root, text="Channel Events", bd=1, font="San-Serif 18 bold", bg="#41B04B", fg="white")
        header.pack(side=TOP, anchor=W, fill=X)

        # container for the main widgets
        mainFrame = Frame(self.root)


        self.__loadUserInputs__(mainFrame)
        self.__loadButtons__(mainFrame)
        self.__loadChannelResultListBox__(mainFrame)
        #self.__loadCheckListControl__(mainFrame)
        self.__loadMessageControls__(mainFrame)
        mainFrame.pack(padx=30, pady=10, fill=BOTH, expand=1)


    def __loadUserInputs__(self, mainFrame):
        """
            Loads the user input controls onto the given parent frame
        """
        lblStorePrefix = Label(mainFrame, text="Store Prefix:", font="Helvetica 14 bold")
        lblStorePrefix.grid(row=1, column=0, sticky=E)

        lblToken = Label(mainFrame, text="Token:", font="Helvetica 14 bold")
        lblToken.grid(row=2, column=0, sticky=E)

        #textboxes
        self.txtPrefix = Entry(mainFrame)
        self.txtToken = Entry(mainFrame)
        self.txtPrefix.grid(row=1,column=1, sticky=W)
        self.txtToken.grid(row=2,column=1, sticky=W)

        lblLevel = Label(mainFrame, text="Level:", font="Helvetica 14 bold")
        lblLevel.grid(row=3, column=0, sticky=E)
        self.strLevel = StringVar()
        self.cboLevel = ttk.Combobox(mainFrame, values = ("all", "info", "warning"), state='readonly', textvariable=self.strLevel, width=8)
        self.cboLevel.set("all")
        self.cboLevel.grid(row=3, column=1, sticky=W)

        lblEntityType = Label(mainFrame, text="Entity Type:", font="Helvetica 14 bold")
        lblEntityType.grid(row=1, column=1, sticky=E)
        self.strEntityType = StringVar()
        self.cboEntityType = ttk.Combobox(mainFrame, values = ("all", "product","product_inventory", "product_ingress", "sale"), state='readonly', textvariable=self.strEntityType, width=10)
        self.cboEntityType.set("product")
        self.cboEntityType.grid(row=1, column=2, sticky=W)

        lblEntityid = Label(mainFrame, text="Entity ID:", font="Helvetica 14 bold")
        lblEntityid.grid(row=2, column=1, sticky=E)
        self.txtEntityId = Entry(mainFrame, width=25)
        self.txtEntityId.grid(row=2, column=2, sticky=W)

        ControlUtil.addControl(self.TEXT_BOXES, self.txtPrefix, self.txtToken)

    def __loadButtons__(self, mainFrame):
        """
            Loads the button controls onto the given parent frame
        """
        btnframe = Frame(mainFrame)
        self.btnGetChannels = Button(btnframe, text="Get Channel Events", command=self.startThread)
        self.btnGetChannels.pack(side=RIGHT, padx=5)
        self.btnReset = Button(btnframe, text="Reset", command=self.reset)
        self.btnReset.pack()
        btnframe.grid(row=3, column=2, padx=0, pady=10, sticky=W)

        self.btnExportCsv = Button(mainFrame, text="Export CSV")
        self.btnExportCsv.grid(row=3, column=4, pady=10, sticky=E)

        ControlUtil.addControl(self.BUTTONS, self.btnGetChannels, self.btnReset)

    def __loadChannelResultListBox__(self, mainFrame):
        """
            Loads the CSV file controls onto the given parent frame
        """
        self.channelEvents = []
        self.chanEventDict = {}

        headings = ["created_at", "action", "entity_type", "entity_id", "unwrapped_error"]

        widths = {
            "created_at" : 160,
            "action" : 280,
            "entity_type" : 150,
            "entity_id" : 300,
            "unwrapped_error" : 450
        }

        frame = Frame(mainFrame)
        frame.grid(row=7, column=0, columnspan=5,rowspan=5, padx=0, pady=5)

        self.channelView = ttk.Treeview(frame, show="headings", selectmode="browse", height=6)
        #self.channelView.grid(row=7, column=0, columnspan=5,rowspan=5, padx=0, pady=5)
        self.channelView.pack(side='left')

        vsb = ttk.Scrollbar(frame, orient='vertical', command=self.channelView.yview)
        vsb.pack(side='right', fill='y')

        self.channelView.configure(yscrollcommand=vsb.set)

        self.channelView['columns'] = headings

        for h in headings:
            self.channelView.heading(h, text=h)
            self.channelView.column(h, width=widths[h], anchor=NW)

        style = ttk.Style()
        style.configure('Treeview', rowheight=80)
        style.configure('Treeview.Heading', font=(None, 15))


    def __loadCheckListControl__(self, mainFrame):
        """
            Loads the check list controls onto the given parent frame
        """
        checklistFrame = Frame(mainFrame, width=200, height=200, bd=1)
        #Label(mainFrame, text="Checklist", font="Helvetica 14 bold").grid(row=0, column=3)
        checklistFrame.grid(row=3, column=1)

        self.paConfirmation = BooleanVar()
        self.tokenExpiry = BooleanVar()
        self.chkPaConfirm = Checkbutton(checklistFrame, text="PA Confirmation", variable=self.paConfirmation)
        self.chkPaConfirm.grid(row=1, sticky=W)
        self.chkTokenExpiry = Checkbutton(checklistFrame, text="Token Expiry Set", variable=self.tokenExpiry)
        self.chkTokenExpiry.grid(row=2, sticky=W)

        ControlUtil.addControl(self.BUTTONS, self.chkPaConfirm, self.chkTokenExpiry)

    def __loadMessageControls__(self, mainFrame):
        """
            Loads the status/result message controls onto the given parent frame
        """
        self.statusMsg = StringVar()
        self.lblStatus = Label(self.root, textvariable=self.statusMsg, bd=1, relief=SUNKEN, anchor=W, bg="#3A4953", fg="white", font="Helvetica 14 italic")
        self.lblStatus.pack(side=BOTTOM, fill=X)

        resultFrame = Frame(mainFrame)
        #resultFrame.grid(row=6,column=0, columnspan=3, rowspan=4)

        self.resultText = StringVar()
        resultLabel = Message(resultFrame, textvariable=self.resultText,font="Helvetica 16", width=500)
        #resultLabel.pack(pady=15)

    def __switchEntityType(self):
        self.btnGetChannels.config(text="Delete {0}".format(self.entityType.get()))
        # switch the process function

    def reset(self):
        """
            Function to reset the state of the GUI.
        """
        self.setStatus("")
        self.setReadyState()
        ControlUtil.clearTextBoxes(self.TEXT_BOXES)
        #self.paConfirmation.set(0)
        #self.tokenExpiry.set(0)
        #del self.csvList[:]
        #self.csvListbox.delete(0,END)
        #self.csvFileDict = {}
        #self.setResult("")

    def deleteFileFromList(self):
        """
            Function to delete the selected file from the CSV listbox as well
            as the corresponding list variable and dictionary.
        """
        selected = self.csvListbox.curselection()

        if selected:
            self.csvListbox.delete(selected[0])
            self.csvFileDict.pop(self.csvList[selected[0]], None)
            del self.csvList[selected[0]]

    def setEntityType(self, entity):
        radio = self.entityToRadio[entity]

        radio.invoke()

    def entriesHaveValues(self):
        """
            Returns true/false whether the required input values have been
            provided
        """
        return ControlUtil.entriesHaveValues(self.TEXT_BOXES)

    def getFilePath(self, filename):
        return self.csvFileDict.get(filename, None)

    def startThread(self):
        """
            Main function to start the thread to the provided function of the
            controller that creates/calls this class.
        """
        self.setStatus("")
        self.setDeletingState()
        thr = threading.Thread(target=self.__callback, args=([self]), kwargs={})

        thr.start()
        #self.setReadyState()

    def getEntityId(self):
        return self.txtEntityId.get().strip()

    def getEntityType(self):
        return self.strEntityType.get()

    def resetTreeview(self):
        self.channelView.delete(*self.channelView.get_children())

    def isChecklistReady(self):
        """ Returns whether the checklist is completed. """
        return self.tokenExpiry.get() and self.paConfirmation.get()

    def getEventLevel(self):
        return self.strLevel.get()

    def openFile(self):
        """
            When the + button is clicked to add CSV files, opens the file opener
            dialog to retrieve the file.
        """
        filepath = askopenfilename(parent=self.root)

        if filepath:
            self.addCsvFile(filepath.split('/')[-1], filepath)

    def disableCsvButtons(self):
        ControlUtil.setControlState([self.btnOpenCsvDialog, self.btnDeleteFile], DISABLED)

    def addRowsToTreeview(self, zippedList):

        index = iid = 0
        for row in zippedList:
            self.channelView.insert('', index, iid, values=row)
            index = iid = index + 1

    def addEventToList(self, eventLine):
        #tempArr = filepath.split("/")

        #filename = tempArr[len(tempArr)-1]

        self.channelEvents.append(eventLine)
        self.channelBox.insert(END, eventLine)
        '''
        self.csvFileDict[filename] = filepath
        self.csvList.append(filename)

        self.csvListbox.insert(END, filename)'''

    def setPrefix(self, prefix):
        self.txtPrefix.delete(0, END)
        self.txtPrefix.insert(0, prefix)

    def getPrefix(self):
        return self.txtPrefix.get().strip()

    def getToken(self):
        return self.txtToken.get().strip()

    def setToken(self, token):
        self.txtToken.delete(0, END)
        self.txtToken.insert(0, token)

    def setStatus(self, msg):
        """ Sets the status message to the provided string. """
        self.statusMsg.set(msg)

    def setResult(self, msg):
        """ Sets the result variable to the given string. """
        self.resultText.set(msg)
        self.btnReset.config(state=NORMAL)

    def getSelectedType(self):
        return self.entityType.get()

    def setDeletingState(self):
        """ Sets all the controls to disabled state to prevent any multi-clicks"""
        ControlUtil.setControlState(self.TEXT_BOXES, DISABLED)
        ControlUtil.setControlState(self.BUTTONS, DISABLED)
        self.root.update()

    def setReadyState(self):
        """ Resets all controls back to normal state."""
        ControlUtil.setControlState(self.TEXT_BOXES, NORMAL)
        ControlUtil.setControlState(self.BUTTONS, NORMAL)
        self.root.update()

    def setExportCsvCommand(self, function):
        self.btnExportCsv.configure(command=function)

    def main(self):
        """ Main loop for this GUI. """
        self.root.mainloop()

    def showMessageBox(self, title, message):
        messagebox.showinfo(title, message)

    def showError(self, title, message):
        messagebox.showerror(title, message)

    def setVersion(self, version):
        self.root.title(f"{self.title} v{version}")
