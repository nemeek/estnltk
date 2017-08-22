import regex as re
from estnltk.text import Layer, SpanList
from .patterns import MACROS, ABBREVIATIONS
from estnltk.layer_operations import resolve_conflicts

initial = re.compile(r'[{UPPERCASE}][{LOWERCASE}]?$'.format(**MACROS))
surname = re.compile(r'[{UPPERCASE}][{LOWERCASE}]{2,}$'.format(**MACROS))

class CompoundTokenTagger:
    def __init__(self, 
                 compound_types_to_merge={'abbrevation', 'name'},
                 conflict_resolving_strategy='MAX'):
        self._layer_name = 'compound_tokens'
        self._attributes = ['type']
        self._depends_on = ['tokens']
        self._conf = ("compound_types_to_merge="+str(compound_types_to_merge)+
                     ", conflict_resolving_strategy="+conflict_resolving_strategy)
        
        self._compound_types_to_merge = compound_types_to_merge
        self._conflict_resolving_strategy = conflict_resolving_strategy

    def tag(self, text: 'Text') -> 'Text':
        layer = Layer(name=self._layer_name,
                      enveloping = 'tokens',
                      attributes=self._attributes,
                      ambiguous=False)
        tokens = text.tokens.text
        name_status = None
        hyphenation_status = None
        last_end = None
        for i, span in enumerate(text.tokens):
            token = span.text

            # abbreviation
            if token.lower() in ABBREVIATIONS:
                spl = SpanList()
                if i+1<len(tokens) and tokens[i+1]=='.':
                    spl.spans = text.tokens[i:i+2]
                else:
                    spl.spans = text.tokens[i:i+1]
                spl.type = 'non_ending_abbreviation'
                layer.add_span(spl)

            # automaton for names
            if name_status is None:
                if initial.match(token):
                    name_status = 'initial'
                    name_start = i
            elif name_status == 'initial':
                if token == '.':
                    name_status = 'point'
                else:
                    name_status = None
            elif name_status == 'point':
                if initial.match(token):
                    name_status = 'initial'
                elif surname.match(token):
                    spl = SpanList()
                    spl.spans = text.tokens[name_start:i+1]
                    spl.type = 'name'
                    layer.add_span(spl)
                    name_status = None
                else:
                    name_status = None

            # hyphenation
            if hyphenation_status is None:
                if last_end==span.start and span.text == '-':
                        hyphenation_status = '-'
                else:
                    hyphenation_start = i
            elif hyphenation_status=='-':
                if last_end==span.start:
                    hyphenation_status = 'second'
                else:
                    hyphenation_status = 'end'
            elif hyphenation_status=='second':
                if last_end==span.start and span.text == '-':
                        hyphenation_status = '-'
                else:
                    hyphenation_status = 'end'
            if hyphenation_status == 'end' and hyphenation_start+1 < i:
                spl = SpanList()
                spl.spans = text.tokens[hyphenation_start:i]
                spl.type = 'hyphenation'
                layer.add_span(spl)
                hyphenation_status = None
                hyphenation_start = i
            last_end = span.end

        # TODO:
        #if self._compound_types_to_merge:
        resolve_conflicts(layer, conflict_resolving_strategy=self._conflict_resolving_strategy)
        
        text[self._layer_name] = layer
        return text

    def configuration(self):
        record = {'name':self.__class__.__name__,
                  'layer':self._layer_name,
                  'attributes':self._attributes,
                  'depends_on': self._depends_on,
                  'conf':self._conf}
        return record

    def _repr_html_(self):
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        df = pandas.DataFrame.from_records([self.configuration()], columns=['name', 'layer', 'attributes', 'depends_on', 'conf'])
        return df.to_html(index=False)