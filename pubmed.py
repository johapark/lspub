#!/usr/bin/env python

## Imports
from eutils import Client
# https://eutils.readthedocs.io/en/stable/modules.html#main-classes

class PubMedArticle(object):
    """Formatting PubMed results stored in `eutils._internal.xmlfacades.pubmedarticle.PubmedArticle` instance for generating bibliography"""
    def __init__(self, pma):
        self.pma = pma
        self.abstract = pma.abstract
        self.authors = pma.authors
        self.year = pma.year
        self.title = pma.title
        self.journal = pma.jrnl
        self.volume = pma.volume
        self.issue = pma.issue
        self.pages = pma.pages

    def bibliography(self, style='default', **kwarg):
        return self._stylizer(style, **kwarg)

    @staticmethod
    def enclose(s, char):
        return f'{char}{s}{char}'

    @staticmethod
    def initialize_name(name, join='.'):
        initials = list()
        tokens = name.split()
        for token in tokens:
            for i, t in enumerate(token.split('-')):
                if i == 0:
                    initials.append(t[0].upper())
                else:
                    initials.append('-'+t[0].upper())
                
        return join.join(initials) + join

    def _stylizer(self, style, highlight_names=False, highlight_journal=False):
        authors = self.authors
        year = self.year
        title = self.title
        journal = self.journal
        volume = self.volume
        issue = self.issue
        pages = self.pages
        abstract = self.abstract

        if style == 'default':

            def _highlight_names(authors, names):
                return [self.enclose(n, '**') if (n in names) else n for n in authors ]

            if highlight_names: authors = _highlight_names(authors, highlight_names)
            if highlight_journal: journal = self.enclose(journal, '**')

            elements = [\
                ', '.join(authors),
                f"({year})",
                f'"{title}"',
                f"_{journal}_",
                f"{volume}({issue}):{pages}"
            ]

            output = ' '.join(elements)

        elif style == 'bibtex':

            def _bibtex_format_authors(authors):
                names = []
                for author in authors:
                    family_name, given_name = map(str.strip, author.split(','))
                    given_name = self.initialize_name(given_name)
                    names.append(f"{family_name}, {given_name}")
                return ' and '.join(names)

            formatted = "@article{"
            label = authors[0].split(',')[0] + year
            author = f"author = {{{_bibtex_format_authors(authors)}}}"
            title = f"title = {{{title}}}"
            year = f"year = {{{year}}}"
            journal = f"journal = {{{journal}}}"
            volume = f"volume = {{{volume}}}"
            issue = f"issue = {{{issue}}}"
            pages = f"pages = {{{pages}}}"
            abstract = f"abstract = {{{abstract}}}"

            elements = [label, author, title, year, journal, volume, issue, pages, abstract] # label should be placed at first

            formatted += ',\n  '.join(elements)
            formatted += "\n}\n"

            output = formatted

        return output


def search_pubmed_by_author(client, author_name, affliations=None):
    """Carry out Esearch with 'eutils.Client' instance.
       Search term uses the combination of author name and affiliations"""

    term_list = [f'({author_name}[Author] AND {aff}[Affiliation])' for aff in affiliations]
    search_term = ' OR'.join( term_list )
    esearch = client.esearch(db='pubmed', term=search_term)
    return esearch

def main(author_name, affiliations=None, api_key=None, style='default', highlight_names=None, highlight_journal=True):
    """Search PubMed via eutils and format the retreived results"""
    ec = Client(api_key=api_key)
    esr = search_pubmed_by_author(ec, author_name, affiliations)
    pmasets = [pma for pma in iter(ec.efetch(db='pubmed', id=esr.ids))]
    pubs = [PubMedArticle(pma) for pma in pmasets]

    for pub in pubs:
        print( pub.bibliography(style=style, highlight_names=highlight_names, highlight_journal=highlight_journal))



if __name__ == '__main__':
    import yaml
    yamlpath = "info.yaml"
    info = yaml.load(open(yamlpath), Loader=yaml.FullLoader)
    api_key = None

    author_name = info['Name']
    affiliations = info['Affiliations']
    bibliography_style = info["Style"]

    main(author_name, affiliations, api_key, bibliography_style, ['Park J'])
