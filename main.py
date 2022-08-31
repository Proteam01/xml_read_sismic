import sys
import schedule
import requests
from datetime import datetime
from helpers import OPTIONS
from PyQt5.uic import loadUiType
from xml.dom.minidom import parseString
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QIcon
import qdarkstyle
import re

from models import Session, Sismo

MainClass, _ = loadUiType('main_window.ui')


class MainWindow(MainClass, QMainWindow):

    alert_signal = pyqtSignal(Sismo)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.icon = QIcon('sismo_16x16.png')
        self.setupUi(self)
        self.style = qdarkstyle.load_stylesheet()
        self.setStyleSheet(self.style)
        self.setFixedSize(self.size())
        self.setWindowIcon(self.icon)
        self.hide_window_btn.clicked.connect(self.hide_window)
        schedule.every(10).minutes.do(self.parse_xml)
        self.executor = ScheduleExecutor()
        self.executor.start()
        self.alert_signal.connect(self.show_alert)

    def hide_window(self):
        self.hide()

    def parse_xml(self):
        self.status_line_edit.setText(
            'Ultima Ejecucion: ' + datetime.now().__str__())
        response = requests.get(OPTIONS['url_sismos'])
        dom = parseString(response.content)
        items = dom.getElementsByTagName('item')
        with Session() as session:
            for item in items:
                sismo = Sismo()
                sismo.title = item.getElementsByTagName(
                    'title')[0].firstChild.nodeValue.strip()
                sismo.description = item.getElementsByTagName(
                    'description')[0].firstChild.nodeValue.strip()
                sismo.link = item.getElementsByTagName(
                    'link')[0].firstChild.nodeValue
                sismo.latitud = float(item.getElementsByTagName(
                    'geo:lat')[0].firstChild.nodeValue)
                sismo.longigud = float(item.getElementsByTagName(
                    'geo:long')[0].firstChild.nodeValue)
                nuevo_sismo = session.query(Sismo).filter(Sismo.title == sismo.title).count() == 0
                if nuevo_sismo:
                    session.add(sismo)
                    session.commit()
                    self.check_if_alert(sismo)

    def check_if_alert(self, sismo: Sismo):
        title = sismo.title
        result = re.search('^\d*\.\d*', title)
        magnitud = float(result[0])
        alerta = float(OPTIONS['alerta'])
        if magnitud > alerta:
            self.alert_signal.emit(sismo)

    @pyqtSlot(Sismo)
    def show_alert(self, sismo: Sismo):
        self.show()
        message = QMessageBox(self)
        message.setWindowTitle("Evento Critico")
        message.setText(f"sismo detectado: {sismo.title}")
        message.setIcon(QMessageBox.Icon.Critical)
        message.exec_()
        # aqui es donde se puede encadenar accion extra

class ScheduleExecutor(QThread):

    def __init__(self):
        super(ScheduleExecutor, self).__init__(parent=None)

    def run(self):
        while True:
            schedule.run_pending()
            self.sleep(1)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    # window.show()
    tray = QSystemTrayIcon()
    tray.setIcon(window.icon)
    tray.setVisible(True)
    menu = QMenu()
    show_window_action = QAction('Mostrar Ventana')
    show_window_action.triggered.connect(window.show)
    menu.addAction(show_window_action)
    tray.setContextMenu(menu)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
