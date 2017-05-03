import re
from collections import defaultdict
from pandas import read_csv
from os.path import dirname, join

class VabamorfCorrectionRewriter:
    
    def __init__(self, replace:bool=True):
        """
        replace: bool (default True)
            If True, replace old analysis with new analysis
            If False, filter old analysis, that is, return the intersection of
            old analysis and new analysis
        """
        self.replace = replace
        file = join(dirname(__file__), 'rules_files/number_analysis_rules.csv')
        self.rules = self.load_number_analysis_rules(file)


    @staticmethod
    def load_number_analysis_rules(file):
        df = read_csv(file, na_filter=False)
        rules = defaultdict(dict)
        for _, r in df.iterrows():
            if r.suffix not in rules[r.number]:
                rules[r.number][r.suffix] = []
            rules[r.number][r.suffix].append({'partofspeech': r.pos, 'form': r.form, 'ending':r.ending})
        return rules


    def analyze_number(self, token):
        m = re.match('-?(\d+\.?)-?(\D*)$', token)
        if not m:
            return []
        m.group(0), 
        number = m.group(1)
        ordinal_number = number.rstrip('.') + '.'
        ending = m.group(2)
        result = []
        for number_re, analyses in self.rules.items():
            if re.match(number_re, number):
                for analysis in analyses[ending]:
                    if analysis['partofspeech'] == 'O':
                        a = {'lemma':ordinal_number, 'root':ordinal_number, 'root_tokens':[ordinal_number], 'clitic':''}
                    else:
                        a = {'lemma':number, 'root':number, 'root_tokens':[number], 'clitic':''}
                    a.update(analysis)
                    result.append(a)
                break
        return result

    def rewrite(self, records):        
        # 'word_normal' should be equal for all records, so use the first one
        word_normal = records[0]['word_normal']
        # no attempt to correct the analysis if the normalized token consists
        # of letters only
        if word_normal.isalpha():
            return records

        start_end = {'start': records[0]['start'], 'end': records[0]['end']}
        # currently only analysis of numeric tokens is corrected 
        analysis = self.analyze_number(word_normal)

        for a in analysis:
            a.update(start_end)
        if analysis:
            if self.replace:
                records =  analysis
            else:
                records =  [rec for rec in records if rec in analysis]

        return records