# DAP Query App

The DAP Query App is a Python application that allows users to query data from the DAP (Data Access Point) API provided by Instructure Canvas. It provides a graphical user interface (GUI) for specifying query parameters and downloading the data in various formats.

## Libraries Used

The following libraries are used in this application:

- `asyncio`: Provides asynchronous programming support for running queries asynchronously.
- `os`: Provides functions for interacting with the operating system, such as file and directory operations.
- `datetime`: Provides classes for working with dates and times.
- `tkinter`: Provides classes for creating graphical user interfaces (GUIs).
- `tkinter.ttk`: Provides themed widgets for creating visually appealing GUIs.
- `tkcalendar`: Provides a calendar widget for selecting dates.
- `dap.api`: Provides the DAPClient for interacting with the DAP API.
- `dap.dap_types`: Provides data types used by the DAP API, such as Format, IncrementalQuery, SnapshotQuery, and Credentials.

## Code Functions

The main functions in the code are:

- `__init__(self, master)`: Initializes the DAPQueryApp class and creates the GUI widgets.
- `browse_output_dir(self)`: Opens a file dialog to select the output directory.
- `select_since_timestamp(self)`: Opens a calendar window to select the since timestamp for incremental queries.
- `start_query(self)`: Starts the query process with the selected parameters.
- `run_query(self, base_url, client_id, client_secret, namespace, table, query_type, since_timestamp, file_format, output_directory)`: Runs the query with the specified parameters using the DAPClient.

## Compiling with PyInstaller

To compile the application into an executable using PyInstaller, follow these steps:

1. Install PyInstaller by running the following command: pip install pyinstaller
2. Open a terminal or command prompt and navigate to the directory where your Python script is located.
3. Run the following command to create an executable: pyinstaller --onefile DAPQueryAppV3.py
4. PyInstaller will create a dist directory containing the executable file.

## GUI User Instructions

1. Launch the DAP Query App executable.

2. Enter the DAP API URL, client ID, client secret, and namespace in the respective fields.

3. Select the desired table from the dropdown menu.

4. Choose the query type: snapshot or incremental.

5. For incremental queries, click the "Select Date" button to choose the since timestamp.

6. Select the desired file format from the dropdown menu.

7. Click the "Browse" button to select the output directory where the downloaded data will be saved.

8. Click the "Start Query" button to initiate the query process.

9. Wait for the query to complete. A success message will be displayed upon completion.

10. The downloaded data will be saved in the specified output directory, with the files renamed to include the table name.

Note: Ensure that you have a stable internet connection and valid credentials for accessing the DAP API.

