# -*- coding: utf-8 -*-

from eurown.lexicon import Lexicon, make_sense, make_synset, make_variant

LEX = Lexicon(filename='data/estwn-et-2.1.0.wip.xml')
LEX.read_xml()

def synsets(lemma: str, pos: str = None) -> list:
    """Returns all synset objects which have lemma as one of the 
    variant literals and fixed pos, if provided.

    Parameters
    ----------
    lemma : str
      Lemma of the synset.
    pos : str, optional
      Part-of-speech specification of the searched synsets, defaults to None.

    Returns
    -------
    list of Synsets
      Synsets which contain `lemma` and of which part-of-speech is `pos`, 
    if specified.
      Empty list, if no match was found.

    """
    lemma_synsets = [make_sense(x) for x in LEX.xml.xpath(
        "/LexicalResource/Lexicon/LexicalEntry/Sense") if x.getparent().find(
            'Lemma').get('writtenForm') == lemma]
    print (lemma_synsets)
    synset_ids = [i.synset for i in lemma_synsets]
    print (synset_ids)

    _synsets = [make_synset(x) for x in LEX.xml.xpath("/LexicalResource/Lexicon/Synset") if x.get('id') in synset_ids ]
    print (_synsets)
    for i in _synsets:
        print(i)

    _ssynsets = [x.add_variant(make_variant(v,x.number)) for x in _synsets for v in LEX.xml.xpath("/LexicalResource/Lexicon/LexicalEntry") if x.number in [i.attrib['synset'] for i in v.findall('Sense')]]

    print (_ssynsets)
    for i in _ssynsets:
        print(i)
    

def test(lemma: str) -> None:
    synsets(lemma)

if __name__ == "__main__":
    test('jama')

