from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL, Qt, QDir
from PyQt4.QtGui import *
import sys
from works.PaodeacucarScrapper import PaodeacucarScrapper

__author__ = 'Rabbi'


class Form(QMainWindow):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.createGui()

    def createGui(self):
        self.btnScrap = QPushButton('&Scrap Data')
        self.btnScrap.clicked.connect(self.scrapAction)

        layout = QGridLayout()
        layout.addWidget(self.btnScrap, 0, 0, Qt.AlignLeft)

        self.browser = QTextBrowser()
        layoutMain = QVBoxLayout()
        layoutMain.addLayout(layout)
        layoutMain.addWidget(self.browser)
        widget = QWidget()
        widget.setLayout(layoutMain)

        self.setCentralWidget(widget)
        screen = QDesktopWidget().screenGeometry()
        self.resize(screen.width() - 300, screen.height() - 300)
        self.setWindowTitle('Paodeacucar Scrapper')

    def scrapAction(self):
        self.paode = PaodeacucarScrapper()
        self.paode.start()
        self.paode.notifyPaode.connect(self.notifyInfo)

    def notifyInfo(self, data):
        try:
            self.browser.document().setMaximumBlockCount(1000)
            self.browser.append(data)
        except Exception, x:
            print x.message


class MainView:
    def __init__(self):
        pass

    def showMainView(self):
        app = QApplication(sys.argv)
        form = Form()
        form.show()
        sys.exit(app.exec_())
