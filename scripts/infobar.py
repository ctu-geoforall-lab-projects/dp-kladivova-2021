#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 01:58:05 2020

@author: linwe
"""


import wx
import wx.aui
import wx.lib.agw.aui as aui
_ = wx.GetTranslation


class InfoBar(wx.PyControl):
    """
    An info bar is a transient window shown at top or bottom of its parent window to display
    non-critical information to the user.
    """

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, name='InfoBar'):
        """
        Default class constructor.
        """

        wx.PyControl.__init__(self, parent, id, pos, size, style|wx.BORDER_NONE, name=name)

        self.SetInitialSize(size)
        self.Init()

        # calling Hide() before Create() ensures that we're created initially
        # hidden
        self.Hide()

        # use special, easy to notice, colours
        colBg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOBK)
        self.SetBackgroundColour(colBg)
        self.SetOwnForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOTEXT))

        # create the controls: icon,text and the close button to dismiss the message
        if wx.Platform == '__WXGTK__':
            bmp = wx.ArtProvider.GetBitmap(wx.ART_CLOSE, wx.ART_BUTTON)
        self._bclose = wx.BitmapButton(self, wx.ID_ANY, bmp, style=wx.BORDER_NONE)

        self._bclose.SetBackgroundColour(colBg)
        self._bclose.SetToolTipString(_("Hide this notification message."))

        # the icon is not shown unless it's assigned a valid bitmap
        self._icon = wx.StaticBitmap(self, wx.ID_ANY, wx.NullBitmap)
        self._text = wx.StaticText(self, wx.TE_MULTILINE, "")

        # LAYOUT
        sizer = wx.BoxSizer(wx.VERTICAL)

        # icon, text, close button
        informationBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        informationBoxSizer.Add(self._icon, proportion=0,
                  flag=wx.TOP | wx.ALL, border=10)
        informationBoxSizer.Add(self._text, proportion=1,
                  flag=wx.EXPAND | wx.ALL, border=5)
        informationBoxSizer.AddStretchSpacer()
        informationBoxSizer.Add(self._bclose, proportion=0,
                  flag=wx.TOP | wx.ALL, border=5)

        self.buttonBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonBoxSizer.AddStretchSpacer(1)

        sizer.Add(informationBoxSizer, proportion=1, flag=wx.EXPAND | wx.ALL)
        sizer.Add(self.buttonBoxSizer, proportion=0, flag=wx.EXPAND | wx.ALL)

        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.OnCloseButton, self._bclose)

    def Init(self):

        self.FLAGS2ART = {wx.ICON_NONE        : wx.ART_MISSING_IMAGE,
                          wx.ICON_INFORMATION : wx.ART_INFORMATION,
                          wx.ICON_QUESTION    : wx.ART_QUESTION,
                          wx.ICON_WARNING     : wx.ART_WARNING,
                          wx.ICON_ERROR       : wx.ART_ERROR
                          }
        self._icon = None
        self._text = None
        self._bclose = None

    def UpdateParent(self):
        """
        Updates the parent layout appearance.
        """
        
        parent = self.GetParent()
        parent.Layout()

    def DoHide(self):
        """ Hides this InfoBar."""

        self.Hide()
        handler = self.GetParent().GetEventHandler()
        managers = (aui.AuiManager, wx.aui.AuiManager)
        
        if not isinstance(handler, managers):
            self.UpdateParent()
        else:
            pane = handler.GetPane(self)
            pane.Show(False)
            handler.Update()

    def DoShow(self):
        """ Shows this InfoBar."""

        self.GetParent().Freeze()
        
        wx.PyControl.Show(self)
        
        # adjust the parent layout to account for us
        self.UpdateParent()
        
        # reset the flag back before really showing the window or it wouldn't be
        # shown at all because it would believe itself already visible
        wx.PyControl.Show(self, False)
        self.GetParent().Thaw()
        
        # finally do really show the window.
        self.Show()

        handler = self.GetParent().GetEventHandler()
        managers = (aui.AuiManager, wx.aui.AuiManager)

        if isinstance(handler, managers):
            pane = handler.GetPane(self)
            pane.Show(True)
            handler.Update()

    def ShowMessage(self, msg, flags=wx.ICON_INFORMATION):
        """
        Show a message in the bar.

        If the bar is currently hidden, it will be shown. Otherwise its message will be updated in place.
        """

        # first update the controls
        icon = flags & wx.ICON_MASK
        
        if not icon or icon == wx.ICON_NONE:
            self._icon.Hide()
            
        else: # do show an icon
            self._icon.SetBitmap(wx.ArtProvider.GetBitmap(self.FLAGS2ART[flags], wx.ART_BUTTON))
            self._icon.Show()
            
        # notice the use of EscapeMnemonics() to ensure that "&" come through
        # correctly
        self._text.SetLabel(wx.PyControl.EscapeMnemonics(msg))
        
        # then show this entire window if not done yet
        if not self.IsShown():
            self.DoShow()
        else: # we're already shown
            # just update the layout to correspond to the new message
            self.Layout()

    def Dismiss(self):
        """
        Hides the InfoBar window.
        """
        
        self.DoHide()

    def AddButton(self, btnid, label, bitmap=wx.NullBitmap):
        """
        Adds a button to be shown in the info bar.
        """
        sizer = self.GetSizer()

        if not sizer:
            raise Exception("must be created first")

        button = wx.Button(self, btnid, label)

        self.buttonBoxSizer.Add(button, proportion=0,
                                flag=wx.ALIGN_CENTER_VERTICAL)


        if self.IsShown():
            self.UpdateParent()

    def OnCloseButton(self, event):
        """
        Default event handler for the `Close` button.
        """
        
        self.DoHide()


class MyFrame(wx.Frame):

    def __init__(self, parent):

        wx.Frame.__init__(self, parent, -1, 'Information InfoBar')

        self._infoBar = InfoBar(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._infoBar, proportion=2, flag=wx.EXPAND | wx.ALL)

        panel = wx.Panel(self)
        sizer.Add(panel, proportion=1)

        self.SetSizer(sizer)

        # use special, easy to notice, colours
        self._infoBar.SetBackgroundColour(wx.Colour(255, 248, 220))
        self._infoBar.SetOwnForegroundColour(wx.Colour(10, 10, 10))

        self._infoBar.AddButton(wx.NewId(), 'Look at video')
        self._infoBar.AddButton(wx.NewId(), 'Check documentation')
        self._infoBar.ShowMessage("Hello GRASS GIS user, you are now in demolocation. To import your own data, first, define its coordinate system through creating a newlocation. Then you can create your mapset, switch to it (make it current) and import data. If you are still confused about GRASS GIS data hiearchy, please watch the following video..."
        , wx.ICON_INFORMATION)


class MyFrame2(wx.Frame):

    def __init__(self, parent):

        wx.Frame.__init__(self, parent, -1, 'Warning InfoBar')

        self._infoBar = InfoBar(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._infoBar, proportion=2, flag=wx.EXPAND | wx.ALL)

        panel = wx.Panel(self)
        sizer.Add(panel, 1, wx.EXPAND)
        
        self.SetSizer(sizer)

        # use special, easy to notice, colours
        self._infoBar.SetBackgroundColour(wx.Colour(205, 92, 92))
        self._infoBar.SetOwnForegroundColour(wx.Colour(255, 255, 255))

        self._infoBar.ShowMessage("Last used mapset was not found. GRASS GIS started in Demolocation."
        , wx.ICON_WARNING)


class MyFrame3(wx.Frame):

    def __init__(self, parent):

        wx.Frame.__init__(self, parent, -1, 'Question InfoBar')

        self._infoBar = InfoBar(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._infoBar, proportion=2, flag=wx.EXPAND | wx.ALL)

        panel = wx.Panel(self)
        sizer.Add(panel, 1, wx.EXPAND)
        
        self.SetSizer(sizer)

        # use special, easy to notice, colours
        self._infoBar.SetBackgroundColour(wx.Colour(224, 255, 255))
        self._infoBar.SetOwnForegroundColour(wx.Colour(10, 10, 10))

        self._infoBar.AddButton(wx.NewId(), 'Create location')
        self._infoBar.ShowMessage("Do you want to create new Location?"
        , wx.ICON_QUESTION)

app = wx.PySimpleApp()

frame = MyFrame(None)
app.SetTopWindow(frame)
frame.Show()

frame2 = MyFrame2(None)
app.SetTopWindow(frame2)
frame2.Show()

frame3 = MyFrame3(None)
app.SetTopWindow(frame3)
frame3.Show()

app.MainLoop()



