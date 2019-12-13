import sys
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing




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

def main():
    usage()
    filename = sys.argv[1]

    dataset = pd.read_csv(filename)
    labels = dataset['user_type']
    data = dataset.drop(['uid'], axis='columns')
    data = data.drop(['user_type'], axis='columns')
    to_num(data, 'category')
    to_num(data, 'site_name')
    data = data.fillna(-1)
    X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2)

    print(len(X_train))
    print(len(X_test))
    model = RandomForestClassifier(n_estimators=10)
    model.fit(X_train, y_train)
    print(model.score(X_test, y_test))

    

if __name__ == "__main__":
    main()
