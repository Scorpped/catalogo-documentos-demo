"""Acervo demonstrativo: metadados fictícios, sem arquivos ou dados reais."""
from __future__ import annotations
import argparse
import csv
import json
import sys
import unicodedata
from pathlib import Path

FIELDS = ("id", "title", "category", "year", "status", "pages")

def normalize(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn").casefold()

def load_documents(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("O catálogo precisa ser uma lista JSON.")
    seen = set()
    for item in data:
        if not isinstance(item, dict) or set(item) != set(FIELDS):
            raise ValueError("Registro com campos inválidos.")
        if any(not isinstance(item[k], str) or not item[k].strip() for k in ("id", "title", "category", "status")):
            raise ValueError("Campos textuais devem ser preenchidos.")
        if type(item["year"]) is not int or not 1900 <= item["year"] <= 2100:
            raise ValueError("Ano inválido.")
        if type(item["pages"]) is not int or item["pages"] <= 0:
            raise ValueError("Número de páginas inválido.")
        if item["id"] in seen:
            raise ValueError("Identificador duplicado.")
        seen.add(item["id"])
    return data

def select_documents(items: list[dict], query: str = "", category: str = "Todas") -> list[dict]:
    return sorted((d for d in items if (category == "Todas" or d["category"] == category)
                   and normalize(query) in normalize(d["title"] + " " + d["id"])), key=lambda d: d["title"])

def export_csv(items: list[dict], path: Path) -> None:
    # Protege a abertura em planilhas caso o exemplo seja adaptado com outras entradas.
    def safe(value):
        return "'" + value if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")) else value
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows({k: safe(v) for k, v in item.items()} for item in items)

def run_gui(items: list[dict]) -> int:
    try:
        from PySide6.QtWidgets import QApplication, QComboBox, QFileDialog, QHeaderView, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
    except ImportError:
        print("Para a interface: python -m pip install -r requirements.txt", file=sys.stderr)
        return 2
    class Window(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Acervo · Catálogo de demonstração")
            self.resize(980, 620)
            body = QWidget(); layout = QVBoxLayout(body); layout.setContentsMargins(32, 28, 32, 28); layout.setSpacing(18)
            label = QLabel("ACERVO / DEMONSTRAÇÃO"); label.setObjectName("eyebrow"); layout.addWidget(label)
            title = QLabel("Documentos, em ordem."); title.setObjectName("title"); layout.addWidget(title)
            layout.addWidget(QLabel("Metadados inteiramente fictícios. Nenhum documento real é armazenado ou aberto."))
            filters = QHBoxLayout()
            self.search = QLineEdit(); self.search.setPlaceholderText("Buscar título ou código…"); self.search.setAccessibleName("Buscar documento")
            self.category = QComboBox(); self.category.addItems(["Todas"] + sorted({d["category"] for d in items})); self.category.setAccessibleName("Categoria")
            export = QPushButton("Exportar seleção CSV"); export.clicked.connect(self.export)
            filters.addWidget(self.search, 2); filters.addWidget(self.category); filters.addWidget(export); layout.addLayout(filters)
            self.count = QLabel(); layout.addWidget(self.count)
            self.table = QTableWidget(0, len(FIELDS)); self.table.setHorizontalHeaderLabels(["Código", "Título", "Categoria", "Ano", "Status", "Páginas"])
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); self.table.setAlternatingRowColors(True)
            self.table.setAccessibleName("Documentos fictícios"); layout.addWidget(self.table)
            layout.addWidget(QLabel("Python + PySide6 · Projeto de portfólio demonstrativo"))
            self.search.textChanged.connect(self.refresh); self.category.currentTextChanged.connect(self.refresh)
            self.setCentralWidget(body); self.refresh()
        def refresh(self):
            self.selected = select_documents(items, self.search.text(), self.category.currentText())
            self.count.setText(f"{len(self.selected)} documentos · {sum(d['pages'] for d in self.selected)} páginas fictícias")
            self.table.setRowCount(len(self.selected))
            for row, item in enumerate(self.selected):
                for col, key in enumerate(FIELDS): self.table.setItem(row, col, QTableWidgetItem(str(item[key])))
        def export(self):
            name, _ = QFileDialog.getSaveFileName(self, "Exportar catálogo fictício", "catalogo-demo.csv", "CSV (*.csv)")
            if name:
                try: export_csv(self.selected, Path(name))
                except OSError as error: QMessageBox.warning(self, "Não foi possível exportar", str(error)); return
                QMessageBox.information(self, "Exportado", "Seleção exportada com sucesso.")
    app = QApplication(sys.argv)
    app.setStyleSheet("QWidget{background:#121c29;color:#e6edf5;font:13px 'Segoe UI';} QLabel#title{font-size:30px;font-weight:600;} QLabel#eyebrow{color:#7ed8c5;font-size:11px;} QLineEdit,QComboBox,QPushButton{padding:10px;border:1px solid #3a4c63;border-radius:6px;background:#1d2c3f;} QPushButton{background:#2a655c;} QTableWidget{background:#172538;alternate-background-color:#1b2c41;gridline-color:#30425a;border:1px solid #30425a;} QHeaderView::section{background:#23364e;padding:9px;border:0;}")
    window = Window(); window.show()
    return app.exec()

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default=""); parser.add_argument("--category", default="Todas")
    parser.add_argument("--export", type=Path); parser.add_argument("--gui", action="store_true")
    args = parser.parse_args(argv)
    try:
        items = load_documents(Path(__file__).with_name("documents.json"))
        if args.gui: return run_gui(items)
        selected = select_documents(items, args.query, args.category)
        if args.export: export_csv(selected, args.export)
        print(json.dumps({"demo": True, "count": len(selected), "documents": selected}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as error:
        print(f"Erro: {error}", file=sys.stderr); return 2

if __name__ == "__main__": raise SystemExit(main())
