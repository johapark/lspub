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

    def _stylizer(self, style, highlight_names=False, highlight_journal=False):
        authors = self.authors
        year = self.year
        title = self.title
        journal = self.journal
        volume = self.volume
        issue = self.issue
        pages = self.pages

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
            """
            @article{Yi2018,
                abstract = {Multiple deadenylases are known in vertebrates, the PAN2-PAN3 (PAN2/3) and CCR4-NOT (CNOT) complexes, and PARN, yet their differential functions remain ambiguous. Moreover, the role of poly(A) binding protein (PABP) is obscure, limiting our understanding of the deadenylation mechanism. Here, we show that CNOT serves as a predominant nonspecific deadenylase for cytoplasmic poly(A) + RNAs, and PABP promotes deadenylation while preventing premature uridylation and decay. PAN2/3 selectively trims long tails (>∼150 nt) with minimal effect on transcriptome, whereas PARN does not affect mRNA deadenylation. CAF1 and CCR4, catalytic subunits of CNOT, display distinct activities: CAF1 trims naked poly(A) segments and is blocked by PABPC, whereas CCR4 is activated by PABPC to shorten PABPC-protected sequences. Concerted actions of CAF1 and CCR4 delineate the ∼27 nt periodic PABPC footprints along shortening tail. Our study unveils distinct functions of deadenylases and PABPC, re-drawing the view on mRNA deadenylation and regulation. Yi et al. show that the CCR4-NOT complex is a generic deadenylase and its two catalytic subunits have distinct activities regarding PABPC: CAF1 trims PABPC-free A tails while CCR4 removes PABPC-bound A tails. PABPC coordinates mRNA deadenylation and decay in a timely order by promoting deadenylation and blocking precocious decay.},
                author = {Yi, Hyerim and Park, Joha and Ha, Minju and Lim, Jaechul and Chang, Hyeshik and Kim, V. Narry},
                doi = {10.1016/j.molcel.2018.05.009},
                file = {:Users/joha/Clouds/Google Drive/Mendeley/2018_Molecular Cell_Yi et al._PABP Cooperates with the CCR4-NOT Complex to Promote mRNA Deadenylation and Block Precocious Decay.pdf:pdf},
                issn = {10972765},
                journal = {Molecular Cell},
                keywords = {CAF1,CCR4,CCR4-NOT,PABPC,PAN2-PAN3,PARN,RNA decay,deadenylation,poly(A) tail,uridylation},
                month = {jun},
                number = {6},
                pages = {1081--1088.e5},
                title = {{PABP Cooperates with the CCR4-NOT Complex to Promote mRNA Deadenylation and Block Precocious Decay}},
                url = {https://linkinghub.elsevier.com/retrieve/pii/S1097276518303599},
                volume = {70},
                year = {2018}
            }
            """

            output = authors


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
        print( pub.bibliography(style=style, highlight_names=highlight_names, highlight_journal=highlight_journal), '<br>' )



if __name__ == '__main__':
    import yaml
    yamlpath = "info.yaml"
    info = yaml.load(open(yamlpath), Loader=yaml.FullLoader)
    api_key = None

    author_name = info['Name']
    affiliations = info['Affiliations']
    bibliography_style = info["Style"]

    main(author_name, affiliations, api_key, bibliography_style, ['Park J'])
