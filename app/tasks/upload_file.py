import datetime
from app import app
import os
import logging

from rq import get_current_job
from pathlib import Path
import openpyxl as openpyxl
import xlrd

log = open("./logs/worker.log", "a")


class TypeOfFileError(Exception):
    pass


class ExcelParser:
    _filename = None
    _obj = None

    def __init__(self, filename):
        self._filename = filename

    def load(self):
        pass

    def count_worksheets(self):
        pass

    def worksheets(self):
        pass

    def get_title_sheet(self, sheet):
        pass

    def get_count_rows(self, sheet):
        pass

    def get_value(self, sheet, row_id, col_id):
        pass


class XLSXParser(ExcelParser):

    def load(self):
        xlsx_file = Path(os.path.join(app.config['UPLOAD_FOLDER'], self._filename))
        if xlsx_file.is_file():
            self._obj = openpyxl.load_workbook(xlsx_file)
        else:
            raise FileNotFoundError("File not found")

    def count_worksheets(self):
        return len(self._obj.worksheets)

    def worksheets(self):
        return self._obj.worksheets

    def get_title_sheet(self, sheet):
        return sheet.title.title()

    def get_count_rows(self, sheet):
        # воркер уходил в таймаут, если считать через дефолтные функции
        count_col = 0
        for col_id in range(100):
            value = self.get_value(sheet, 1, count_col + 1)
            if value == "":
                break
            count_col += 1

        count_rows = 0
        row_id = 0
        while True:
            is_empty = True
            for col_id in range(count_col):
                value = self.get_value(sheet, row_id + 1, col_id + 1)
                if value != "":
                    count_rows += 1
                    row_id += 1
                    is_empty = False
                    break
            if is_empty:
                break
        return count_rows

    def get_value(self, sheet, row_id, col_id):
        cell_value = sheet.cell(row_id, col_id).value
        if cell_value is None:
            return ""
        if type(cell_value) == int or type(cell_value) == float:
            return cell_value
        return cell_value.strip()


class XLSParser(ExcelParser):

    def load(self):
        xlsx_file = Path(os.path.join(app.config['UPLOAD_FOLDER'], self._filename))
        if xlsx_file.is_file():
            self._obj = xlrd.open_workbook(xlsx_file)
        else:
            raise FileNotFoundError("File not found")

    def count_worksheets(self):
        return self._obj.nsheets

    def worksheets(self):
        sheets = []
        for sh in range(self._obj.nsheets):
            sheets.append(self._obj.sheet_by_index(sh))
        return sheets

    def get_title_sheet(self, sheet):
        return sheet.name

    def get_count_rows(self, sheet):
        return sheet.nrows

    def get_value(self, sheet, row_id, col_id):
        if col_id - 1 >= sheet.ncols:
            return ""
        cell_value = sheet.cell_value(rowx=row_id - 1, colx=col_id - 1)
        if cell_value is None:
            return ""
        if type(cell_value) == int or type(cell_value) == float:
            return cell_value
        return cell_value.strip()


def get_parser(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'xlsx':
        return XLSXParser(filename)
    elif ext == 'xls':
        return XLSParser(filename)
    else:
        raise TypeOfFileError("Wrong type of file")


def formated_print(text, job_id):
    string = "job_id = {0}. Text: {1}".format(job_id, text)
    print(string)
    log.writelines([string])


def start(filename: str):
    job = get_current_job()
    job_id = job.get_id()
    formated_print("Start task... upload_file.py", job_id)
    job.meta['started_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    job.meta['ended_at'] = None
    job.meta['status'] = 'processing'
    job.save_meta()

    formated_print("Check format and load file {0}".format(filename), job_id)
    parser = get_parser(filename)
    parser.load()
    formated_print("Start parsing", job_id)
    result = []
    count_sheets = parser.count_worksheets()
    sheet_idx = 0
    for sheet in parser.worksheets():
        formated_print("Check sheet name = {0}".format(parser.get_title_sheet(sheet)), job_id)
        sheet_idx += 1
        # переменная для определения положения нужных столбцов
        need_columns = {
            "before": 0,
            "after": 0
        }
        row_id = 1
        col_id = 1
        while True:
            value = parser.get_value(sheet, row_id, col_id)
            formated_print("Check header. value by row_id={0}, col_id={1}".format(row_id, col_id), job_id)
            if value == "":
                break
            if value in need_columns:
                need_columns[value] = col_id
            col_id += 1

        if need_columns['before'] == 0 or need_columns['after'] == 0:
            formated_print("Not found needed fields. Continue...", job_id)
            job.meta['progress'] = 100 / count_sheets * sheet_idx
            job.save_meta()
            continue
        before_items = set()
        after_items = set()
        row_id = 0
        while row_id < parser.get_count_rows(sheet):
            formated_print("Check value by row_id={0}, col_id={1}".format(row_id, col_id), job_id)
            row_id += 1
            if row_id == 1:
                continue
            value = parser.get_value(sheet, row_id, need_columns['before'])
            if value == "":
                continue
            before_items.add(value)

            value = parser.get_value(sheet, row_id, need_columns['after'])
            if value == "":
                continue
            after_items.add(value)
        count_before = len(before_items)
        count_after = len(after_items)
        if count_after > count_before and count_after - count_before == 1:
            result_list = list(after_items - before_items)
            result.append({
                'sheet': parser.get_title_sheet(sheet),
                'result': "added: {0}".format(result_list[0])
            })
        elif count_before > count_after and count_before - count_after == 1:
            result_list = list(before_items - after_items)
            result.append({
                'sheet': parser.get_title_sheet(sheet),
                'result': "removed: {0}".format(result_list[0])
            })
        else:
            formated_print("Error in sheet. After and before diff error", job_id)
        job.meta['progress'] = 100 / count_sheets * sheet_idx
        job.save_meta()
    job.meta['progress'] = 100
    job.meta['ended_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    job.meta['result'] = result
    job.save_meta()
    formated_print("End task... upload_file.py", job_id)
    return result
