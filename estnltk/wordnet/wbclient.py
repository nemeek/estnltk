#!/usr/bin/env python3

"""Wordnet workbench client

"""

import requests

from wnconfig import WNWB_PREFIX, WNWB_LEXID, HYPERNYM_IDS, HYPONYM_IDS, APP_CONFIG_SECRET_KEY, SYNSET_RELATIONS

WNWB_SNSET = WNWB_PREFIX + 'synset/'
OMW_NAMES = set([x[1] for x in SYNSET_RELATIONS])
SNSET_OMW_REL = [{'omw_name':x,
    'ids':[y[0] for y in SYNSET_RELATIONS if y[1] == x]} for x in OMW_NAMES if x]


def make_query(lexid, search, root):
    """
    Make query in function
    """
    tulem = []
    r = requests.get(root, params={
        'lexid':lexid, 'word':search}
                         )
    if r.status_code != 200:
        return flash('Ei saa serveriga ühendust!')
    else:
        vastus = r.json()
        tulem = vastus['results']
        if vastus['count'] > len(vastus['results']):
            r = requests.get(vastus['next'])
            if r.status_code == 200:
                tulem.extend(r.json()['results'])
        return tulem

    
def main(otsi):
    print(make_query(WNWB_LEXID, otsi, WNWB_SNSET))


if __name__ == "__main__":
    main('jama')
