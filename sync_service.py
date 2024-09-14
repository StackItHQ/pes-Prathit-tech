from google_sheets_listener import GoogleSheetsListener
from database_listener import DatabaseListener

class SyncService:
    def __init__(self, sheet_id, db_config):
        self.sheets_service = GoogleSheetsListener(sheet_id).service
        self.db_connection = DatabaseListener(db_config).connection
        self.sheet_id = sheet_id

    def update_database(self, changes):
        cursor = self.db_connection.cursor()
        for change_type, row_index, data in changes:
            if change_type == 'update':
                # Assuming the first column is the ID
                cursor.execute(
                    "INSERT INTO your_table (id, col1, col2) VALUES (%s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE col1=%s, col2=%s",
                    (data[0], data[1], data[2], data[1], data[2])
                )
            elif change_type == 'delete':
                cursor.execute("DELETE FROM your_table WHERE id=%s", (row_index,))
        self.db_connection.commit()

    def update_sheets(self, changes):
        batch_update_values_request_body = {
            'value_input_option': 'USER_ENTERED',
            'data': []
        }
        for change_type, row_index, data in changes:
            if change_type == 'update':
                batch_update_values_request_body['data'].append({
                    'range': f'A{row_index + 1}:Z{row_index + 1}',
                    'values': [data]
                })
            elif change_type == 'delete':
                batch_update_values_request_body['data'].append({
                    'range': f'A{row_index + 1}:Z{row_index + 1}',
                    'values': [['']] * len(data)  # Clear the row
                })
        self.sheets_service.spreadsheets().values().batchUpdate(
            spreadsheetId=self.sheet_id,
            body=batch_update_values_request_body
        ).execute()