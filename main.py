import time
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from openai import OpenAI
from composio_openai import ComposioToolSet, App, Action

# Configuration constants
SPREADSHEET_ID = "1i8OwCM_o2E4tmpZ18-2Jgu8G42ntPWoUgGhfbcyxnoo"
POLLING_INTERVAL = 60  # seconds
CREDENTIALS_FILE = "key.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Set up logging configuration
logging.basicConfig(
    filename='sheet_monitor.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

def get_all_sheets(spreadsheet_id, credentials):
    """
    Fetch all sheets from the given Google Spreadsheet.

    Args:
    spreadsheet_id (str): The ID of the Google Spreadsheet.
    credentials (google.oauth2.service_account.Credentials): Google service account credentials.

    Returns:
    list: A list of sheet objects containing metadata about each sheet.
    """
    logging.info(f'Fetching all sheets for spreadsheet: {spreadsheet_id}')
    service = build("sheets", "v4", credentials=credentials)
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    logging.info(f'Found {len(sheets)} sheets')
    return sheets

def get_sheet_data(service, spreadsheet_id, sheet_name):
    """
    Retrieve data from a specific sheet in the spreadsheet.

    Args:
    service (googleapiclient.discovery.Resource): Google Sheets API service object.
    spreadsheet_id (str): The ID of the Google Spreadsheet.
    sheet_name (str): The name of the sheet to retrieve data from.

    Returns:
    list: A 2D list containing the sheet data.
    """
    logging.info(f'Getting data for sheet: {sheet_name}')
    range_name = f"{sheet_name}!A:Z"  # Adjust the range as needed
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    logging.info(f'Retrieved {len(values)} rows from sheet {sheet_name}')
    return values

def compare_data(previous, current):
    """
    Compare previous and current data to detect changes.

    Args:
    previous (list): Previous state of the sheet data.
    current (list): Current state of the sheet data.

    Returns:
    list: A list of strings describing the changes detected.
    """
    logging.info('Comparing previous and current data...')
    changes = []

    # Check for deletions and updates
    for i, row in enumerate(previous):
        if i >= len(current):
            changes.append(f"Row {i+1} was deleted: {row}")
        elif row != current[i]:
            changes.append(f"Row {i+1} was updated from {row} to {current[i]}")

    # Check for additions
    for i in range(len(previous), len(current)):
        changes.append(f"Row {i+1} was added: {current[i]}")

    logging.info(f'Detected {len(changes)} changes')
    return changes

def execute_openai_composio(changes):
    """
    Execute changes on the company database using OpenAI and Composio.

    This function uses OpenAI's API to generate SQL queries based on the detected changes,
    and then executes these queries using Composio's SQL tool.

    Args:
    changes (list): A list of strings describing the changes to be applied to the database.

    Returns:
    str: The response from the Composio tool execution.
    """
    logging.info('Executing changes on company database...')

    # Initialize OpenAI client and Composio toolset
    openai_client = OpenAI()
    composio_toolset = ComposioToolSet()
    actions = composio_toolset.get_tools(apps=[App.SQLTOOL])

    # Define instructions for the AI assistant
    assistant_instruction = """
    You are a super intelligent SQL assistant. When given a description of changes made to a Google Sheet,
    write appropriate SQL queries to implement those changes in the 'company' database. Each change should be a separate SQL query.
    If this is the initial sync, create TABLES with the sheet names first, and then INSERT statements for all rows.
    Use the tool at your disposal. Connection string will always be company.db.
    If this is not the initial sync then use the sheet names as the Table names always.
    """
    my_task = "\n".join(changes)

    # Create an OpenAI assistant
    assistant = openai_client.beta.assistants.create(
        name="SQL Assistant",
        instructions=assistant_instruction,
        model="gpt-4-1106-preview",
        tools=actions,
    )

    # Create a thread and add the task message
    thread = openai_client.beta.threads.create()
    openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=my_task
    )

    # Run the assistant
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    # Handle the assistant's response and execute tool calls
    response = composio_toolset.wait_and_handle_assistant_tool_calls(
        client=openai_client,
        run=run,
        thread=thread,
    )

    logging.info('Database changes executed.')
    logging.info(response)
    print('Database changes executed:')
    print(response)
    return response

def monitor_all_sheets(spreadsheet_id, interval=10):
    """
    Main function to monitor all sheets in the spreadsheet for changes.

    This function continuously checks for changes in all sheets of the specified Google Spreadsheet
    at regular intervals. When changes are detected, it updates the local database accordingly.

    Args:
    spreadsheet_id (str): The ID of the Google Spreadsheet to monitor.
    interval (int): The time interval (in seconds) between checks for changes.
    """
    logging.info(f'Starting to monitor spreadsheet: {spreadsheet_id}')
    
    # Set up Google Sheets API credentials
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials)

    # Get all sheets in the spreadsheet
    all_sheets = get_all_sheets(spreadsheet_id, credentials)
    previous_data = {}

    # Perform initial data load and sync
    logging.info("Initial data load and sync...")
    print("Initial data load and sync...")
    initial_changes = []

    for sheet in all_sheets:
        sheet_name = sheet['properties']['title']
        sheet_data = get_sheet_data(service, spreadsheet_id, sheet_name)
        previous_data[sheet_name] = sheet_data
        initial_changes.extend([f"Initial data for sheet '{sheet_name}':"] + 
                               [f"Row {i+1} added: {row}" for i, row in enumerate(sheet_data)])

    # Execute OpenAI and Composio code for initial sync
    execute_openai_composio(initial_changes)

    logging.info("Initial sync complete. Monitoring for changes...")
    print("Initial sync complete. Monitoring for changes...")

    # Main monitoring loop
    while True:
        time.sleep(interval)
        changes_detected = False
        all_changes = []

        # Check each sheet for changes
        for sheet in all_sheets:
            sheet_name = sheet['properties']['title']
            current_data = get_sheet_data(service, spreadsheet_id, sheet_name)

            if current_data != previous_data[sheet_name]:
                changes = compare_data(previous_data[sheet_name], current_data)
                if changes:
                    logging.info(f"Changes detected in sheet: {sheet_name}")
                    print(f"\nChanges detected in sheet: {sheet_name}")
                    for change in changes:
                        logging.info(change)
                        print(change)
                    all_changes.extend(changes)
                    changes_detected = True
                previous_data[sheet_name] = current_data

        # Execute changes if any were detected
        if changes_detected:
            response = execute_openai_composio(all_changes)
            logging.info(f"Tool call output: {response}")
        else:
            logging.info("No changes detected in any sheet.")
            print("No changes detected in any sheet.")

# Main execution
if __name__ == "__main__":
    monitor_all_sheets(SPREADSHEET_ID, POLLING_INTERVAL)