#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the new eurown module.

>>> import eurown
>>> a = eurown.Synset(43,'n')
>>> b = eurown.Variant('loom',1)
>>> c = eurown.Variant('elajas',2)
>>> a.add_variant(b)
>>> print(a)
0 @43@ WORD_MEANING
  1 PART_OF_SPEECH "n"
  1 VARIANTS
    2 LITERAL "loom"
      3 SENSE 1
>>> print(b)
    2 LITERAL "loom"
      3 SENSE 1
>>> print(c)
    2 LITERAL "elajas"
      3 SENSE 2
>>> a.add_variant(c)
>>> print(a)
0 @43@ WORD_MEANING
  1 PART_OF_SPEECH "n"
  1 VARIANTS
    2 LITERAL "loom"
      3 SENSE 1
    2 LITERAL "elajas"
      3 SENSE 2
>>> a.variants[0].gloss = "elusorganism, mida tavaliselt iseloomustab \
vabatahtliku liikumise võime ja närvisüsteemi olemasolu"
>>> print(a)
0 @43@ WORD_MEANING
  1 PART_OF_SPEECH "n"
  1 VARIANTS
    2 LITERAL "loom"
      3 SENSE 1
      3 DEFINITION "elusorganism, mida tavaliselt iseloomustab vabatahtliku liikumise võime ja närvisüsteemi olemasolu"
    2 LITERAL "elajas"
      3 SENSE 2
>>>

"""

import time
start_time = time.time()

from lxml import etree
from lxml.etree import fromstring, tostring


def _pos_from_number(iStr):
    return iStr.split('-')[-1]

def _no_from_id(iStr):
    return '-'.join(iStr.split('-')[-2:])


def _msn(element):
    try:
        defin = Definition(element.find('Definition').get('language'),
                           element.find('Definition').text,
                           element.find('Definition').get('sourceSense')
        )
    except AttributeError:
        defin = None

    ili = element.attrib['ili']
    # print(element)
    # print(element.attrib)
    ili_relations = []
    # print('ILI: {}'.format(ili))

    if ili:
        ili_relation = EqLink(name = 'eq_synonym',
                                  target_concept = Synset(ili))
        ili_relations.append(ili_relation)

    relations = element.findall('SynsetRelation')
    rels = [InternalLink(x.get('relType'),
                             Synset(x.get('target'))
                        ) for x in relations]
    # no = _no_from_id(element.get('id'))
    no = element.get('id')    
    pos = _pos_from_number(no)
    snset = Synset(no, definition = defin,
                       pos = pos,
                       internal_links = rels,
                       eq_links = ili_relations)
    # print(snset)
    return snset


def _mex(iList):
    return [Example(x.text) for x in iList]


def _mvar(element):
    lexical_entry_id =  element.get('id')
    lemma = element.find('Lemma').get('writtenForm')
    senses = element.findall('Sense')
    s = [(x.get('id'),
              x.get('synset'),
              x.findall('Example'),
              x.get('status'),
              x.get('synset')) for x in senses]

    variant = Variant(
        literal = lemma
        )
    return [(Variant(
        lemma, x,
        examples=_mex(z),
        status = a,
        synset = b
    ),y) for x,y,z,a,b in s]


def xml_variants(word, root):
    variants = [_mvar(x) for x in root.xpath(
        "//*[local-name()='LexicalEntry']"
        ) if x.find('Lemma').get('writtenForm') == word]
    return [y for x in variants for y in x]

def xml_synsets(word, variants, root):
    ids = [x[-1] for x in variants]
    synsets = [_msn(x) for x in root.xpath("//*[local-name()='Synset']") if x.get('id') in ids]
    all_variants_a = [_mvar(x) for x in root.xpath(
        "//*[local-name()='LexicalEntry']"
        ) if x.find('Sense').get('synset') in ids]
    all_variants = [y for x in all_variants_a for y in x]
    for n,i in enumerate(synsets):
        synsets[n].variants = [x[0] for x in all_variants if x[0].synset == i.number]
    return synsets


def xml_synset_no(number, root):
    ids = [number]
    synsets = [_msn(x) for x in root.xpath("//*[local-name()='Synset']") if x.get('id') == number]
    all_variants_a = [_mvar(x) for x in root.xpath(
        "//*[local-name()='LexicalEntry']"
        ) if number in [y.get('synset') for y in x.findall('Sense')]]
    #print(all_variants_a)
    all_variants = [y for x in all_variants_a for y in x]
    #print(all_variants)
    for n,i in enumerate(synsets):
        synsets[n].variants = [x[0] for x in all_variants if x[0].synset == i.number]
    return synsets


def format_polaris(level, field, value=None,
                       record=None, quot='"',
                       ident=2):
    """Format Polaris export line
    
    >>> format_polaris(0, 'WORD_MEANING', record=222)
    '0 @222@ WORD_MEANING'

    >>> format_polaris(3, 'DEFINITION', 'This is the definition')
    '      3 DEFINITION "This is the definition"'
    """

    if record:
        out = ident*level*' ' + '{} @{}@ {}'.format(level, record, field)
        return out
    if value:
        if quot:
            out = ident*level*' ' + '{} {} {}{}{}'.format(level, field,
                                                              quot, value, quot)
        else:
            out = ident*level*' ' + '{} {} {}'.format(level, field, value)
    else:
        out = ident*level*' ' + '{} {}'.format(level, field)
    return out


def parse_line(iStr):
    """
    Parses one line (iStr) of EuroWN file

    Returns dict with keys
    level
    field
    value
    drn
    """
    comment = '#'
    out = {}
    if iStr.strip() and not(iStr.strip().startswith(comment)):
        iList = iStr.strip().split(maxsplit=1)
        level = int(iList.pop(0))
        out['level'] = level
        other = iList[0]
        if level == 0 and other.startswith('@'):
            out['drn'], field = other.split('@',2)[1:]
            out['field'] = field.strip()
        elif level == 0:
            out['field'] = other.strip()
        else:
            if '"' in other:
                out['field'], value = other.split('"',1)
                out['value'] = value.strip()
                if out['value'].endswith('"'):
                    out['value'] = out['value'][:-1]
            elif '@' in other:
                out['field'], value = other.split('@',1)
                out['value'] = value.rstrip('@').strip()
            elif ' ' in other:
                out['field'], value = other.split(None,1)
                out['value'] = value.rstrip().strip()
            else:
                out['field'] = other.strip()
        out['field'] = out['field'].strip()
    else:
        out = {'field':None, 'level':-1}
    return out


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

    __slots__ = ['number','pos','variants','definition','internal_links',
                 'eq_links','properties','wordnet_offset',
                 'add_on_id','fieldname','lexicon','comment',
                     'domain']
    
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


class Variant(object):
    def __init__(self, literal=None, sense=None,
                 gloss=None, examples=None,
                 external_info=None,
                 usage_labels=None, status=None,
                 features=None, translations=None,
                     synset = None, wb=None):
        self.literal = literal
        self.sense = sense
        self.gloss = gloss
        self.examples = examples or []
        self.external_info = external_info or []
        self.usage_labels = usage_labels or []
        self.status = status
        self.features = features or []
        self.translations = translations or []
        self.synset = synset or None

        if wb:
            self.wnwb(wb)

    def wnwb(self, data: dict):
        self.literal = data['lexical_entry']['lemma']
        self.sense = data['nr']
        self.gloss = data['primary_definition']

    def add_example(self, example):
        self.examples.append(example)

    def add_external_info(self, external_inf):
        self.external_info.append(external_inf)

    def add_usage_label(self, usage_label):
        self.usage_labels.append(usage_label)

    def add_feature(self, feature):
        self.features.append(feature)

    def add_translation(self, translation):
        self.translations.append(translation)


    def __str__(self):
        out = format_polaris(2, 'LITERAL', self.literal)
        out = '{}\n{}'.format(out,
                              format_polaris(3, 'SENSE', self.sense,
                                             None, False)
                              )
        if self.gloss:
            out = '{}\n{}'.format(out,            
                              format_polaris(3, 'DEFINITION', self.gloss)
                                  )
        if self.status:
            out = '{}\n{}'.format(out,            
                                  format_polaris(3, 'STATUS', self.status,
                                                 None, False)
                                  ) # TODO: jutumärgid või ilma? Praegu ilma
        if self.synset:
            out = '{}\n{}'.format(out,            
                                  format_polaris(3, 'SYNSET', self.synset)
                                  )

        if self.examples:
            out = '{}\n{}'.format(out,
                                  format_polaris(3,
                                                 'EXAMPLES')
                                  )
            out = '{}\n{}'.format(out,
                                  '\n'.join([str(i) for i in self.examples])
                                  )
        if self.translations:
            out = '{}\n{}'.format(out,
                                  format_polaris(3,
                                                 'TRANSLATIONS')
                                  )
            out = '{}\n{}'.format(out,
                                  '\n'.join([str(i) for i in self.translations])
                                  )

        if self.usage_labels:
            out = '{}\n{}'.format(out,
                                  format_polaris(3,
                                                 'USAGE_LABELS')
                                  )
            out = '{}\n{}'.format(out,
                                  '\n'.join([str(i) for i in self.usage_labels])
                                  )
        if self.features:
            out = '{}\n{}'.format(out,
                                  format_polaris(3,
                                                 'FEATURES')
                                  )
            out = '{}\n{}'.format(out,
                                  '\n'.join([str(i) for i in self.features])
                                  )            
        if self.external_info:
            out = '{}\n{}'.format(out,
                                  format_polaris(3,
                                                 'EXTERNAL_INFO')
                                  )
            out = '{}\n{}'.format(out,
                                '\n'.join([str(i) for i in self.external_info])
                                  )
        return out


class Example:
    def __init__(self, text=None):
        self.text = text

    def __str__(self):
        out = format_polaris(4, 'EXAMPLE', self.text)
        return out

class Translation:
    def __init__(self, text=None):
        self.text = text

    def __str__(self):
        out = format_polaris(4, 'TRANSLATION', self.text)
        return out


class UsageLabel:
    def __init__(self, label=None, value=None):
        self.label = label
        self.value = value

    def __str__(self):
        out = format_polaris(4, 'USAGE_LABEL', self.label)
        if self.value:
            out = '{}\n{}'.format(out,            
                                  format_polaris(5,
                                                 'USAGE_LABEL_VALUE',
                                                 self.value)
            )

        return out


class ExternalInfo(object):
    def __init__(self, source_id=None, text_key=None,
                 number_key=None, corpus_id=None,
                 frequency=None, parole_id=None):
        self.source_id = source_id 
        self.corpus_id = corpus_id 
        self.frequency = frequency
        self.text_key = text_key
        self.number_key = number_key
        self.parole_id = parole_id

    def __str__(self):
        out = ''
        if self.corpus_id:
            out = format_polaris(4, 'CORPUS_ID', self.corpus_id, None, False)
            if self.frequency:
                out = '{}\n{}'.format(out,            
                                  format_polaris(5, 'FREQUENCY', self.frequency, None, False)
                )
        if self.source_id:
            if not out:
                out = format_polaris(4, 'SOURCE_ID', self.source_id, None, False)
            else:
                out = '{}\n{}'.format(out,            
                                  format_polaris(4, 'SOURCE_ID', self.text_key)
                                  )

        if self.text_key:
            out = '{}\n{}'.format(out,            
                                  format_polaris(5, 'TEXT_KEY', self.text_key)
                                  )
        elif self.number_key:
            out = '{}\n{}'.format(out,            
                                  format_polaris(5, 'NUMBER_KEY',
                                                 self.number_key,
                                                 None, False)
                                  )
        if self.parole_id:
            if not out:
                out = format_polaris(4, 'PAROLE_ID', self.parole_id, None, False)
            else:
                out = '{}\n{}'.format(out,            
                                  format_polaris(4, 'PAROLE_ID', self.text_key)
                                  )
            
        return out


class InternalLink:
    def __init__(self, name=None, target_concept=None,
                     features=None,
                     external_info=None):
        self.name = name
        self.target_concept = target_concept
        self.external_info = external_info or []
        self.features = features or []
        self.relation_label = 'RELATION'
        self.target_type = 'TARGET_CONCEPT'
        self.source_id = None

    def add_feature(self, feature):
        self.features.append(feature)

    def add_external_info(self, external_inf):
        self.external_info.append(external_inf)

    def __str__(self):
        tgv = None
        tgwno = None
        adonid = None
        tgpos = None
        try:
            tgv = self.target_concept.variants[0]
        except Exception:
            if self.target_concept:
                if self.target_concept.wordnet_offset:
                    tgwno = self.target_concept.wordnet_offset
                elif self.target_concept.add_on_id:
                    adonid = self.target_concept.add_on_id
        try:
            tgpos = self.target_concept.pos
        except Exception:
            tgpos = None
        out = format_polaris(2, self.relation_label, self.name)
        if self.target_concept and (
            self.target_concept.number and not (
            self.target_concept.wordnet_offset or self.target_concept.variants)
                ):
            # do and nothing more
            out = '{}\n{}'.format(out,
                                format_polaris(3, self.target_type,
                                                   self.target_concept.number,
                                                   None,'@')
                                )
            return out

        out = '{}\n{}'.format(out,
                              format_polaris(3, self.target_type)
                              )
        out = '{}\n{}'.format(out,
                                  format_polaris(4, 'PART_OF_SPEECH', tgpos)
                                  )
        if tgv:
            out = '{}\n{}'.format(out,
                                  format_polaris(4, 'LITERAL', tgv.literal)
            )
            out = '{}\n{}'.format(out,
                                  format_polaris(5, 'SENSE', tgv.sense,
                                                 None, False)
                              )
        elif tgwno:
            out = '{}\n{}'.format(out,
                                  format_polaris(4, 'WORDNET_OFFSET', tgwno,
                                                 None, False)
                              )
        elif adonid:
            out = '{}\n{}'.format(out,
                                  format_polaris(4, 'ADD_ON_ID', adonid,
                                                 None, False)
                              )
        if self.features:
            out = '{}\n{}'.format(out,
                        format_polaris(3, 'FEATURES'))
            out = '{}\n{}'.format(out,
                                  '\n'.join([str(i) for i in self.features])
                                  )
        if self.source_id:
            out = '{}\n{}'.format(out,
                        format_polaris(3, 'SOURCE_ID', self.source_id,        
                                                 None, False)
                              )
        if self.external_info:
            out = '{}\n{}'.format(out,
                                  format_polaris(3,
                                                 'EXTERNAL_INFO')
                                  )
            out = '{}\n{}'.format(out,
                                '\n'.join([str(i) for i in self.external_info])
                                  )
            
        return out
        

class EqLink(InternalLink):
    def __init__(self, name=None, target_concept=None, features=None):
        super().__init__(name, target_concept, features)
        self.relation_label = 'EQ_RELATION'
        self.target_type = 'TARGET_ILI'

        
class Feature(object):
    def __init__(self, negative=False, reversed=False,
                     disjunctive=0, conjunctive=0,
                     factive=None, non_factive=None,
                 vtov_source=None, vtov_target=None, 
                 label=None, value=None):
        self.negative = negative
        self.reversed = reversed
        self.vtov_source = vtov_source
        self.vtov_target = vtov_target
        self.label = label
        self.value = value
        self.disjunctive = disjunctive
        self.conjunctive = conjunctive
        self.factive = factive
        self.non_factive = non_factive

        # TODO:
        # factive and non_factive are mutually exclusive

    def __str__(self):
        out = ''
        if self.label:
            out = format_polaris(4, 'FEATURE', self.label)
            out = '{}\n{}'.format(out,
                        format_polaris(5, 'FEATURE_VALUE', self.value))
        if self.conjunctive:
            out = format_polaris(4, 'CONJUNCTIVE', self.conjunctive,
                                     None, False)
        if self.disjunctive:
            out = format_polaris(4, 'DISJUNCTIVE', self.disjunctive,
                                     None, False)
        if self.factive:
            out = format_polaris(4, 'FACTIVE')
        if self.non_factive:
            out = format_polaris(4, 'NON_FACTIVE')

        if self.negative:
            out = format_polaris(4, 'NEGATIVE')
        elif self.reversed:
            out = format_polaris(4, 'REVERSED')
        if self.vtov_source:
            if out:
                out = '{}\n{}'.format(out,
                        format_polaris(4, 'VARIANT_TO_VARIANT'))
            else:
                out = format_polaris(4, 'VARIANT_TO_VARIANT')

            out = '{}\n{}'.format(out,
                        format_polaris(5, 'SOURCE_VARIANT', self.vtov_source))

            out = '{}\n{}'.format(out,
                        format_polaris(5, 'TARGET_VARIANT', self.vtov_target))
            
        return out


class Lexicon:
    """
    Lecicon class
    """
    def __init__(self, name=None, language=None,
                 version=None, filename=None,
                 confidenceScore=None, email=None, id=None, label=None,
                 license=None, note=None, status=None):
        self.name = name
        self.language = language
        self.version = version
        self.filename = filename
        self.confidenceScore = confidenceScore or ''
        self.email = email or None
        self.id = id or self.name or None
        self.label = label or None
        self.license = license or None
        self.note = note or None
        self.status = status or None
        self.data = []
        self._xml_attrs = ['confidenceScore','email',
                           'id','label','language','license',
                           'note','status','version']

    def read(self):
        "Read lexicon from Polaris file"
        self.data = read_file(self.filename)
        return True

    def read_xml(self):
        "Read lexicon from XML file"
        root = etree.parse(self.filename)
        lex = root.xpath("//*[local-name()='Lexicon']")
        # print (lex[0].items())
        for k,v in lex[0].items():
            if k in self._xml_attrs and v:
                self.__dict__[k] = v

        snsets = [_msn(x) for x in root.xpath("//*[local-name()='Synset']")]
        variants = [_mvar(x) for x in root.xpath("//*[local-name()='LexicalEntry']")]

        # print(self.__dict__)
        # for i in snsets:
        #     print(i)

        # for i in variants:#[:3]:
        #     for k in i:
        #         print(k[0])

        vs = [y for x in variants for y in x]

        while vs:
            vse = vs.pop()
            snsi = [x.add_variant(vse[0]) for x in snsets if (x.number == vse[-1])]
            self.data.append(snsi[0])
            # if len(snsi[0].variants) > 1:
            # print(snsi[0])
                    

        # return True
        # print(etree.tostring(root, pretty_print=True))

    def write(self):
        with open(self.filename, 'w') as f:
            f.write('\n\n'.join([str(i) for i in self.data]))
        return True

    def write_xml(self):
        resource = etree.Element('LecicalResource')
        lexicon = etree.SubElement(resource, 'Lexicon')
        for i,k in self.__dict__.items():
            if i in self._xml_attrs and k:
                lexicon.set(i,k)

        root = resource.getroottree()

        root.write(self.filename)
        # print ('Kirjutasin faili {}'.format(self.filename))
        # print(self.__dict__)

def process(i, a, v=False, r='internal'):
    if i and not i.startswith('#'):
        i = parse_line(i)
        # print(i)
        if i['level'] == 0:
            if i['field'] == 'WORD_MEANING':
                if 'drn' in i:
                    a = Synset(i['drn'])
                else:
                    a = Synset()
        elif i['level'] == 1:
            if i['field'] == 'PART_OF_SPEECH':
                a.pos = i['value']
            elif i['field'] == 'VARIANTS':
                a.variants = []
                r = 'literal'
            elif i['field'] == 'INTERNAL_LINKS':
                a.internal_links = []
                r = 'internal'
            elif i['field'] == 'EQ_LINKS':
                a.eq_links = []
                r = 'eq'
        elif i['level'] == 2:
            if i['field'] == 'LITERAL':
                a.add_variant(Variant(i['value']))
            elif i['field'] == 'RELATION':
                a.add_internal_link(InternalLink(i['value']))
            elif i['field'] == 'EQ_RELATION':
                a.add_eq_link(EqLink(i['value']))
        elif i['level'] == 3:
            if i['field'] == 'SENSE':
                a.variants[-1].sense = i['value']
            elif i['field'] == 'STATUS':
                a.variants[-1].status = i['value']
            elif i['field'] == 'DEFINITION':
                a.variants[-1].gloss = i['value']
            elif i['field'] == 'EXAMPLES':
                a.variants[-1].examples = []
            elif i['field'] == 'TRANSLATIONS':
                a.variants[-1].translations = []
            elif i['field'] == 'USAGE_LABELS':
                a.variants[-1].usage_labels = []
            elif i['field'] == 'EXTERNAL_INFO':
                a.variants[-1].external_info = []
            elif i['field'] == 'TARGET_CONCEPT':
                a.internal_links[-1].target_concept = Synset()
            elif i['field'] == 'SOURCE_ID':
                if r == 'internal':
                    a.internal_links[-1].source_id = i['value']
                elif r == 'eq':
                    a.eq_links[-1].source_id = i['value']
            elif i['field'] == 'FEATURES':
                if r == 'internal':
                    a.internal_links[-1].features = []
                elif r == 'literal':
                    a.variants[-1].features = []
            elif i['field'] == 'TARGET_ILI':
                a.eq_links[-1].target_concept = Synset()
        elif i['level'] == 4:
            if i['field'] == 'EXAMPLE':
                a.variants[-1].add_example(Example(i['value']))
            elif i['field'] == 'TRANSLATION':
                a.variants[-1].add_translation(Translation(i['value']))
            elif i['field'] == 'FEATURE':
                a.variants[-1].add_feature(Feature(label = i['value']))
            elif i['field'] == 'USAGE_LABEL':
                a.variants[-1].add_usage_label(UsageLabel(i['value']))
            elif i['field'] == 'SOURCE_ID':
                a.variants[-1].add_external_info(
                    ExternalInfo(source_id = i['value']))
            elif i['field'] == 'CORPUS_ID':
                a.variants[-1].add_external_info(
                    ExternalInfo(corpus_id = i['value']))
            elif i['field'] == 'PART_OF_SPEECH':
                if r == 'internal':
                    a.internal_links[-1].target_concept.pos = i['value']
                elif r == 'eq':
                    a.eq_links[-1].target_concept.pos = i['value']
            elif i['field'] == 'LITERAL':
                if r == 'internal':
                    a.internal_links[-1].target_concept.add_variant(
                        Variant(i['value']))
            elif i['field'] == 'NEGATIVE':
                if r == 'internal':
                    a.internal_links[-1].add_feature(Feature(negative=True))
            elif i['field'] == 'REVERSED':
                if r == 'internal':
                    a.internal_links[-1].add_feature(Feature(reversed=True))
            elif i['field'] == 'WORDNET_OFFSET':
                if r == 'eq':
                    a.eq_links[-1].target_concept.wordnet_offset = i['value']
            elif i['field'] == 'ADD_ON_ID':
                if r == 'eq':
                    a.eq_links[-1].target_concept.add_on_id = i['value']
        elif i['level'] == 5:
            if i['field'] == 'TEXT_KEY':
                a.variants[-1].external_info[-1].text_key = i['value']
            elif i['field'] == 'NUMBER_KEY':
                a.variants[-1].external_info[-1].number_key = i['value']
            elif i['field'] == 'FREQUENCY':
                a.variants[-1].external_info[-1].frequency = i['value']
            if i['field'] == 'USAGE_LABEL_VALUE':
                a.variants[-1].usage_labels[-1].value = i['value']
            elif i['field'] == 'SENSE':
                if r == 'internal':
                    a.internal_links[-1].target_concept.variants[-1].sense = i['value']
            elif i['field'] == 'SOURCE_VARIANT':
                if r == 'internal':
                    a.internal_links[-1].add_feature(Feature(vtov_source=i['value']))
            elif i['field'] == 'TARGET_VARIANT':
                if r == 'internal':
                    a.internal_links[-1].features[-1].vtov_target=i['value']
            elif i['field'] == 'FEATURE_VALUE':
                if r == 'literal':
                    a.variants[-1].features[-1].value=i['value']

        else:
            pass
    else:
        v = True
    return a,v,r

def make_snsets(iList):
    oList = []
    snset = []
    while iList:
        a = iList.pop(0)
        if a['level'] == 0:
            if snset:
                oList.append(snset)
            snset = [a]
        else:
            snset.append(a)
    print(oList)

def dl2variants(iList, start):
    variantList = []
    level = 1
    j = start + 1
    while iList[j]['level'] > level:
        if iList[j]['field'] == 'LITERAL':
            variantList.append(Variant(iList[j]['value']))
        elif iList[j]['field'] == 'SENSE':
            variantList[-1].sense = iList[j]['value']
        elif iList[j]['field'] == 'DEFINITION':
            variantList[-1].gloss = iList[j]['value']
        elif iList[j]['field'] == 'EXAMPLES':
            j +=1
            while iList[j]['field'] == 'EXAMPLE':
                variantList[-1].add_example(Example(iList[j]['value']))
                j +=1
            j -=1
        elif iList[j]['field'] == 'TRANSLATIONS':
            j +=1
            while iList[j]['field'] == 'TRANSLATION':
                variantList[-1].add_translation(Translation(iList[j]['value']))
                j +=1
            j -=1
        elif (iList[j]['level'],
            iList[j]['field']) == (3, 'STATUS'):
                variantList[-1].status = iList[j]['value']
        elif (iList[j]['level'],
              iList[j]['field']) == (3, 'FEATURES'):
            j +=1
            while iList[j]['level'] > 3:
                if iList[j]['level'] == 4:
                    if iList[j]['field'] == 'FEATURE':
                        variantList[-1].add_feature(
                            Feature(label = iList[j]['value'])
                            )
                elif iList[j]['level'] == 5:
                    if iList[j]['field'] == 'FEATURE_VALUE':
                        variantList[-1].features[-1].value = iList[j]['value']
                j +=1
            j -=1
                

        elif (iList[j]['level'],
            iList[j]['field']) == (3, 'USAGE_LABELS'):
            j +=1
            while iList[j]['level'] > 3:
                if iList[j]['level'] == 4:
                    if iList[j]['field'] == 'USAGE_LABEL':
                        variantList[-1].add_usage_label(
                            UsageLabel(label = iList[j]['value'])
                            )
                elif iList[j]['level'] == 5:
                    if iList[j]['field'] == 'USAGE_LABEL_VALUE':
                        variantList[-1].usage_labels[-1].value = iList[j]['value']
                j +=1
            j -=1

        elif (iList[j]['level'],
              iList[j]['field']) == (3, 'EXTERNAL_INFO'):
            j +=1
            while iList[j]['level'] > 3:
                if iList[j]['level'] == 4:
                    if iList[j]['field'] == 'SOURCE_ID':
                        try:
                            variantList[-1].add_external_info(
                                ExternalInfo(source_id = iList[j]['value'])
                                )
                        except KeyError:
                            print(iList[j])
                    elif iList[j]['field'] == 'CORPUS_ID':
                        variantList[-1].add_external_info(
                            ExternalInfo(corpus_id = iList[j]['value'])
                            )
                elif iList[j]['level'] == 5:
                    if iList[j]['field'] == 'TEXT_KEY':
                        variantList[-1].external_info[-1].text_key = iList[j]['value']
                    elif iList[j]['field'] == 'NUMBER_KEY':
                        variantList[-1].external_info[-1].number_key = iList[j]['value']
                    elif iList[j]['field'] == 'FREQUENCY':
                        variantList[-1].external_info[-1].frequency = iList[j]['value']
                j +=1
            j -=1
        j +=1
    return j, variantList


def dl2internal_links(iList, start):
    internal_linkList = []
    stop = len(iList)-1
    level = 1
    j = start + 1
    while iList[j]['level'] and iList[j]['level'] > level:
        if iList[j]['field'] == 'RELATION':
            internal_linkList.append(InternalLink(iList[j]['value']))
        elif iList[j]['field'] == 'TARGET_CONCEPT':
            internal_linkList[-1].target_concept = Synset()
        elif iList[j]['field'] == 'PART_OF_SPEECH':
            internal_linkList[-1].target_concept.pos = iList[j]['value']
        elif iList[j]['field'] == 'WORDNET_OFFSET':
            internal_linkList[-1].target_concept.wordnet_offset = iList[j]['value']
        elif (iList[j]['level'],
              iList[j]['field']) == (3, 'FEATURES'):
            pass
        elif (iList[j]['level'],
              iList[j]['field']) == (4, 'VARIANT_TO_VARIANT'):
            internal_linkList[-1].add_feature(Feature())
        elif (iList[j]['level'],
              iList[j]['field']) == (5, 'SOURCE_VARIANT'):
            internal_linkList[-1].features[-1].vtov_source = iList[j]['value']
        elif (iList[j]['level'],
              iList[j]['field']) == (5, 'TARGET_VARIANT'):
            internal_linkList[-1].features[-1].vtov_target = iList[j]['value']
        elif (iList[j]['level'],
              iList[j]['field']) == (4, 'LITERAL'):
            internal_linkList[-1].target_concept.add_variant(Variant(iList[j]['value']))
        elif (iList[j]['level'],
              iList[j]['field']) == (5, 'SENSE'):
            internal_linkList[-1].target_concept.variants[0].sense = iList[j]['value']
        elif (iList[j]['level'],
              iList[j]['field']) == (3, 'SOURCE_ID'):
            internal_linkList[-1].source_id = iList[j]['value']
        elif (iList[j]['level'],
              iList[j]['field']) == (4, 'REVERSED'):
            internal_linkList[-1].add_feature(Feature(reversed=True))
        if j < stop:
            j +=1
    return j, internal_linkList

def dl2eq_links(iList, start):
    eq_linkList = []
    level = 1
    j = start + 1
    while iList[j]['level'] and iList[j]['level'] > level:
        if iList[j]['field'] == 'EQ_RELATION':
            eq_linkList.append(EqLink(iList[j]['value']))
        elif iList[j]['field'] == 'TARGET_ILI':
            eq_linkList[-1].target_concept = Synset()
        elif iList[j]['field'] == 'PART_OF_SPEECH':
            eq_linkList[-1].target_concept.pos = iList[j]['value']
        elif iList[j]['field'] == 'WORDNET_OFFSET':
            eq_linkList[-1].target_concept.wordnet_offset = iList[j]['value']
        elif iList[j]['field'] == 'ADD_ON_ID':
            eq_linkList[-1].target_concept.add_on_id = iList[j]['value']
        elif (iList[j]['level'],
              iList[j]['field']) == (3, 'FEATURES'):
            pass
        elif (iList[j]['level'],
              iList[j]['field']) == (5, 'SOURCE_VARIANT'):
            eq_linkList[-1].features[-1].vtov_source = iList[j]['value']
        elif (iList[j]['level'],
              iList[j]['field']) == (5, 'TARGET_VARIANT'):
            eq_linkList[-1].features[-1].vtov_target = iList[j]['value']
        elif (iList[j]['level'],
              iList[j]['field']) == (4, 'LITERAL'):
            eq_linkList[-1].target_concept.add_variant(Variant(iList[j]['value']))
        elif (iList[j]['level'],
              iList[j]['field']) == (5, 'SENSE'):
            eq_linkList[-1].target_concept.variants[0].sense = iList[j]['value']
        elif (iList[j]['level'],
              iList[j]['field']) == (3, 'SOURCE_ID'):
            eq_linkList[-1].source_id = iList[j]['value']
            
        j +=1
    return j, eq_linkList
    

def dl2snsets(iList, soi, vidx, irlidx):
    """Converts list of dicts to list of synsets
    iList - raw lexicon (dicts)
    soi - input list (idx, Snset)
    """
    j = 0
    vidx.reverse()
    irlidx.reverse()
    while vidx:
        soi[j][1].variants = dl2variants(iList, vidx.pop())
        j +=1
    j = 0
    while irlidx:
        soi[j][1].internal_links = dl2internal_links(iList, irlidx.pop())
        j +=1
    return soi

def read_synset(dict_list, start):
    """
    Reads synset from dict_list starting from start

    Args:
        dict_list (list): List of dicts with lexicon data
        start (int): Starting index in dict_list

    Returns: Synset instance

    We assume, that every Synset has always drn and part of speech.

    TODO: STATUS
    """
    snset = Synset(dict_list[start]['drn'],
                   dict_list[start+1]['value'])
    start +=2
    while dict_list[start]['level'] > 0:
        if (dict_list[start]['level'],
            dict_list[start]['field'] ) == (1,'VARIANTS'):
            start, snset.variants = dl2variants(dict_list, start)
        elif (dict_list[start]['level'],
            dict_list[start]['field'] ) == (1,'INTERNAL_LINKS'):
            start, snset.internal_links = dl2internal_links(dict_list, start)
        elif (dict_list[start]['level'],
            dict_list[start]['field'] ) == (1,'EQ_LINKS'):
            start, snset.eq_links = dl2eq_links(dict_list, start)
        else:
            start +=1

    return snset


def read_file(filename):
    lex = []
    with open(filename, 'r') as f:
        for line in f:
            lex.append(parse_line(line))
    lex.append({'field':None, 'level':-1})
    
    soi = [ read_synset(lex, j) for j,i in enumerate(lex) if i['level'] == 0]
    return soi

def test_xml():
    synsets = []
    
    return synsets

def write_xml(synsets):
    root = etree.Element('LexicalResource')
    lexicon = etree.Element('Lexicon')
    for i in synsets:
        snset = etree.Element('Synset')
        if i.number:
            snset.set('id', i.number)
        lexicon.append(snset)

    root.append(lexicon)

    print(tostring(
        root,
        pretty_print=True,
        encoding='UTF-8').decode('UTF-8')
              )


def main(filename):
    out = read_file(filename)
    for i in out:
        print(i)
        print()

if __name__ == '__kain__':
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help="Lexicon file name")
    
    args = parser.parse_args()
    
    main(args.filename)
    print("--- {} seconds ---".format(time.time() - start_time),
          file = sys.stderr)

if __name__ == '__sain__':
    a = Synset('43','n')
    write_xml([a])


if __name__ == '__main__':
    a = Lexicon(filename = 'leksikonitest.xml',
                name = 'test')
    # a.write_xml()
    b = Lexicon(filename = '../data/estwn/estwn-et-2.1.0.wip.xml')
    b.read_xml()
    
    b.filename = 'test21a.xml'
    b.write()
            
