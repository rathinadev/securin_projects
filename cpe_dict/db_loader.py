import json
from pymongo import MongoClient
from datetime import datetime

def get_title(title_data):
    if isinstance(title_data, dict):
        return title_data.get('#text', '')
    elif isinstance(title_data, list):
        for item in title_data:
            if isinstance(item, dict):
                return item.get('#text', '')
    return ''

def process_cpe_item(item):
    processed_item = {
        'cpe_title': get_title(item.get('title', {})),
        'cpe_22_uri': '',
        'cpe_23_uri': '',
        'reference_links': [],
        'cpe_22_deprecation_date': None,
        'cpe_23_deprecation_date': None
    }
    
    references = item.get('references', {})
    if references:
        refs = references.get('reference', [])
        if isinstance(refs, dict):
            processed_item['reference_links'] = [refs.get('@href', '')]
        elif isinstance(refs, list):
            processed_item['reference_links'] = [ref.get('@href', '') for ref in refs]
    
    if item.get('@deprecated') == 'true' and item.get('@deprecation_date'):
        try:
            if item.get('@name', '').startswith('cpe:/'):
                original_date = datetime.strptime(
                    item['@deprecation_date'], 
                    '%Y-%m-%dT%H:%M:%S.%fZ'
                )

                if item.get('cpe-23:cpe23-item', {}).get('cpe-23:deprecation', {}).get('@date'):
                    processed_item['cpe_23_deprecation_date'] = item.get('cpe-23:cpe23-item', {}).get('cpe-23:deprecation', {}).get('@date')
                if item.get('cpe-22:cpe22-item', {}).get('cpe-22:deprecation', {}).get('@date'):
                    processed_item['cpe_22_deprecation_date'] = item.get('cpe-22:cpe22-item', {}).get('cpe-22:deprecation', {}).get('@date')
        except ValueError:
            pass
    
    cpe23_item = item.get('cpe-23:cpe23-item', {})
    if isinstance(cpe23_item, dict):
        processed_item['cpe_23_uri'] = cpe23_item.get('@name', '')
    if item.get('cpe-22:cpe23-item', {}):
        processed_item['cpe_22_uri'] = item.get('cpe-22:cpe23-item', {}).get('@name', '')
        
    
    return processed_item

def import_to_mongodb():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['CPE_DATABASE']
    collection = db['CPE_COLLECTION']
    
    with open('xml.json', 'r') as file:
        data = json.load(file)
        cpe_items = data['cpe-list']['cpe-item']
        
        processed_items = []
        count = 0
        
        for item in cpe_items:
            try:
                processed_item = process_cpe_item(item)
                processed_items.append(processed_item)
                count += 1
                
                if len(processed_items) >= 1000:
                    collection.insert_many(processed_items)
                    processed_items = []
                    print(f"Processed {count} items")
            except Exception as e:
                print(f"Error processing item {count}: {str(e)}")
                continue
                
        if processed_items:
            collection.insert_many(processed_items)
            
        print(f"Completed processing {count} items")

if __name__ == "__main__":
    try:
        import_to_mongodb()
    except Exception as e:
        print(f"Error: {str(e)}")