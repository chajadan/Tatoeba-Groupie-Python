import pickle
import wx

def pickleLoad(filepath):
    infile = open(filepath, "rb")
    outObject = pickle.load(infile)
    infile.close()
    return outObject

def pickleDump(filepath, outObject):
    outfile = open(filepath, "wb")
    pickle.dump(outObject, outfile)
    outfile.close()
    
class LabeledCtrl(wx.Panel):
    def __init__(self, parent, id, ctrl, labelText = ""):
        wx.Panel.__init__(self, parent, id)
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        self.label = wx.StaticText(self, -1, labelText, style = wx.ALIGN_CENTER_VERTICAL)
        self.ctrl = ctrl
        self.ctrl.Reparent(self)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.label, flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, border = 5)
        self.sizer.Add(self.ctrl, flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, border = 5)
        self.SetSizer(self.sizer)
    
class ChoiceWithOther(wx.Choice):
    def __init__(self, parent, id, choices = [], otherChoiceString = "Other...", default = "", sorted = True, validator = None):
        self.choices = [] + choices
        if otherChoiceString in self.choices:
            self.choices.remove(otherChoiceString)
        self.sorted = sorted
        if self.sorted:
            self.choices.sort()
        if validator is None:
            wx.Choice.__init__(self, parent, id, choices = self.choices)
        else:
            wx.Choice.__init__(self, parent, id, choices = self.choices, validator = validator)
        self.otherChoiceString = otherChoiceString
        self.AddOtherChoiceEntry()
        if len(default) > 0:
            self.SetStringSelection(default)
        self.Bind(wx.EVT_CHOICE, self.OnChoose)

    def OnChoose(self, event):
        if self.GetStringSelection() == self.otherChoiceString:
            dlg = wx.TextEntryDialog(self, 'What new choice do you want?',
                'New Choice')
            if dlg.ShowModal() == wx.ID_OK:
                self.DoAddNewChoice(dlg.GetValue())
            dlg.Destroy()
        event.Skip()

    def DoAddNewChoice(self, newChoice):
        if newChoice not in self.choices:
            self.choices.append(newChoice)
            self.Clear()
            if self.sorted:
                self.choices.sort()
            self.AppendItems(self.choices)
            self.AddOtherChoiceEntry()
            self.SetStringSelection(newChoice)
        else:
            wx.MessageBox("That choice already exists.", "Choice Exists")

    def AddOtherChoiceEntry(self):
            self.Append(self.otherChoiceString)