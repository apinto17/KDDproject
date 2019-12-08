import json
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import re


NUM_PER_OUTPUT = 10


def main():
    pass



def input_per_output():
    data_file = open("categories.json", "r+")
    data = json.load(data_file)

    data = pd.DataFrame({'input_category' : data["input_categories"],
                        'output_category' : data["output_categories"]})

    data = clean(data)

    cats_so_far = {}
    for i in range(len(data)):
        if(data['output_category'].iloc[i] in cats_so_far.keys()):
            cats_so_far[data['output_category'].iloc[i]].append(data['cleaned'].iloc[i])
        else:
            cats_so_far[data['output_category'].iloc[i]] = []

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

    data["cleaned"] = data["input_category"].apply(lambda x: " ".join([stemmer.stem(i) for i in re.sub("[^a-zA-Z]", " ", x).split() if i not in words]).lower())


    return data


def get_occurences(data, item, indexes_so_far):
    indexes = []
    for i in range(len(data)):
        if(data['output_category'].iloc[i] == item and i not in indexes_so_far):
            indexes.append(i)

    return indexes



if(__name__ == "__main__"):
    main()
