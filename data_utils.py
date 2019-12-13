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

TRX_COLUMN_NAMES = 'uid,profession,pid,item_description,price,category,site_name'
PROFESSIONS = ['EE', 'ME', 'CSC', 'CE', 'IE', 'CPE']

SITE_SEEDING = {
    'Speedy Metals' : { 'ME' : 0.4, 'CE' : 0.4 },
    'QC Supply' : { 'CPE' : 0.4, 'EE' : 0.4 },
    'Tanner Bolt' : { 'ME' : 0.25, 'CE' : 0.25, 'IE' : 0.25 },
    'Bailiegh Industrial' : {},
    'dillonsupply.com' : {},
    'Automation Direct' : { 'EE' : 0.25, 'CPE' : 0.25, 'ME' : 0.25 },
    'Blackhawk Industrial' : {}
}


class User:
    def __init__(self, id : int, profession : str):
        self.id = id
        self.profession = profession

    def __repr__(self):
        return ','.join([str(self.id), self.profession])

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

def read_item_data(path='item_data.csv'):
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

    sites_set = frozenset(sites)
    with open('sites.csv', 'w') as output:
        output.write(','.join(sites_set))

    return items, sites_set

# Create k random transactions 
def create_transactions(k : int, items_by_site : dict, uid_start=0):
    trxs = []
    trx_counter = build_trx_counter()

    tot = 0
    u_counter = uid_start # In case you want to create a new set of users w/ transactions
    while tot < k:

        num_trans = random.randint(MIN_TRX, MAX_TRX)
        num_sites = random.randint(MIN_SITES,MAX_SITES)

        user_sites = random.sample(items_by_site.keys(), num_sites)
        u_id =  u_counter
        profession = select_profession(trx_counter, user_sites)
        user = User(u_id, profession)

        for _ in range(num_trans):
            item = select_item(profession, user_sites, items_by_site, trx_counter)
            trxs.append((user,item))

        u_counter += 1
        tot += num_trans
    return trxs, trx_counter

def calc_ratios(trx_counter: dict):
    for s in trx_counter.keys():
        site_total = sum(trx_counter[s].values())
        for p in trx_counter[s].keys():
            trx_counter[s][p] /= site_total

    print(trx_counter)

def update_ratios(site, profession, site_ratios):
    pass

def build_trx_counter():
    trx_counter = {}
    for s in SITE_SEEDING.keys():
        trx_counter[s] = {}
        for p in PROFESSIONS:
            trx_counter[s][p] = 0

    return trx_counter

# Selects a site below the given ratios
def select_profession(trx_counter : dict, user_sites=[]):
    profession = PROFESSIONS[random.randint(0, len(PROFESSIONS)-1)] # Random choice, will reassign if necessary
    np.random.shuffle(user_sites)

    for s in user_sites:
        profs = SITE_SEEDING[s].keys()
        site_total = sum(trx_counter[s].values())
        for p in profs:
            goal_ratio = SITE_SEEDING[s][p]

            prof_total = trx_counter[s][p]
            current_ratio =  prof_total / site_total if site_total > 0 else 0

            if current_ratio < goal_ratio:
                profession = p
                break

    return profession


def select_item(profession : str, user_sites : list, items_by_site : dict, trx_counter : dict):
    site = user_sites[random.randint(0, len(user_sites)-1)] # Random choice, will reassign if necessary
    # for s,ratios_by_prof in SITE_SEEDING.items():

    for s in user_sites:
        site_total = sum(trx_counter[s].values())
        prof_total = trx_counter[s][profession]

        current_ratio =  prof_total / site_total if site_total > 0 else 0
        
        if profession in SITE_SEEDING[s].keys():
            goal_ratio = SITE_SEEDING[s][profession]
        else:
            continue

        if current_ratio < goal_ratio:
            site = s
            break

    trx_counter[site][profession] += 1
    site_items = items_by_site[site]
    return site_items[random.randint(0, len(site_items)-1)]


def get_items_by_sites(items : list, sites : frozenset):
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
        filename = 'transactions1.csv'
    else:
        trx_strs = ['{},{}'.format(t[0], t[1].id) for t in trxs]
        filename = 'trx_idx.csv'

    trx_strs.insert(0,TRX_COLUMN_NAMES)

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

    # print(u_matrix)
    return u_matrix

# def read_utiliy_matrix(path='ratings.csv'):
#     sites = read_sites_file()

#     with open(path, 'r') as file:
#         lines = file.readlines()

#     u_matrix = pd.DataFrame(columns=sites)
#     for l in lines():


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

def main():
    ## Used to create a utility matrix and write out a ratings list
    # trxs = read_trx_file()
    # sites = read_sites_file()
    # sites_by_user = get_trx_count_per_sites(trxs)
    # u_matrix = build_utiliy_matrix(sites, sites_by_user)
    # write_utility_matrix(u_matrix)

    # create transactions
    items, sites = read_item_data()
    items_by_site = get_items_by_sites(items, sites)
    trxs, site_ratios = create_transactions(10000, items_by_site)
    breakpoint()
    write_trxs(trxs)





if __name__ == "__main__":
    main()