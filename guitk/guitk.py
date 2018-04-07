#! /usr/bin/env python

"""Module: guitk.py
Author: Christopher Sean Hilton
  Date: 7-Apr, 2018 1900 EDT

GuiTk is a class that implements a decorator for a python
function. The decorated function executes as normal but in a gui
context with a Tkinter::Text() Widget as it's output.
"""


import time, sys

from Tkinter import *
from ttk import *

from Queue import Queue, Empty
from threading import Thread

class RedirectOutput(object):

    def __init__(self, outputQueue):
        self.isReadable = False
        self.isWritable = True
        self.OutputQueue = outputQueue
        self.Buffer = ""
    
    def write(self, msg):
        if self.isWritable:
            if msg == "\n":
                self.OutputQueue.put( ('STATUS', self.Buffer + "\n") )
                self.Buffer = ""
            else:
                lines = msg.split("\n")
                self.Buffer += lines[0]

                for l in lines[1:]:
                    self.OutputQueue.put('STATUS', self.Buffer + "\n")
                    self.Buffer = l
        else:
            raise ValueError("RedirectOutput() is closed.")

    def flush(self):
        if self.Buffer:
            self.OutputQueue.put( (STATUS, self.Buffer) )
            self.Buffer = ""                                  

    def close(self):
        self.isReadable = False
        self.isWritable = False

    def getvalue(self):
        return "\n".join(self.Output)


class GuiTk(Tk):

    def getIsRunning(self):

        return self._IsRunning.get()

    def setIsRunning(self, value):

        if value:
            self._IsRunning.set(True)
            return True
        else:
            self._IsRunning.set(False)
            return False            

    def watchIsRunning(self, *args, **kw):

        if self.getIsRunning():
            self.quitButton.state(['disabled'])
        else:
            self.quitButton.state(['!disabled'])
            
    def __init__(self, guiFn, **kw):

        Tk.__init__(self, **kw)

        self.__doc__ = guiFn.__doc__
        self.__name__ = guiFn.__name__
        self.__module__ = guiFn.__module__
        
        self._IsRunning = BooleanVar()
        self._IsRunning.set(0)
        self._IsRunning.trace("w", self.watchIsRunning)

        f = LabelFrame(self, text="Status Log")
        self.StatusLog = Text(f)
        self.StatusLog.pack(side=TOP, expand=True, fill=BOTH)
        f.pack(side=TOP, expand=True, fill=BOTH)

        f = Frame(self)
        self.quitButton = Button(f, text="Quit", command=self.quit)
        self.quitButton.pack(side=RIGHT, expand=False, fill=None)
        f.pack(side=TOP, expand=True, fill=X)
        
        self.GuiFn = guiFn

    def runUserFn(self, *args, **kw):

        self.ctrlQueue.put( ('START', None) )
        resultCode = self.GuiFn(*args, **kw)
        self.ctrlQueue.put( ('FINISHED', resultCode) )
            

    def checkUserFn(self):

        while True:
            try:
                t = self.ctrlQueue.get(False)

            except Empty:
                break

            msg = t[0]
            if msg == "START":
                self.setIsRunning(True)

            elif msg == "FINISHED":
                self.workerThread.join()
                self.setIsRunning(False)
                self.resultCode = t[1]

            elif msg == "STATUS":
                statusMsg = t[1]
                self.StatusLog.insert(END, statusMsg + "\n")
                    
        if self.getIsRunning():
            self.after(500, self.checkUserFn)

        
    def startUserFn(self):

        args = self.callArgs
        kw = self.callKw
        self.workerThread = Thread(name="WorkerThread", group=None, target=self.runUserFn, args=self.callArgs, kwargs=self.callKw)
        self.workerThread.start()
        self.checkUserFn()
        
    def __call__(self, *args, **kw):

        self.callArgs = args
        self.callKw = kw

        try:
            self.ctrlQueue = Queue()

            self.RedirectOutput = RedirectOutput(self.ctrlQueue)
            self.oldStdout = sys.stdout
            sys.stdout = self.RedirectOutput

            self.after_idle(self.startUserFn)
            self.mainloop()

        finally:
            sys.stdout = self.oldStdout
        
        return self.resultCode


if __name__ == '__main__':
    
    @GuiTk
    def wrapped_fn(*args, **kw):

        '''Doc string.'''
        
        print "wrapped_fn(args=%s, kw=%s)" % (args, kw)
        print "Sleeping..."
        for i in range(0, 30):
            time.sleep(1)
            print "Countup: %d..." % i
        
        print "Finished"
        print
        return 0

    
    def main():
        print wrapped_fn.__doc__
        print wrapped_fn.__name__
        print wrapped_fn.__module__

        wrapped_fn("foo", "bar", "baz", a="bimble", b="bumble")

    main()
