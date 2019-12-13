import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import re
from sklearn import datasets
from sklearn.multiclass import OneVsRestClassifier
from sklearn.calibration import CalibratedClassifierCV
import json
from data_explore import *
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_recall_fscore_support
# import sshtunnel
# import mysql.connector


# TODO find a way to use categorical data instead of treating it like text data

def main():
    svm = LinearSVC(random_state=0, max_iter=10000, C=.4)
    clf = CalibratedClassifierCV(svm)
    vect = CountVectorizer(ngram_range=(1,2))
    pipeline = Pipeline([
            ("vect", vect),
            ("clf", clf)
    ])
    train, test = train_test_split()

    y_pred = OneVsRestClassifier(pipeline).fit(train["cleaned"], train["output_category"]).predict(test['cleaned'])

    accur = accuracy_score(test['output_category'], y_pred)
    prec, recall, f1, support = precision_recall_fscore_support(test['output_category'], y_pred, average='micro')

    print("Accuracy: " + str(accur))
    print("Precision: " + str(prec))
    print("Recall: " + str(recall))
    print("F1: " + str(f1))




def select_training_data():
    server = Server()
    cats = {}
    input_categories, output_categories = server.Select_Training_Data_From_DB()
    cats["input_categories"] = input_categories
    cats["output_categories"] = output_categories
    cat_file = open("categories.json", "w+")
    json.dump(cats, cat_file)
    del server



def train():
    svm = LinearSVC(random_state=0, max_iter=10000, C=.4)
    clf = CalibratedClassifierCV(svm)
    vect = CountVectorizer(ngram_range=(1,2))
    pipeline = Pipeline([
            ("vect", vect),
            ("clf", clf)
    ])
    data = get_data()

    return OneVsRestClassifier(pipeline).fit(data["cleaned"], data["output_category"])


def classify(model, category):

    return model.predict(category)



# sql queries only work on windows for some reason
class Server:
    server = None
    connection = None
    mycursor = None

    def __init__(self):
        sshtunnel.SSH_TIMEOUT = 350.0
        sshtunnel.TUNNEL_TIMEOUT = 350.0
        self.server = sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='iclam19', ssh_password='@astest@1234',
            remote_bind_address=('iclam19.mysql.pythonanywhere-services.com', 3306)
        )
        self.server.start()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                user='iclam19', password='astest1234',
                host='127.0.0.1', port=self.server.local_bind_port,
                database='iclam19$AssembledSupply',
            )
            if(self.connection.is_connected()):
                self.mycursor = self.connection.cursor()
            else:
                print("Did not connect")
                return None

        except Error as e:
            print(e)


    def __del__(self):
        if(self.server is not None):
            self.server.stop()


    def Select_Training_Data_From_DB(self):
         #new session input & output_category data that only has the primary category the user selected
        self.connect()

        sql = "Select input_category, output_category From ft_ml_categories Where output_category is not null limit 10000"

        self.mycursor.execute(sql,)
        returned_items = list(self.mycursor.fetchall())
        self.connection.close()

        input_categories = []
        output_categories = []
        for cat in returned_items:
            input_categories.append(cat[0])
            output_categories.append(cat[1])

        return (input_categories, output_categories)








if (__name__ == "__main__"):
    main()
