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
