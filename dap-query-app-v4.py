import asyncio
import os
from datetime import datetime, timezone
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import Calendar

from dap.api import DAPClient
from dap.dap_types import Format, IncrementalQuery, SnapshotQuery, Credentials

class DAPQueryApp:
    def __init__(self, master):
        self.master = master
        master.title("DAP Query App")

        # Create input fields and labels
        self.create_input_fields()

        # Create a dropdown for selecting the table
        self.create_table_dropdown()

        # Create radio buttons for selecting the query type
        self.create_query_type_radio()

        # Create fields for since timestamp
        self.create_since_timestamp_field()

        # Create a dropdown for selecting the file format
        self.create_file_format_dropdown()

        # Create an entry field and button for selecting the output directory
        self.create_output_directory_field()

        # Create a button to start the query process
        self.create_start_query_button()

    def create_input_fields(self):
        fields = [
            ("DAP API URL", "api_url_entry", "https://api-gateway.instructure.com"),
            ("Client ID", "client_id_entry", ""),
            ("Client Secret", "client_secret_entry", ""),
            ("Namespace", "namespace_entry", "canvas")
        ]

        for i, (label_text, attr_name, default_value) in enumerate(fields):
            tk.Label(self.master, text=label_text).grid(row=i, column=0, sticky="w")
            entry = tk.Entry(self.master, width=50)
            entry.insert(0, default_value)
            entry.grid(row=i, column=1)
            setattr(self, attr_name, entry)

    def create_table_dropdown(self):
        tk.Label(self.master, text="Table").grid(row=4, column=0, sticky="w")
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
        self.table_dropdown = ttk.Combobox(self.master, values=table_names, state="readonly")
        self.table_dropdown.current(0)  # Set the default selected item
        self.table_dropdown.grid(row=4, column=1)

    def create_query_type_radio(self):
        tk.Label(self.master, text="Query Type").grid(row=5, column=0, sticky="w")
        self.query_type_var = tk.StringVar(value="snapshot")
        tk.Radiobutton(self.master, text="Snapshot", variable=self.query_type_var, value="snapshot").grid(row=5, column=1, sticky="w")
        tk.Radiobutton(self.master, text="Incremental", variable=self.query_type_var, value="incremental").grid(row=6, column=1, sticky="w")

    def create_since_timestamp_field(self):
        tk.Label(self.master, text="Since Timestamp (Incremental)").grid(row=7, column=0, sticky="w")
        self.since_timestamp_var = tk.StringVar()
        self.since_timestamp_entry = tk.Entry(self.master, textvariable=self.since_timestamp_var, state="readonly")
        self.since_timestamp_entry.grid(row=7, column=1)
        tk.Button(self.master, text="Select Date", command=self.select_since_timestamp).grid(row=7, column=2)

    def create_file_format_dropdown(self):
        tk.Label(self.master, text="File Format").grid(row=8, column=0, sticky="w")
        file_formats = ["jsonl", "csv", "tsv", "parquet"]
        self.file_format_var = tk.StringVar(value=file_formats[0])
        self.file_format_dropdown = ttk.Combobox(self.master, values=file_formats, state="readonly", textvariable=self.file_format_var)
        self.file_format_dropdown.current(0)  # Set the default selected item
        self.file_format_dropdown.grid(row=8, column=1)

    def create_output_directory_field(self):
        tk.Label(self.master, text="Output Directory").grid(row=9, column=0, sticky="w")
        self.output_dir_entry = tk.Entry(self.master, width=50)
        self.output_dir_entry.grid(row=9, column=1)
        tk.Button(self.master, text="Browse", command=self.browse_output_dir).grid(row=9, column=2)

    def create_start_query_button(self):
        tk.Button(self.master, text="Start Query", command=self.start_query).grid(row=10, columnspan=3, pady=10)

    def browse_output_dir(self):
        """Open a file dialog to select the output directory"""
        output_dir = filedialog.askdirectory()
        self.output_dir_entry.delete(0, 'end')
        self.output_dir_entry.insert(0, output_dir)

    def select_since_timestamp(self):
        """Open a calendar window to select the since timestamp for incremental queries"""
        def set_date():
            selected_date = cal.get_date()
            selected_time = f"{hour.get()}:{minute.get()}:{second.get()}"
            selected_datetime = f"{selected_date} {selected_time}"
            try:
                # Parse the datetime to ensure it's valid
                parsed_datetime = datetime.strptime(selected_datetime, "%Y-%m-%d %H:%M:%S")
                # Format the datetime as required
                formatted_datetime = parsed_datetime.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                self.since_timestamp_var.set(formatted_datetime)
                top.destroy()
            except ValueError:
                tk.messagebox.showerror("Invalid Date", "Please select a valid date and time.")

        top = tk.Toplevel(self.master)
        top.title("Select Date and Time")

        # Calendar
        cal = Calendar(top, selectmode='day', date_pattern="yyyy-mm-dd")
        cal.pack(padx=10, pady=10)

        # Time selection
        time_frame = ttk.Frame(top)
        time_frame.pack(padx=10, pady=5)

        hour = ttk.Spinbox(time_frame, from_=0, to=23, width=3, format="%02.0f")
        minute = ttk.Spinbox(time_frame, from_=0, to=59, width=3, format="%02.0f")
        second = ttk.Spinbox(time_frame, from_=0, to=59, width=3, format="%02.0f")

        hour.set("00")
        minute.set("00")
        second.set("00")

        hour.pack(side=tk.LEFT, padx=2)
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        minute.pack(side=tk.LEFT, padx=2)
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        second.pack(side=tk.LEFT, padx=2)

        # Set button
        ttk.Button(top, text="Set", command=set_date).pack(pady=10)

        top.grab_set()  # Make the window modal
        self.master.wait_window(top)  # Wait for the top-level window to be destroyed

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
                    since_datetime = datetime.strptime(since_timestamp, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=timezone.utc)

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
root = tk.Tk()
app = DAPQueryApp(root)
root.mainloop()

