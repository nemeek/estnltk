from eurown.backends import format_polaris

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
