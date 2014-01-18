import json
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
        previous_item['end'] = previous_item['start']
        items.append(previous_item)        

        card_id += 1
    
    return {
        'lanes': lanes,
        'items': items,
    }
    


if __name__ == "__main__":
    input_file = sys.argv[1]
    with open(input_file) as f:
        data = f.readline()
        card = json.loads(data)

    cards = [card]
    output = construct_lanes(cards)
    print json.dumps(output)