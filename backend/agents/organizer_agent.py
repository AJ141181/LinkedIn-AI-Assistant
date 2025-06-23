from google.adk.agents import BaseAgent
from typing import ClassVar, Optional
import os
import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


class OrganizerAgent(BaseAgent):
    folder_name: str = "F_LinkedIn_AI_Curation"
    sheet_name: str = "S_LinkedIn_AI_Curation"
    creds_path: str = os.getenv("GOOGLE_SHEET_CREDS_PATH")

    drive_service: ClassVar[Optional[object]] = None
    sheets_service: ClassVar[Optional[object]] = None
    spreadsheet_id: ClassVar[Optional[str]] = None

    def __init__(self):
        super().__init__(name="organizer_agent")

        creds = Credentials.from_service_account_file(
            self.creds_path,
            scopes=["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
        )

        OrganizerAgent.drive_service = build("drive", "v3", credentials=creds)
        OrganizerAgent.sheets_service = build("sheets", "v4", credentials=creds)

        folder_id = self._get_or_create_folder(self.folder_name)
        OrganizerAgent.spreadsheet_id = self._get_or_create_sheet(self.sheet_name, folder_id)

        self._ensure_headers()

    def _get_or_create_folder(self, folder_name):
        response = self.drive_service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id, name)"
        ).execute()
        files = response.get("files", [])
        if files:
            return files[0]["id"]

        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        folder = self.drive_service.files().create(body=folder_metadata, fields="id").execute()
        return folder["id"]

    def _get_or_create_sheet(self, sheet_name, folder_id):
        response = self.drive_service.files().list(
            q=f"name='{sheet_name}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
            fields="files(id, name, parents)"
        ).execute()
        files = response.get("files", [])

        if files:
            file = files[0]
            file_id = file["id"]
            current_parents = file.get("parents", [])

            if not current_parents:
                print(f"⚠️ WARNING: Sheet '{sheet_name}' exists but is orphaned (no parents). Cannot move it to folder.")
                return file_id

            if folder_id not in current_parents:
                self.drive_service.files().update(
                    fileId=file_id,
                    addParents=folder_id,
                    removeParents=",".join(current_parents),
                    fields="id, parents"
                ).execute()

            return file_id

        sheet_metadata = {
            "name": sheet_name,
            "mimeType": "application/vnd.google-apps.spreadsheet",
        }
        file = self.drive_service.files().create(body=sheet_metadata, fields="id").execute()
        file_id = file["id"]

        self.drive_service.files().update(
            fileId=file_id,
            addParents=folder_id,
            fields="id, parents"
        ).execute()

        return file_id

    def _ensure_headers(self):
        expected_headers = [
            "Timestamp", "Author", "Summary", "Tags", "Likes",
            "Comments", "Reposts", "Followers", "URL", "Other Sources"
        ]

        response = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range="Sheet1!A1:J1"
        ).execute()

        current_headers = response.get("values", [])

        if not current_headers or current_headers[0] != expected_headers:
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range="Sheet1!A1:J1",
                valueInputOption="RAW",
                body={"values": [expected_headers]}
            ).execute()

    def run(self, input_data: dict):
        curated = input_data["curated"]
        summary = input_data["summary"]
        tags = input_data["tags"]
         # 🐞 DEBUG: Print engagement fields
        print("✅ Curated data received in OrganizerAgent:")
        print("Author:", curated.get("author"))
        print("Likes:", curated.get("likes"))
        print("Comments:", curated.get("comments"))
        print("Reposts:", curated.get("reposts"))
        print("Followers:", curated.get("followers"))
        print("URL:", curated.get("url"))
        print("Newsletter:", curated.get("newsletter"))
        timestamp = curated.get("timestamp") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [[
            timestamp,
            curated.get("author", ""),
            summary,
            "\n".join(tags) if isinstance(tags, list) else tags,
            curated.get("likes", 0),
            curated.get("comments", 0),
            curated.get("reposts", 0),
            curated.get("followers", ""),
            curated.get("url", ""),
            curated.get("newsletter", "")
        ]]

        # Append data row to sheet
        self.sheets_service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range="Sheet1!A2",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": row}
        ).execute()

        # Apply text wrapping to Summary (C) and Tags (D)
        self.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={
                "requests": [
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": 0,
                                "startColumnIndex": idx,
                                "endColumnIndex": idx + 1
                            },
                            "cell": {
                                "userEnteredFormat": {
                                    "wrapStrategy": "WRAP"
                                }
                            },
                            "fields": "userEnteredFormat.wrapStrategy"
                        }
                    }
                    for idx in [2, 3, 9]  # Columns: Summary (C), Tags (D)
                ]
            }
        ).execute()

        return {
            "curated": curated,
            "summary": summary,
            "tags": tags
        }


organizer_agent = OrganizerAgent()
