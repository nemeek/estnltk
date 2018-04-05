# -*- coding: utf-8 -*-
"""Eurown synset

Example
-------
>>> import eurown
>>> a = eurown.Synset(43,'n')
>>> b = eurown.Variant('loom',1)
>>> c = eurown.Variant('elajas',2)
>>> a.add_variant(b)
>>> print(a)
"""

from eurown.backends import format_polaris

class Definition(object):
    def __init__(self, lang='', text='', sourceSense=''):
        self.lang = lang or 'et'
        self.text = text or ''
        self.sourceSense = sourceSense or ''

    def __str__(self):
        out = format_polaris(2, 'TEXT', self.text)
        out = '{}\n{}'.format(out,
                              format_polaris(2, 'LANGUAGE', self.lang,
                                             None)
                              )
        if self.sourceSense:
            out = '{}\n{}'.format(out,
                                format_polaris(2, 'SOURCE_SENSE', self.sourceSense,
                                                None)
                                )
        return out


class Synset(object):
    def __init__(self, number='', pos='', variants=None,
        definition = None,
        internal_links=None, eq_links=None,
        properties=None, 
        wordnet_offset=None,
        add_on_id=None):
        
        self.definition = definition or Definition()
        self.pos = pos
        self.variants = variants or []
        self.internal_links = internal_links or []
        self.eq_links = eq_links or []
        self.properties = properties or []
        self.number = number
        self.fieldname = 'WORD_MEANING'
        self.wordnet_offset = wordnet_offset
        self.add_on_id = add_on_id

        self.lexicon = None
        self.comment = None

    def read(self, data):
        """Reads data depending of back system

        """
        pass

    def wnwb(self, data: dict):
        """Parses data from wnwb rest service

        Parametres
        ----------
        data
            Result from wnwb rest service that carries info
            about synset

        """
        self.lexicon = data['lexicon']
        self.number, self.pos = data['label'].split('-')
        self.domain = data['domain']
        self.comment = data['comment']
        self.definition = Definition(text = data['primary_definition'])

        self.variants = [Variant(wb = i) for i in data['senses']]
        self.internal_links = [Variant(wb = i) for i in data['senses']]        
        

    def add_variant(self, variant):
        self.variants.append(variant)
        return self

    def add_variants(self, variants):
        self.variants = variants
        
    def add_internal_link(self, internal_link):
        self.internal_links.append(internal_link)
        
    def add_eq_link(self, eq_link):
        self.eq_links.append(eq_link)

    def __str__(self):
        if self.number:
            out = format_polaris(0, self.fieldname, None, self.number)
        else:
            out = format_polaris(0, self.fieldname)
        if self.pos: # should always be true
            out = '{}\n{}'.format(out,
                                  format_polaris(1,
                                                 'PART_OF_SPEECH',
                                                 self.pos)
                                    )
            
        if self.definition:
            out = '{}\n{}'.format(out,
                                  format_polaris(1,
                                                 'DEFINITION')
                                  )
            out = '{}\n{}'.format(out,
                                  self.definition
                                  )
        if self.variants:
            out = '{}\n{}'.format(out,
                                  format_polaris(1,
                                                 'VARIANTS')
                                  )
            out = '{}\n{}'.format(out,
                                  '\n'.join([str(i) for i in self.variants])
                                  )
        if self.internal_links:
            out = '{}\n{}'.format(out,
                                  format_polaris(1,
                                                 'INTERNAL_LINKS')
                                  )
            out = '{}\n{}'.format(out,
                                  '\n'.join(
                                      [str(i) for i in self.internal_links])
                                  )
        if self.eq_links:
            out = '{}\n{}'.format(out,
                                  format_polaris(1,
                                                 'EQ_LINKS')
                                  )
            out = '{}\n{}'.format(out,
                                  '\n'.join([str(i) for i in self.eq_links])
                                  )
        return out

    
class Instance(Synset):
    def __init__(self, number='', variants=None,
                     internal_links=None, eq_links=None,
                     property_values=None,
                     wordnet_offset=None,
                     add_on_id=None):
        Synset.__init__(self,number,variants,internal_links,
                        eq_links,wordnet_offset,add_on_id)
        self.pos = 'pn'
        self.property_values = property_values or []
        self.fieldname = 'WORD_INSTANCE'
