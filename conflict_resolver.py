class ConflictResolver:
    def check_conflicts(self, sheets_changes, db_changes):
        conflicts = []
        sheets_changes_dict = {change[1]: change for change in sheets_changes}
        db_changes_dict = {change[1]: change for change in db_changes}

        for row_index in set(sheets_changes_dict.keys()) & set(db_changes_dict.keys()):
            if sheets_changes_dict[row_index] != db_changes_dict[row_index]:
                conflicts.append((row_index, sheets_changes_dict[row_index], db_changes_dict[row_index]))

        return conflicts

    def resolve_conflicts(self, conflicts):
        for row_index, sheets_change, db_change in conflicts:
            # Implement your conflict resolution strategy here
            # For example, you could use a "last write wins" strategy:
            if sheets_change[0] == 'update' and db_change[0] == 'update':
                # Compare timestamps and choose the most recent change
                if sheets_change[2][-1] > db_change[2][-1]:  # Assuming last column is timestamp
                    return sheets_change
                else:
                    return db_change
            elif sheets_change[0] == 'delete':
                return sheets_change
            elif db_change[0] == 'delete':
                return db_change

        # You might want to log unresolved conflicts or implement a more sophisticated strategy