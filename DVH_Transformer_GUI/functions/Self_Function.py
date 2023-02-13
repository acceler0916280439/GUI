# from PyQt5 import QtCore, QtGui, QtWidgets

import os
import shutil
import csv
import pandas as pd
import plotly.graph_objects as go
import warnings
import numpy as np
import re
from plotly.subplots import make_subplots
# from PyQt5.QtWebEngineWidgets import QWebEngineView
warnings.filterwarnings("ignore")

# 用於執行DVH轉換程序之Function (用於被主程式呼叫)

def hasNumber(stringVal):
    '''用以判斷字串當中是否包含數值，只要包含任意數值便回傳True'''
    isValues = [elem.isdigit() for elem in stringVal]
    valueNum = 0
    for string in isValues: # 計算True出現的次數
        if string == True:
            valueNum += 1
    if valueNum > len(stringVal)//2:
        return any(elem.isdigit() for elem in stringVal)

def transpose(list1):
    '''用於轉置type: list 參數之矩陣'''
    return [list(row) for row in zip(*list1)]

def isfloat(num):
    pattern = re.compile(r'(.*)\.(.*)\.(.*)')
    if pattern.match(num):
        return False
    return num.replace(".", "").isdigit()

def read_dvh(path):
    # dvhfile = glob.glob(os.path.join(path, '*.dvh'))[0]
    dvhfile = path
    csvfile = dvhfile.replace('.dvh', '.csv')
    # csvname = csvfile.split('/')[-1]
    try:
        shutil.copy(dvhfile, csvfile)  # convert dvh file to csv file.
    except:
        pass

    n = 0
    ROINamelist = []  # 儲存所有ROI之名稱
    DoseVallist = []  # 儲存個別ROI之劑量數值
    DosePercentlist = []  # 儲存個別ROI之劑量%
    TotalDoselist = []  # 儲存所有ROI之劑量數值
    TotalDosePerclist = []  # 儲存所有ROI之劑量%
    with open(csvfile, newline='') as dvhinfo:
        rows = csv.reader(dvhinfo)
        for row in rows:
            if not row or row[0] == '\t':
                # print('Row: %d 為空白欄位' % (n))
                if len(DoseVallist) == 0: # 判斷例外情況：dvh檔案中有記錄名稱但沒有數值資料
                    ROINamelist.remove(CurROI) # 剔除無資料的ROI
                    continue

                DoseVallist.reverse()  # 劑量由大至小排序
                DosePercentlist.reverse()  # 劑量%依據劑量之排序重新排序

                if len(DoseVallist) < 402:
                    print('Row:%d' %n)
                    DoseVallist = list(map(float, DoseVallist))
                    DosePercentlist = list(map(float, DosePercentlist))
                    DVList, DPList = interpolate_till402(DoseVallist, DosePercentlist)
                    DVList = list(map(str, DVList))
                    DPList = list(map(str, DPList))
                else:
                    DVList = DoseVallist
                    DPList = DosePercentlist

                TotalDoselist.append(DVList)  # 儲存該ROI之劑量數值
                TotalDosePerclist.append(DPList)
                DoseVallist = []  # 重置ROI之劑量數值
                DosePercentlist = []
                n += 1
                continue

            #         print('%d : '%(n),row)
            row = row[0]
            if 'RoiName' in row:
                # print('%d : ' % (n), row)
                CurROI = row.split(':')[-1]
                ROINamelist.append(CurROI)
            if 'Dose unit' in row:
                # print('%d : ' % (n), row)
                D_unit = row.split(':')[-1]
            if hasNumber(row) == True:
                # print('%d : ' % (n), row)
                DoseVal = row.split('\t')[0]
                DosePercent = row.split('\t')[1]
                DoseVallist.append(DoseVal)
                DosePercentlist.append(DosePercent)
            n += 1
    if len(TotalDoselist) < len(ROINamelist):
        DoseVallist.reverse()  # 劑量由大至小排序
        DosePercentlist.reverse()  # 劑量%依據劑量之排序重新排序
        TotalDoselist.append(DoseVallist)  # 儲存該ROI之劑量數值
        TotalDosePerclist.append(DosePercentlist)
    TransTTDose = transpose(TotalDoselist)  # 轉置以便於轉換為pandas dataframe資料格式
    ROIDoseUnit = [ROI + ':' + D_unit for ROI in ROINamelist]
    ROIDosePercent = [ROI + ': Vol. [%]' for ROI in ROINamelist]
    # print('''ROI數量:{}
    # 總儲存的Dose資料量:{}
    # 最後一筆ROI的vol:{}
    # 最後一筆ROI的 %:{}
    # 轉置後的TTD:{}'''.format(len(ROINamelist), len(TotalDosePerclist),
    #                         len(DoseVallist), len(DosePercentlist), len(TransTTDose)))

    return TransTTDose, TotalDoselist, TotalDosePerclist, ROIDoseUnit, ROIDosePercent, ROINamelist

def transfer2csv(TransTTD, TDP, ROIDU, ROIDP, ROIN, ROI_Select, savepath):
    '''params:
    轉置之TotalDoselist, TotalDosePerclist, ROIDoseUnit, ROIDosePercent'''
    # newDF = pd.DataFrame(TransTTD, columns=ROIDU)
    newDF = pd.DataFrame()
    selected_DL = []
    selected_DPL = []
    position = 1
    for i in range(len(ROI_Select)):
        cur_index = ROIN.index(ROI_Select[i]) # 取得指定ROI在所有ROI清單中的位址
        # 將清單中的字串(str)轉為數字(float)
        # 數字由大到小排序
        number_DL = list(map(float, TransTTD[cur_index]))
        numberDPL = list(map(float, TDP[cur_index]))
        # DL = number_DL
        # DPL = numberDPL
        DL, DPL = interpolate_per_cGy(number_DL, numberDPL) # 線性插值
        selected_DL.append(DL)
        selected_DPL.append(DPL)

        # 建立該ROI的資料表單 (依迴圈向右堆疊)
        emptyF0 = pd.DataFrame(columns=[np.nan])
        DLframe = pd.DataFrame(DL, columns=[ROIDU[cur_index]])
        DPframe = pd.DataFrame(DPL, columns=[ROIDP[cur_index]])
        emptyF1 = pd.DataFrame(columns=[np.nan])
        NDF = pd.concat([emptyF0, DLframe, DPframe, emptyF1], axis=1)
        newDF = pd.concat([newDF, NDF], axis=1)

    # newDF.to_csv(os.path.join(savepath, 'newDVH_0.csv'), index=False)
    return newDF, selected_DL, selected_DPL

def plot_dvh_curve(ROIN, TDP, TTD, preDataframe, ROI_Select, ROI_Select_VOL, savepath):
    '''Params: ROINamelist, TotalDosePerclist, TotalDoselist'''

    # ----------Dose與cc值組成的DVH curve----------
    print('圖表生成中...')
    DVH_CC_DOSE = go.Figure()
    position = 1
    if not os.path.isdir(savepath):
        os.makedirs(savepath)
    for i in range(len(ROI_Select)):
        # 取得並計算相關數值
        cur_ROI_VOL = ROI_Select_VOL[i]
        numberDPL = TDP[i]
        number_DL = TTD[i]
        VOLCC = [numberDPL[i] * cur_ROI_VOL * 0.01 for i in range(len(numberDPL))]  # ROI體積 * 劑量百分比 * %

        # 將填入的vol[cm^3]數值以及計算出的ROI vol[cc]插入之前建立的表單中
        ROIVFcm = pd.DataFrame([cur_ROI_VOL], columns=['ROI_vol.[cm^3]'])
        ROIVFcc = pd.DataFrame(VOLCC, columns=['ROI_vol[cc]'])
        preFrame1 = preDataframe.iloc[:, :position]
        preFrame2 = preDataframe.iloc[:, position:position+2]
        preFrame3 = preDataframe.iloc[:, position+2:]
        preDataframe = pd.concat([preFrame1, ROIVFcm, preFrame2, ROIVFcc, preFrame3], axis=1)
        position += 6

        # 繪製dvh
        DVH_CC_DOSE.add_trace(go.Scatter(x=number_DL, y=VOLCC,
                                         name=ROI_Select[i],
                                         mode='lines'))
    try:
        preDataframe.to_csv(os.path.join(savepath, 'newDVH.csv'), index=False)
        print('勾選的ROI csv檔案 已生成')
    except:
        print('無法生成ROI csv file (請確認是否開啟:newDVH.csv，若是，請關閉再嘗試。)')

    DVH_CC_DOSE.update_layout(
        xaxis_title='Plan dose: ID2 [cGy]',
        yaxis_title='Volume [cc]',
        width=900, height=600, )
    # DVH_CC_DOSE.show()

    # 儲存dvh影像
    DVH_CC_DOSE.update_layout({'paper_bgcolor': 'rgba(0, 0, 0, 0)'})  # 設定背景為透明
    DVH_CC_DOSE.write_image(os.path.join(savepath, "DVH_Dose_cc.png"))


    # ----------Dose與 vol% 值組成的DVH curve----------
    DVH_CC_P = go.Figure()
    for i in range(len(ROI_Select)):
        cur_index = ROIN.index(ROI_Select[i])  # 取得指定ROI在所有ROI清單中的位址
        # cur_ROI_VOL = ROI_Select_VOL[i]
        # numberDPL = list(map(float, TDP[cur_index]))  # 將清單中的字串轉為數字
        # number_DL = list(map(float, TTD[cur_index]))
        numberDPL = TDP[i]
        number_DL = TTD[i]
        # VOLCC = [numberDPL[i] * cur_ROI_VOL * 0.01 for i in range(len(numberDPL))]

        DVH_CC_P.add_trace(go.Scatter(x=number_DL, y=numberDPL,
                                      name=ROI_Select[i],
                                      mode='lines'))

    DVH_CC_P.update_layout(
        xaxis_title='Plan dose: ID2 [cGy]',
        yaxis_title='Volume [%]',
        width=900, height=600, )

    # DVH_CC_P.show()

    DVH_CC_P.update_layout({'paper_bgcolor': 'rgba(0, 0, 0, 0)'})  # 設定背景為透明
    DVH_CC_P.write_image(os.path.join(savepath, "DVH_Dose_Percent.png"))

    figures_to_html([DVH_CC_DOSE, DVH_CC_P], savepath)

def figures_to_html(figs, savepath):
    print('將 DVH figure 儲存為 html file...')
    filename = os.path.join(savepath, "dashboard.html")
    with open(filename, 'w') as dashboard:
        dashboard.write("<html><head></head><body>" + "\n")
        for fig in figs:
            inner_html = fig.to_html().split('<body>')[1].split('</body>')[0]
            dashboard.write(inner_html)
        dashboard.write("</body></html>" + "\n")
    os.system(filename)

def interpolate_per_cGy(DL, DPL):
    ''' 以Dose:1cGy為單位插入新值 '''
    Max_Dose = int(DL[0])+1000
    for i in range(Max_Dose): # 執行至該ROI之最大劑量數值為止
        if i == len(DL)-1: # 若判斷到最後一個位址，則不再內插
            break
        else:
            start_D = DL[i]
            end_D = DL[i+1]
            diff = start_D - end_D
        if abs(diff) <= 1:
            pass
        elif abs(diff) > 1: # 前後差值>1，則插入新值
            start_P = DPL[i]
            end_P = DPL[i + 1]

            if diff > 0: # 差值為正數
                interD = start_D-1 # 欲內插的新劑量值 (由於排序為大到小，因此-1)
            elif diff < 0: # 差值為負數
                interD = start_D + 1

            add_P = ((end_P - start_P) / (end_D - start_D)) * (interD - start_D)
            interP = start_P + add_P # 內插的新劑量百分比值

            # 往該位址插入新值，原本於該位址的數值以及後續的數值，均往後順延
            DL.insert(i+1, interD)
            DPL.insert(i+1, interP)

    return DL, DPL

def interpolate_till402(DL, DPL):
    ''' 以Dose:1cGy為單位插入新值 '''
    Max_Dose = int(DL[0])
    for i in range(Max_Dose):
        if len(DL) >= 402: # 插入資料直到筆數=402筆為止
            break
        else:
            start_D = DL[i]
            end_D = DL[i+1]
            diff = start_D - end_D
        if abs(diff) <= 1:
            pass
        elif abs(diff) > 1: # 前後差值>1，則插入新值
            start_P = DPL[i]
            end_P = DPL[i + 1]

            if diff > 0: # 差值為正數
                interD = start_D-1 # 欲內插的新劑量值 (由於排序為大到小，因此-1)
            elif diff < 0: # 差值為負數
                interD = start_D + 1

            add_P = ((end_P - start_P) / (end_D - start_D)) * (interD - start_D)
            interP = start_P + add_P # 內插的新劑量百分比值

            # 往該位址插入新值，原本於該位址的數值以及後續的數值，均往後順延
            DL.insert(i+1, interD)
            DPL.insert(i+1, interP)

    return DL, DPL
