#!/usr/bin/env python3

"""Wordnet workbench client

"""
import sys
import requests

from wnconfig import WNWB_PREFIX, WNWB_LEXID, HYPERNYM_IDS, HYPONYM_IDS, APP_CONFIG_SECRET_KEY, SYNSET_RELATIONS

from eurown import Synset

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
    print(r.url)
    if r.status_code != 200:
        print ('Ei saa serveriga ühendust!', sys.stderr)
        return None
    else:
        vastus = r.json()
        tulem = vastus['results']
        if vastus['count'] > len(vastus['results']):
            r = requests.get(vastus['next'])
            if r.status_code == 200:
                tulem.extend(r.json()['results'])
        return tulem

    
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description = 'connect to wnwb server')
    parser.add_argument("word")

    args = parser.parse_args()
    
    tulem = make_query(WNWB_LEXID, args.word, WNWB_SNSET)

    uus = tulem[0]
    for i,j in uus.items():
        print(i,type(j))
    show = ['id','label','synset_type','variants_str','sensess']
    for i,j in uus.items():
        if i in show:
            print('{}: {}'.format(i,j))
        elif i == 'senses':
            for k,n in j[0].items():
                print(k, type(n))
                if k in ['lexical_entry','nr']:
                    print(n)

    for w in tulem:
        s = Synset()
        s.wnwb(w)
        print(s)

if __name__ == "__main__":
    main()
