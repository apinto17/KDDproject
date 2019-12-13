import collections
import math
import sys

import numpy as np
import pandas as pd
from surprise import (SVD, BaselineOnly, Dataset, KNNBaseline, KNNBasic,
                      KNNWithMeans, KNNWithZScore, NormalPredictor, Reader, AlgoBase)
from surprise.model_selection import cross_validate

from data_utils import read_sites_file, read_trx_file

ALGORITHM_MAP = {
    0 : 'SVD',
    1 : 'KNNBasic',
    2 : 'KNNBaseline',
    3 : 'KNNWithZScore',
    4 : 'KNNWithMeans',
    5 : 'BaselineOnly',
    6 : 'NormalPredictor',
}

THRESHOLD = 2.322223953887303 # Average Rating (discovered empirically from dataset)

def print_algorithms():
    print('--- Algorithms ---')
    for i in ALGORITHM_MAP.items():
        print('{}: {}'.format(i[0], i[1]))

def get_algorithm(index : int):
    algorithm_name = ALGORITHM_MAP[index]
    if algorithm_name == 'KNNBasic':
        return KNNBasic()
    elif algorithm_name == 'KNNBaseline': 
        return KNNBaseline()
    elif algorithm_name == 'KNNWithZScore': 
        return KNNWithZScore()
    elif algorithm_name == 'KNNWithMeans': 
        return KNNWithMeans()
    elif algorithm_name == 'SVD': 
        return SVD()
    elif algorithm_name == 'NormalPredictor':
        return NormalPredictor()
    elif algorithm_name == 'BaselineOnly':
        return BaselineOnly()
    
    raise ValueError

def evaluate_recommender(algorithm : AlgoBase, path='ratings.csv'):

    reader = Reader(line_format='user item rating', sep=',')
    data = Dataset.load_from_file(path, reader=reader)

    # cross_validate(svd_algorithm, data, cv=10, verbose=True)
    cross_validate(algorithm, data, cv=10, verbose=True)

    return algorithm

def get_conf_matrix(algorithm : AlgoBase, path='ratings.csv'):
    reader = Reader(line_format='user item rating', sep=',')
    data = Dataset.load_from_file(path, reader=reader)

    trainset = data.build_full_trainset()
    algorithm.fit(trainset)

    conf_matrix = np.zeros(shape=(2,2))

    with open(path, 'r') as f:
        lines = f.readlines()
    data = [l.strip().split(',') for l in lines]

    for d in data:
        uid = d[0] # uid should be a string for predict()
        iid = d[1]  # iid should be a string for predict()
        actual = float(d[2])

        pred = algorithm.predict(uid, iid, r_ui=actual, verbose=True)
        estimate = pred.est

        # True positive
        if estimate > THRESHOLD and actual > THRESHOLD:
            conf_matrix[0][0] += 1
        # False negative
        if estimate <= THRESHOLD and actual > THRESHOLD:
            conf_matrix[0][1] += 1
        # False positive
        if estimate > THRESHOLD and actual <= THRESHOLD:
            conf_matrix[1][0] += 1
        # True negative
        if estimate <= THRESHOLD and actual <= THRESHOLD:
            conf_matrix[1][1] += 1

    print(conf_matrix)
    return conf_matrix







def get_trx_count_per_sites(trxs : list):
    sites_by_user = {}

    for t in trxs:
        u_idx = t[0].id
        if u_idx not in sites_by_user.keys():
            sites_by_user[u_idx] = []
        sites_by_user[u_idx].append(t[1].site)

    return {k : collections.Counter(v) for k,v in sites_by_user.items()}

def build_utiliy_matrix(sites : list, sites_by_user : dict):
    users = sites_by_user.keys()

    u_matrix = pd.DataFrame(index=users, columns=sites)
    for user in users:
        u_sites = sites_by_user[user]
        for site,count in u_sites.items():
            # Using log-scale for user interaction to indicate positve, but less than linear
            # correlation with user interaction.  Shifted +1 to remove negative values
            u_matrix.at[user,site] = math.log2(1 + count)

    # print(u_matrix)
    return u_matrix

def write_utility_matrix(u_matrix : pd.DataFrame, path='ratings.csv'):
    users = u_matrix.index
    sites = u_matrix.columns
    ratings = []
    for u in range(len(users)):
        for i in range(len(sites)):
            r = u_matrix.iat[u,i]
            if not np.isnan(r):
                ratings.append('{},{},{}'.format(u, i,r))

    print(ratings)
    with open(path, 'w') as output:
        output.write('\n'.join(ratings))


def process_transactions(write=False, trx_path='transactions1.csv', site_path='sites.csv'):
    ## Used to create a utility matrix and write out a ratings list
    trxs = read_trx_file(trx_path)
    sites = read_sites_file()
    sites_by_user = get_trx_count_per_sites(trxs)
    u_matrix = build_utiliy_matrix(sites, sites_by_user)
    print(u_matrix)
    if write:
        write_utility_matrix(u_matrix)

    return u_matrix

if __name__ == "__main__":
    if sys.argv[1] == 'process':
        process_transactions(True)
        exit(0)

    try:
        if sys.argv[1] == '-a':
            for key in ALGORITHM_MAP.keys():
                algorithm = get_algorithm(key)
                evaluate_recommender(algorithm)
        else:
            algorithm = get_algorithm(int(sys.argv[1]))
            evaluate_recommender(algorithm)
    except (IndexError, KeyError) as _:
        print('Usage: python3 site_recommender.py <algorithm>')
        print_algorithms()
