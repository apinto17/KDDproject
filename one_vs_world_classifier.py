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
from data_explore import clean


# TODO try a random forrest or decision tree classifier
# TODO get more data for a more clean train-test split

def main():
    svm = LinearSVC(random_state=0, max_iter=10000, C=.4)
    clf = CalibratedClassifierCV(svm)
    vect = CountVectorizer(ngram_range=(1,2))
    pipeline = Pipeline([
            ("vect", vect),
            ("clf", clf)
    ])
    data_file = open("categories.json", "r+")
    data = json.load(data_file)

    data = pd.DataFrame({'input_category' : data["input_categories"],
                        'output_category' : data["output_categories"]})

    data = clean(data)

    train_indx = int((.7 * len(data)))

    train = data[:train_indx]
    test = data[train_indx:]
    print(OneVsRestClassifier(pipeline).fit(train["cleaned"], train["output_category"]).predict(test['cleaned']))


    # x_train, x_test, y_train, y_test = train_test_split(data["input_category"], data["cleaned"], test_size=.3)

    # print(OneVsRestClassifier(pipeline).fit(x_train, y_train).predict(x_test))



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
        self.server.stop()


    def Select_Training_Data_From_DB(self):
         #new session input & output_category data that only has the primary category the user selected
        self.connect()

        sql = "Select input_category, output_category From ft_ml_categories Where output_category is not null"

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
