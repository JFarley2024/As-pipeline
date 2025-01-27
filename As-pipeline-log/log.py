import json
import requests
import urllib3
from typing import Dict, List, Optional
from datetime import datetime

def fetch_all_physical_objects() -> List[Dict]:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    all_results = []
    next_url = 'http://192.168.1.69:8008/api/physical-objects/'
    
    while next_url:
        response = requests.get(next_url, headers={'accept': 'application/json'}, verify=False)
        response.raise_for_status()
        data = response.json()
        all_results.extend(data['results'])
        next_url = data['next']
    
    return all_results

def load_json_file(filename: str) -> Optional[List[Dict]]:
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_and_print(file, message: str):
    print(message)
    file.write(message + '\n')

def compare_objects(json_file: str = 'ArchivesSpace_Events.json'):
    api_objects = fetch_all_physical_objects()
    json_objects = load_json_file(json_file)
    
    with open('log_diff_report.txt', 'w') as report:
        write_and_print(report, f"Comparison Report Generated: {datetime.now()}\n")
        write_and_print(report, f"API objects: {len(api_objects)}")
        write_and_print(report, f"JSON objects: {len(json_objects)}\n")
        
        api_dict = {obj['internal_identifier']: obj for obj in api_objects}
        json_dict = {obj.get('Component ID'): obj for obj in json_objects if obj.get('Component ID')}
        
        missing_in_api = set(json_dict.keys()) - set(api_dict.keys())
        missing_in_json = set(api_dict.keys()) - set(json_dict.keys())
        
        write_and_print(report, f"Items in JSON but missing from API: {len(missing_in_api)}")
        for key in missing_in_api:
            write_and_print(report, f"- {key}: {json_dict[key]['Archival Object']}")
        
        write_and_print(report, f"\nItems in API but missing from JSON: {len(missing_in_json)}")
        for key in missing_in_json:
            write_and_print(report, f"- {key}: {api_dict[key]['name']}")

if __name__ == "__main__":
    compare_objects()
