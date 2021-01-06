import sys
import os
import json
from functools import partial
from Qt import QtCore, QtGui, QtWidgets
from Qt import _loadUi

import util

class MyWindow(QtWidgets.QDialog):
    def __init__(self):
        super(MyWindow, self).__init__()
        _loadUi('vc.ui', self)
        #self.setCentralWidget(self.widget)

        self.uniqueTopN = []
        self.oriColorTop = []
        self.compColorTop = []
        self.diffColorTop = []
        self.master = []
        self.filterList = []
        self.oriFilter = True   # a flag determine get filter list from original dictionary

        self.linkFunc()
        self.show()

        self.stackedWidget.setCurrentIndex(3)
        self.dropBtn.setCurrentIndex(3)

        #self.filePathEdit.setText(r'C:\Users\Lei\Desktop\vc\test\setting1.ma')
        #self.compFilePathEdit.setText(r'C:\Users\Lei\Desktop\vc\test\setting2.ma')

    def linkFunc(self):
        self.midListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.fileBrwBtn.clicked.connect(self.fileBrowse)
        self.compFileBrwBtn.clicked.connect(self.compFileBrowse)
        self.createBtn.clicked.connect(self.checkJson)
        self.viewBtn.clicked.connect(self.populate)
        self.compBtn.clicked.connect(self.populate)

        self.topListWidget.itemClicked.connect(self.populateSec)

        self.midListWidget.itemSelectionChanged.connect(self.clearRoot)
        self.midListWidget.itemSelectionChanged.connect(self.populateRoot)
        self.midListWidget.itemSelectionChanged.connect(self.populateFilter)

        self.dropBtn.currentIndexChanged.connect(self.setPageIndex)
        #self.textViewCheckBox.stateChanged.connect(self.setPageIndex)

    '''Setting the right most widget page index'''
    def setPageIndex(self):
        if self.dropBtn.currentIndex() == 0:
            self.stackedWidget.setCurrentIndex(0)  # text view
        elif self.dropBtn.currentIndex() == 1:
            self.stackedWidget.setCurrentIndex(1)  #
        elif self.dropBtn.currentIndex() == 2:
            self.stackedWidget.setCurrentIndex(2)  #
        else:
            self.stackedWidget.setCurrentIndex(3)  # table view

    def fileBrowse(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Select your original file', r'C:\Users\Lei\Desktop\vc\test')[0]
        self.filePathEdit.setText(fileName)

    def compFileBrowse(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Select your file to compare', r'C:\Users\Lei\Desktop\vc\test')[0]
        self.compFilePathEdit.setText(fileName)

    '''Check Json exist or need update based on time'''
    def checkJson(self):
        self.filePath = self.filePathEdit.text()
        self.jsonFilePath = os.path.splitext(self.filePath)[0] + os.extsep + 'json'
        mayaFilePath = os.path.splitext(self.filePath)[0] + os.extsep + 'ma'

        if os.path.isfile(self.jsonFilePath):
            maFileTime = os.path.getmtime(mayaFilePath)
            jsonFileTime = os.path.getmtime(self.jsonFilePath)
            if jsonFileTime >= maFileTime:
                QtWidgets.QMessageBox.information(self, "Json Check", "Json already exist and up to date")
            else:
                msgBox = QtWidgets.QMessageBox(self)
                msgBox.setIcon(QtWidgets.QMessageBox.Question)
                msgBox.setWindowTitle('Json Check')
                msgBox.setText( "Json not up to date, update?" )
                msgBox.addButton( QtGui.QMessageBox.Yes )
                msgBox.addButton( QtGui.QMessageBox.No )

                msgBox.setDefaultButton( QtGui.QMessageBox.No )
                returnV = msgBox.exec_()
                if returnV == QtWidgets.QMessageBox.Yes:
                    self.createJson()
        else:
            QtWidgets.QMessageBox.information(self, "Json Check", "Creating new Json for current file")
            self.createJson()

    '''Create Json for the current maya file'''
    def createJson(self):
        import subprocess
        pyPath = r'C:\Users\Lei\Desktop\vc\createJson.py'
        command = 'mayapy ' + pyPath + ' ' + self.filePath
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        print(process.returncode)

    '''Coloring the leftmost widget'''
    #TOFIX: color not showing right under some condition
    def colorFunc(self, widget, list, color):
        for index in range(widget.count()):
            item = widget.item(index)
            if item.text() in list:
                item.setBackground(QtGui.QColor(color))

    '''Coloring the leftmiddle widget'''
    def colorSecFunc(self, widget, sets, item, color):
        if sets is self.oriColorTop: signal = '-'
        elif sets is self.compColorTop: signal = '+'
        elif sets is self.diffColorTop: signal = '!'

        if item in sets:
            self.colorS = []
            for eachLine in self.master:
                if item in eachLine[1] and eachLine[0] == signal:
                    self.colorS.append(eachLine[2])
            self.colorFunc(widget, self.colorS, color)

    '''Populating list of node types in leftmost widget'''
    def populate(self):
        self.topListWidget.clear()  # clear widget
        self.midListWidget.clear()

        self.filePath = self.filePathEdit.text()
        self.jsonFilePath = os.path.splitext(self.filePath)[0] + os.extsep + 'json'  # make sure its always getting the json

        if os.path.isfile(self.jsonFilePath):
            with open(self.jsonFilePath, "r") as f:
                self.rawData = json.load(f)
                self.data = util.sortDict(self.rawData)
                print('original json load success')
        else:
            print('file not exist')

        if self.compFilePathEdit.text():  # compare method
            self.compFilePath = self.compFilePathEdit.text()
            self.compJsonFilePath = os.path.splitext(self.compFilePath)[0] + os.extsep + 'json'

            if os.path.isfile(self.compJsonFilePath):
                with open(self.compJsonFilePath, "r") as f:  # example file
                    self.rawCompData = json.load(f)
                    self.compData = util.sortDict(self.rawCompData)
                    print('compared json load success')
            else:
                print('file not exist')

            self.genInfo()  # this will also create color list

        for topFilter in self.data['file info'].keys():
            self.topListWidget.addItem(topFilter)
            self.topListWidget.sortItems()

        if self.compColorTop:
            self.uniqueTopN = []  # reset list
            for nodes in self.compColorTop:
                if nodes not in self.data['file info'].keys():
                    self.uniqueTopN.append(nodes)
                    self.topListWidget.addItem(nodes)
                    self.topListWidget.sortItems()

        # set color to list (order matters)
        self.colorFunc(self.topListWidget, self.oriColorTop, 'red')
        self.colorFunc(self.topListWidget, self.compColorTop, 'green')
        self.colorFunc(self.topListWidget, self.diffColorTop, 'yellow')  # different overrides color at last

    '''Populating list of node names in left-middle widget'''
    def populateSec(self):
        self.midListWidget.clear()
        self.finalTextBrowser.clear()
        self.finalTableWidget.clear()
        self.A2BTextBrw.clear()
        self.B2ATextBrw.clear()

        self.filterList = []

        for i in reversed(range(self.scrollVLayout.count())):
            self.scrollVLayout.itemAt(i).widget().setParent(None)  # clear scroll area layout

        currentItem = self.topListWidget.currentItem().text()

        if currentItem in self.uniqueTopN:
            for node in self.uniqueTopN:
                for eachLine in self.master:
                    if node in eachLine[1]:
                        self.midListWidget.addItem(eachLine[2])
        else:
            midList = []
            for midFilter in self.data['file info'][str(currentItem)].keys():
                self.midListWidget.addItem(midFilter)
                midList.append(midFilter)

            if currentItem in self.compColorTop:
                for eachLine in self.master:
                    if currentItem in eachLine[1] and eachLine[2] not in midList:
                        self.midListWidget.addItem(eachLine[2])

        # color secondary (order doesn't matter)
        self.colorSecFunc(self.midListWidget, self.diffColorTop, currentItem, 'yellow')
        self.colorSecFunc(self.midListWidget, self.oriColorTop, currentItem, 'red')
        self.colorSecFunc(self.midListWidget, self.compColorTop, currentItem, 'green')

    '''Populating list of attribute filter in rightmiddle widget'''
    def populateFilter(self):
        self.filterList = []

        for i in reversed(range(self.scrollVLayout.count())):
            self.scrollVLayout.itemAt(i).widget().setParent(None)  # clear scroll area layout

        tpCurrentItem = self.topListWidget.currentItem().text()

        if self.midListWidget.selectedItems():
            if self.oriFilter:
                for attrFilter in self.data['file info'][str(tpCurrentItem)][self.midListWidget.selectedItems()[0].text()].keys():
                    self.addCheckBox(attrFilter)
            else:
                for attrFilter in self.compData['file info'][str(tpCurrentItem)][self.midListWidget.selectedItems()[0].text()].keys():
                    self.addCheckBox(attrFilter)

    '''Populating list of attribute and value in right-most widget'''
    '''can pick 4 different view from drop down'''
    def populateRoot(self):
        self.finalTextBrowser.clear()
        self.finalTableWidget.clear()
        self.A2BTextBrw.clear()
        self.B2ATextBrw.clear()
        self.oriFilter = True

        tpCurrentItem = self.topListWidget.currentItem().text()

        items = self.midListWidget.selectedItems()
        midCurrentItems = []
        for i in range(len(items)):
            midCurrentItems.append(str(self.midListWidget.selectedItems()[i].text()))

        if len(midCurrentItems) is 1:  # one selection
            currentSignal = ''  # reset currentSignal

            for eachLine in self.master:
                if midCurrentItems[0] in eachLine[2]:
                    currentSignal = eachLine[0]

            if not currentSignal:
                oriAV = self.data['file info'][str(tpCurrentItem)][str(midCurrentItems[0])]
                self.fillTextBrowser(oriAV, currentSignal)
                self.fillTable(oriAV, currentSignal)

            # red case
            elif currentSignal == '-':
                oriAV = self.data['file info'][str(tpCurrentItem)][str(midCurrentItems[0])]
                temp, tempDict = self.getTempInfo(midCurrentItems[0], oriAV)  # tempDict not in use

                self.fillTextBrowser(oriAV, currentSignal, temp)
                self.fillTable(oriAV, currentSignal, temp)

            # green case
            elif currentSignal == '+':
                self.oriFilter = False  # get filter list from the compare dictionary

                compAV = self.compData['file info'][str(tpCurrentItem)][str(midCurrentItems[0])]
                temp, tempDict = self.getTempInfo(midCurrentItems[0], compAV)  # tempDict not in use

                self.fillTextBrowser(compAV, currentSignal, temp)
                self.fillTable(compAV, currentSignal, temp)

            # yellow case
            elif currentSignal == '!':
                oriAV = self.data['file info'][str(tpCurrentItem)][str(midCurrentItems[0])]
                compAV = self.compData['file info'][str(tpCurrentItem)][str(midCurrentItems[0])]

                temp, tempDict = self.getTempInfo(midCurrentItems[0], compAV)
                print(temp, tempDict)

                self.fillTextBrowser(oriAV, currentSignal, temp, tempDict)
                self.fillTable(oriAV, currentSignal, temp, tempDict)
                self.fillA2BTextBrw(oriAV, midCurrentItems[0], temp, tempDict)
                self.fillB2ATextBrw(oriAV, midCurrentItems[0], temp, tempDict)

        else:  # multiple selection
            for midCurrentItem in midCurrentItems:
                self.finalTextBrowser.append(midCurrentItem + ':')
                oriAV = self.data['file info'][str(tpCurrentItem)][str(midCurrentItem)]
                for rootFilter in oriAV.items():
                    if rootFilter[0] in self.filterList:
                        self.finalTextBrowser.append('    ' + rootFilter[0] + ':   ' + str(rootFilter[1]))
                    if not self.filterList:
                        self.finalTextBrowser.append('    ' + rootFilter[0] + ':   ' + str(rootFilter[1]))

    '''A->B view'''
    def fillA2BTextBrw(self, dict, node, temp=[], tempDict=[]):
        self.A2BTextBrw.append('///Setting original file to comparison file value:///')
        self.A2BTextBrw.append('\nimport maya.cmds as cmds')

        for rootFilter in dict.items():
            if rootFilter[0] in self.filterList and rootFilter[0] in temp:  # unique
                value = tempDict[rootFilter[0]]
                self.A2BTextBrw.append("cmds.setAttr('%s.%s', %s)" % (node, rootFilter[0], value[1]))  # enter your python command here
            elif not self.filterList and rootFilter[0] in temp:
                value = tempDict[rootFilter[0]]
                self.A2BTextBrw.append("cmds.setAttr('%s.%s', %s)" % (node, rootFilter[0], value[1]))

    '''B->A view'''
    def fillB2ATextBrw(self, dict, node, temp=[], tempDict=[]):
        self.B2ATextBrw.append('///Setting comparison file to original file value:///')
        self.B2ATextBrw.append('\nimport maya.cmds as cmds')

        for rootFilter in dict.items():
            if rootFilter[0] in self.filterList and rootFilter[0] in temp:  # unique
                value = tempDict[rootFilter[0]]
                self.B2ATextBrw.append("cmds.setAttr('%s.%s', %s)" % (node, rootFilter[0], value[0]))  # enter your python command here
            elif not self.filterList and rootFilter[0] in temp:
                value = tempDict[rootFilter[0]]
                self.B2ATextBrw.append("cmds.setAttr('%s.%s', %s)" % (node, rootFilter[0], value[0]))

    '''Text view'''
    def fillTextBrowser(self, dict, signal='', temp=[], tempDict=[]):
        for rootFilter in dict.items():
            if rootFilter[0] in self.filterList and rootFilter[0] not in temp:
                self.finalTextBrowser.append(rootFilter[0] + ':   ' + str(rootFilter[1]))
            elif rootFilter[0] in self.filterList and rootFilter[0] in temp:  # unique
                if not tempDict:
                    self.finalTextBrowser.append(signal + rootFilter[0] + ':   ' + str(rootFilter[1]))
                else:
                    value = tempDict[rootFilter[0]]
                    self.finalTextBrowser.append(signal + rootFilter[0] + ':   ' + str(value[0]) + '--->' + str(value[1]))

            if not self.filterList and rootFilter[0] not in temp:
                self.finalTextBrowser.append(rootFilter[0] + ':   ' + str(rootFilter[1]))
            elif not self.filterList and rootFilter[0] in temp:
                if not tempDict:
                    self.finalTextBrowser.append(signal + rootFilter[0] + ':   ' + str(rootFilter[1]))
                else:
                    value = tempDict[rootFilter[0]]
                    self.finalTextBrowser.append(signal + rootFilter[0] + ':   ' + str(value[0]) + '--->' + str(value[1]))

    '''Table view'''
    def fillTable(self, dict, signal='', temp=[], tempDict=[]):
        self.finalTableWidget.setColumnCount(2)
        self.finalTableWidget.setRowCount(len(dict.items()))

        self.finalTableWidget.verticalHeader().setVisible(False)
        self.finalTableWidget.horizontalHeader().setStretchLastSection(True)
        #self.finalTableWidget.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)

        self.finalTableWidget.setHorizontalHeaderLabels(['attr', 'value'])
        filterCount = 0

        for i, rootFilter in enumerate(dict.items()):
            # filter not enable
            if not self.filterList:
                if rootFilter[0] not in temp:
                    self.finalTableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(str(rootFilter[0])))
                    self.finalTableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(rootFilter[1])))
                elif rootFilter[0] in temp:
                    if not tempDict:
                        self.finalTableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(str(rootFilter[0])))
                        self.finalTableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(rootFilter[1])))

                        if signal == '+':
                            self.finalTableWidget.item(i, 1).setBackground(QtGui.QColor('green'))
                        else:
                            self.finalTableWidget.item(i, 1).setBackground(QtGui.QColor('red'))
                    else:
                        self.finalTableWidget.setColumnCount(3)
                        self.finalTableWidget.setHorizontalHeaderLabels(['attr', 'file1_value', 'file2_value'])
                        #self.finalTableWidget.horizontalHeader().setResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
                        #self.finalTableWidget.horizontalHeader().setResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

                        value = tempDict[rootFilter[0]]
                        self.finalTableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(str(rootFilter[0])))
                        self.finalTableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(value[0])))
                        self.finalTableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(str(value[1])))

                        self.finalTableWidget.item(i, 1).setBackground(QtGui.QColor('yellow'))
                        self.finalTableWidget.item(i, 2).setBackground(QtGui.QColor('yellow'))

            # filter enabled
            else:
                self.finalTableWidget.setRowCount(len(self.filterList))
                if rootFilter[0] in self.filterList and rootFilter[0] not in temp:  # white case
                    self.finalTableWidget.setItem(filterCount, 0, QtWidgets.QTableWidgetItem(str(rootFilter[0])))
                    self.finalTableWidget.setItem(filterCount, 1, QtWidgets.QTableWidgetItem(str(rootFilter[1])))
                    filterCount += 1

                elif rootFilter[0] in self.filterList and rootFilter[0] in temp:
                    if not tempDict:  # red/green case
                        self.finalTableWidget.setItem(filterCount, 0, QtWidgets.QTableWidgetItem(str(rootFilter[0])))
                        self.finalTableWidget.setItem(filterCount, 1, QtWidgets.QTableWidgetItem(str(rootFilter[1])))
                        if signal == '+':
                            self.finalTableWidget.item(filterCount, 1).setBackground(QtGui.QColor('green'))
                        else:
                            self.finalTableWidget.item(filterCount, 1).setBackground(QtGui.QColor('red'))
                        filterCount += 1
                    else:  # yellow case
                        self.finalTableWidget.setColumnCount(3)
                        self.finalTableWidget.setHorizontalHeaderLabels(['attr', 'file1_value', 'file2_value'])
                        #self.finalTableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
                        #self.finalTableWidget.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.ResizeToContents)

                        value = tempDict[rootFilter[0]]
                        self.finalTableWidget.setItem(filterCount, 0, QtWidgets.QTableWidgetItem(str(rootFilter[0])))
                        self.finalTableWidget.setItem(filterCount, 1, QtWidgets.QTableWidgetItem(str(value[0])))
                        self.finalTableWidget.setItem(filterCount, 2, QtWidgets.QTableWidgetItem(str(value[1])))

                        self.finalTableWidget.item(filterCount, 1).setBackground(QtGui.QColor('yellow'))
                        self.finalTableWidget.item(filterCount, 2).setBackground(QtGui.QColor('yellow'))
                        filterCount += 1

    '''sub function for rightmost widget generation'''
    def getTempInfo(self, item, dict):
        temp = []
        tempDict = {}
        for eachLine in self.master:
            if item in eachLine[2]:
                tempDict.update(eachLine[-1])
        for key in tempDict.keys():
            if key in dict.keys():
                temp.append(key)
        return temp, tempDict

    '''sub function for rightmost widget generation'''
    def genInfo(self):
        output = util.compare_dictionaries(self.rawData, self.rawCompData)  # must use raw data, otherwise format error
        self.master = util.intOutString(output)
        print(self.master)

        for eachLine in self.master:
            if len(eachLine) is not 1:
                if eachLine[0] == '-':
                    self.oriColorTop.append(eachLine[1])
                elif eachLine[0] == '+':
                    self.compColorTop.append(eachLine[1])
                elif eachLine[0] == '!':
                    self.diffColorTop.append(eachLine[1])
                else:
                    print('error on master output')

        self.oriColorTop = util.uniqueList(self.oriColorTop)
        self.compColorTop = util.uniqueList(self.compColorTop)
        self.diffColorTop = util.uniqueList(self.diffColorTop)

    '''sub function for generating filter list checkbox'''
    def addCheckBox(self, text='None'):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        label = QtWidgets.QLabel(text)
        label.setAlignment(QtCore.Qt.AlignLeft)
        label.setMaximumSize(200, 16)

        check = QtWidgets.QCheckBox()
        check.setMaximumSize(16, 16)

        layout.addWidget(check)
        layout.addWidget(label)
        self.scrollVLayout.insertWidget(-1, widget)
        check.stateChanged.connect(partial(self.addToFilterList, text=text))

    '''sub function for adding filters to filter list'''
    def addToFilterList(self, text):
        if text not in self.filterList:
            self.filterList.append(text)
        elif text in self.filterList:
            self.filterList.remove(text)
        self.filterList.sort()
        self.populateRoot()  # populate the filtered list

    def clearRoot(self):
        self.filterList = []
        self.finalTextBrowser.clear()
        self.finalTableWidget.clear()
        self.A2BTextBrw.clear()
        self.B2ATextBrw.clear()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
