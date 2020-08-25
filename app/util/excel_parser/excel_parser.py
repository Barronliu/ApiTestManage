# coding=utf-8
import xlrd
import sys
from importlib import reload
from ..global_variable import *

reload(sys)
import traceback
from datetime import datetime
from xlrd import xldate_as_tuple


class excelHandle:
    def decode(self, filename, sheetname):
        try:
            filename = filename.decode('utf-8')
            sheetname = sheetname.decode('utf-8')
        except Exception:
            print(traceback.print_exc())
        return filename, sheetname

    def read_excel(self, book, sheetname):
        sheet = book.sheet_by_name(sheetname)
        rows = sheet.nrows
        cols = sheet.ncols
        all_content = []
        for i in range(rows):
            row_content = []
            for j in range(cols):
                rd_xf = book.xf_list[sheet.cell_xf_index(i, j)]
                cell_font = book.font_list[rd_xf.font_index].struck_out
                if cell_font:
                    continue
                ctype = sheet.cell(i, j).ctype  # 表格的数据类型
                cell = sheet.cell_value(i, j)
                if ctype == 2 and cell % 1 == 0:  # 如果是整形
                    cell = int(cell)
                elif ctype == 3:
                    # 转成datetime对象
                    date = datetime(*xldate_as_tuple(cell, 0))
                    cell = date.strftime('%Y/%d/%m %H:%M:%S')
                elif ctype == 4:
                    cell = True if cell == 1 else False
                row_content.append(cell)
            all_content.append(row_content)
            print('[' + ','.join("'" + str(element) + "'" for element in row_content) + ']')
        return all_content

    def is_delete(self, book, sheet, x, y):
        rd_xf = book.xf_list[sheet.cell_xf_index(x, y)]
        cell_font = book.font_list[rd_xf.font_index]
        is_delete = cell_font.struck_out
        return is_delete

    def is_empty(self, sheet, x, y):
        if sheet.cell_value(x, y):
            is_empty = False
        else:
            is_empty = True
        return is_empty

    def paser_excel_data(self, book, sheetname):
        """
        data = {
            "event": "",
            "is_page": 0,
            "page_and_element_names": {}
        }
        """
        data = {
            "event": "",
            "is_page": 0,
            "page_and_element_names": {}
        }

        sheet = book.sheet_by_name(sheetname)
        rows = sheet.nrows
        cols = sheet.ncols
        data['event'] = sheet.cell_value(0, 1)
        if sheet.cell_value(2, 2) == 'page_name':
            data['is_page'] = 1

        for i in range(5, rows):
            if self.is_delete(book, sheet, i, 2) or self.is_empty(sheet, i, 2):
                continue
            page_or_element_name = sheet.cell_value(i, 2)
            params = {page_or_element_name: {}}
            for j in range(3, cols):
                if not self.is_empty(sheet, i, j) and not self.is_delete(book, sheet, i, j):
                    parm_name = sheet.cell_value(2, j)
                    parm_type = sheet.cell_value(3, j)
                    if not parm_name == 'log_extra':
                        params[page_or_element_name].update({parm_name: parm_type})
            data['page_and_element_names'].update(params)
        return data

    def parser_sheet(self, filename):
        _file = os.path.join(FILE_ADDRESS, filename)
        rbook = xlrd.open_workbook(_file, formatting_info=True)
        result = []
        for sheetname in rbook.sheet_names():
            data = self.paser_excel_data(rbook, sheetname)
            result.append(data)
        return result


if __name__ == '__main__':
    eh = excelHandle()
    filename = r'知识库埋点.xls'
    maidian_data = eh.parser_sheet(filename)
    for event in maidian_data:
        for element, value in event['page_and_element_names'].items():
            for param in value:
                print("event: ", event['event'])
                print("page_or_element_name: ", element)
                print("is_page: ", event['is_page'])
                print("params: ", param)
                print("params_type: ", value[param])
