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
