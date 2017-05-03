import requests
import csv
from org_mapping import org_mapping


content = requests.get("https://pubs.er.usgs.gov/pubs-services/publication/?", params={"page_size": "50", "page_number": "1"}).json()


affiliation_dict = {}
record_counter = 0
for record in content['records']:
    affiliation_list = []
    if record.get('contributors',{}).get('authors'):
        for author in record['contributors']['authors']:
            if author.get('affiliations'):
                for affiliation in author['affiliations']:
                    affiliation_item = {'id': affiliation['id'], 'name': affiliation['text'], 'usgs': affiliation.get('usgs', False)}
                    if affiliation_item not in affiliation_list:
                        affiliation_list.append(affiliation_item)
    for item in affiliation_list:
        if str(item['id']) in affiliation_dict.keys():
            item_id = item['id']
            original_count = affiliation_dict[item_id]['count']
            new_count = original_count + 1
            affiliation_dict[item['id']]['count'] = new_count
        else:
            affiliation_dict[item['id']] = {'count': 1, 'name': item['name'], 'usgs': item['usgs']}
    record_counter += record_counter

# now we need to clean up the various names



with open('offices.csv', 'w') as csvfile:
    fieldnames = ['organization', 'count', 'usgs', 'id']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for key, value in affiliation_dict.items():
        writer.writerow({'id': key, 'organization': value['name'], 'count': value['count'], 'usgs': value['usgs']})