import json
from os import listdir
from os.path import isfile, join
import pprint
import sys

import dateutil.parser
import numpy


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

def is_complete(card):
    for phase in card['lifetime']:
        phase_after_list = phase.get('after_list', {}).get('name')
        phase_after_list_type = list_to_class(phase_after_list) if phase_after_list else None
        
        if phase_after_list_type == 'done':
            return True
    return False


def get_phase_time(card, phase_type):
    phase_time = 0
    phase_start_time = None
    for phase in card['lifetime']:
        phase_after_list = phase.get('after_list', {}).get('name')
        phase_after_list_type = list_to_class(phase_after_list) if phase_after_list else None
        
        if phase_start_time:
            phase_end_time = dateutil.parser.parse(phase['date'])
            phase_time += (phase_end_time - phase_start_time).total_seconds()
            phase_start_time = None
        
        if phase_after_list_type == phase_type:
            phase_start_time = dateutil.parser.parse(phase['date'])

    return phase_time / 24. / 3600

def summarize_card_times(card):
    queue_time = get_phase_time(card, 'queued')
    dev_time = get_phase_time(card, 'dev')
    review_time = get_phase_time(card, 'review')
    ready_time = get_phase_time(card, 'ready')
    return queue_time, dev_time, review_time, ready_time

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
    
def compute_stats(arr):
    return {
        'count': len(arr),
        'avg': numpy.average(arr),
        'median': numpy.median(arr),
        'std': numpy.std(arr),
        'min': min(arr),
        'max': max(arr),
    }
    

def process_times(all_card_times):
    queue_times = [card[1] for card in all_card_times]
    dev_times = [card[2] for card in all_card_times]
    review_times = [card[3] for card in all_card_times]
    ready_times = [card[4] for card in all_card_times]

    total_time_in_flight = [card[1] + card[2] + card[3] + card[4] for card in all_card_times]
    total_active_time = [card[2] + card[3] + card[4] for card in all_card_times]
    dev_to_review_ratio = []

    for card in all_card_times:
        if card[2] > 0.5 and card[3] > 0.5:
            dev_to_review_ratio.append(card[2] / card[3])

    stats = {
        'total': compute_stats(total_time_in_flight),
        'active': compute_stats(total_active_time),
        'review': compute_stats(review_times),
        'dev': compute_stats(dev_times),
        'ready': compute_stats(ready_times),
        'queue': compute_stats(queue_times),
        'dev_to_review_ratio': compute_stats(dev_to_review_ratio)
    }
    return stats


def sanitize_float(float_val):
    if float_val < 0.01:
        return 0
    else:
        return float_val
    
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
    with open('lanes.json', 'w') as f:
        print >>f, json.dumps(output)


    card_time_data = []
    for card in cards:
        if is_complete(card):
            data = [card['name'].replace(',', ' ').replace('\n', '')]
            times = summarize_card_times(card)
            data.extend(times)
            
            card_time_data.append(data)
            
    with open('card_times.csv', 'w') as f:
        print >>f, ','.join(['name','queued','dev','review','ready'])
        for data in card_time_data:
            output_arr = [data[0]]
            output_arr.extend(str(sanitize_float(i)) for i in data[1:])
            print >>f, ','.join(output_arr)


    stats = process_times(card_time_data)

    column_order = ['avg', 'std', 'median', 'min', 'max', 'count']
    print "name\t%s" % '\t'.join(column_order)
    for row in ['active', 'queue', 'dev', 'review', 'ready', 'total', 'dev_to_review_ratio']:
        output_row = [row]
        for col in column_order:
            output_row.append("%.2f" % stats[row][col])
        
        print "\t".join(output_row)
        



        #'count': len(arr),
        #'avg': numpy.average(arr),
        #'median': numpy.median(arr),
        #'std': numpy.std(arr),
        #'min': min(arr),
        #'max': max(arr),

    
