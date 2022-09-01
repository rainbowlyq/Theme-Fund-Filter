# _*_coding:utf-8_*_
# @Project: main.py
# @File_Name: GUI
# @Author: lyq
# @Time: 2022-08-24 13:21
# @Software: Pycharm
import os
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QAction
from functools import partial
import GUI
import Config
import main


def run_all(ui: GUI.Ui_MainWindow, win: QMainWindow):
    configs = Config.get_params(ui)
    main.main_process(configs)
    if QMessageBox.Yes == QMessageBox.question(win, '成功', '程序运行结束,是否要退出程序?', QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.Yes):
        win.close()


def industry_only(ui: GUI.Ui_MainWindow, win: QMainWindow):
    configs = Config.get_params(ui)
    main.industry_only(configs)
    if QMessageBox.Yes == QMessageBox.question(win, '成功', '程序运行结束,是否要退出程序?', QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.Yes):
        win.close()


def change_mode(ui: GUI.Ui_MainWindow):
    # 自定义股票池
    if ui.radioButton_2.isChecked():
        ui.plainTextEdit_2.setEnabled(False)
        ui.pushButton.setEnabled(True)
        ui.groupBox.setEnabled(False)
    else:
        ui.plainTextEdit_2.setEnabled(True)
        ui.pushButton.setEnabled(False)
        ui.groupBox.setEnabled(True)


def open_custom_stockpool():
    os.startfile('自定义股票池.xls')


def help():
    os.startfile('说明.docx')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = GUI.Ui_MainWindow()
    ui.setupUi(MainWindow)

    ui.pushButton_4.clicked.connect(partial(run_all, ui, MainWindow))
    ui.pushButton_2.clicked.connect(partial(industry_only, ui, MainWindow))
    ui.radioButton.clicked.connect(partial(change_mode, ui))
    ui.radioButton_2.clicked.connect(partial(change_mode, ui))
    ui.pushButton.clicked.connect(open_custom_stockpool)
    ui.help_action = QAction(MainWindow)
    ui.help_action.setObjectName('menu')
    ui.help_action.triggered.connect(help)
    ui.help_action.setText('帮助')
    ui.menubar.addAction(ui.help_action)

    MainWindow.show()
    sys.exit(app.exec_())
