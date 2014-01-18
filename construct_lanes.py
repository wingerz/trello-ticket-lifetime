import json
from os import listdir
from os.path import isfile, join
import sys

def construct_lanes(cards):
    lanes = []
    items = []
    card_id = 0
    thing_id = 0
    
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

            # TODO figure out what to do here
            item['class'] = 'past'
            item['desc'] = phase['after_list']['name']
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