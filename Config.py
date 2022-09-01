# _*_coding:utf-8_*_
# @Project: main.py
# @File_Name: GUIplus
# @Author: lyq
# @Time: 2022-08-25 9:33
# @Software: Pycharm
from PyQt5.QtWidgets import QMainWindow
import GUI


class Config:
    def __init__(self, ui: GUI.Ui_MainWindow):
        self.theme = ui.plainTextEdit.toPlainText()
        self.filterlist = ui.plainTextEdit_4.toPlainText().replace("，", ",").split(',')
        self.indexlist = ui.plainTextEdit_2.toPlainText().replace("，", ",").split(',')
        self.lastquarter = ui.plainTextEdit_3.toPlainText()
        if ui.radioButton_2.isChecked():
            self.custom_stockpool = 1
        else:
            self.custom_stockpool = 0
        self.quarternum = int(ui.plainTextEdit_5.toPlainText())
        self.threshold = float(ui.plainTextEdit_6.toPlainText())
        self.threshold2 = float(ui.plainTextEdit_9.toPlainText())
        self.qnum_1 = int(ui.plainTextEdit_7.toPlainText())
        self.qnum_2 = int(ui.plainTextEdit_8.toPlainText())
        if ui.radioButton_12.isChecked():
            self.auto = 1
        else:
            self.auto = 0
        self.med2 = ui.checkBox.isChecked()
        if ui.radioButton_3.isChecked():
            self.type = '中信'
        elif ui.radioButton_4.isChecked():
            self.type = '申万'
        elif ui.radioButton_5.isChecked():
            self.type = 'Wind1'
        elif ui.radioButton_6.isChecked():
            self.type = 'Wind2'
        else:
            self.type = '中信'
        self.filter1only = ui.checkBox_3.isChecked()
        self.alwaysfilter1 = ui.checkBox_4.isChecked()


def get_params(ui: GUI.Ui_MainWindow):
    configs = Config(ui)
    return configs
