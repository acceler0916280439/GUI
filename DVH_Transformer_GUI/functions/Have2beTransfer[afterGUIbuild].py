from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import threading

# ***以下函式的內容，在GUI設計完成後必須自行添加至GUI的main檔案內***

from functions.Self_Function import *  # (此行必須添加)


def __init__(self):
    self.ROI_selected_record = []

def retranslateUi(self, Dialog):
    self.ROI_check_Button.clicked.connect(self.ROIButtonClicked)
    self.ROI_uncheck_Button.clicked.connect(self.ROIUnclickButton)
    self.upload_Button.clicked.connect(self.ImportButtonClicked)
    self.diliver_Button.clicked.connect(self.VolDiliverButtonClicked)

# 設定視窗圖標
# if __name__ == "__main__":
#     import os
#     os.chdir(os.path.dirname(__file__)) # 將工作目錄變為當前執行文件所在的絕對路徑
#     DVH_Figure_Generator.setWindowIcon(QtGui.QIcon('icons/takodachi.ico'))

def ImportButtonClicked(self):
    _translate = QtCore.QCoreApplication.translate
    try:
        # 開啟檔案對話視窗 (選擇dvh檔)
        filename, filetype = QtWidgets.QFileDialog.getOpenFileName()
        if filename:
            print('Current work directory:', filename)
            self.inpath_lineEdit.setText(filename)
            self.process_label.setText(_translate("Dialog",
                                                  "<html><head/><body><p align=\"center\"><span style=\" font-weight:600; color:#dcdcdc;\">上傳中，請稍後...</span></p></body></html>"))
            TransTTD, TTD, TDP, ROIDU, ROIDP, ROIN = read_dvh(filename)
            self.process_label.setText(_translate("Dialog",
                                                  "<html><head/><body><p align=\"center\"><span style=\" font-weight:600; color:#dcdcdc;\">資料上傳完畢</span></p></body></html>"))
            layout = self.ROICheckbox(ROIN)
            layout.addWidget(self.ROI_scroll)

            # 用於後續插入列(column)資料
            Transpose_TTD = np.transpose(TransTTD).tolist()

            pathchar = filename.split('/')[:-1]
            self.savepath = "/".join(pathchar)
            self.TransTTD = Transpose_TTD
            self.TTD = TTD
            self.TDP = TDP
            self.ROIDU = ROIDU
            self.ROIDP = ROIDP
            self.ROIN = ROIN
    except:
        self.inpath_lineEdit.setText('dvh檔案不存在或是路徑錯誤')
        self.process_label.setText(_translate("Dialog",
                                              "<html><head/><body><p align=\"center\"><span style=\" font-weight:600; color:#dcdcdc;\">錯誤警告！</span></p></body></html>"))


def ROICheckbox(self, ROIN):
    form_layout = QtWidgets.QFormLayout()
    self.ROI_groupBox = QtWidgets.QGroupBox()
    print('\r\nROI in dvh file:')
    for n in range(len(ROIN)):
        New_ROI = QtWidgets.QCheckBox(ROIN[n])
        form_layout.addRow('%d.' % n, New_ROI)
        print('%d.' % n, New_ROI.text())
    self.ROI_groupBox.setLayout(form_layout)  # 將此layout作為ROI_groupBox的子類
    self.ROI_scroll.setWidget(self.ROI_groupBox)
    layout = QtWidgets.QVBoxLayout()
    return layout


def ROIButtonClicked(self):
    # _translate = QtCore.QCoreApplication.translate
    try:
        # 遍歷 ROI_groupBox的子類中的所有 checkbox物件
        self.ROI_selected_list = []
        for checkbox in self.ROI_groupBox.findChildren(QtWidgets.QCheckBox):
            if checkbox.isChecked() == True:
                self.ROI_selected_list.append(checkbox.text())
        # print('ROI selected: ', self.ROI_selected_list)

        # 連動至 Table 的功能
        # 首先將 Table 中的 default row 移除
        if self.ROI_selected_table.verticalHeaderItem(0).text() == "Default":
            self.ROI_selected_table.removeRow(self.ROI_selected_table.rowCount() - 1)
        numofROI = len(self.ROI_selected_list)  # 使用者選定的ROI數量
        # print('ROI num:', numofROI)
        if numofROI == 0:  # 當ROI勾選框被清空時，如果按下確認按鈕則回歸默認－"Default"
            self.ROI_selected_table.setRowCount(1)  # 只保留單一個row
            self.ROI_selected_table.setVerticalHeaderLabels(['Default'])
            self.ROI_selected_table.clearContents()

        # 除了默認狀態外，判斷當前table是否已存在新增的ROI row
        elif self.ROI_selected_table.rowCount() >= 1:
            # print(self.ROI_selected_table.rowCount())
            RVC = 0  # Remove Volume Count 已刪除的 ROI vol. 欄位計數
            for i in range(self.ROI_selected_table.rowCount()):  # 以當前table中存在的行數判斷
                Pre_ROI = self.ROI_selected_record[i]
                # print(Pre_ROI)
                if Pre_ROI not in self.ROI_selected_list:
                    self.ROI_selected_table.removeRow(i - RVC)  # 清除不存在當前ROI選項中的vol數值
                    RVC += 1

        # 對 Table 進行增刪
        for i in range(numofROI):  # 遍歷已選擇的ROI
            # cur_ROI = self.ROI_selected_list[i]
            position = self.ROI_selected_table.rowCount()  # 當前table中的row數量
            if position == numofROI:  # 如果當前欄位的數量 已經等於 使用者選擇的ROI數量，則不改變欄位數量
                break
            elif position < numofROI:  # 當前Table中存在的row數量 < 使用者選定的ROI數量
                # print('sum:', position)
                self.ROI_selected_table.insertRow(position)  # 插入新的一個row
            elif position > numofROI:  # 當前Table中存在的row數量 > 使用者選定的ROI數量
                # print('remove position num:', position)
                self.ROI_selected_table.setRowCount(numofROI)  # 將Table中的row數量與 ROI選定數量 同步
                # removeCount = position - numofROI
                # self.ROI_selected_table.removeRow(removeCount)

        # 增刪完row後，統一為每個row增加ROI label
        self.ROI_selected_table.setVerticalHeaderLabels(self.ROI_selected_list)
        self.ROI_selected_record = self.ROI_selected_list[:]
    except:
        print('發生例外錯誤！')
        pass


def ROIUnclickButton(self):
    try:
        for checkbox in self.ROI_groupBox.findChildren(QtWidgets.QCheckBox):
            if checkbox.isChecked() == True:
                checkbox.setChecked(False)
    except:
        pass


def VolDiliverButtonClicked(self):
    try:
        numofROI = len(self.ROI_selected_list)
        if numofROI == 0:
            print('您並未選擇任何ROI，請確認是否確實勾選ROI項目')
        elif numofROI != 0:
            ROI_dataframe = transfer2csv(self.TransTTD, self.TDP,
                                         self.ROIDU, self.ROIDP,
                                         self.ROIN, self.ROI_selected_list,
                                         self.savepath)
            # 取得使用者填入的 ROI volume
            volumes = []
            for i in range(numofROI):
                # 偵測Table欄位中是否為空值
                CurTableItem = self.ROI_selected_table.item(i, 0)
                if CurTableItem == None:
                    print('已存在的欄位不可為空白')
                    break
                elif CurTableItem.text() == "":
                    print('已存在的欄位不可為空白')
                    break
                else:
                    volume = CurTableItem.text()
                    volumes.append(float(volume))

            # plot_dvh_curve(self.ROIN, self.TDP, self.TTD, ROI_dataframe,
            # self.ROI_selected_list, volumes, self.savepath)
            # 為此函式新增一個執行序thread
            dvh_thread = threading.Thread(target=plot_dvh_curve(self.ROIN, self.TDP, self.TTD, ROI_dataframe,
                                                                self.ROI_selected_list, volumes, self.savepath))
            dvh_thread.start()  # 執行此thread的目標任務target function

            print('Your selected ROI:', self.ROI_selected_list)
            print('Your input ROI volume:', volumes)
            print('圖表已生成~')

    except:
        print('發生錯誤：ROI vol.輸入欄位內均需為數字 (也可能是發生例外錯誤)')
        pass

# ***----------------------------------------------------***