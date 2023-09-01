from infrastructure.google import Google
import os
from rich.console import Console
from rich.table import Table


class SheetData:
    __rows = []

    def __init__(self, with_headers=True):
        self.__headers_added = False
        self.__headers = []

    def __add_headers(self, headers):
        if self.__headers_added:
            return
        headers_as_list = []
        for key in headers:
            headers_as_list.append(key)
        self.__rows.append(headers_as_list)
        self.__headers_added = True

    def add_row(self, data):
        keys = data.keys()
        self.__add_headers(keys)
        row = []
        for key in keys:
            row.append(str(data[key]))
        self.__rows.append(row)

    def get_rows(self, with_headers=True):
        return self.__rows if with_headers else self.__rows[1:]

    def get_headers(self):
        return self.__rows[0]

    def plot_on_terminal(self, with_headers=True):
        console = Console()
        table = Table(show_header=with_headers, header_style="bold magenta")
        for column in self.get_headers():
            table.add_column(column)

        for row in self.__rows[1:]:
            table.add_row(*row)

        console.print(table)


class SheetsService:

    def __init__(self, google: Google):
        self.__sheets = google.sheets_client()
        self.__sheet_id = os.getenv('REPORT_SHEET_ID')

    def update_sheet(self, sheet_data: SheetData, page_name: str = '', update_range: str = 'A:Z'):
        body = {
            'values': sheet_data.get_rows()
        }
        if page_name:
            update_range = f'{page_name}!{update_range}'
        self.__sheets.spreadsheets().values().update(
            spreadsheetId=self.__sheet_id, range=update_range,
            valueInputOption='USER_ENTERED', body=body).execute()

    def add_page(self, page_name: str, ):
        body = {
            "requests": {
                "addSheet": {
                    "properties": {
                        "title": page_name
                    }
                }
            }
        }

        self.__sheets.spreadsheets().batchUpdate(spreadsheetId=self.__sheet_id, body=body).execute()

    def get_pages(self):
        result = self.__sheets.spreadsheets().get_rows(
            spreadsheetId=self.__sheet_id).execute()
        return result


if __name__ == "__main__":
    sheets = SheetsService(google=Google())
    sheets.get_pages()
