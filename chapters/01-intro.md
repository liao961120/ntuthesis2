簡介
========================

`ntuthesis2` 是透過 [Pandoc](https://github.com/jgm/pandoc) 建立的論文模板，讓使用者能透過 (Pandoc) **Markdown** 語法撰寫論文 (無須安裝與了解 LaTeX!!)。此專案的前身是 [R 套件](https//github.com/liao961120/ntuthesis)，但由於 R + Bookdown + LaTeX 的設定相對龐雜，對非 R 的使用者而言有相當難度，因此改以 Python 3 + Pandoc 實作 (這兩者在 Windows 與 Unix 上的安裝都相當容易)，希望讓更多人能夠使用。

輸出範例：

- [中文 PDF](https://yongfu.name/ntuthesis2/thesis-zh.pdf)
- [英文 PDF](https://yongfu.name/ntuthesis2/thesis-en.pdf)


安裝
------------------

只要電腦上有 Python (3.5 以上) 即可使用 (無須安裝其它東西)

1. Clone 或[下載](https://github.com/liao961120/ntuthesis2/archive/main.zip) 這個 repo

2. 安裝相關套件： 
    
    ```bash
    pip install -r requirements.txt 
    ```

3. 執行主程式：

    ```bash
    python3 main.py  
    # python main.py 
    ```

    第一次執行主程式時，會自動下載 Pandoc 執行檔 (置於 `pandoc/` 當中)，之後便會出現互動式界面引導使用者輸出論文。


使用
------------------

`ntuthesis2` 運作的流程如圖：

![運作想法](https://img.yongfu.name/ntuthesis/design.png){#fig:design}

由於 LaTeX ([TeX Live](https://www.tug.org/texlive) 或 [MikTeX](https://miktex.org) 的安裝十分令人頭痛，而且即使安裝完成，後續生成 PDF 的過程仍會常常出錯。為了儘量避開這些問題，`ntuthesis2` 在設計上結合 [Overleaf](https://www.overleaf.com)，讓使用者能將輸出的 `.tex` 檔透過 (免費) 網路服務輸出成 PDF 檔 (上圖綠色箭號流程)。當然，若使用者個人電腦上已有 LaTeX，也可直接在電腦上輸出 PDF。此外，`ntuthesis2` 也提供一個相當簡約的 `.html` 輸出格式，目的是方便在撰寫時預覽論文 (因為 LaTeX 的輸出相當耗時)。


### 輸出論文

```bash
/
├── front_matter.yml       # 論文封面設定
├── thesis-setup.yml       # 論文格式設定、摘要、謝辭
├── ref.bib                # 引用文獻 (可直接覆寫)
├── cite-style.csl         # Citation style
├── chapters/              # 章節內容 (Markdown 文件), 章節照檔名排序
│   ├── 01-intro.md         
│   ├── 02-literature.md            
│   └── 90-references.md       # 這個檔案不須更改 (除了想更改標題)
├── figures/               # 論文用到的圖片 (需用相對路徑，以 repo 根目錄為準)
│   ├── os_meme.png            # 範例圖片   
│   └── watermark.png          # PDF 論文右上角的浮水印
├── fonts/                 # 字體檔
├── latex/                 # 模板
├── pandoc/                # Pandoc 執行檔 (程式會自動下載)
├── output/                # 輸出論文 (PDF/HTML/Overleaf)
├── ntuthesis.cls          # LaTeX 格式設定 (論文封面)
├── requirements.txt       # Python dependencies
├── main.py                # 互動式主程式 (安裝 Pandoc、輸出論文)
└── README.md
```

上方是論文模板 (即此 repo) 的檔案結構及其內容說明，下方為論文的輸出說明 (檔案對應至上方的結構):

1. 製作論文封面 (封面、口試委員審定書)
    1. 在 `front_matter.yml` 修改相關資訊 (姓名、日期、指導教授...)
    2. 執行互動主程式 `python3 main.py`

        - 若電腦上**有 LaTeX**，在終端機依序輸入 `pdf`, `english` (或 `chinese`) 與 `front_matter`：

            ```txt
            [USER] Select output format [html / pdf / overleaf / exit] > pdf 
                [USER] Select language [chinese / english] > english
                [USER] Which to output [thesis / front_matter] > front_matter
            ...
            [OUTPUT] output/front_matter.pdf
            ```

        - 若**無 LaTeX**，
        
            1. 在終端機依序輸入 `overleaf`, `english` (或 `chinese`)：

                ```txt
                [USER] Select output format [html / pdf / overleaf / exit] > overleaf
                    [USER] Select language [chinese / english] > english
                ...
                [OUTPUT] output/overleaf.zip
                ```
            
            2. 這時便可將 `output/overleaf.zip` 上傳至 [Overleaf](https://overleaf.com) (需註冊帳號)
                1. 上傳之後，Overleaf 會自動解壓展開檔案，請點選 `front_matter.tex` (這時自動 Compile 應會失敗)
                2. 點選左方 Menu，Compiler 選擇 `XeLaTeX` (見下圖 @fig:overleaf)
                3. 點選畫面左上方 `Recompile`
                4. 輸出完成後，下載 PDF 檔 (`Recompile` 右側的下載鍵) 至 `output/` 並將檔名命名為 `front_matter.pdf`
2. 輸出完整論文
    1. 編輯論文：
        - 在 `thesis-setup.yml` 設定論文相關格式、撰寫摘要、謝辭
        - 在 `chapters/` 裡的 `.md` 檔編輯論文章節。若需要用到圖片，需將圖片置於 `figures/`，並以相對路徑連結圖片，例如，`figures/os_meme.png` (相對路徑以**此 repo 根目錄作為起點**)
        - 將文獻管理軟體 (EndNote, Zotero, JabRef, ...) 中的引用資料輸出成 `.bib` 檔，取代掉原本的 `ref.bib`
        - 若要修改引用格式 (原本的 `cite-style.csl` 為 APA 格式)，可至 <https://www.zotero.org/styles> 或 <https://github.com/citation-style-language/styles> 下載需要的格式 (`.csl`檔)，取代掉原本的 `cite-style.csl`
    2. 執行互動主程式 `python3 main.py`
        - 若電腦上**有 LaTeX**，在終端機依序輸入 `pdf`, `english` (或 `chinese`) 與 `thesis`：

            ```txt
            [USER] Select output format [html / pdf / overleaf / exit] > pdf 
                [USER] Select language [chinese / english] > english
                [USER] Which to output [thesis / front_matter] > thesis
            ...
            [OUTPUT] output/thesis.pdf
            ```

        - 若**無 LaTeX**，
            1. 請依照上方**輸出封面**的方式操作主程式
            2. 將 `output/overleaf.zip` 上傳至 [Overleaf](https://overleaf.com) 後，
                1. 點選 `thesis.tex`，並將 Compiler 設為 `XeLaTeX`
                2. 點選左上方新增資料夾 (New Folder) `output` 並將 `front_matter.pdf` 放入 `output/`
                3. Recompile 後下載輸出的 PDF 檔


![將 Compiler 設為 `XeLaTex`](https://img.yongfu.name/ntuthesis/overleaf.png){#fig:overleaf}


### 論文撰寫：文內超連結

|      | 定義                              |   引用    |
|:----:|-----------------------------------|:---------:|
| 段落 | `Section Two {#sec:2}`            | `@sec:id` |
| 圖片 | `![Caption.](image.png){#fig:id}` | `@fig:id` |
| 公式 | `$$ y = mx + b $$ {#eq:id}`       | `@eq:id`  |
| 表格 | `Table: Caption. {#tbl:id}`       | `@tbl:id` |

Table: Cross-reference 語法. {#tbl:cross-ref}

詳見 [pandoc-xnos](https://github.com/tomduck/pandoc-xnos)。


### 論文撰寫：文獻引用

文獻引用是透過 `.bib` 檔裡的書目資料以及 [Pandoc's Citation syntax](https://pandoc.org/MANUAL.html#citation-syntax) 達成。`.bib` 檔的產生方式可以由 Endnote, Zotero, JabRef 等書目管理軟體匯出。匯出後，將檔名命名為 `ref.bib` 取代根目錄中原本的檔案。

下方是 `.bib` 內的一篇引用資料 (一個 `.bib` 可以有很多篇)：

```bib
@article{leung2008,
  title = {Multicultural Experience Enhances Creativity: {{The}} When and How.},
  volume = {63},
  issn = {1935-990X(Electronic),0003-066X(Print)},
  doi = {10.1037/0003-066X.63.3.169},
  number = {3},
  journaltitle = {American Psychologist},
  date = {2008},
  pages = {169-181},
  keywords = {*Cognition,*Creativity,
    *Culture (Anthropological),
    *Experiences (Events),Multiculturalism},
  author = {Leung, Angela Ka-yee and 
    Maddux, William W. and 
    Galinsky, Adam D. and Chiu, Chi-yue}
}
```

其中第一行的 `leung2008` 即為 **citation key**。Pandoc 透過 `@citekey` (e.g., `@leung2008`) 在 `.md` 檔中插入 citation。匯出論文時，Pandoc 會依據 `cite-style.csl` 的格式自動產生引用文獻。下方為一些文獻引用語法的範例，詳見 [Pandoc's Citation syntax](https://pandoc.org/MANUAL.html#citation-syntax)。

|          | 內文                                 | 輸出 (根據 `.csl` 改變)            |
|:--------:|--------------------------------------|------------------------------------|
|   單篇   | `[@stanford2008]`                    | [@stanford2008]                    |
|   多篇   | `[@stanford2008; @kassin2017]`       | [@stanford2008; @kassin2017]       |
| 文內引用 | `@stanford2008 says ...`             | @stanford2008 says ...             |
| 隱藏作者 | `Stanford says ... [-@stanford2008]` | Stanford says ... [-@stanford2008] |
| 其它註解 | `see @kassin2017, pp. 33-35`         | see @kassin2017, pp. 33-35         |

Table: 文獻引用語法. {#tbl:citation}


尋求協助
--------------------

若有套件使用上的問題，可在 [GitHub](https://github.com/liao961120/ntuthesis2/issues) 回報。若沒有 GitHub 帳號，可透過 Email^[liao961120@gmail.com] 聯絡 [Yongfu Liao](https://yongfu.name)。


特別感謝
--------------------

此論文模板的封面是根據 [tzhuan/ntu-thesis](https://github.com/tzhuan/ntu-thesis) 修改而成。
