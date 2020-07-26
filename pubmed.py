#!/usr/bin/env python

## Imports
from eutils import Client
# https://eutils.readthedocs.io/en/stable/modules.html#main-classes

class PubMedCitation(object):
    """Formatting PubMed results stored in `eutils._internal.xmlfacades.pubmedarticle.PubmedArticle` instance for citation"""
    def __init__(self, pma):
        self.pma = pma
        self.authors = self.pma.authors
        self.year = self.pma.year
        self.title = self.pma.title
        self.journal = self.pma.jrnl
        self.volume = self.pma.volume
        self.issue = self.pma.issue
        self.pages = self.pma.pages
        
    def citation(self, style='default', **kwarg):
        return self._stylizer(style, **kwarg)
    
    @staticmethod
    def enclose(s, char):
        return f'{char}{s}{char}'

    def _stylizer(self, style, highlight_names=False, highlight_journal=False):       
        authors = self.authors
        year = self.year
        title = self.title
        journal = self.journal
        volume = self.volume
        issue = self.issue
        pages = self.pages
        enclose = self.enclose
        
        def _highlight_names(authors, names):
            return [enclose(n, '**') if (n in names) else n for n in authors ]
        
        if highlight_names: authors = _highlight_names(authors, highlight_names)
        if highlight_journal: journal = enclose(journal, '**')
            

        if style == 'default':
            structured = [\
                ', '.join(authors),
                f"({year})",
                f'"{title}"',
                f"_{journal}_",
                f"{volume}({issue}):{pages}"
            ]
            
        return ' '.join(structured)

def search_pubmed_by_author(client, author_name, affliations=None):
    """Carry out Esearch with 'eutils.Client' instance.
       Search term uses the combination of author name and affiliations"""

    term_list = [f'({author_name}[Author] AND {aff}[Affiliation])' for aff in affiliations]
    search_term = ' OR'.join( term_list )
    esearch = client.esearch(db='pubmed', term=search_term)
    return esearch

def main(author_name, api_key=None, style='default', highlight_names=None, highlight_journal=True):
    """Search PubMed via eutils and reformat the retreived results"""
    ec = Client(api_key=api_key)
    esr = search_pubmed_by_author(ec, author_name)
    pmasets = [pma for pma in iter(ec.efetch(db='pubmed', id=esr.ids))]
    pubs = [PubMedCitation(pma) for pma in pmasets]

    for pub in pubs:
        print( pub.citation(style=style, highlight_names=highlight_names, highlight_journal=highlight_journal), '<br>' )
               
        

if __name__ == '__main__':
    import yaml
    yamlpath = "info.yaml"
    info = yaml.load(open(yamlpath), Loader=yaml.FullLoader)
    api_key = None

    author_name = info['Name']
    affiliations = info['Affiliations']
    citation_style = info["Style"]

    main(author_name, api_key, citation_style, ['Park J'])
