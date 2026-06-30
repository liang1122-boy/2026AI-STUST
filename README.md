# 2026 AI - STUST 學習筆記

南臺科技大學 (STUST) 2026 AI 課程的個人練習與作業 repo，記錄從 Python 基礎到資料視覺化的學習過程。

---

## 環境需求

```bash
pip install matplotlib pandas openpyxl
```

中文字型預設使用 `Microsoft JhengHei`（Windows 內建）。

---

## 目錄結構

```
project/
├── hello.md                          # Markdown 練習
├── Week1/
│   ├── DAY2/                         # Python 基礎：變數、條件、邏輯、函式
│   ├── DAY3/                         # 迴圈、列表、檔案 I/O、matplotlib 圖表
│   └── DAY4/                         # Excel 讀取 + 真實人口資料分析
└── README.md
```

---

## Week 1

### DAY 2 — Python 基礎語法

主題：變數、型別、運算子、條件判斷、布林邏輯、函式與模組。

| 檔案 | 內容 |
|---|---|
| `變數教學.py` | 變數宣告、運算子、`type()` 查看型別 |
| `變數類型.py` | 同一變數放入 `int` / `float` / `str` 時的型別變化 |
| `四則運算.py` | 字串相加 (`+`) 的範例 |
| `輸入.py` | `input()` 取得使用者輸入，搭配 `float()` 做加法 |
| `布林比較.py` | `>`、`<`、`>=`、`<=`、`==` 比較運算子 |
| `邏輯.py` | `and`、`or` 布林邏輯運算 |
| `邏輯題目and.py` | 情境題：超商買珍奶（年齡 ∧ 金錢） |
| `邏輯題目or.py` | 情境題：出門帶傘（下雨 ∨ 大太陽） |
| `如果條件.py` | `if / elif / else` 三向分支 |
| `文字遊戲(手搓版).py` | 用 `input` + `if` 做簡單心情回應遊戲 |
| `畢氏定理.py` | 自訂函式 `畢氏定理(a, b)` 計算斜邊；展示 `import math as 數學` |
| `斜向拋射.py` | 計算飛行時間 / 最大高度 / 水平射程，使用 `math.radians`、`math.sin` |
| `main.py` | 跨檔 `import 畢氏定理` 模組呼叫範例 |

### DAY 3 — 迴圈、列表、檔案 I/O、matplotlib

主題：流程控制、容器型別、CSV 處理、基礎資料視覺化。

| 檔案 | 內容 |
|---|---|
| `for迴圈.py` | `range()` 與 list 迭代寫法 |
| `while迴圈.py` | `while` 配合 `time.sleep` 做倒數 |
| `列表.py` | List 宣告、索引取值、`len()`、`type()` |
| `列表的append.py` | `append` 收集資料再繪製二次函式折線圖 |
| `開啟檔案.py` | 原始 `open()` + `split()` 拆 CSV，理解編碼與分隔 |
| `台南人口統計.py` | 用 `csv.reader` + `dict(zip(header, row))` 讀取台南人口資料，畫出各區人口佔比圓餅圖 |
| `matplotlib 折線圖教學.py` | matplotlib `plt.plot` 入門 |
| `matplotlib改圖.py` | 加上中文字型、`xlim` / `ylim` / 標題 / 軸標籤 |
| `直方圖.py` | `plt.hist` 繪製成績分布 |
| `散步圖.py` | `plt.scatter` 散點圖 |
| `985ed9fd-…csv` | 台南市各區人口統計資料來源檔 |

### DAY 4 — Excel 讀取與人口分析作業

| 檔案 | 內容 |
|---|---|
| `data.xlsx` / `data.csv` | 湖西鄉（澎湖）逐月人口統計資料。註：兩個檔案內容相同，皆為 xlsx 二進位格式 |
| `作業-湖西鄉人口圖表統計.py` | **作業**：用 `pandas.read_excel` 讀入 65 個月的資料，計算「出生 − 死亡」的自然增加數，繪製單條長條圖：正成長朝上 (藍)，負成長朝下 (紅)，並以 `axhline(0)` 標出 0 軸 |

執行結果：65 個月中 19 個月正成長、39 個月負成長、7 個月持平。湖西鄉人口呈現自然減少趨勢。

---

## hello.md

Markdown 語法初體驗，練習標題與項目符號。

---

## 學習脈絡

```
DAY2 語法基礎  →  DAY3 迴圈 + 視覺化  →  DAY4 真實資料 + pandas
   (變數/條件)        (列表/檔案/plt)         (Excel/作業)
```

每個檔名都用中文命名，方便對照當天課程主題快速回頭翻閱。
