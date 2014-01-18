import json
from os import listdir
from os.path import isfile, join
import sys

def get_action_list(card):
    events = []
    unrecognized_actions = []
    for action in card['actions']:
        if action['type'] == 'createCard':
            create_event = {
                'date': action['date'],
                'after_list': action['data']['list'],
            }
            events.append(create_event)
        elif action['type'] == 'updateCard' and 'listAfter' in action['data']:
            move_event = {
                'date': action['date'],
                'after_list': action['data']['listAfter']
            }
            events.append(move_event)
        else:
            unrecognized_actions.append(action)

    events = sorted(events, key=lambda(x): x['date'])
    return events, unrecognized_actions
    
def transform_card(card):
    return_dict = {}
    for key in ['id', 'url', 'name']:
        return_dict[key] = card[key]

    return_dict['lifetime'], _ = get_action_list(card)
    return return_dict
    

if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    data_files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]
    for card_file in data_files:
        with open(join(input_dir, card_file), 'r') as f:
            data = f.readline()
            card = json.loads(data)
        new_card = transform_card(card)
        with open(join(output_dir, card_file), 'w') as f:
            print >>f, json.dumps(new_card)