---
name: reference-docx-layout-verification
description: docx 排版/分页必须用本机 Word COM 无头渲染出 PDF 实测，不能靠字体度量推算；含仿宋行高、atLeast 陷阱、pymupdf 句柄、表尾幽灵页等实测结论。
metadata:
  type: reference
---

# 校验 .docx 排版与页数的唯一可靠办法：本机 Word 无头渲染

**Why:** 2026-09-22~23 改 6 份评优申报表排版时，我用 simfang.ttf 的 OS/2 typo 值（1.14×）建模算行高，
反复误判"不会裁切""是 2 页"，实际 Word 渲染是 3 页，白跑了十几轮。装上 Office 后改用真实渲染，
一次就定位到全部问题（"（1）"被裁、表尾幽灵页、意见行不等高）。**推算不可信，渲染才可信。**

**How to apply:** 任何涉及 docx 分页、行高、单元格裁切、"两页要对齐"的任务，先建这条链路再动手。

## 渲染链路

```python
import pythoncom, win32com.client as wc
app = wc.DispatchEx('Word.Application')   # 必须 DispatchEx，Dispatch 会附到用户已开的实例
app.Visible = False; app.DisplayAlerts = 0
d = app.Documents.Open(abspath, ReadOnly=True, AddToRecentFiles=False, Visible=False)
pages = d.ComputeStatistics(2)            # 2 = wdStatisticPages
d.ExportAsFixedFormat(abspath_pdf, 17)    # 17 = wdExportFormatPDF
d.Close(False); app.Quit(); pythoncom.CoUninitialize()
```
再用 `pymupdf` 出图用眼睛看：`pg.get_pixmap(dpi=100).save(...)`。

- 本机 Word：`C:\Program Files\Microsoft Office\Root\Office16\WINWORD.EXE`。
- **WPS 不能这么用**：`KWPS.Application` 的 CLSID 指向未安装时的 Word CLSID，COM 起不来；
  WPS 个人版也不支持 `--convert-to pdf`。
- **WPS 与 Word 对同一份 docx 报的页数会不同**（本例 WPS 报 3 页、Word 报 2 页）。
  以交付目标（学校用哪个软件打开）为准，别混着信。
- 用户可能正开着 Word：只操作**副本**，绝不杀 WINWORD 进程。

## 实测到的排版事实

| 事项 | 结论 |
|---|---|
| 仿宋单倍行距 | ≈ **1.29×字号**（14pt→18pt，12pt→15pt）。不是字体文件里的 1.14 倍 |
| `w:trHeight hRule="atLeast"` | 内容会自己撑高行，**把设定值调小无效**；要钉死只能 `exact`，而 exact 下超出即裁切 |
| Word `Row.Height` | 返回的是**设定值**，不是渲染高度。真实行高要从 PDF 量相邻表格横线间距 |
| 表格后那个必需段落 | 若没有 `<w:spacing w:line="20" w:lineRule="exact"/>`（≈1pt），页面填满后它会自己顶出**一个幽灵页**。WPS 建的文件常缺这个，Office 存过的才有 |
| 版心宽 vs 表宽 | 表格比版心宽时 Word 不报错，只是往两边溢出。让 `pgMar left=right=(pgSz-表宽)/2` 即两页边线自动对齐 |
| 中文字符宽度 | 1 字 = 1em，ASCII 数字/字母 = 0.5em（用 fontTools 读 hmtx 可精确算，但**只能判断横向溢出，判不了分页**） |

## 两个工具坑

- **pymupdf 打开 PDF 不 `close()`** 会占住句柄，下一轮 Word `ExportAsFixedFormat` 覆写同名 PDF 时报
  "无法保存此文件，因为它为只读文件"。导出前先 `os.remove(pdf)`，读完必 `close()`。
- 搜"最大可用高度"这类单调边界时，**`best` 不能初始化成起始值**：所有探测都失败时会把起点当成
  "已验证可用"报出来。我就是因此误报过一次"6 份都是 2 页"。必须每档当场渲染验证才算数。

相关：[[reference-youpei-zhengshu-check]]、[[feedback-no-unverified-cause-claims]]、
[[feedback-rigor-audit]]、[[feedback-ghostwriting-no-falsifiable-claims]]
