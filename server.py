#!/usr/bin/env python3
"""Local-only Pilot Survey server; Python standard library only."""
import io
import json
import zipfile
import xml.sax.saxutils as sx
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent
LABELS = [
    ("name", "專案名稱"),
    ("dept", "提案部門"),
    ("owner", "提案員工"),
    ("supervisor", "直屬主管"),
    ("proposalDate", "提案日期"),
    ("asIs", "目前工作流程與執行方式"),
    ("problems", "主要問題與瓶頸"),
    ("toBe", "AI 導入後工作方式"),
    ("goal", "預期改善目標"),
    ("currentTime", "目前每次處理時間（分鐘）"),
    ("futureTime", "預期每次處理時間（分鐘）"),
    ("frequency", "每月執行次數"),
    ("cost", "年度新增成本"),
    ("resources", "所需資源"),
    ("notes", "主管審核意見"),
    ("approval", "主管審核狀態"),
    ("executiveApproval", "高階管理層批准狀態"),
]


def column(n):
    value = ""
    while n:
        n, r = divmod(n - 1, 26)
        value = chr(65 + r) + value
    return value


def worksheet(rows):
    out = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
        '<sheetFormatPr defaultRowHeight="18"/>'
        '<cols><col min="1" max="1" width="34" customWidth="1"/>'
        '<col min="2" max="2" width="75" customWidth="1"/>'
        '<col min="3" max="5" width="29" customWidth="1"/></cols><sheetData>'
    ]
    for row_number, row in enumerate(rows, 1):
        out.append(f'<row r="{row_number}">')
        for index, value in enumerate(row, 1):
            ref = f"{column(index)}{row_number}"
            encoded = sx.escape(str(value if value is not None else ""))
            out.append(
                f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{encoded}</t></is></c>'
            )
        out.append("</row>")
    out.append("</sheetData></worksheet>")
    return "".join(out)


def export_xlsx(data):
    proposals = [["項目", "內容"]] + [
        [label, data.get(key, "")] for key, label in LABELS
    ]
    try:
        original = float(data.get("currentTime") or 0)
        expected = float(data.get("futureTime") or 0)
        monthly = float(data.get("frequency") or 0)
        proposals.extend([
            ["每次預估節省（分鐘）", str(original - expected)],
            ["年度節省工時", str((original - expected) * monthly * 12 / 60)],
        ])
    except (ValueError, TypeError):
        pass
    stages = [["實施事項", "預定完成日期", "檢查點／驗收標準", "檢查結果"]]
    stages.extend([
        [item.get(key, "") for key in ("title", "date", "check", "status")]
        for item in data.get("stages", [])
        if isinstance(item, dict)
    ])

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>",
        )
        archive.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            "</Relationships>",
        )
        archive.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
            ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="專案提案" sheetId="1" r:id="rId1"/>'
            '<sheet name="實施節點" sheetId="2" r:id="rId2"/></sheets></workbook>',
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>'
            "</Relationships>",
        )
        archive.writestr("xl/worksheets/sheet1.xml", worksheet(proposals))
        archive.writestr("xl/worksheets/sheet2.xml", worksheet(stages))
    return buffer.getvalue()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        name = self.path.split("?")[0].lstrip("/") or "index.html"
        if name not in ("index.html", "app.js", "style.css"):
            self.send_error(404)
            return
        body = (BASE / name).read_bytes()
        mime = {
            "index.html": "text/html; charset=utf-8",
            "app.js": "application/javascript; charset=utf-8",
            "style.css": "text/css; charset=utf-8",
        }[name]
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/export":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > 2_000_000:
                raise ValueError("Invalid request size")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict) or not isinstance(data.get("stages", []), list):
                raise ValueError("Invalid JSON object")
            body = export_xlsx(data)
        except (ValueError, TypeError, KeyError) as exc:
            self.send_error(400, str(exc))
            return
        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.send_header(
            "Content-Disposition",
            "attachment; filename=smart-citizen-poc.xlsx",
        )
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print("請開啟 http://localhost:3333", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 3333), Handler).serve_forever()
