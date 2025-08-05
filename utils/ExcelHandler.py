from openpyxl.worksheet.worksheet import Worksheet
from utils.constants import ReportColumn

class ExcelHandler:
    @staticmethod
    def write_metadata_sheet(ws: Worksheet,root_tree : dict):
        result_attribs = root_tree.attrib
        build_elem = root_tree.find('Build')
        build_attribs = build_elem.attrib if build_elem is not None else {}

        ws.column_dimensions['A'].width = 20
        
        # Ghi phần Result
        ws.append(["[Result Information]"])
        for k, v in result_attribs.items():
            ws.append([k, v])

        ws.append([])  # Dòng trống
        ws.append(["[Build Information]"])
        for k, v in build_attribs.items():
            ws.append([k, v])

    @staticmethod
    def create_header_row(ws: Worksheet):
        ws.column_dimensions['B'].width = 30
        # Ghi header
        headers = [col.value for col in ReportColumn]
        ws.append(headers)
        return ws
