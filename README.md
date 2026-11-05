# Pilot Survey — 智慧公民 AI 改善專案提案系統

這是可在本機運作的 **AI PoC 提案表單系統**，以員工填寫的 **目前狀況（As-Is）** 與 **預期改善狀況（To-Be）** 為核心，並加入簡潔的實施節點（時間、檢查點）、效益估算和主管審核紀錄。

## 功能

- 專案基本資料：名稱、部門、提案人、直屬主管及日期。
- **As-Is**：目前業務流程、主要問題與瓶頸。
- **To-Be**：AI 導入後的工作方式及預期改善目標。
- 預估效益：每次處理時間、每月作業次數、預估年度節省工時及投入成本。
- **實施節點**：新增／刪除里程碑，記錄完成日期、檢查點及結果。
- 主管意見、主管審核和高階管理層核准狀態（僅為記錄欄位）。
- 儲存於目前瀏覽器、匯出含「專案提案」及「實施節點」兩張工作表的真正 Excel `.xlsx`。

## 系統要求

Windows 10/11 或 macOS／Linux、Python 3.8 以上，以及 Chrome、Edge 或其他現代瀏覽器。無須安裝 Python 第三方套件，無須 Node.js 或資料庫。

## Windows 安裝

可從 GitHub 的 **Code → Download ZIP** 下載程式碼，或使用 Git：

```powershell
git clone https://github.com/PMPai/Pilot-Survey.git C:\Pilot-Survey
```

如果使用 ZIP，解壓縮並確認 `server.py`、`index.html`、`app.js`、`style.css` 都位於 `C:\Pilot-Survey`。

開啟 PowerShell：

```powershell
cd C:\Pilot-Survey
py server.py
```

若 `py` 指令不可用，改用 `python server.py`。接著在瀏覽器開啟：

**http://localhost:3333**

停止服務：在 PowerShell 按 **Ctrl+C**。

## macOS / Linux

```bash
git clone https://github.com/PMPai/Pilot-Survey.git
cd Pilot-Survey
python3 server.py
```

macOS 也提供 `start.command`，可在終端機使用 `sh start.command` 啟動。

## 操作流程

1. 填寫專案基本資料、現況（As-Is）及預期狀況（To-Be）。
2. 估算目前和改善後每次處理時間，以及每月執行次數。
3. 增加實施里程碑，填入預定日期及檢查點。
4. 點選「儲存到本機」，或使用「匯出 Excel」下載 `.xlsx`。
5. 提案先與直屬主管討論；**正式啟動 PoC 前須取得高階管理層批准**。

年度預估節省工時 =（目前每次處理分鐘數 − 預期每次處理分鐘數）× 每月次數 × 12 ÷ 60。這是預期效益，**不等於已確認的現金收益或 ROI**。

## 資料及安全限制

- 伺服器僅監聽 `127.0.0.1:3333`，不開放其他設備連線。
- 表單資料存放於目前瀏覽器的 `localStorage`，不會自動同步；清除瀏覽資料可能導致資料遺失，建議定期匯出 Excel。
- Excel 在本機 Python 服務內生成，不連接外部 API。
- 「現況流程圖」檔案欄位**只顯示檔名**，不會保存附件，也不會加入 Excel。
- 審核狀態可由本機使用者選擇，**並非有身份驗證的正式電子簽核**。
- 沒有登入、權限管理或加密儲存，不適合作為企業正式多用戶簽核平台。
- 這是 **Public** GitHub 倉庫。切勿提交客戶資料、公司機密、密碼、API 金鑰或實際業務提案。

## 專案檔案

```text
Pilot-Survey/
├── index.html      # HTML 提案表單
├── style.css       # 響應式樣式
├── app.js          # 表單、節點和 Excel 匯出前端
├── server.py       # 本機 Port 3333 服務及 XLSX 生成
├── start.command   # macOS 啟動腳本
└── README.md       # 安裝及使用說明
```

## 背景

本系統用於「智慧公民」AI 導入框架中的驗證階段：鼓勵員工從工作問題提出方案，經主管討論、業務價值篩選及正式批准後進行 PoC，再根據可測量的成效與員工學習成果決定是否推廣。