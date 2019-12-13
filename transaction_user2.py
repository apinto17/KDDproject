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
    profession = ['EE', 'ME', 'CPE']
    

    for i in range(len(dataset)):
        if random.random() > 0.4:
            if dataset['site_name'][i] == 'Tanner Bolt':
                dataset.at[i, 'profession'] = 'ME'
            elif dataset['site_name'][i] == 'dillonsupply.com':
                dataset.at[i, 'profession'] = 'ME'
            elif dataset['site_name'][i] == 'Automation Direct':
                dataset.at[i, 'profession'] = 'CPE'
            elif dataset['site_name'][i] == 'Bailiegh Industrial':
                dataset.at[i, 'profession'] = 'EE'
            elif dataset['site_name'][i] == 'Speedy Metals':
                dataset.at[i, 'profession'] = 'ME'
            elif dataset['site_name'][i] == 'QC Supply':
                dataset.at[i, 'profession'] = 'CPE'
            elif dataset['site_name'][i] == 'Blackhawk Industrial':
                dataset.at[i, 'profession'] = 'EE'
            else:
                dataset.at[i, 'profession'] = 'other'
                print("okaY")
        else:
            dataset.at[i, 'profession'] = profession[random.randint(0,2)]

    dataset.to_csv('user_transaction2.csv', index=False)

if __name__ == "__main__":
    main()
