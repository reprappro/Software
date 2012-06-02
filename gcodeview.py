#!/usr/bin/env python
import os
try:
    import wx
except:
    print _("WX is not installed. This program requires WX to run.")
    raise
import sys, glob, time, threading, traceback, gviz, traceback, cStringIO, subprocess
try:
    os.chdir(os.path.split(__file__)[0])
except:
    pass
StringIO=cStringIO

thread=threading.Thread
winsize=(800,500)

class GCodeWindow(wx.Frame):
    def __init__(self, filename=None,size=winsize):
        self.filename=filename
        wx.Frame.__init__(self,None,title="GCode Viewer",size=size);
        self.panel=wx.Panel(self,-1,size=size)
        self.panel.SetBackgroundColour("white")
        self.build_dimensions_list = self.get_build_dimensions('140x140x100+0+0+0')
        self.f=None
        self.popmenu()
        self.popwindow()

    def popmenu(self):
        self.menustrip = wx.MenuBar()
        # File menu
        m = wx.Menu()
        self.Bind(wx.EVT_MENU, self.loadfile, m.Append(-1,"&Open..."," Opens file"))
        self.SetMenuBar(self.menustrip)

    def popwindow(self):
        self.gviz=gviz.window([],
            build_dimensions=self.build_dimensions_list,
            grid=(10,50),
            extrusion_width=0.5)
        #self.gviz.showall=1
        self.gwindow=gviz.window([],
            build_dimensions=self.build_dimensions_list,
            grid=(10,50),
            extrusion_width=0.5)
        #self.gviz.Bind(wx.EVT_LEFT_DOWN,self.showwin)
        self.gviz.Bind(wx.EVT_CLOSE,lambda x:self.gwindow.Hide())
        #self.gviz.Bind(wx.EVT_LEFT_DOWN,self.showwin)
        self.loadbtn=wx.Button(self.panel,-1,"Load file")
        self.loadbtn.Bind(wx.EVT_BUTTON,self.loadfile)
        vcs=wx.BoxSizer(wx.VERTICAL)
        vcs.Add(self.loadbtn)
        vcs.Add(self.gviz,1,flag=wx.SHAPED)
        self.panel.SetSizer(vcs)
        self.status=self.CreateStatusBar()

    def showwin(self,event):
        if(self.f is not None):
            self.gwindow.Show(True)

    def loadfile(self,event,filename=None):
        basedir = "."
        try:
            basedir=os.path.split(self.filename)[0]
        except:
            pass
        dlg=wx.FileDialog(self,"Open file to print",basedir,style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        dlg.SetWildcard("GCODE files (;*.gcode;*.gco;*.g;)")
        if(filename is not None or dlg.ShowModal() == wx.ID_OK):
            if filename is not None:
                name=filename
            else:
                name=dlg.GetPath()
            if not(os.path.exists(name)):
                self.status.SetStatusText("File not found!")
                return
            path = os.path.split(name)[0]
            if name.lower().endswith(".gcode"):
                self.filename=name
                of=open(self.filename)
                self.f=[i.replace("\n","").replace("\r","") for i in of]
                of.close
                self.status.SetStatusText("Loaded " + name + ", %d lines" % (len(self.f),))
                threading.Thread(target=self.loadviz).start()

    def loadviz(self):
        self.gviz.p.clear()
        self.gwindow.p.clear()
        self.gviz.p.addfile(self.f)
        #print "generated 2d view in %f s"%(time.time()-t0)
        #t0=time.time()
        self.gwindow.p.addfile(self.f)
        #print "generated 3d view in %f s"%(time.time()-t0)
        #self.gviz.showall=1
        wx.CallAfter(self.gviz.Refresh)

    def kill(self,e):
        try:
            self.gwindow.Destroy()
        except:
            pass
        self.Destroy()

    def get_build_dimensions(self,bdim):
        import re
        # a string containing up to six numbers delimited by almost anything
        # first 0-3 numbers specify the build volume, no sign, always positive
        # remaining 0-3 numbers specify the coordinates of the "southwest" corner of the build platform
        # "XXX,YYY"
        # "XXXxYYY+xxx-yyy"
        # "XXX,YYY,ZZZ+xxx+yyy-zzz"
        # etc
        bdl = re.match(
        "[^\d+-]*(\d+)?" + # X build size
        "[^\d+-]*(\d+)?" + # Y build size
        "[^\d+-]*(\d+)?" + # Z build size
        "[^\d+-]*([+-]\d+)?" + # X corner coordinate
        "[^\d+-]*([+-]\d+)?" + # Y corner coordinate
        "[^\d+-]*([+-]\d+)?"   # Z corner coordinate
        ,bdim).groups()
        defaults = [200, 200, 100, 0, 0, 0]
        bdl_float = [float(value) if value else defaults[i] for i, value in enumerate(bdl)]
        return bdl_float

if __name__ == '__main__':
    app = wx.App(False)
    main = GCodeWindow()
    main.Show()
    try:
        app.MainLoop()
    except:
        pass

