import json
from os import listdir
from os.path import isfile, join
import sys


def list_to_class(list_name):
    if list_name in ('In Review', 'Code Review'):
        return 'review'
    elif list_name.startswith('Done'):
        return 'done'
    elif list_name in ('Dev', 'Doing'):
        return 'dev'
    elif list_name in ('Ready/Push Queue', 'Ready'):
        return 'ready'
    else:
        return 'queued'


def construct_lanes(cards):
    lanes = []
    items = []
    card_id = 0
    thing_id = 0

    lists = set()
    
    for card in cards:
        lane_id = card_id
        lanes.append({
            'id': lane_id,
            'label': card['name']
        })

        item_base = {
            'lane': lane_id,
        }

        previous_item = None
        for phase in card['lifetime']:
            # close off previous item
            if previous_item:
                previous_item['end'] = phase['date']
                items.append(previous_item)
            
            item = item_base.copy()
            item['id'] = phase['after_list']['name'] #thing_id

            item['desc'] = phase['after_list']['name']
            item['class'] = list_to_class(item['desc'])
            item['start'] = phase['date']

            previous_item = item
            thing_id += 1
            
        if previous_item:
            previous_item['end'] = previous_item['start']
            items.append(previous_item)        

        card_id += 1
    
    return {
        'lanes': lanes,
        'items': items,
        'lists': list(lists)
    }
    

if __name__ == "__main__":
    input_dir = sys.argv[1]
    data_files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]
    cards = []
    for file in data_files:
        with open(join(input_dir, file)) as f:
            data = f.readline()
        card = json.loads(data)
        cards.append(card)
    output = construct_lanes(cards)
    print json.dumps(output)