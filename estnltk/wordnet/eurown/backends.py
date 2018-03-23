# Wordnet workbench
# =================
def make_wnwb_query(lexid, search, root):
    """
    Make query in function
    """
    tulem = []
    r = requests.get(root, params={
        'lexid':lexid, 'word':search}
                         )
    print(r.url)
    if r.status_code != 200:
        print ('Ei saa serveriga ühendust!', sys.stderr)
        return None
    else:
        vastus = r.json()
        tulem = vastus['results']
        if vastus['count'] > len(vastus['results']):
            r = requests.get(vastus['next'])
            if r.status_code == 200:
                tulem.extend(r.json()['results'])
        return tulem


# Polaris import-export
# =====================

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
