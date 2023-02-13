【GUI設計指南】
步驟：
1. 以QT designer 設計完 GUI 並儲存為ui檔 (.ui)

2. 透過下列代碼將ui檔轉換為py檔 (*表示為該專案的存放路徑與檔名)：
	pyuic5 -x *****.ui -o ******.py  # 生成對應的GUI主程式

3. 透過下列代碼將qrc檔轉換為py檔 (*表示為該專案的存放路徑與檔名)：
	pyrcc5 ****.qrc -o ****_rc.py # 生成儲存圖像資訊的程式碼 (需要與主程式放置於同個資料夾下)

4. 將所設計的功能與GUI做連結 (請自行搜尋想要呈現的功能的實現方式) 

5. 如果後續要修正GUI中的物件擺位或新增初始物件(ex: button, checkbox, ...etc)，需要再次執行步驟1~2 
* 透過步驟2執行轉檔後，在步驟4所添加的所有額外功能性程式碼將會消失，所以請做好備份，以便再次移植功能程式碼至GUI主程式。

# ------------------------------------------------------
【DVH_Transformer_GUI操作指南】

* 使用 DVH_Transformer_GUI 須具備的python package：
	1. pytest-shutil
	2. PyQt5
	3. plotly
	4. pandas
	5. numpy

步驟：
1. 點擊『選取檔案並上傳』，選取欲觀測的DVH檔案(.dvh)。

2. 在ROI select window中會呈現出該DVH檔案中的所有ROI。

3. 勾選欲觀測的ROI，並點擊『確認選擇』，在右側的ROI table中會出現相應的項目。

4. 在ROI table中填入對應的 ROI vol.[cm^3]數值，並點擊『送出』。  (送出後，請稍後至圖表跳出)

5. 程式會主動將『DVH figure.png, 歸納後的dvh文件.csv, DVH figure.html』存入input dvh file所在的資料夾

* 若要"一次性"取消所有已勾選的ROI，請點擊『移除勾選』。
* DVH_Transformer_GUI 之操作方式，也可觀看本人錄製的操作影片。
* 轉換後的數值以 1 cGy為單位 表示