import sys
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
import random
import one_vs_world_classifier



def main():
    filename = sys.argv[1]
    dataset = pd.read_csv(filename)
    dataset = dataset.drop(['item_description'], axis = 'columns')
#    profession = ['EE', 'ME', 'CSC', 'CE', 'IE', 'CPE']
    

    model = one_vs_world_classifier.train()
    new_values = []
#    for i in range(len(dataset)):
#        new_values.append(profession[random.randint(0,len(profession)-1)])
#        print(dataset['category'][i])

    print(dataset['category'].values)
    dataset['category'] = one_vs_world_classifier.classify(model, dataset['category'].values)


    
#    dataset['user_type'] = new_values
    dataset.to_csv('user_transaction.csv', index=False)




if __name__ == "__main__":
    main()
