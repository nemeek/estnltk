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
