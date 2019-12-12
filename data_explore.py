import json
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import re
import random
from sklearn.datasets import make_classification

NUM_PER_OUTPUT = 10
NUM_OF_FEATURES = 10

def main():
    train, test = train_test_split()
    print(train)


def get_data():
    data_file = open("categories.json", "r+")
    data = json.load(data_file)

    input_categories = []
    for i in range(len(data['input_categories'])):
        input_data_point = data["input_categories"][i].split("|")
        if(len(input_data_point) < NUM_OF_FEATURES):
            for j in range(NUM_OF_FEATURES - len(input_data_point)):
                input_data_point.append("")
        elif(len(input_data_point) > NUM_OF_FEATURES):
            raise ValueError("Increase NUM_OF_FEATURES")
        input_categories.append(input_data_point)

    data = pd.DataFrame({'input_category' : input_categories,
                        'output_category' : data["output_categories"]})

    data = clean(data)

    return data


def train_test_split():
    data = get_data()
    num_of_test_data = int(.3 * len(data))
    test = {}
    test['input_category'] = []
    test['cleaned'] = []
    test['output_category'] = []
    train = {}
    train['input_category'] = []
    train['cleaned'] = []
    train['output_category'] = []
    cats_so_far = {}
    i = 0
    test_indexes = []


    while(i < num_of_test_data):
        indx = random.randint(0, len(data) - 1)
        if(data['output_category'].iloc[indx] in cats_so_far.keys() and len(cats_so_far[data['output_category'].iloc[indx]]) <= 3):
            cats_so_far[data['output_category'].iloc[indx]].append(data['input_category'].iloc[indx])
            i += 1
            test_indexes.append(indx)
            test['input_category'].append(data['input_category'].iloc[indx])
            test['cleaned'].append(data['cleaned'].iloc[indx])
            test['output_category'].append(data['output_category'].iloc[indx])
        elif(data['output_category'].iloc[indx] not in cats_so_far.keys()):
            cats_so_far[data['output_category'].iloc[indx]] = [data['input_category'].iloc[indx]]
            i += 1
            test_indexes.append(indx)
            test['input_category'].append(data['input_category'].iloc[indx])
            test['cleaned'].append(data['cleaned'].iloc[indx])
            test['output_category'].append(data['output_category'].iloc[indx])


    for i in range(len(data)):
        if(i not in test_indexes):
            train['input_category'].append(data['input_category'].iloc[i])
            train['cleaned'].append(data['cleaned'].iloc[i])
            train['output_category'].append(data['output_category'].iloc[i])

    return (pd.DataFrame(train), pd.DataFrame(test))






def input_per_output():
    data = get_data()

    cats_so_far = {}
    for i in range(len(data)):
        if(data['output_category'].iloc[i] in cats_so_far.keys()):
            cats_so_far[data['output_category'].iloc[i]].append(data['cleaned'].iloc[i])
        else:
            cats_so_far[data['output_category'].iloc[i]] = [data['cleaned'].iloc[i]]

    print("------------after---------------")
    for k, v in cats_so_far.items():
        print("")
        print(k + ": " + str(v) + "\n\n\n")






def clean(data):
    stemmer = SnowballStemmer("english")
    words = stopwords.words("english")
    indexes = []

    for i in range(len(data)):
        if(len(data[data['output_category'] == data['output_category'].iloc[i]]) < NUM_PER_OUTPUT):
            new_indexes = get_occurences(data, data['output_category'].iloc[i], indexes)
            indexes.extend(new_indexes)

    for i in indexes:
        data = data.drop(i)

    cleaned = []
    for i in range(len(data["input_category"])):
        cleaned.append([stemmer.stem(re.sub("[^a-zA-Z]", "", w)) for w in data["input_category"].iloc[i] if w not in words])
    data["cleaned"] = cleaned


    return data


def get_occurences(data, item, indexes_so_far):
    indexes = []
    for i in range(len(data)):
        if(data['output_category'].iloc[i] == item and i not in indexes_so_far):
            indexes.append(i)

    return indexes



if(__name__ == "__main__"):
    main()
