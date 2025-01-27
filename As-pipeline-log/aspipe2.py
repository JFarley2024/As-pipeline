import json
from typing import List, Dict
from asnake.client import ASnakeClient

def fetch_archival_objects_details(client: ASnakeClient, repo_id: int = 2) -> List[Dict]:
    """
    Fetch comprehensive details for archival objects in a repository.
    
    :param client: Authenticated ASnakeClient
    :param repo_id: Repository ID (default 2)
    :return: List of dictionaries containing archival object details
    """
    # Fetch all archival object IDs
    arch_obj = client.get(f'repositories/{repo_id}/archival_objects', params={'all_ids': True}).json()
    
    objects = []
    for obj in arch_obj:
        try:
            # Fetch individual archival object details
            endpoint = f'repositories/{repo_id}/archival_objects/{obj}'
            obj_details = client.get(endpoint).json()
            
            # Create graph data dictionary
            graph_data = {}
            
            # Fetch resource details
            resource_uri = obj_details['resource']['ref']
            res = client.get(resource_uri).json()
            
            # Populate basic object information
            if 'title' in res:
                graph_data['Collection'] = res['title']
            
            graph_data['Archival Object'] = obj_details['display_string']
            
            # Add optional identifiers
            if 'ref_id' in obj_details:
                graph_data['Reference ID'] = obj_details['ref_id']
            
            if 'component_id' in obj_details:
                graph_data['Component ID'] = obj_details['component_id']
            
            # Process instances and locations
            if obj_details.get('instances'):
                arch_object_instance = obj_details['instances']
                if arch_object_instance and 'sub_container' in arch_object_instance[0]:
                    top_container = arch_object_instance[0]['sub_container']['top_container']['ref']
                    top_container_details = client.get(top_container).json()
                    
                    if top_container_details.get('container_locations'):
                        top_container_location = top_container_details['container_locations'][0]['ref']
                        location = client.get(top_container_location).json()
                        graph_data['Object Location'] = location.get('title')
            
            objects.append(graph_data)
        
        except Exception as e:
            print(f"Error processing archival object {obj}: {e}")
    
    return objects

def save_archival_objects_to_json(objects: List[Dict], filename: str = 'ArchivesSpace_Events.json'):
    """
    Save archival objects details to a JSON file.
    
    :param objects: List of archival objects details
    :param filename: Output JSON filename
    """
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(objects, json_file, indent=4)

def main():
    from secrets_2 import baseurl, username, password
    
    # Initialize client
    client = ASnakeClient(baseurl=baseurl, username=username, password=password)
    client.authorize()
    
    # Fetch archival objects details
    objects = fetch_archival_objects_details(client)
    
    # Save to JSON
    save_archival_objects_to_json(objects)
    
    print(f"Processed {len(objects)} archival objects")

if __name__ == "__main__":
    main()