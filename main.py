# -*- coding: utf-8 -*-
# ## creat by wangxinlei 20201104
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow,QTableWidgetItem,QTableWidget,QMessageBox,QWidget
from PyQt5.QtCore import  QThread ,  pyqtSignal,  QDateTime , QObject,Qt
from ui_main import Ui_MainWindow
import sys
import os
import time
import threading
import G_Function as vs 
import PyDoIP_SWDL as swdl
from datetime import datetime
from multiprocessing import Process
#reload(sys)
#sys.setdefaultencoding('utf8')
import multiprocessing


os.environ["NLS_LANG"] = "SIMPLIFIED CHINESE_CHINA.UTF8"
class MyMainWindow(QMainWindow, Ui_MainWindow):
    update_middle_message = pyqtSignal(str)
    update_message = pyqtSignal(str)  


    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        vs.read_config()
        self.setupUi(self)
        self.item_row=20
        self.status_label = QtWidgets.QLabel(self.centralwidget)
        self.statusbar.addWidget(self.status_label)
        self.vin=''
        self.status_label.setText('creat by wangxinlei viersion 2020.11.04')
        self.update_message.connect(self.message_control)
        self.update_middle_message.connect(self.middle_message_control)
        self.head_message.returnPressed.connect(lambda:self.mbuttion1clicked())
        self.start_btn.clicked.connect(lambda:self.mbuttion1clicked())

        self.init_history_table()
        self.history_table.itemClicked.connect(self.get_item)
        self.set_windows_size()
        self.showMaximized()
        self.process_flag=0
        self.ui_control()
        


    def set_windows_size(self):
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        height = self.screenRect.height()
        width = self.screenRect.width()
        self.resize(width,height)

    def initUI(self):
        self.update_window()
    def get_item(self,item):
        print('yuo select=>'+item.text())

    def middle_message_control(self, text):
        cursor = self.middle_message.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.middle_message.setTextCursor(cursor)
        self.middle_message.ensureCursorVisible()

    def message_control(self, text):
        cursor = self.message.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.message.setTextCursor(cursor)
        self.message.ensureCursorVisible()



   


    def mbuttion1clicked(self):
        try:
            self.vin=str(self.head_message.text())  
            self.test_control(self.vin)
        except Exception as e:
            self.middle_message_control(str(e))


    def test_control(self,vin):
        if not self.start_btn.isEnabled():return 1
        if len(vin)>0:
            self.head_message.setText(vin)
            self.set_window_0()
            self.update_history_table()
            vs.check_mac_address()
            self.init_variable()                          
            self.swdl_process = threading.Thread(target=swdl.LL, args=(self.vin,))
            self.swdl_process.setDaemon(True)
            self.swdl_process.start()
            self.process_flag=1
        else:
            self.set_window_1()
            self.init_variable()
            self.head_message.setText('')




    def init_variable(self):
        #vs.VARIABLE={}
        #vs.RM_VARIABLE={}
        pass

    def set_window_0(self):
        self.start_btn.setEnabled(False)
        self.head_message.setReadOnly(True)
        self.message.setPlainText("")
        self.middle_message.setPlainText("")
        self.status_label.setText(self.vin)



    def set_window_1(self):
        self.start_btn.setEnabled(True)
        self.head_message.setReadOnly(False)
        self.message.setPlainText("")
        self.middle_message.setPlainText("")
        self.status_label.setText("")



    def set_window_9(self):
        self.start_btn.setEnabled(True)
        self.head_message.setReadOnly(False)


    def ui_control(self):
        self.ui_process = threading.Thread(target=self.update_window(),args=())
        self.ui_process.setDaemon(True)
        self.ui_process.start()  

    def update_window(self):
        while True:
            if len(vs.mid_message_list)>0:
                v=vs.mid_message_list.pop(0)
                if str(v)[-2:].find('\n')<0:
                    v=str(v)+'\n'
                self.update_middle_message.emit(v)


            if len(vs.secreen_log_message)>0:
                j=vs.secreen_log_message.pop(0)
                if str(j)[-2:].find('\n')<0:
                    j=str(j)+'\n'
                self.update_message.emit(j)
            if self.process_flag==1 and not self.swdl_process.is_alive():
                self.set_window_9()

            QApplication.processEvents()       
            time.sleep(0.01)



    def init_history_table(self):
        self.history_table.verticalHeader().setVisible(False)
        #self.history_table.setHorizontalHeaderLabels(["Test Time"," VIN"])
        self.history_table.horizontalHeader().setVisible(False)
        self.history_table.setColumnWidth(0,200)
        self.history_table.setColumnWidth(1,200)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)
        self.history_table.horizontalHeader().setStretchLastSection(True)




    def update_history_table(self):
        
        starttime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row=self.history_table.rowCount()
        self.history_table.setColumnCount(2)
        self.history_table.setRowCount(row+1)
        if row==0:self.init_history_table()
        t_starttime=QTableWidgetItem(starttime)
        self.history_table.setItem(row,0,t_starttime)
        t_vin=QTableWidgetItem(self.vin)
        self.history_table.setItem(row,1,t_vin)  

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self,'x-car',"Are you sure you want to exit？",QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            os._exit(0)
        else:
            event.ignore()



def start_main() -> int:
    try:
        multiprocessing.freeze_support()
        app = QtWidgets.QApplication(sys.argv)
        win = MyMainWindow()
        win.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.information(None, "error", str(e), QMessageBox.Ok, QMessageBox.Ok)
        return 0



if __name__ == "__main__":

    start_main()


