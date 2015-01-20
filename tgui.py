import os
import sys
import sqlite3
from multiprocessing.pool import ThreadPool
from chajLib import *

# wxPython related imports
import wx
from wx.lib.agw import ultimatelistctrl as ulc
import wx.lib.agw.hyperlink as hl
import wx.adv
from numpy import minimum

class StatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(1)
        self.SetStatusWidths([-1])
        
class ExportOptionsDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent)
        self.SetTitle("Export Options")
        
        explanationString = 'It is recommended that you limit export to only groupies that have relatively few translations within any one language. The "ideal" situation is one sentence per language, but up to 2 is often easily worked with. Otherwise, many translations tends to indicate indirect translations that overflowed into several distinct sentences -- not really a groupie!!\n\nPlease specific the minimum and maximum sentence count per language that will determine which groupies get exported.'

        self.explanation = wx.StaticText(self, -1, explanationString)
        self.explanation.Wrap(400)
        self.minimum = ChoiceWithOther(self, -1, choices = ["1", "2", "3", "4", "5"], default = "1")
        self.labeledMinimum = LabeledCtrl(self, -1, self.minimum, "Minimum required: ")
        self.maximum = ChoiceWithOther(self, -1, choices = ["1", "2", "3", "4", "5"], default = "2")
        self.labeledMaximum = LabeledCtrl(self, -1, self.maximum, "Maximum allowed: ")
        
        self.okButton = wx.Button(self, wx.ID_OK, "OK")
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        
        self.minMaxBox = wx.BoxSizer(wx.HORIZONTAL)
        self.minMaxBox.Add(self.labeledMinimum, 0, wx.ALL, border = 5)
        self.minMaxBox.Add(self.labeledMaximum, 0, wx.ALL, border = 5)
        
        self.submitBox = wx.BoxSizer(wx.HORIZONTAL)
        self.submitBox.Add(self.okButton, 0, wx.ALL, border = 5)
        self.submitBox.Add(self.cancelButton, 0, wx.ALL, border = 5)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.explanation, 0, wx.ALL, border = 5)
        self.sizer.Add(self.minMaxBox, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.AddSpacer(10)
        self.sizer.Add(self.submitBox, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        self.SetSizerAndFit(self.sizer)
        
        
class GroupieGrid(ulc.UltimateListCtrl):
    def __init__(self, parent):
        ulc.UltimateListCtrl.__init__(self, parent, -1, agwStyle=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | ulc.ULC_NO_HIGHLIGHT | ulc.ULC_SHOW_TOOLTIPS | ulc.ULC_HAS_VARIABLE_ROW_HEIGHT)
        self.Freeze()
        
        self.InsertColumn(0, "Language")
        self.InsertColumn(1, "TatId")
        self.InsertColumn(2, "Sentence")
        
        self.SetColumnWidth(0, 125)
        self.SetColumnWidth(1, 50)
        self.SetColumnWidth(2, 500)
        
        self.Thaw()
        self.Update()
    
class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size = (750, 400))
        self.conn = None
        self.langs = None
        self.fullLanguageNames = None
        self.chosenLanguageIds = None
        self.groupies = None
        self.SetTitle("Tatoeba Groupie")
        self.CreateMenu()
        self.status = StatusBar(self)
        self.SetStatusBar(self.status)
        icon = wx.Icon('tatoebaGroupie.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
        self.picker = wx.Button(self, -1, "Choose Languages...")
        self.picker.Disable()
        self.Bind(wx.EVT_BUTTON, self.SelectLanguages, self.picker)
        
        self.groupieList = wx.Choice(self, -1)
        self.Bind(wx.EVT_CHOICE, self.ShowGroupie, self.groupies)
        self.groupieList.Disable()
        
        self.control = wx.BoxSizer(wx.HORIZONTAL)
        self.control.Add(self.picker, 0, wx.ALL, border = 5)
        self.control.Add(self.groupieList, 0, wx.ALL, border = 5)
        
        self.groupieGrid = GroupieGrid(self)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.control, 0)
        self.sizer.Add(self.groupieGrid, 1, flag = wx.EXPAND)
        self.SetSizer(self.sizer)
        
    def Initialize(self):
        img = wx.Bitmap('groupieSplash.jpg', wx.BITMAP_TYPE_JPEG)
        self.splash = wx.adv.SplashScreen(img, wx.adv.SPLASH_CENTER_ON_PARENT | wx.adv.SPLASH_NO_TIMEOUT, 6000, self)
        wx.Yield()
        
        wx.BeginBusyCursor()        
        self.OpenDatabase()
        if self.DatabaseComplete():
            self.LoadData()
        else:
            wx.EndBusyCursor()
            self.splash.Destroy()
            #wx.MessageBox("To begin, use the data menu to select the location of the Tatoeba data files to process.", "Step One", wx.OK | wx.ICON_INFORMATION)
            wx.MessageBox("Could not locate complete database of Tatoeba sentences in groupies. Please make sure you have the correct tatoebaGroupie.sqlite3 file in the same folder as the tgui.py file.")             
        
    def LoadData(self):
        pool = ThreadPool(processes=1)
        self.async_result = pool.apply_async(AsyncLoadData, (), callback = self.LoadDataComplete)
    
    def LoadDataComplete(self, resultTuple):
        self.langs = resultTuple[0]
        self.groupies = resultTuple[1]
        self.splash.Destroy()
        wx.EndBusyCursor()
        self.Update()
        self.picker.Enable()
        
    def ShowGroupie(self, event):
        groupieId = None
        try:
            groupieId = int(self.groupieList.GetStringSelection())
        except:
            return
                
        self.SetStatusText("Beginning groupie display...", number=0)
        self.groupieGrid.DeleteAllItems()

        c = self.conn.cursor()
        if not self.chosenLanguageList or len(self.chosenLanguageList) == 0:
            c.execute("select sentence, langId, sentenceId from sentences where groupieId = ? order by langId", (groupieId,))
        else:
            c.execute("select sentence, langId, sentenceId from sentences where groupieId = ? and langId in (" + self.chosenLanguageList + ") order by langId", (groupieId,))
        
        for record in c:
            sentence = record[0]
            langId = record[1]
            tatoebaId = str(record[2])
            langInfo = self.langs.get(langId)
            if not langInfo:
                langInfo = ["---", "---"]
            index = self.groupieGrid.InsertStringItem(sys.maxsize, langInfo[1])
            hyperlink = hl.HyperLinkCtrl(self.groupieGrid, wx.ID_ANY, tatoebaId, URL="http://tatoeba.org/eng/sentences/show/" + tatoebaId)
            self.groupieGrid.SetItemWindow(index, 1, hyperlink)
            self.groupieGrid.SetStringItem(index, 2, sentence)
        c.close()
        
        self.SetStatusText("Groupie display complete.", number=0)
        
        
    def SelectLanguages(self, evt):
        if not self.fullLanguageNames:
            self.fullLanguageNames = []
            for langId in self.langs:
                self.fullLanguageNames.append(self.langs[langId][1])
            self.fullLanguageNames.sort()
            
        dlg = wx.MultiChoiceDialog(self, "Pick a combination of languages...", "Language Selection", self.fullLanguageNames)
        if (dlg.ShowModal() == wx.ID_OK):
            selections = [self.fullLanguageNames[which] for which in dlg.GetSelections()]
            self.chosenLanguageIds = []
            for langId in self.langs.keys():
                if self.langs[langId][1] in selections:
                    self.chosenLanguageIds.append(langId)
            self.chosenLanguageList = ""
            for langId in self.chosenLanguageIds:
                if len(self.chosenLanguageList) > 0:
                    self.chosenLanguageList += ","
                self.chosenLanguageList += str(langId)
            self.DetermineGroupies()
        dlg.Destroy()        
        
    def DetermineGroupies(self):
        groupies = []
        langIdSet = set(self.chosenLanguageIds)
        x = 1
        for groupieId in self.groupies["groupieToLangs"].keys():
            if langIdSet <= self.groupies["groupieToLangs"][groupieId]:
                if x < 10:
                    self.groupies["groupieToLangs"][groupieId]
                    x += 1
                groupies.append(str(groupieId))
        self.SetStatusText("Groupies determined, " + str(len(groupies)) + " total.", number=0)
        self.groupieList.Disable()
        self.groupieList.SetItems(groupies)
        self.groupieList.Append("View Groupie...")
        self.groupieList.SetStringSelection("View Groupie...")
        self.groupieList.Fit()
        self.groupieList.Enable()
            
        
    def CreateMenu(self):
        self.ID_ProcessData = 101
        self.ID_ExportGroupiesCsv = 201
        menuBar = wx.MenuBar()
        #dataMenu = wx.Menu()
        #dataMenu.Append(self.ID_ProcessData, "Process data files...", "The Tatoeba csv files need to be processed.")
        #self.Bind(wx.EVT_MENU, self.ProcessDataEvent, id=self.ID_ProcessData)
        exportMenu = wx.Menu()
        exportMenu.Append(self.ID_ExportGroupiesCsv, "Groupies to CSV...", "All groupies from the dropdown list will be exported.")
        self.Bind(wx.EVT_MENU, self.ExportGroupiesToCsv, id=self.ID_ExportGroupiesCsv)
        #menuBar.Append(dataMenu, "&Data")
        menuBar.Append(exportMenu, "&Export")
        self.SetMenuBar(menuBar)                             

    def GetGroupieAsCsvLine(self, groupieId, cursor, minCountRequired = 1, maxCountAllowed = 2):
        count = None
        maxCountEncountered = 1
        FORMAT_WINDOWS = "\r\n"
        FORMAT_NIX = "\n"
        FORMAT_CLASSICMAC = "\r"
        format = FORMAT_NIX
        line = str(groupieId)
        line += "\t["
        currentLang = None
        oneSentencePerLanguage = True
        allShort = True
        history = []
        cursor.execute("select sentence, langId from sentences where groupieId = ? and langId in (" + self.chosenLanguageList + ") order by langId", (groupieId,))
        records = cursor.fetchall()
        for record in records:
            sentence = record[0]
            langId = record[1]
            if not currentLang or langId != currentLang:
                count = 1 # since we are switching languages or starting our first one
                history = []
                if currentLang: # we are switching languages
                    line += "]\t["
                currentLang = langId
            else: # another sentence in same language
                count += 1
                if count > maxCountEncountered:
                    maxCountEncountered = count
                if count > maxCountAllowed:
                    return None
                oneSentencePerLanguage = False
                if sentence in history:
                    continue
                else:
                    history.append(sentence)
                    line += "] ["
            line += sentence
            if allShort and len(sentence) > 30:
                allShort = False
        if maxCountEncountered < minCountRequired:
            return None
        
        line += "]\t"
        tags = ""
        if oneSentencePerLanguage:
            tags += "oneEach"
        if allShort:
            if len(tags) > 0:
                tags += ","
            tags += "allShort"
        line += tags + format
        return line
                
    def ExportGroupiesToCsv(self, event):
        if not self.chosenLanguageIds or len(self.chosenLanguageIds) == 0:
            wx.MessageBox("Please select at least one language from the available choices.", "Export What?", wx.OK | wx.ICON_QUESTION)
            return
        
        if not self.groupies or len(self.groupies) == 0:
            wx.MessageBox("There are no groupies to export based on the choice of languages.", "No Groupies Exist", wx.OK | wx.ICON_INFORMATION)
            return
        
        minimum = None
        maximum = None
        
        optionsDlg = ExportOptionsDialog(self)
        if optionsDlg.ShowModal() == wx.ID_OK:
            minimumSelection = optionsDlg.minimum.GetStringSelection()
            maximumSelection = optionsDlg.maximum.GetStringSelection()
            try:
                minimum = int(minimumSelection)
                maximum = int(maximumSelection)
            except ValueError:
                wx.MessageBox("Only numbers are accepted. Try again.", "Invalid Entry", wx.OK | wx.ICON_EXCLAMATION)
                return
            if minimum < 1 or maximum < 1:
                wx.MessageBox("Only numbers 1 or higher are accepted. Try again.", "Invalid Entry", wx.OK | wx.ICON_EXCLAMATION)
                return
            if maximum < minimum:
                wx.MessageBox("Maximum allowed must not be less than minimum required. Try again.", "Invalid Entry", wx.OK | wx.ICON_EXCLAMATION)
                return
        else:
            return
        
        outfilePath  = None
        dlg = wx.FileDialog(self, "Save exported groupies (as .txt recommended):", style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            outfilePath = dlg.GetPath()     
        dlg.Destroy()
        
        if outfilePath:
            cursor = self.conn.cursor()
            notifyIndex = 0
            lines = []
            for item in self.groupieList.Items:
                notifyIndex += 1
                if notifyIndex % 10 == 0:
                    self.SetStatusText("Export in progress, working on item " + str(notifyIndex) + "...", number=0)
                line = None
                try:
                    line = self.GetGroupieAsCsvLine(int(item), cursor, minimum, maximum)
                except ValueError:
                    pass
                if line:
                    lines.append(line)
            
            csvfile = open(outfilePath, "w", encoding="utf-8")
            csvfile.writelines(lines)
            csvfile.close()
            cursor.close()
            wx.MessageBox("Export complete.", "Completed", wx.OK | wx.ICON_INFORMATION)
        
    def ProcessDataEvent(self, event):
        self.ProcessData(False)
        
    def ProcessData_GetGroupieDict(self, dataDirectory):
        if (os.path.isfile(os.path.join(os.getcwd(), "groupieDict.pickle"))):
            return pickleLoad("groupieDict.pickle")
        else:
            nextGroupieId = int(self.GetMetaValue("nextGroupieId"))
            groupieDict = {"idToGroupie":{}, "groupieToIds":{}, "groupieToLangs":{}}
            for link in open(os.path.join(dataDirectory, "links.csv")):
                id1, id2 = link.split("\t")
                id1 = int(id1)
                id2 = int(id2)            
                id1group = groupieDict["idToGroupie"].get(id1)
                id2group = groupieDict["idToGroupie"].get(id2)
                if id1group and id2group and id1group != id2group:
                    # both exist with different groups -- merge them
                    idsSet = groupieDict["groupieToIds"].get(id2group)
                    groupieDict["groupieToIds"][id2group] = set()
                    groupieDict["idToGroupie"][id2] = id1group 
                    if idsSet:
                        for theId in idsSet:
                            groupieDict["idToGroupie"][theId] = id1group
                elif id1group:
                    groupieDict["idToGroupie"][id2] = id1group
                    groupieDict["groupieToIds"][id1group].add(id2)
                elif id2group:
                    groupieDict["idToGroupie"][id1] = id2group
                    groupieDict["groupieToIds"][id2group].add(id1)
                else:
                    groupieDict["idToGroupie"][id1] = nextGroupieId
                    groupieDict["idToGroupie"][id2] = nextGroupieId
                    groupieDict["groupieToIds"][nextGroupieId] = set([id1, id2])
                    nextGroupieId += 1
            self.SetMetaValue("nextGroupieId", str(nextGroupieId))
            pickleDump("groupieDict.pickle", groupieDict)
            return groupieDict
                
    def ProcessData(self, update):
        
        dataDirectory = self.DetermineDataDirectory()
        if not dataDirectory:
            return
        
        self.SetStatusText("Beginning data processing... grabbing groupies", number=0)
        
#         if self.GetMetaValue('sentencesComplete') == ('true'):
#             return
        
        groupieDict = self.ProcessData_GetGroupieDict(dataDirectory)
        self.SetStatusText("Groupies determined. Stocking up sentences...", number=0)
        
        langDict = {}
        FIELD_ID = 0
        FIELD_LANGCODE = 1
        FIELD_SENTENCE = 2
        nextLangId = int(self.GetMetaValue("nextLangId"))
        
        c = self.conn.cursor()
        
        if os.path.isfile("groupies.pickle"):
            self.groupies = pickleLoad("groupies.pickle")
        else:
            notifyIndex = 1
            for record in open(os.path.join(dataDirectory, "sentences_detailed.csv"), encoding="utf-8"):
                notifyIndex += 1
                if notifyIndex % 1000 == 0:
                    self.SetStatusText("Stocking up sentences..., working on entry " + str(notifyIndex), number=0)
                fields = record.split("\t")
                for i in range(len(fields)):
                    fields[i] = fields[i].strip()
                    
                sentenceId = int(fields[FIELD_ID])
                langCode = fields[FIELD_LANGCODE]
                
                groupieId = groupieDict["idToGroupie"].get(sentenceId)
                if not groupieId:
                    groupieId = 0  
                
                langId = langDict.get(langCode)
                if not langId:
                    langId = nextLangId
                    nextLangId += 1
                    langDict[langCode] = langId
                
                
                if groupieId != 0: # ensure this sentence's language is part of its groupie language list
                    langSet = groupieDict["groupieToLangs"].get(groupieId)
                    if langSet:
                        langSet.add(langId)
                    else:
                        groupieDict["groupieToLangs"][groupieId] = set([langId])
                            
                c.execute("insert into sentences values (?, ?, ?, ?)", (sentenceId, groupieId, langId, fields[FIELD_SENTENCE]))
            
            pickleDump("groupies.pickle", groupieDict)
            self.groupies = groupieDict
            
        self.ProcessData_SaveLangTable(langDict, c) 
        self.conn.commit()
        c.close()

        self.SetMetaValue("nextLangId", str(nextLangId))
        self.SetMetaValue("complete", "true")
        self.SetMetaValue("sentencesComplete", "true")
        self.SetStatusText("Processing complete!", number=0)
        self.picker.Enable()     
        
    def ProcessData_SaveLangTable(self, langDict, cursor):
        iso639_3_dict = pickleLoad("iso639_3.pickle")
        
        persisted = {}
        for key in langDict.keys():
            langName = iso639_3_dict.get(key)
            if not langName:
                langName = '"' + key + '"'
            persisted[langDict[key]] = [key, langName]
            cursor.execute("insert into langs values (?, ?, ?)", (langDict[key], key, langName))
            
        pickleDump("langs.pickle", persisted)
        self.langs = persisted
            
        del iso639_3_dict
                
    def AllTatoebaDataFilesFound(self, dataDirectory):
        if os.path.isfile(os.path.join(dataDirectory, "links.csv")) and \
            os.path.isfile(os.path.join(dataDirectory, "sentences_detailed.csv")):
                return True
        elif os.path.isfile(os.path.join(dataDirectory, "links.tar")) or \
            os.path.isfile(os.path.join(dataDirectory, "links.tar.bz2")) or \
            os.path.isfile(os.path.join(dataDirectory, "sentences_detailed.tar")) or \
            os.path.isfile(os.path.join(dataDirectory, "sentences_detailed.tar.bz2")):
                wx.MessageBox("You must extract the files -- expecting plain csv files, not archives.", "Files Not Located", wx.OK | wx.ICON_INFORMATION)
        return False
       
    def DetermineDataDirectory(self):
        dataDirectory = None
        dlg = wx.DirDialog(self, "Data directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

        if dlg.ShowModal() == wx.ID_OK:
            dataDirectory = dlg.GetPath()
            if not self.AllTatoebaDataFilesFound(dataDirectory):
                wx.MessageBox("Tatobea data files not located. Looking for \"links.csv\" and \"sentences_detailed.csv\". These can be downloaded from http://tatoeba.org/eng/downloads", "Files Not Located", wx.OK | wx.ICON_INFORMATION)     
        dlg.Destroy()
        return dataDirectory
        
    def OpenDatabase(self):
        if self.conn:
            self.CloseDatabase() 
        exists = os.path.isfile("tatoebaGroupie.sqlite3")
        self.conn = sqlite3.connect("tatoebaGroupie.sqlite3")
        if not exists:
            self.CreateDatabase()
            
    def CloseDatabase(self):
        self.conn.close()
        self.conn = None      

    def CreateDatabase(self):
        c = self.conn.cursor()
        c.execute("create table sentences (sentenceId integer, groupieId integer, langId integer, sentence text)")
        c.execute("create table langs (langId integer primary key, langCode text unique, langName text)")
        c.execute("create table meta (key text, value text)")
        c.execute("create index indexSentences on sentences (groupieId, langId)")
        self.conn.commit()
        c.close()
        self.SetMetaValue("nextLangId", "1")
        self.SetMetaValue("nextGroupieId", "1")
        
    def DatabaseComplete(self):
        val = self.GetMetaValue('complete')
        return val == ('true')
    
    def GetMetaValue(self, key):
        c = self.conn.cursor()
        c.execute("select value from meta where key = ?", (key,))
        val =  c.fetchone()
        c.close()
        if val:
            return val[0]
        else:
            return None
    
    def SetMetaValue(self, key, value):
        c = self.conn.cursor()
        c.execute("insert into meta values (?, ?)", (key, value))
        self.conn.commit()
        c.close()             
        
        
def LaunchApp():
    app = wx.App(False)
    TopWnd = MainWindow()
    TopWnd.Show(True)
    TopWnd.Initialize()
    app.MainLoop()
    
def main():
    LaunchApp()
    
def AsyncLoadData():
    langs = pickleLoad("langs.pickle")
    groupies = pickleLoad("groupies.pickle")
    return (langs, groupies)
    
if __name__ == "__main__":
    main()