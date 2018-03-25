#!/usr/bin/env python3

"""Test eurown module

"""

import eurown

def main():
    a = eurown.Synset(43, 'n')
    b = eurown.Variant('loom',1)
    a.add_variant(b)
    c = eurown.Variant('elajas',2)
    a.variants[0].gloss = "elusorganism, mida tavaliselt iseloomustab \
vabatahtliku liikumise võime ja närvisüsteemi olemasolu"
    a.add_variant(c)

    d = eurown.Synset(44)        
    print(a)
    d.add_variant(eurown.Variant('elusolend',1))
    d.add_variant(eurown.Variant('organism',2))
    d.variants[0].gloss = 'elusorganism, hrl. inimene v. loom'
    print(d)
    a.add_internal_link(eurown.InternalLink('has_hyponym',d))

    e = eurown.Synset(pos='n', wordnet_offset='88123456')
    a.add_eq_link(eurown.EqLink('eq_synonym',e))
    print(a)

if __name__ == "__main__":
    main()
