from decouple import config
import requests
import json

apikey = "Bearer secret_4tY6KTbAgCKT9eWoLnuXlYKPmXK8wksK1xWQFjiK1Jm"

notion_header = {
    "Notion-Version": "2021-05-13",
    "Content-Type": "application/json"
}


class NotionClient:
    def __init__(self):
        self.db_id = "db387e99888a48ac9cf84bb546dce57d"
        self.db_url = f"https://api.notion.com/v1/databases/{self.db_id}"
        self.db_query_url = f"https://api.notion.com/v1/databases/{self.db_id}/query"

        # Define auth
        notion_header["Authorization"] = config("NOTION_TOKEN")
        self.auth_header = notion_header

    def get_database(self):
        try:
            response = requests.request("GET", self.db_url, headers=self.auth_header)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    def get_database_by_filter(self, filter):
        payload = json.dumps(filter)
        try:
            response = requests.request("POST", self.db_query_url, headers=notion_header, data=payload)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
