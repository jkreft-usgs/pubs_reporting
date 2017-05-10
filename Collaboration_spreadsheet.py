import requests
import csv
from copy import deepcopy
from org_mapping import org_mapping


content = requests.get("https://pubs.er.usgs.gov/pubs-services/publication/?",
                       params={"page_size": "5000", "page_number": "1", 'year': 2016}).json()


def build_affiliation_dict(content):
    affiliation_dict = {}
    id_list = []
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
            if item['id'] not in id_list:
                id_list.append(item['id'])
            if item['id'] in affiliation_dict.keys():
                item_id = item['id']
                original_count = affiliation_dict[item_id]['count']
                new_count = original_count + 1
                affiliation_dict[item['id']]['count'] = new_count
            else:
                affiliation_dict[item['id']] = {'count': 1, 'name': item['name'], 'usgs': item['usgs']}
    return affiliation_dict, id_list

# now we need to clean up the various names


def clean_up_affiliation_data(affiliation_dict, id_list, org_mapping):
    """

    :param affiliation_dict:
    :param id_list:
    :param org_mapping:
    :return:
    """
    cleaned_up_dict = {}
    org_id_list = []
    for key, mapping in org_mapping.items():
        mapping_copy = deepcopy(mapping)
        same_as_list = mapping_copy['same_as']
        all_related = same_as_list+[key]
        intersection_list = list(set(all_related).intersection(id_list))
        if intersection_list:
            count = 0
            for element in intersection_list:
                count = count + affiliation_dict[element]['count']
                if element not in org_id_list:
                    org_id_list.append(element)
            cleaned_up_dict[key] = {'count': count, 'name': mapping['name'], 'usgs': mapping.get('usgs', False)}
    # Now we need to add the id's that are not in the mapping list
    orgs_to_add = set(id_list)-set(org_id_list)
    for org_id in orgs_to_add:
        cleaned_up_dict[org_id] = affiliation_dict[org_id]
    return cleaned_up_dict




def build_output_csv(affiliation_dict, filename='offices.csv'):
    with open(filename, 'w') as csvfile:
        fieldnames = ['organization', 'count', 'usgs', 'id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key, value in affiliation_dict.items():
            writer.writerow({'id': key, 'organization': value['name'], 'count': value['count'], 'usgs': value['usgs']})
    csvfile.close()

affiliation_dict, id_list = build_affiliation_dict(content)
cleaned_up_dict = clean_up_affiliation_data(affiliation_dict, id_list, org_mapping)

build_output_csv(affiliation_dict, filename='raw_offices.csv')

build_output_csv(cleaned_up_dict, filename='cleaned_offices.csv')