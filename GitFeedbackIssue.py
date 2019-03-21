from GitHubApi import *
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import tkinter.ttk as ttk
import getpass

def submitIssue():
    gitApi = GitHubApi(owner='minstack', repo='VendChannelEvents', token='')
    gitApi.createIssue(title=f"[Feedback]{txtuser.get()}", body=f"{txtfeedback.get()}\n{txtemail.get()}", assignees=["minstack"], )


root = Tk()
root.geometry("300x400")
root.call('tk','scaling', 2.0)

lbluser = Label(root, text="User")
lblemail = Label(root, text="Email")
lblfeedback = Label(root, text="Feedback")
lbllabel = Label(root, text="Type")


txtuser = Entry(root, width=100)
txtuser.insert(0, getpass.getuser())
txtemail = Entry(root, width=100)
txtfeedback = Text(root, width=100, bd=1)
#txtfeedback = ScrolledText(root, width=100, bd=1)
cboLabel = ttk.Combobox(root, values=("Feedback", "Enhancement", "Question", "Bug"))

lbluser.pack(fill=X)
txtuser.pack(padx=5)
lblemail.pack(fill=X)
txtemail.pack(padx=5)
lbllabel.pack(fill=X)
cboLabel.pack(padx=5, fill=X)
lblfeedback.pack(fill=X)
txtfeedback.pack(padx=5)


btnSubmit = Button(root, text="Submit", command=submitIssue)
btnSubmit.pack()

root.mainloop()
