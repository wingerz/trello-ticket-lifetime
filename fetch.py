import json
import trello
import yaml


DATA_DIR = 'data/'
    
def get_client(config):
    client = trello.TrelloClient(config['key'], api_secret=config['secret'], token=config['oauth_token'], token_secret=config['oauth_token_secret'])
    return client

def card_to_json(card):
    card.fetch()
    card.fetch_actions(action_filter='all')
    card_actions = card.actions
    return_dict = {}
    for key in ['id', 'closed', 'description', 'due', 'labels', 'list_id', 'member_ids', 'name', 'short_id', 'url']:
        return_dict[key] = getattr(card, key)
    return_dict['actions'] = card_actions
    return return_dict

if __name__ == "__main__":
    with open('secret.yaml') as f:
        config = yaml.load(f)


    client = get_client(config)
    boards = client.list_boards()
    mobile_board = client.get_board('51bba780ac3b4aae26006928')

    cards = mobile_board.all_cards()
    for card in cards:
        with open(DATA_DIR + card.id + '.json', 'w') as f:
            print >>f, json.dumps(card_to_json(card))
