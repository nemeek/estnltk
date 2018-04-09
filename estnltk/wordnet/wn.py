# -*- coding: utf-8 -*-

from eurown.lexicon import Lexicon, make_sense

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
    senses = [make_sense(x) for x in LEX.xml.xpath("/LexicalResource/Lexicon/LexicalEntry/Sense")]
    print (senses)

def test(lemma: str) -> None:
    synsets(lemma)

if __name__ == "__main__":
    test('jama')

