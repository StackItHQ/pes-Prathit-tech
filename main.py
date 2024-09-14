import time
from google_sheets_listener import GoogleSheetsListener
from database_listener import DatabaseListener
from sync_service import SyncService
from conflict_resolver import ConflictResolver

class GoogleSheetsDatabaseSync:
    def __init__(self, sheet_id, db_config):
        self.sheets_listener = GoogleSheetsListener(sheet_id)
        self.db_listener = DatabaseListener(db_config)
        self.sync_service = SyncService(sheet_id, db_config)
        self.conflict_resolver = ConflictResolver()

    def run(self):
        while True:
            # Check for changes in Google Sheets
            sheets_changes = self.sheets_listener.get_changes()
            if sheets_changes:
                self.sync_service.update_database(sheets_changes)

            # Check for changes in the database
            db_changes = self.db_listener.get_changes()
            if db_changes:
                self.sync_service.update_sheets(db_changes)

            # Handle conflicts (optional)
            conflicts = self.conflict_resolver.check_conflicts(sheets_changes, db_changes)
            if conflicts:
                self.conflict_resolver.resolve_conflicts(conflicts)

            time.sleep(5)  # Poll every 5 seconds

if __name__ == "__main__":
    sheet_id = "your_google_sheet_id"
    db_config = {
        "host": "localhost",
        "user": "your_username",
        "password": "your_password",
        "database": "your_database"
    }
    
    sync_app = GoogleSheetsDatabaseSync(sheet_id, db_config)
    sync_app.run()