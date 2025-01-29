#!/usr/bin/env python3
import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox
import customtkinter
import csv


class DiscordMessageReader:
    def __init__(self):
        self.root_window = customtkinter.CTk()
        self.root_window.title("Discord Message Reader")
        self.root_window.geometry('700x600')
        self.root_window.columnconfigure(0, weight=1)
        self.messages_folder = None
        self.channel_index = {}
        self.server_names = {}  # Dict to store {server_id: server_name}
        self.output_format = tk.StringVar(value="Markdown")
        self.only_export_messages = tk.BooleanVar(value=False)
        self.selected_server_id = tk.StringVar()
        self.selected_channel_id = tk.StringVar()
        self.setup_ui()

    def setup_ui(self):
        # Header
        header_label = customtkinter.CTkLabel(
            self.root_window,
            text="Discord Message Reader",
            font=("Arial", 24, 'bold')
        )
        header_label.grid(pady=10)

        # Folder selection
        folder_frame = customtkinter.CTkFrame(self.root_window)
        folder_frame.grid(pady=10, padx=20, sticky="ew")
        folder_frame.columnconfigure(1, weight=1)

        select_button = customtkinter.CTkButton(
            folder_frame, text="Select Folder", command=self.select_directory
        )
        select_button.grid(row=0, column=0, padx=5, pady=5)

        self.selected_folder_label = customtkinter.CTkLabel(
            folder_frame, text="No folder selected", anchor="w"
        )
        self.selected_folder_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Server selection
        server_frame = customtkinter.CTkFrame(self.root_window)
        server_frame.grid(pady=5, padx=20, sticky="ew")
        server_frame.columnconfigure(1, weight=1)

        server_label = customtkinter.CTkLabel(
            server_frame, text="Select Server:"
        )
        server_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.server_dropdown = customtkinter.CTkOptionMenu(
            server_frame,
            values=[],
            variable=self.selected_server_id,
            command=self.on_server_select,
        )
        self.server_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.server_dropdown.configure(state="disabled")

        # Channel selection
        channel_frame = customtkinter.CTkFrame(self.root_window)
        channel_frame.grid(pady=5, padx=20, sticky="ew")
        channel_frame.columnconfigure(1, weight=1)

        channel_label = customtkinter.CTkLabel(
            channel_frame, text="Select Channel:"
        )
        channel_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.channel_dropdown = customtkinter.CTkOptionMenu(
            channel_frame,
            values=[],
            variable=self.selected_channel_id,
        )
        self.channel_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.channel_dropdown.configure(state="disabled")

        # Channel info display
        self.channel_info_label = customtkinter.CTkLabel(
            self.root_window, text="", wraplength=600
        )
        self.channel_info_label.grid(pady=5, padx=20)

        # Output format selection
        format_frame = customtkinter.CTkFrame(self.root_window)
        format_frame.grid(pady=10, padx=20, sticky="w")

        format_label = customtkinter.CTkLabel(format_frame, text="Select Output Format:")
        format_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        markdown_radio = customtkinter.CTkRadioButton(
            format_frame, text="Markdown", variable=self.output_format, value="Markdown"
        )
        markdown_radio.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        csv_radio = customtkinter.CTkRadioButton(
            format_frame, text="CSV", variable=self.output_format, value="CSV"
        )
        csv_radio.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Only export messages checkbox
        checkbox_frame = customtkinter.CTkFrame(self.root_window)
        checkbox_frame.grid(pady=5, padx=20, sticky="w")

        export_checkbox = customtkinter.CTkCheckBox(
            checkbox_frame, text="Only Export Messages", variable=self.only_export_messages
        )
        export_checkbox.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Extract button
        self.extract_button = customtkinter.CTkButton(
            self.root_window,
            text="Extract Messages",
            command=self.extract_messages,
            state="disabled"
        )
        self.extract_button.grid(pady=10, padx=20)

        # Status display
        self.status_label = customtkinter.CTkLabel(
            self.root_window, text="", wraplength=600
        )
        self.status_label.grid(pady=10, padx=20)

    def select_directory(self):
        self.messages_folder = filedialog.askdirectory()
        if self.messages_folder:
            print(f"\nSelected folder: {self.messages_folder}")
            self.selected_folder_label.configure(
                text=f"Selected folder: {self.messages_folder}"
            )
            self.load_channel_index()
            self.server_dropdown.configure(state="normal")
            self.extract_button.configure(state="normal")

    def load_channel_index(self):
        index_path = os.path.join(self.messages_folder, 'index.json')
        try:
            print(f"Loading index from: {index_path}")
            with open(index_path, 'r', encoding='utf-8') as f:
                self.channel_index = json.load(f)
            print(f"Successfully loaded index with {len(self.channel_index)} channels")

            self.populate_server_dropdown()

        except FileNotFoundError:
            print("ERROR: index.json not found")
            messagebox.showerror(
                "Error", "index.json not found in selected folder"
            )
            self.channel_index = {}
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse index.json - {str(e)}")
            messagebox.showerror(
                "Error", f"Failed to parse index.json: {str(e)}"
            )
            self.channel_index = {}

    def populate_server_dropdown(self):
        # Extract and store server names
        self.server_names = {}
        for channel_id, channel_info in self.channel_index.items():
            parts = channel_info.split(" in ", 1)
            if len(parts) == 2:
                channel_name, server_name = parts
                self.server_names[server_name] = server_name  # Store server names (using name as id)

        server_list = list(self.server_names.keys())
        self.server_dropdown.configure(values=server_list)
        print(f"Populated server dropdown with: {server_list}")

    def on_server_select(self, selected_server):
        print(f"Selected Server: {selected_server}")
        self.selected_server_id.set(selected_server)  # Update the StringVar
        self.populate_channel_dropdown(selected_server)

    def populate_channel_dropdown(self, selected_server):
        channel_list = []
        for channel_id, channel_info in self.channel_index.items():
            if channel_info.endswith(f" in {selected_server}"):
                channel_name = channel_info.replace(f" in {selected_server}", "")
                channel_list.append((channel_id, channel_name))

        # Sort channels alphabetically
        channel_list.sort(key=lambda x: x[1])

        channel_names = [name for id, name in channel_list]
        self.channel_dropdown.configure(values=channel_names, state="normal")
        print(f"Populated channel dropdown with: {[name for id, name in channel_list]}")

        # Enable channel dropdown
        if channel_names:
            self.channel_dropdown.configure(state="normal")
        else:
            self.channel_dropdown.configure(state="disabled")

    def get_messages_by_id(self, channel_id):
        messages = []
        channel_info = self.channel_index.get(channel_id, "Unknown Channel")
        print(f"\nSearching for messages:")
        print(f"Channel ID: {channel_id}")
        print(f"Channel Info: {channel_info}")
        print(f"Base folder: {self.messages_folder}")

        # Iterate through each subfolder to find the matching channel.json
        for item in os.listdir(self.messages_folder):
            dir_path = os.path.join(self.messages_folder, item)
            if os.path.isdir(dir_path):
                channel_json_path = os.path.join(dir_path, 'channel.json')
                if os.path.exists(channel_json_path):
                    try:
                        with open(channel_json_path, 'r', encoding='utf-8') as f:
                            channel_data = json.load(f)
                        current_channel_id = channel_data.get("id")
                        if str(current_channel_id) == str(channel_id):
                            print(f"Matching channel found in folder: {dir_path}")
                            messages_path = os.path.join(dir_path, 'messages.json')
                            if os.path.exists(messages_path):
                                try:
                                    print(f"\nReading: {messages_path}")
                                    with open(messages_path, 'r', encoding="utf-8") as json_file:
                                        channel_messages = json.load(json_file)
                                        print(f"Found {len(channel_messages)} total messages in file")
                                        for message in channel_messages:
                                            # Add channel info to each message
                                            message["ChannelInfo"] = channel_info
                                            messages.append(message)
                                        print(f"Added {len(channel_messages)} messages from {messages_path}")
                                except Exception as e:
                                    print(f"Error reading {messages_path}: {str(e)}")
                            else:
                                print(f"No messages.json found in {dir_path}")
                            # Since channel IDs are unique, we can break after finding the match
                            break
                    except Exception as e:
                        print(f"Error reading {channel_json_path}: {str(e)}")
                else:
                    print(f"No channel.json found in {dir_path}")

        print(f"\nTotal messages found: {len(messages)}")
        return messages

    def format_message_markdown(self, message):
        """
        Formats a message into Markdown.
        """
        # Handle timestamp
        timestamp_raw = message.get("Timestamp") or message.get("timestamp")
        if timestamp_raw:
            try:
                # Attempt to parse the timestamp
                timestamp = datetime.strptime(timestamp_raw, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                # If parsing fails, retain the original string
                timestamp = timestamp_raw
        else:
            timestamp = "Unknown Time"

        # Handle ChannelInfo
        channel_info = message.get("ChannelInfo", "Unknown Channel")

        # Handle Content
        content = message.get("Contents") or message.get("Content") or message.get("content") or "*No content*"

        # Handle Attachments
        attachments = message.get("Attachments") or message.get("attachments") or ""
        if attachments and not self.only_export_messages.get():
            attachments_section = f"- **Attachments:** {attachments}\n"
        else:
            attachments_section = ""

        return f"""### Message in {channel_info}
- **Time:** {timestamp}
- **Content:** {content}
{attachments_section}
"""

    def export_to_csv(self, messages, output_filename):
        """
        Exports messages to a CSV file.
        """
        try:
            with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Timestamp', 'Content']
                if not self.only_export_messages.get():
                    fieldnames.append('Attachments')
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for message in messages:
                    row = {
                        'Timestamp': message.get("Timestamp") or message.get("timestamp") or "Unknown Time",
                        'Content': message.get("Contents") or message.get("Content") or message.get(
                            "content") or "*No content*"
                    }
                    if not self.only_export_messages.get():
                        row['Attachments'] = message.get("Attachments") or message.get("attachments") or ""
                    writer.writerow(row)
            print(f"\nSaved messages to: {output_filename}")
            self.status_label.configure(
                text=f"Messages have been saved to {output_filename}"
            )
            messagebox.showinfo(
                "Success", f"Messages have been extracted to {output_filename}"
            )
        except Exception as e:
            print(f"Error writing to {output_filename}: {str(e)}")
            messagebox.showerror(
                "Error", f"Failed to write messages to file: {str(e)}"
            )

    def extract_messages(self):
        selected_channel = self.selected_channel_id.get()
        if not selected_channel:
            messagebox.showerror("Error", "Please select a channel")
            return

        # Get the channel ID from the dropdown selection
        channel_id = None
        for id, info in self.channel_index.items():
            if info.startswith(selected_channel):
                channel_id = id
                break
        if not channel_id:
            messagebox.showerror("Error", "Channel ID not found in index")
            return

        self.status_label.configure(text="Extracting messages...")
        self.root_window.update()

        messages = self.get_messages_by_id(channel_id)
        if not messages:
            self.status_label.configure(text="No messages found for this channel ID")
            return

        messages.sort(key=lambda x: x.get("Timestamp") or x.get("timestamp", ""))  # Sort by timestamp

        # Create output filename based on channel info
        channel_info = self.channel_index[channel_id]
        safe_filename = "".join(x for x in channel_info if x.isalnum() or x in (' ', '-', '_')).strip().replace(' ',
                                                                                                                '_')

        output_format = self.output_format.get()
        if output_format == "Markdown":
            output_filename = f"messages_{safe_filename}.md"
            try:
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write(f"# Messages from {channel_info}\n\n")
                    for message in messages:
                        markdown = self.format_message_markdown(message)
                        f.write(markdown)
                print(f"\nSaved messages to: {output_filename}")
                self.status_label.configure(
                    text=f"Messages have been saved to {output_filename}"
                )
                messagebox.showinfo(
                    "Success", f"Messages have been extracted to {output_filename}"
                )
            except Exception as e:
                print(f"Error writing to {output_filename}: {str(e)}")
                messagebox.showerror(
                    "Error", f"Failed to write messages to file: {str(e)}"
                )
        elif output_format == "CSV":
            output_filename = f"messages_{safe_filename}.csv"
            self.export_to_csv(messages, output_filename)
        else:
            messagebox.showerror("Error", "Unsupported output format selected.")
            print("Unsupported output format selected.")

    def run(self):
        self.root_window.mainloop()


if __name__ == "__main__":
    app = DiscordMessageReader()
    app.run()