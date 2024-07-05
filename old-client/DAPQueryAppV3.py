# DAPQueryAppV3

import asyncio
import os
from datetime import datetime, timezone
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, Radiobutton, StringVar
from tkinter.ttk import Combobox
from tkcalendar import Calendar

from dap.api import DAPClient
from dap.dap_types import Format, IncrementalQuery, SnapshotQuery, Credentials

class DAPQueryApp:
    def __init__(self, master):
        self.master = master
        master.title("DAP Query App")

        # Create input fields and labels for API URL, client ID, client secret, and namespace
        Label(master, text="DAP API URL").grid(row=0, column=0, sticky="w")
        self.api_url_entry = Entry(master, width=50)
        self.api_url_entry.insert(0, "https://api-gateway.instructure.com")
        self.api_url_entry.grid(row=0, column=1)

        Label(master, text="Client ID").grid(row=1, column=0, sticky="w")
        self.client_id_entry = Entry(master, width=50)
        self.client_id_entry.grid(row=1, column=1)

        Label(master, text="Client Secret").grid(row=2, column=0, sticky="w")
        self.client_secret_entry = Entry(master, width=50, show="*")
        self.client_secret_entry.grid(row=2, column=1)

        Label(master, text="Namespace").grid(row=3, column=0, sticky="w")
        self.namespace_entry = Entry(master, width=50)
        self.namespace_entry.insert(0, "canvas")
        self.namespace_entry.grid(row=3, column=1)

        # Create a dropdown for selecting the table
        Label(master, text="Table").grid(row=4, column=0, sticky="w")
        table_names = [
            "access_tokens", "account_users", "accounts", "assessment_question_banks",
            "assessment_questions", "assignment_groups", "assignment_override_students",
            "assignment_overrides", "assignments", "attachment_associations", "attachments",
            "calendar_events", "canvadocs_annotation_contexts", "comment_bank_items",
            "communication_channels", "content_migrations", "content_participation_counts",
            "content_participations", "content_shares", "content_tags", "context_external_tools",
            "context_module_progressions", "context_modules", "conversation_message_participants",
            "conversation_messages", "conversation_participants", "conversations",
            "course_account_associations", "course_sections", "courses",
            "custom_gradebook_column_data", "custom_gradebook_columns",
            "developer_key_account_bindings", "developer_keys", "discussion_entries",
            "discussion_entry_participants", "discussion_topic_participants",
            "discussion_topics", "enrollment_dates_overrides", "enrollment_states",
            "enrollment_terms", "enrollments", "favorites", "folders", "grading_period_groups",
            "grading_periods", "grading_standards", "group_categories", "group_memberships",
            "groups", "late_policies", "learning_outcome_groups", "learning_outcome_question_results",
            "learning_outcome_results", "learning_outcomes", "lti_line_items",
            "lti_resource_links", "lti_results", "master_courses_child_content_tags",
            "master_courses_child_subscriptions", "master_courses_master_content_tags",
            "master_courses_master_migrations", "master_courses_master_templates",
            "master_courses_migration_results", "originality_reports", "outcome_proficiencies",
            "outcome_proficiency_ratings", "post_policies", "pseudonyms", "quiz_groups",
            "quiz_questions", "quiz_submissions", "quizzes", "role_overrides", "roles",
            "rubric_assessments", "rubric_associations", "rubrics", "score_statistics",
            "scores", "submission_comments", "submission_versions", "submissions",
            "user_account_associations", "user_notes", "users", "web_conference_participants",
            "web_conferences", "wiki_pages", "wikis"
        ]
        self.table_dropdown = Combobox(master, values=table_names, state="readonly")
        self.table_dropdown.current(0)  # Set the default selected item to the first table name
        self.table_dropdown.grid(row=4, column=1)

        # Create radio buttons for selecting the query type (snapshot or incremental)
        Label(master, text="Query Type").grid(row=5, column=0, sticky="w")
        self.query_type_var = StringVar(value="snapshot")
        Radiobutton(master, text="Snapshot", variable=self.query_type_var, value="snapshot").grid(row=5, column=1, sticky="w")
        Radiobutton(master, text="Incremental", variable=self.query_type_var, value="incremental").grid(row=6, column=1, sticky="w")

        # Create an entry field and button for selecting the since timestamp (incremental query)
        Label(master, text="Since Timestamp (Incremental)").grid(row=7, column=0, sticky="w")
        self.since_timestamp_var = StringVar()
        self.since_timestamp_entry = Entry(master, textvariable=self.since_timestamp_var, state="readonly")
        self.since_timestamp_entry.grid(row=7, column=1)
        Button(master, text="Select Date", command=self.select_since_timestamp).grid(row=7, column=2)

        # Create a dropdown for selecting the file format
        Label(master, text="File Format").grid(row=8, column=0, sticky="w")
        file_formats = ["jsonl", "csv", "tsv", "parquet"]
        self.file_format_var = StringVar(value=file_formats[0])
        self.file_format_dropdown = Combobox(master, values=file_formats, state="readonly", textvariable=self.file_format_var)
        self.file_format_dropdown.current(0)  # Set the default selected item to the first file format
        self.file_format_dropdown.grid(row=8, column=1)

        # Create an entry field and button for selecting the output directory
        Label(master, text="Output Directory").grid(row=9, column=0, sticky="w")
        self.output_dir_entry = Entry(master, width=50)
        self.output_dir_entry.grid(row=9, column=1)
        Button(master, text="Browse", command=self.browse_output_dir).grid(row=9, column=2)

        # Create a button to start the query process
        Button(master, text="Start Query", command=self.start_query).grid(row=10, columnspan=3, pady=10)

    def browse_output_dir(self):
        """Open a file dialog to select the output directory"""
        output_dir = filedialog.askdirectory()
        self.output_dir_entry.delete(0, 'end')
        self.output_dir_entry.insert(0, output_dir)

    def select_since_timestamp(self):
        """Open a calendar window to select the since timestamp for incremental queries"""
        calendar_window = Tk()
        calendar_window.title("Select Date")
        calendar = Calendar(calendar_window, date_pattern="yyyy-mm-dd")
        calendar.pack()

        def set_since_timestamp():
            """Set the selected date as the since timestamp"""
            selected_date = calendar.get_date()
            self.since_timestamp_var.set(selected_date)
            calendar_window.destroy()

        Button(calendar_window, text="Select", command=set_since_timestamp).pack()
        calendar_window.mainloop()

    def start_query(self):
        """Start the query process with the selected parameters"""
        base_url = self.api_url_entry.get()
        client_id = self.client_id_entry.get()
        client_secret = self.client_secret_entry.get()
        namespace = self.namespace_entry.get()
        table = self.table_dropdown.get()
        query_type = self.query_type_var.get()
        since_timestamp = self.since_timestamp_var.get()
        file_format = self.file_format_var.get()
        output_directory = self.output_dir_entry.get()

        asyncio.run(self.run_query(base_url, client_id, client_secret, namespace, table, query_type, since_timestamp, file_format, output_directory))

    async def run_query(self, base_url, client_id, client_secret, namespace, table, query_type, since_timestamp, file_format, output_directory):
        """Run the query with the specified parameters"""
        try:
            credentials = Credentials.create(client_id=client_id, client_secret=client_secret)
            async with DAPClient(base_url=base_url, credentials=credentials) as dap_client:
                # Get the table schema
                schema = await dap_client.get_table_schema(namespace, table)
                print(f"Table schema version: {schema.version}")

                if query_type == "snapshot":
                    # Perform a snapshot query
                    snapshot_query = SnapshotQuery(format=Format[file_format.upper()], mode=None)
                    snapshot_result = await dap_client.get_table_data(namespace, table, snapshot_query)
                    print(f"Snapshot query completed. Job ID: {snapshot_result.job_id}")

                    # Save snapshot data to the specified output directory
                    snapshot_dir = os.path.join(output_directory, "snapshot")
                    os.makedirs(snapshot_dir, exist_ok=True)
                    download_result = await dap_client.download_table_data(namespace, table, snapshot_query, snapshot_dir, decompress=True)
                    
                    # Rename the downloaded files by appending the table name
                    for file_path in download_result.downloaded_files:
                        directory, filename = os.path.split(file_path)
                        new_filename = f"{table}_{filename}"
                        new_file_path = os.path.join(directory, new_filename)
                        os.rename(file_path, new_file_path)
                        print(f"Renamed file: {new_file_path}")
                    
                    print(f"Snapshot data downloaded and decompressed to: {snapshot_dir}")
                else:
                    # Convert the since_timestamp string to a datetime object with timezone
                    since_datetime = datetime.strptime(since_timestamp, "%Y-%m-%d").replace(tzinfo=timezone.utc)

                    # Perform an incremental query
                    incremental_query = IncrementalQuery(format=Format[file_format.upper()], mode=None, since=since_datetime, until=None)
                    incremental_result = await dap_client.get_table_data(namespace, table, incremental_query)
                    print(f"Incremental query completed. Job ID: {incremental_result.job_id}")

                    # Save incremental data to the specified output directory
                    incremental_dir = os.path.join(output_directory, "incremental")
                    os.makedirs(incremental_dir, exist_ok=True)
                    download_result = await dap_client.download_table_data(namespace, table, incremental_query, incremental_dir, decompress=True)
                    
                    # Rename the downloaded files by appending the table name
                    for file_path in download_result.downloaded_files:
                        directory, filename = os.path.split(file_path)
                        new_filename = f"{table}_{filename}"
                        new_file_path = os.path.join(directory, new_filename)
                        os.rename(file_path, new_file_path)
                        print(f"Renamed file: {new_file_path}")
                    
                    print(f"Incremental data downloaded and decompressed to: {incremental_dir}")

            messagebox.showinfo("Query Completed", "Data query, download, and decompression completed successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during the query process:\n{str(e)}")

# Create the main window and start the application
root = Tk()
app = DAPQueryApp(root)
root.mainloop()
