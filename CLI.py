import tkinter  # tkinter with small t for python 3
#import ttk  # nicer widgets

root = tkinter.Tk()

mainFrame = tkinter.Frame(root)
mainFrame.grid()
button = tkinter.Button(mainFrame, text="dummy")
button.grid()


entryFrame = tkinter.Frame(mainFrame, width=454, height=20)
entryFrame.grid(row=0, column=1)

# allow the column inside the entryFrame to grow    
entryFrame.columnconfigure(0, weight=10)  

# By default the frame will shrink to whatever is inside of it and 
# ignore width & height. We change that:
entryFrame.grid_propagate(False)
# as far as I know you can not set this for x / y separately so you
# have to choose a proper height for the frame or do something more sophisticated

# input entry
inValue = tkinter.StringVar()
inValueEntry = tkinter.Entry(entryFrame, textvariable=inValue)
inValueEntry.grid(sticky="we")


root.mainloop()