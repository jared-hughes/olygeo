import json
import random

with open('raw_data/isl.json') as raw_data_file:
    data = json.load(raw_data_file)

random.shuffle(data)
cutoff = int(0.8 * len(data))

with open('training_data/isl.json', 'w') as training_data_file:
    json.dump(data[:cutoff], training_data_file)

with open('test_data/isl.json', 'w') as test_data_file:
    json.dump(data[cutoff:], test_data_file)
