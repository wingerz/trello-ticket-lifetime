import json
import pprint
import sys

def get_action_list(card):
    events = []
    for action in card['actions']:
        pprint.pprint(action)
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

    events = sorted(events, key=lambda(x): x['date'])
    return events
    
def transform_card(card):
    return_dict = {}
    for key in ['id', 'url', 'name']:
        return_dict[key] = card[key]

    return_dict['lifetime'] = get_action_list(card)
    return return_dict
    

if __name__ == "__main__":
    card_file = sys.argv[1]
    with open(card_file, 'r') as f:
        data = f.readline()
        card = json.loads(data)

    new_card = transform_card(card)
    print json.dumps(new_card)