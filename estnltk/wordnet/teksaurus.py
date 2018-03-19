import re
import os
import builtins

from flask import Flask, flash, render_template, redirect, url_for, request, Markup, send_from_directory
from wtforms import Form, TextField, validators

import requests

from config import WNWB_PREFIX, WNWB_LEXID, HYPERNYM_IDS, HYPONYM_IDS, APP_CONFIG_SECRET_KEY, SYNSET_RELATIONS

WNWB_SNSET = WNWB_PREFIX + 'synset/'
OMW_NAMES = set([x[1] for x in SYNSET_RELATIONS])
SNSET_OMW_REL = [{'omw_name':x, 'ids':[y[0] for y in SYNSET_RELATIONS if y[1] == x]} for x in OMW_NAMES if x]

P = re.compile('([^_]+)([_])(\d{1,2})([(]\w{1,2}[)])')

app = Flask(__name__,static_url_path='/docs/build/html/')
app.config['SECRET_KEY'] = APP_CONFIG_SECRET_KEY

__version__ = '2.0.1b1'

class ReusableForm(Form):
    otsi = TextField('Otsi:', validators=[validators.required()])

@app.template_filter('hypernyms')
def hypernyms(synset):
     return [x for x in synset['relations'] if (
            x['rel_type'] in HYPERNYM_IDS and str(x['a_synset']) == str(synset['id']))
                         ]
 
@app.template_filter('hyponyms')
def hyponyms(synset):
     return [x for x in synset['relations'] if (
            x['rel_type'] in HYPONYM_IDS and str(x['a_synset']
            ) == str(synset['id']))
                         ]

@app.template_filter()
def others(synset):
     out = [x for x in synset['relations'] if (
            x['rel_type'] not in HYPONYM_IDS+HYPERNYM_IDS and str(x['a_synset']
            ) == str(synset['id']))
                         ]
     g_others = [{'omw_name':x['omw_name'], 'relation':[i for i in out if int(i['rel_type']) in x['ids']]} for x in SNSET_OMW_REL ]
     return [x for x in g_others if x['relation']]

@app.template_filter()
def snset_pos(synsets):
    posnames = {'n':'nimisõna','a':'omadussõna','v':'tegusõna','b':'määrsõna'}
    poses = set([x['label'].split('-')[-1] for x in synsets])
    g_snsets = [{'pos':x, 'posname':posnames[x],
                 'snsets':[
                     y for y in synsets if y['label'].split('-')[-1] == x
                 ]} for x in poses]
    return g_snsets


@app.template_filter()
def varheader(iStr):
    if '[' in iStr:
        ksta = iStr[iStr.find('[')+1:iStr.find(']')] # kandiliste sulgudeta
    else:
        ksta = iStr
    return Markup(P.sub(r'\1&nbsp;<sub>\3\4</sub>',ksta))

@app.template_filter()
def sortiir(snsets, alus=None):
    if alus:
        synsets = sorted(
            snsets,
                key=lambda a: int(
                    a['variants_str'][a['variants_str'].find(
                        '_',a['variants_str'].find(alus))+1:a['variants_str'].find(
                            '(',a['variants_str'].find(alus))]
                             )
            )
    else:
        synsets = snsets
    return synsets
    

@app.template_filter()
def get_ili(externals,system="systems"):
    if system == "systems":
        vahe = [(x['system'],
                    x['sys_id']['id']) for x in externals]
        vahe.sort(key=lambda a:a[1], reverse=True)
        out = [x[0] for x in vahe]

    elif system == "best":
        for i in ['CILI',"PWN-3.0","ILI-1.5"]:
            cili =  [x for x in externals if x['system'] == i]
            oout = [{'eq_relation':x['type_ref_code'],
                    'literals':x['variants_str'],
                     'definition':x['definition'],
                     'system':i} for x in cili]
            out = [x for x in oout if x['eq_relation'] == 'eq_synonym']
            if len(out) == 1:
                return out
        
    else:
        cili =  [x for x in externals if x['system'] == system]

        out = [{'eq_relation':x['type_ref_code'],
                    'literals':x['variants_str'],
                    'definition':x['definition']} for x in cili]
    return out

@app.template_filter()
def eq_synonym(external):
    out = [x for x in external if x['eq_relation'] == 'eq_synonym']
    return out


@app.template_filter('len')
def length(x):
    return len(x) 


@app.template_filter()
def len_by(x):
    kokku = sum([len([i for i in k['relation']]) for k in x])
    return '{}/{}'.format(kokku,len(x))


def _word_variants(x):
    """
    Generate other spelling variants
    """
    out = []
    for i in ['lower','upper','title']:
        method_to_call = getattr(str, i)
        y = method_to_call(x)
        if y != x:
            out.append(y)
    return out


def _make_query(lexid, search, root):
    """
    Make query in function
    """
    tulem = []
    r = requests.get(root, params={
        'lexid':lexid, 'word':search}
                         )
    if r.status_code != 200:
        return flash('Ei saa serveriga ühendust!')
    else:
        vastus = r.json()
        tulem = vastus['results']
        if vastus['count'] > len(vastus['results']):
            r = requests.get(vastus['next'])
            if r.status_code == 200:
                tulem.extend(r.json()['results'])
        return tulem


@app.route('/', methods=['GET', 'POST'])
def search():
    otsi = None
    pikkus = None
    tulem = []
    tulemid = {}
    avada = True

    form = ReusableForm(request.form)
    if request.method == 'POST':
        otsi=request.form['otsi']
        if form.validate():
            tulem = _make_query(WNWB_LEXID, otsi, WNWB_SNSET)
            if tulem:
                return render_template('search.html',form=form,results=tulem,
                                otsi=otsi, pikkus=len(tulem))
            else:
                print (_word_variants(otsi))
                for i in _word_variants(otsi):
                    tulemid[i] = _make_query(WNWB_LEXID, i, WNWB_SNSET)
                avatav = sum([len(v) for k,v in tulemid.items()])
                avada = avatav or False
                return render_template('search.html',otsi=otsi,avada=avada,
                                           form=form,tulemid=tulemid)
        else:
            flash('Otsisõna peab olema!')
    return render_template('search.html',form=form,results=tulem,pikkus=len(tulem),
                               otsi=otsi)            


@app.route('/synset/<number>')
def show_synset(number):
    rs = requests.get('{}{}'.format(WNWB_SNSET, number))
    if rs.status_code != 200:
        flash('Ei saa serveriga ühendust!')
    else:
        vastus = rs.json()
        hypers = hypernyms(vastus)
        hypos = hyponyms(vastus)
        othss = others(vastus)
    return render_template('synset.html', number=number, hypernyms=hypers,
                               hyponyms=hypos,othes=othss,
                               result=vastus)


@app.route('/about')
def about():
    return render_template('about.html')

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs","build", "html")


@app.route('/docs/<path:path>', methods=['GET'])
def static_proxy(path):
    return send_from_directory(root, path)


@app.route('/_static')
def real_stat():
    return redirect('/docs/build/html/_static')


if __name__ == "__main__":
    app.run(debug=True)
