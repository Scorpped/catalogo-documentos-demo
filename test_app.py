import csv
import json
import tempfile
import unittest
from pathlib import Path
from app import export_csv, load_documents, select_documents

class CatalogTests(unittest.TestCase):
    def setUp(self): self.items = load_documents(Path(__file__).with_name('documents.json'))
    def test_search_without_accents(self): self.assertEqual(len(select_documents(self.items, 'relatorio')), 1)
    def test_combined_filters(self): self.assertEqual(select_documents(self.items, 'relatorio', 'Guias'), [])
    def test_export_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'export.csv'; export_csv(self.items, path)
            with path.open(encoding='utf-8-sig', newline='') as file: self.assertEqual(len(list(csv.DictReader(file))), 6)
    def test_spreadsheet_formula_is_escaped(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'export.csv'; export_csv([{**self.items[0], 'title': '=1+1'}], path)
            with path.open(encoding='utf-8-sig', newline='') as file: self.assertEqual(next(csv.DictReader(file))['title'], "'=1+1")
    def test_duplicate_id_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'bad.json'; path.write_text(json.dumps([self.items[0], self.items[0]]),encoding='utf-8')
            with self.assertRaises(ValueError): load_documents(path)
    def test_invalid_pages_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'bad.json'; path.write_text(json.dumps([{**self.items[0], 'pages': -1}]),encoding='utf-8')
            with self.assertRaises(ValueError): load_documents(path)
if __name__ == '__main__': unittest.main()
