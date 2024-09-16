[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/AHFn7Vbn)
# Superjoin Hiring Assignment

# My Readme Section 

- [x] My code's working just fine! 🥳
- [x] I have recorded a video showing it working and embedded it in the README ▶️
- [x] I have tested all the normal working cases 😎
- [x] I have even solved some edge cases (brownie points) 💪
- [x] I added my very planned-out approach to the problem at the end of this README 📜

### How It Works

The script connects to the Google Sheets API using the provided service account credentials.
It fetches data from all sheets in the specified spreadsheet.
For each subsequent check:

It compares the current state of each sheet with the previous state.
If changes are detected, it generates a list of change descriptions.
These changes are sent to an OpenAI model, which generates appropriate SQL queries.
The SQL queries are executed on the local database using the Composio SQL tool.

### Features

Continuous monitoring of multiple sheets within a Google Spreadsheet
Detection of additions, deletions, and updates in sheet data
Automatic generation and execution of SQL queries to update a local database
Logging of all activities and changes
Initial sync capability for new sheet setups

Imports and Configuration
pythonCopyimport time
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from openai import OpenAI
from composio_openai import ComposioToolSet, App, Action

# Sheet Monitor Code Explanation

## Overview

The Sheet Monitor script is designed to monitor changes in a Google Spreadsheet and update a local database accordingly. Here's a detailed breakdown of how the code works:

## Imports and Configuration

```python
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
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
```

This section imports necessary libraries and sets up configuration constants. It uses Google's API client libraries, OpenAI's API, and the Composio tool for database operations.

## Logging Setup

```python
logging.basicConfig(
    filename='sheet_monitor.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)
```

This sets up logging to track the script's activities in a file named `sheet_monitor.log`.

## Main Functions

### `get_all_sheets(spreadsheet_id, credentials)`

This function retrieves metadata about all sheets in the specified Google Spreadsheet.

### `get_sheet_data(service, spreadsheet_id, sheet_name)`

This function fetches the actual data from a specific sheet within the spreadsheet.

### `compare_data(previous, current)`

This function compares the previous state of a sheet with its current state to detect changes (additions, deletions, updates).

### `execute_openai_composio(changes)`

This function is responsible for:
1. Creating an OpenAI assistant with specific instructions for generating SQL queries.
2. Sending the detected changes to the OpenAI model.
3. Receiving and executing the generated SQL queries using the Composio tool.

### `monitor_all_sheets(spreadsheet_id, interval=10)`

This is the main function that orchestrates the entire monitoring process:
1. It sets up the Google Sheets API service.
2. Performs an initial sync of all sheet data.
3. Enters a continuous loop to check for changes at specified intervals.
4. When changes are detected, it calls `execute_openai_composio()` to update the database.

## Detailed Workflow

1. **Initialization**:
   - The script starts by setting up logging and Google Sheets API credentials.
   - It retrieves all sheets from the specified spreadsheet.

2. **Initial Sync**:
   - Data from all sheets is fetched and stored as the initial state.
   - This initial data is processed as if it were all new additions.

3. **Continuous Monitoring**:
   - The script enters a while loop that runs indefinitely.
   - In each iteration:
     a. It waits for the specified polling interval.
     b. Fetches the current state of each sheet.
     c. Compares the current state with the previous state using `compare_data()`.
     d. If changes are detected, it logs them and adds them to a list of all changes.

4. **Database Update**:
   - If any changes were detected, `execute_openai_composio()` is called.
   - This function uses OpenAI's API to generate appropriate SQL queries based on the changes.
   - The generated queries are then executed using the Composio SQL tool.

5. **Logging**:
   - Throughout the process, the script logs important events and information.
   - This includes when it starts monitoring, detects changes, and executes database updates.

## Error Handling

The current version of the script has minimal explicit error handling. In a production environment, it would be advisable to add try-except blocks around critical operations, especially API calls and database operations.

## Extensibility

The script is designed in a modular way, making it relatively easy to extend or modify:
- Additional sheets or spreadsheets could be monitored by modifying the `monitor_all_sheets()` function.
- The database update process could be changed by modifying the `execute_openai_composio()` function.
- Different types of change detection could be implemented by modifying the `compare_data()` function.

This design allows for future enhancements and adaptations to different use cases or environments.

## Demo Video

[Watch the demo video](https://github.com/StackItHQ/pes-Prathit-tech/blob/main/video.mp4)

### Welcome to Superjoin's hiring assignment! 🚀

### Objective
Build a solution that enables real-time synchronization of data between a Google Sheet and a specified database (e.g., MySQL, PostgreSQL). The solution should detect changes in the Google Sheet and update the database accordingly, and vice versa.

### Problem Statement
Many businesses use Google Sheets for collaborative data management and databases for more robust and scalable data storage. However, keeping the data synchronised between Google Sheets and databases is often a manual and error-prone process. Your task is to develop a solution that automates this synchronisation, ensuring that changes in one are reflected in the other in real-time.

### Requirements:
1. Real-time Synchronisation
  - Implement a system that detects changes in Google Sheets and updates the database accordingly.
   - Similarly, detect changes in the database and update the Google Sheet.
  2.	CRUD Operations
   - Ensure the system supports Create, Read, Update, and Delete operations for both Google Sheets and the database.
   - Maintain data consistency across both platforms.
   
### Optional Challenges (This is not mandatory):
1. Conflict Handling
- Develop a strategy to handle conflicts that may arise when changes are made simultaneously in both Google Sheets and the database.
- Provide options for conflict resolution (e.g., last write wins, user-defined rules).
    
2. Scalability: 	
- Ensure the solution can handle large datasets and high-frequency updates without performance degradation.
- Optimize for scalability and efficiency.

## Submission ⏰
The timeline for this submission is: **Next 2 days**

Some things you might want to take care of:
- Make use of git and commit your steps!
- Use good coding practices.
- Write beautiful and readable code. Well-written code is nothing less than a work of art.
- Use semantic variable naming.
- Your code should be organized well in files and folders which is easy to figure out.
- If there is something happening in your code that is not very intuitive, add some comments.
- Add to this README at the bottom explaining your approach (brownie points 😋)
- Use ChatGPT4o/o1/Github Co-pilot, anything that accelerates how you work 💪🏽. 

Make sure you finish the assignment a little earlier than this so you have time to make any final changes.

Once you're done, make sure you **record a video** showing your project working. The video should **NOT** be longer than 120 seconds. While you record the video, tell us about your biggest blocker, and how you overcame it! Don't be shy, talk us through, we'd love that.

We have a checklist at the bottom of this README file, which you should update as your progress with your assignment. It will help us evaluate your project.



## Got Questions❓
Feel free to check the discussions tab, you might get some help there. Check out that tab before reaching out to us. Also, did you know, the internet is a great place to explore? 😛

We're available at techhiring@superjoin.ai for all queries. 

All the best ✨.

## Developer's Section
*Add your video here, and your approach to the problem (optional). Leave some comments for us here if you want, we will be reading this :)*
