from openpyxl.worksheet.worksheet import Worksheet
from utils.constants import ReportColumn,ReportTriageColumns
from xml.etree.ElementTree import ElementTree

class ExcelHandler:
    @staticmethod
    def write_metadata_sheet(ws: Worksheet,root_tree : ElementTree):
        """
        Write metadata (Result and Build information) into the worksheet.

        Args:
            ws: The Excel worksheet to write into.
            root_tree: The root XML element containing 'attrib' and optional 'Build' child.
        """
        result_attribs = root_tree.attrib
        build_elem = root_tree.find('Build')
        build_attribs = build_elem.attrib if build_elem is not None else {}

        ws.column_dimensions['A'].width = 20
        
        # Ghi phần Result
        ExcelHandler._write_section(ws, title = "[Result Information]", data = result_attribs)

        ws.append([])  # Dòng trống
        ExcelHandler._write_section(ws, title = "[Build Information]", data = build_attribs)

    @staticmethod
    def create_header_row(ws: Worksheet, is_triage : bool = True):
        """
        Create and write the report header row into the worksheet.

        Args:
            ws: The Excel worksheet to write into.

        Returns:
            The updated worksheet.
        """
        if is_triage:
            ws.column_dimensions['B'].width = 35
            ws.column_dimensions['C'].width = 50
            ws.column_dimensions['D'].width = 20
            ws.column_dimensions['E'].width = 50
            ws.column_dimensions['F'].width = 30
            headers = [col.value for col in ReportTriageColumns]
        else:
            ws.column_dimensions['B'].width = 30
            headers = [col.value for col in ReportColumn]
        ws.append(headers)
        return ws

    @staticmethod
    def _write_section(ws: Worksheet, title: str, data: dict) -> None:
        """
        Helper to write a section title and key-value rows into worksheet.

        Args:
            ws: The worksheet to write into.
            title: The section title.
            data: Dictionary of key-value pairs to write.
        """
        ws.append([title])
        for key, value in data.items():
            ws.append([key, value])