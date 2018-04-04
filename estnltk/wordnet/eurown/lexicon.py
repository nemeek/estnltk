import time
start_time = time.time()

import sys

from lxml import etree
from lxml.etree import fromstring, tostring

from .synset import Definition, Synset
from .relations import InternalLink, EqLink
from .variant import Variant, Example

def _pos_from_number(iStr):
    return iStr.split('-')[-1]

def make_synset(element: etree.Element) -> Synset:
    """Reads element Synset, makes eurown.Synset object
    with appropriate data: number, definition, internal and 
    external relations.

    Parameters
    ----------
    element
        Synset element

    Returns
    -------
    Synset
        appropriate eurown.Synset object

    """
    try:
        defin = Definition(element.find('Definition').get('language'),
                           element.find('Definition').text,
                           element.find('Definition').get('sourceSense')
        )
    except AttributeError:
        defin = None

    ili = element.attrib['ili']
    ili_relations = []

    if ili:
        ili_relation = EqLink(name = 'eq_synonym',
                                  target_concept = Synset(ili))
        ili_relations.append(ili_relation)

    relations = element.findall('SynsetRelation')
    rels = [InternalLink(x.get('relType'),
                             Synset(x.get('target'))
                        ) for x in relations]
    no = element.get('id')    
    pos = _pos_from_number(no)
    snset = Synset(no, definition = defin,
                       pos = pos,
                       internal_links = rels,
                       eq_links = ili_relations)
    return snset


def _mvar(element):
    """Obsolete.

    TODO: delete this function

    """
    lexical_entry_id =  element.get('id')
    lemma = element.find('Lemma').get('writtenForm')
    senses = element.findall('Sense')
    s = [(x.get('id'),
              # x.get('synset'),
              x.findall('Example'),
              x.get('status'),
              x.get('synset')) for x in senses]

    # variant = Variant(
    #     literal = lemma
    #     )
    return [Variant(
        lemma, x,
        examples=_mex(z),
        status = a,
        synset = b
    ) for x,z,a,b in s]


def make_variant(element: etree.Element, synset: str = None) -> Variant:
    """Finds from LexicalEntry elements these Senses,
    where "synset" attributes are equal to synset parameter.

    Parameters
    ----------
    element
        element in which to search

    synset
        synset identifier

    Returns
    -------
    Variant
        the only variant that corresponds to this synset.
        If more than one, rise error.

    """
    lexical_entry_id =  element.get('id')
    lemma = element.find('Lemma').get('writtenForm')
    senses = element.findall('Sense')
    if synset:
        s = [(x.get('id'),
              x.findall('Example'),
              x.get('status'),
              x.get('synset')) for x in senses if x.attrib['synset'] == synset]
    else:
        s = [(x.get('id'),
              x.findall('Example'),
              x.get('status'),
              x.get('synset')) for x in senses]
        
        
    variant = [Variant(
        lemma, x,
        examples=_mex(z),
        status = a,
        synset = b
    ) for x,z,a,b in s]

    if len(variant) == 1:
        return variant[0]
    else:
        return None # Should rise error

    
def make_sense(element: etree.Element) -> Variant:
    """Reads Sense element and adds correspongind LexicalEntry/Lemma[writtenForm]

    Parameters
    ----------
    element
        element in which to search

    Returns
    -------
    Variant
        based on Sense

    """
    lexical_entry = element.getparent()
    lexical_entry_id =  lexical_entry.get('id')
    lemma_element = lexical_entry[0] # Või findall? Kas neid on parajasti 1?
    lemma = lemma_element.get('writtenForm')
    sense_id = element.get('id')
    examples = element.findall('Example')
    status = element.get('status')
    note = element.get('note')
    synset = element.get('synset')

    variant = Variant(
        literal = lemma,
        sense = sense_id,
        examples = _mex(examples),
        status = status,
        synset = synset)

    return variant
    

def _mex(iList):
    return [Example(x.text) for x in iList]


class Lexicon(object):
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

    def read_xml(self): # vana xml
        "Read lexicon from XML file"
        root = etree.parse(self.filename)
        lex = root.xpath("//*[local-name()='Lexicon']")
        # print (lex[0].items())
        for k,v in lex[0].items():
            if k in self._xml_attrs and v:
                self.__dict__[k] = v

        print('Reading synsets...', file=sys.stderr)
        snsets = [make_synset(x) for x in root.xpath("//*[local-name()='Synset']")]
        snsets.sort(key=lambda synset: synset.number)

        print ('Number of synsets: {}'.format(len(snsets)))

        for i in snsets[:4]:
            print (i.number)

        
        print('Reading variants...', file=sys.stderr)
        otsing = 'estwn-et-266-n'
        # variants = [make_variant(x,y) for x in root.xpath("//*[local-name()='LexicalEntry' and ./Sense[@synset='{}']]".format(y.number)) for y in snsets]
        # variants = [make_variant(x) for x in root.xpath("//*[local-name()='LexicalEntry']")]
        
        senses = [make_sense(x) for x in root.xpath("//*[local-name()='Sense']")]


        # synohulgad = [print(x.add_variant(make_variant(v, x.number))) for x in snsets for v in root.xpath("//*[local-name()='LexicalEntry' and ./Sense[@synset='{}']]".format(x.number))]
        
        print('Senses read!', file=sys.stderr)

        for i in senses[:4]:
            print (i.synset)

        
        senses.sort(key=lambda sense: sense.synset)

        for i in senses[:4]:
            print (i.synset)

        # tõmba kokku
        pikkus = len(snsets)

        ss = [i.add_variants([k for k in senses if k.synset == i.number]) for i in snsets ]
        print(len(ss))
        
        # print(snsets[0])
        # print(15*'#')
        # for i in variants:
        #     print (10*'=')
        #     print (i)
        # print(variants[0][0])

        # print("Mapping...", file=sys.stderr)
        # self.data = [print(i.add_variant(k[0][0])) for i in snsets for k in variants if k[0][1]==i.number]
        # print("Mapped!", file=sys.stderr)        

        # print(self.__dict__)
        # for i in snsets:
        #     print(i)

        # for i in variants:#[:3]:
        #     for k in i:
        #         print(k[0])

        # vs = [y for x in variants for y in x]

        # while vs:
        #     vse = vs.pop()
        #     snsi = [x.add_variant(vse[0]) for x in snsets if (x.number == vse[-1])]
        #     self.data.append(snsi[0])
        #     # if len(snsi[0].variants) > 1:
        #     #     print(snsi[0])
                    

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

    def read_uxml(self):
        """Reads xml file (self.filename)

        """
        pass
    
        
