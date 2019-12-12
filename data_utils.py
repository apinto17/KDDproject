import re
import sys
import random
import numpy as np
import pandas as pd
import collections
import math

DATA_PATTERN = re.compile('''((?:[^,\"']|\"[^\"']*\"|['\"]*')+)''')

# Per user ranges when generating transactions
MIN_TRX = 1
MAX_TRX = 25
MIN_SITES = 2
MAX_SITES = 4

TRX_COLUMN_NAMES = 'uid,pid,item_description,price,category,site_name'

class Item:
    def __init__(self,
                 id : int,
                 description : str,
                 price : float,
                 category : str,
                 site : str):
        self.id = id
        self.description = description
        self.price = price
        self.category = category
        self.site = site

    def __repr__(self):
        return ','.join([str(self.id), self.description, str(self.price), self.category, self.site])

def read_item_data(path : str):
    ''' Data format - csv with colummns:
        - Item ID
        - Description
        - Price
        - Category
        - Site (Vendor) '''
    with open(path) as f:
        lines = f.readlines()

    items = []
    sites = []
    for l in lines[1:]:
        data = DATA_PATTERN.split(l.strip())[1::2]
        try:
            id = int(data[0])
            description = data[1]
            try:
                price = float(re.sub('[^.0-9]', '', data[2]))
            except ValueError as e:
                price = np.NaN
            category = data[3]
            site = data[4]
        except ValueError as e:
            print(data)
            print(e)
            exit(0)

        item = Item(id, description, price, category, site)
        items.append(item)
        sites.append(site)

    with open('sites.csv', 'w') as output:
        output.write(','.join(frozenset(sites)))

    return items, sites

# Create k random transactions 
def create_transactions(k : int, items_by_site : dict, uid_start=0):
    trxs = []

    tot = 0
    u_counter = uid_start # In case you want to create a new set of users w/ transactions
    while tot < k:
        user =  u_counter
        print('----- User {} -----'.format(user))
        num_trans = random.randint(MIN_TRX, MAX_TRX)
        num_sites = random.randint(MIN_SITES,MAX_SITES)

        user_sites = random.sample(items_by_site.keys(), num_sites)
        for _ in range(num_trans):
            site = user_sites[random.randint(0, num_sites-1)]
            site_items = items_by_site[site]
            item = site_items[random.randint(0, len(site_items)-1)]
            trxs.append((user,item))


        u_counter += 1
        tot += num_trans
    return trxs

def get_items_by_sites(items : list, sites : list):
    items_by_site = {}
    for s in sites:
        if s not in items_by_site.keys():
            items_by_site[s] = []

    for i in items:
        items_by_site[i.site].append(i)

    return items_by_site

def get_trx_count_per_sites(trxs : list):
    sites_by_user = {}
    for t in trxs:
        u_idx = t[0]
        if u_idx not in sites_by_user.keys():
            sites_by_user[u_idx] = []
        sites_by_user[u_idx].append(t[1].site)

    return {k : collections.Counter(v) for k,v in sites_by_user.items()}

def write_trxs(trxs : list, id_only=False):
    if not id_only:
        trx_strs = ['{},{}'.format(t[0], t[1]) for t in trxs]
        filename = 'transactions.csv'
    else:
        trx_strs = ['{},{}'.format(t[0], t[1].id) for t in trxs]
        filename = 'trx_idx.csv'

    trx_strs[::]= TRX_COLUMN_NAMES

    with open(filename, 'w') as output:
        output.write('\n'.join(trx_strs))

def read_sites_file(path='sites.csv'):
    with open(path, 'r') as file:
        sites = file.readline().strip().split(',')
    return sites

def read_trx_file(path='transactions.csv'):
    with open(path, 'r') as file:
        lines = file.readlines()

    trxs = []
    for l in lines[1:]:
        data = DATA_PATTERN.split(l.strip())[1::2]
        try:
            user_id = int(data[0])
            id = int(data[1])
            description = data[2]
            try:
                price = float(re.sub('[^.0-9]', '', data[3]))
            except ValueError as e:
                price = np.NaN
            category = data[4]
            site = data[5]
        except ValueError as e:
            print(data)
            print(e)
            exit(0)

        item = Item(id, description, price, category, site)
        trxs.append((user_id, item))

    return trxs

def build_utiliy_matrix(sites : list, sites_by_user : dict):
    users = sites_by_user.keys()

    u_matrix = pd.DataFrame(index=users, columns=sites)
    for user in users:
        u_sites = sites_by_user[user]
        for site,count in u_sites.items():
            # Using log-scale for user interaction to indicate positve, but less than linear
            # correlation with user interaction.  Shifted +1 to remove negative values
            u_matrix.at[user,site] = math.log2(1 + count)

    print(u_matrix)
    return u_matrix



def main():
    trxs = read_trx_file()
    sites = read_sites_file()
    sites_by_user = get_trx_count_per_sites(trxs)
    build_utiliy_matrix(sites, sites_by_user)


if __name__ == "__main__":
    main()