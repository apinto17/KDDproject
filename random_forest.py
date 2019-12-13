import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing

from sklearn.model_selection import GridSearchCV




digits = load_digits()
for i in range(4):
    plt.matshow(digits.images[i])



def usage():
    if len(sys.argv) < 2:
        print("Usage: python <filename>")
        exit()

def to_num(df, column_name):
    le = preprocessing.LabelEncoder()
    df[column_name] = le.fit_transform(df.site_name.values)
    print(len(np.unique(df[column_name])))

def train(filename):
    dataset = pd.read_csv(filename)
    labels = dataset['user_type']
    data = dataset.drop(['uid'], axis='columns')
    data = data.drop(['user_type'], axis='columns')
    to_num(data, 'category')
    to_num(data, 'site_name')
    data = data.fillna(-1)
    X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2)
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    return model

def display(results):
    print(f'Best parameters are: {results.best_params_}')
    print("\n")
    mean_score = results.cv_results_['mean_test_score']
    std_score = results.cv_results_['std_test_score']
    params = results.cv_results_['params']
    for mean,std,params in zip(mean_score,std_score,params):
        print(f'{round(mean,3)} + or -{round(std,3)} for the {params}')

def main():
    usage()
    filename = sys.argv[1]

    dataset = pd.read_csv(filename)
    labels = dataset['profession']
    data = dataset.drop(['uid'], axis='columns')
    data = data.drop(['profession'], axis='columns')
#    data = data.drop(['category'], axis='columns')
#    data = data.drop(['pid'], axis='columns')
#    data = data.drop(['price'], axis='columns')
    to_num(data, 'category')
    to_num(data, 'site_name')
    data = data.fillna(-1)
    X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2)

    print(len(X_train))
    print(len(X_test))
#    for i in range(10, 1000):
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    print(model.score(X_test, y_test))
#    parameters = {
#    "n_estimators":[5,10,50,100,250],
#    "max_depth":[2,4,8,16,32,None]
#    
#    }
#    cv = GridSearchCV(model,parameters,cv=5)
#    cv.fit(X_train, y_train)
#    display(cv)


    

if __name__ == "__main__":
    main()
