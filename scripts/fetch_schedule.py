import argparse
import gspread
import json
from typing import Optional, Dict

SPREADSHEET_ID = '1TB4PQx-xKl6aYQ7d8w0Asy4pTIVufY3lq84huYTz0-8'

def fetch_data_for_date(date_str: str) -> Optional[Dict]:
    try:
        # Authenticate using the service account file
        # This requires a credentials.json file in the root of your project
        gc = gspread.service_account(filename='credentials.json')
        
        # Open the Google Sheet by its ID
        sh = gc.open_by_key(SPREADSHEET_ID)
        
        # --- 1. Service Details (Assumes first worksheet) ---
        ws_service = sh.get_worksheet(0)
        
        # Helper to extract and warn if empty
        def get_value(row_dict: dict, field_name: str, *possible_keys: str) -> str:
            for key in possible_keys:
                val = row_dict.get(key)
                if val:
                    val_str = str(val).strip()
                    if val_str:
                        return val_str
            print(f"Warning: Missing value for '{field_name}' on date '{date_str}'.")
            return ''

        # Fetch all values to avoid duplicate header errors with getting records directly
        service_values = ws_service.get_all_values()
        service_records = []
        if len(service_values) > 1:
            # The actual column headers (Date, Preacher, etc.) are in the second row
            headers = [h.strip() for h in service_values[1]]
            for row in service_values[2:]:
                record = {}
                for i, header in enumerate(headers):
                    if header:
                        record[header] = row[i] if i < len(row) else ''
                service_records.append(record)
        
        service_data = None
        for row in service_records:
            row_date = str(row.get('Date', '')).strip()
            if row_date == date_str:
                service_data = {
                    'Preacher': get_value(row, 'Preacher', 'Preacher'),
                    'Sermon title': get_value(row, 'Sermon title', 'Sermon title'),
                    'Scripture reading reference': get_value(row, 'Scripture reading reference', 'Scripture reading reference', 'Scripture reading', 'Scripture Reading'),
                    'Call to worship': get_value(row, 'Call to worship', 'Call to worship', 'Call To Worship'),
                    'Offerings': get_value(row, 'Offerings', 'Offerings')
                }
                break
        
        # --- 2. Worship Service Songs Details ---
        try:
            ws_songs = sh.worksheet("Worship Service Songs")
            song_values = ws_songs.get_all_values()
            song_records = []
            if len(song_values) > 1:
                # The headers are in the second row
                headers = [h.strip() for h in song_values[1]]
                for row in song_values[2:]:
                    record = {}
                    for i, header in enumerate(headers):
                        if header:
                            record[header] = row[i] if i < len(row) else ''
                    song_records.append(record)
        except gspread.exceptions.WorksheetNotFound:
            print("Warning: Worksheet 'Worship Service Songs' not found.")
            song_records = []

        song_data = None
        for row in song_records:
            row_date = str(row.get('Date', '')).strip()
            if row_date == date_str:
                song_data = {
                    'Song service song 1': get_value(row, 'Song service song 1', 'Song service song 1'),
                    'Song service song 2': get_value(row, 'Song service song 2', 'Song service song 2'),
                    'Opening song': get_value(row, 'Opening song', 'Opening song'),
                    'Closing song': get_value(row, 'Closing song', 'Closing song')
                }
                break

        if not service_data and not song_data:
            print(f"No data found for date: {date_str}")
            return None
            
        result = {
            'date': date_str,
            'service_details': service_data or {},
            'song_details': song_data or {}
        }
        return result

    except FileNotFoundError:
        print("Error: 'credentials.json' not found. Please follow the setup instructions to create a Google Service Account.")
        return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Worship Service data from Google Sheets")
    parser.add_argument("date", help="Date to fetch data for (e.g., '4/18/2026' or '2026-04-18', must exactly match the formatting shown in your Google Sheet's Date column)")
    args = parser.parse_args()
    
    data = fetch_data_for_date(args.date)
    if data:
        print(f"--- Service Details for {data['date']} ---")
        for k, v in data['service_details'].items():
            print(f"{k}: {v}")
            
        print(f"\n--- Song Details for {data['date']} ---")
        for k, v in data['song_details'].items():
            print(f"{k}: {v}")
