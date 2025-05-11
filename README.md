# file-browser-cli

一個基於 Typer 與 Textual 的互動式檔案瀏覽與建立工具。

## 特色

- 以 CLI 方式啟動互動式 TUI 檔案瀏覽器
- 可選擇檔案或資料夾並自動建立新檔案
- 支援自動建立父資料夾
- 直覺的指令列操作

## 安裝

```bash
pip install file-browser-cli
```

## 使用方式

```bash
browser-cli code create
```

或

```bash
python -m file_browser_cli.cli code create
```

## 依賴

- [Typer](https://typer.tiangolo.com/)
- [Textual](https://textual.textualize.io/)

## 授權

MIT