# -*- coding: utf-8 -*-
"""
batterydataextractor.reader.elsevier

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Elsevier XML reader
coauthor:: Callum Court <cc889@cam.ac.uk>
author:
"""
import six
from ..scrape.clean import clean, Cleaner
from ..doc.meta import MetaData
from .markup import XmlReader
from lxml import etree

# XML stripper that removes the tags around numbers in chemical formulas
strip_els_xml = Cleaner(strip_xpath='.//ce:inf | .//ce:italic | .//ce:bold | .//ce:formula | .//mml:* | .//ce:sup',
                        kill_xpath='.//ce:cross-ref//ce:sup | .//ce:table//ce:sup | .//ce:cross-ref | .//ce:cross-refs')


def fix_elsevier_xml_whitespace(document):
    """ Fix tricky xml tags"""
    # space hsp  and refs correctly
    for el in document.xpath('.//ce:hsp'):
        parent = el.getparent()
        previous = el.getprevious()
        if parent is None:
            continue
        # Append the text to previous tail (or parent text if no previous), ensuring newline if block level
        if el.text and isinstance(el.tag, six.string_types):
            if previous is None:
                if parent.text:
                    if parent.text.endswith(' '):
                        parent.text = (parent.text or '') + '' + el.text
                    else:
                        parent.text = (parent.text or '') + ' ' + el.text
            else:
                if previous.tail:
                    if previous.tail.endswith(' '):
                        previous.tail = (previous.tail or '') + '' + el.text
                    else:
                        previous.tail = (previous.tail or '') + ' ' + el.text
        # Append the tail to last child tail, or previous tail, or parent text, ensuring newline if block level
        if el.tail:
            if len(el):
                last = el[-1]
                last.tail = (last.tail or '') + el.tail
            elif previous is None:
                if el.tail.startswith(' '):
                    parent.text = (parent.text or '') + '' + el.tail
                else:
                    parent.text = (parent.text or '') + ' ' + el.tail
            else:
                if el.tail.startswith(' '):
                    previous.tail = (previous.tail or '') + '' + el.tail
                else:
                    previous.tail = (previous.tail or '') + ' ' + el.tail

        index = parent.index(el)
        parent[index:index + 1] = el[:]
    return document


def els_xml_whitespace(document):
    """ Remove whitespace in xml.text or xml.tails for all elements, if it is only whitespace """
    # selects all tags and checks if the text or tail are spaces
    for el in document.xpath('//*'):
        if str(el.text).isspace():
            el.text = ''
        if str(el.tail).isspace():
            el.tail = ''
    return document


class ElsevierXmlReader(XmlReader):
    """Reader for Elsevier XML documents."""

    cleaners = [clean, fix_elsevier_xml_whitespace, els_xml_whitespace, strip_els_xml]

    etree.FunctionNamespace("http://www.elsevier.com/xml/svapi/article/dtd").prefix = 'default'
    etree.FunctionNamespace("http://www.elsevier.com/xml/bk/dtd").prefix = 'bk'
    etree.FunctionNamespace("http://www.elsevier.com/xml/common/cals/dtd").prefix = 'cals'
    etree.FunctionNamespace("http://www.elsevier.com/xml/common/dtd").prefix = 'ce'
    etree.FunctionNamespace("http://www.elsevier.com/xml/ja/dtd").prefix = 'ja'
    etree.FunctionNamespace("http://www.w3.org/1998/Math/MathML").prefix = 'mml'
    etree.FunctionNamespace("http://www.elsevier.com/xml/common/struct-aff/dtd").prefix = 'sa'
    etree.FunctionNamespace("http://www.elsevier.com/xml/common/struct-bib/dtd").prefix = 'sb'
    etree.FunctionNamespace("http://www.elsevier.com/xml/common/table/dtd").prefix = 'tb'
    etree.FunctionNamespace("http://www.w3.org/1999/xlink").prefix = 'xlink'
    etree.FunctionNamespace("http://www.elsevier.com/xml/xocs/dtd").prefix = 'xocs'
    etree.FunctionNamespace("http://purl.org/dc/elements/1.1/").prefix = 'dc'
    etree.FunctionNamespace("http://purl.org/dc/terms/").prefix = 'dcterms'
    etree.FunctionNamespace("http://prismstandard.org/namespaces/basic/2.0/").prefix = 'prism'
    etree.FunctionNamespace("http://www.w3.org/2001/XMLSchema-instance").prefix = 'xsi'

    root_css = 'default|full-text-retrieval-response'
    title_css = 'dc|title'
    heading_css = 'ce|section-title'
    table_css = 'ce|table'
    metadata_css = 'xocs|meta'
    metadata_title_css = 'xocs|normalized-article-title'
    metadata_author_css = 'xocs|normalized-first-auth-surname'
    metadata_journal_css = 'xocs|srctitle'
    metadata_volume_css = 'xocs|vol-first, xocs|volume-list xocs|volume'
    metadata_issue_css = 'xocs|issns xocs|issn-primary-formatted'
    metadata_publisher_css = 'xocs|copyright-line'
    metadata_date_css = 'xocs|available-online-date, xocs|orig-load-date'
    metadata_firstpage_css = 'xocs|first-fp'
    metadata_lastpage_css = 'xocs|last-lp'
    metadata_doi_css = 'xocs|doi, xocs|eii'
    metadata_pii_css = 'xocs|pii-unformatted'
    table_caption_css = 'ce|table ce|caption'
    table_head_row_css = 'cals|thead cals|row'
    table_body_row_css = 'cals|tbody cals|row'
    table_cell_css = 'ce|entry'
    table_footnote_css = 'table-wrap-foot p'
    figure_css = 'ce|figure'
    figure_caption_css = 'ce|figure ce|caption'
    figure_label_css = 'ce|figure ce|label'
    reference_css = 'ce|cross-refs'
    citation_css = 'ce|bib-reference'
    ignore_css = 'ce|bibliography, ce|acknowledgment, ce|correspondence, ce|author, ce|doi, ja|jid, ja|aid, ce|pii, xocs|oa-sponsor-type, xocs|open-access, default|openaccess,'\
                 'default|openaccessArticle, dc|format, dc|creator, dc|identifier,'\
                'default|eid, default|pii, xocs|meta, xocs|ref-info, default|scopus-eid,'\
                 'xocs|normalized-srctitle,' \
                 'xocs|eid, xocs|hub-eid, xocs|normalized-first-auth-surname,' \
                 'xocs|normalized-first-auth-initial, xocs|refkeys,' \
                 'xocs|attachment-eid, xocs|attachment-type,' \
                 'ja|jid, ce|given-name, ce|surname, ce|affiliation, ce|cross-refs, ce|cross-ref,' \
                 'ce|grant-sponsor, ce|grant-number, prism|copyright,' \
                 'xocs|pii-unformatted, xocs|ucs-locator, ce|copyright,' \
                 'prism|publisher, prism|*, xocs|copyright-line, xocs|cp-notice,' \
                 'dc|description'

    url_prefix = 'https://sciencedirect.com/science/article/pii/'

    def detect(self, fstring, fname=None):
        """Elsevier document detection based on string found in xml"""
        if fname and not fname.endswith('.xml'):
            return False
        if b'xmlns="http://www.elsevier.com/xml/svapi/article/dtd"' in fstring:
            return True
        return False

    def _parse_metadata(self, el, refs, specials):
        title = self._css(self.metadata_title_css, el)
        authors = self._css(self.metadata_author_css, el)
        publisher = self._css(self.metadata_publisher_css, el)
        journal = self._css(self.metadata_journal_css, el)
        date = self._css(self.metadata_date_css, el)
        language = self._css(self.metadata_language_css, el)
        volume = self._css(self.metadata_volume_css, el)
        issue = self._css(self.metadata_issue_css, el)
        firstpage =self._css(self.metadata_firstpage_css, el)
        lastpage=self._css(self.metadata_lastpage_css, el)
        doi = self._css(self.metadata_doi_css, el)
        pdf_url = self._css(self.metadata_pdf_url_css, el)
        html_url = self._css(self.metadata_html_url_css, el)

        metadata = {
                '_title': title[0].text if title else None,
                '_authors': [i.text for i in authors] if authors else None,
                '_publisher': publisher[0].text if publisher else None,
                '_journal': journal[0].text if journal else None,
                '_date': date[0].text if date else None,
                '_language': language[0].text if language else None,
                '_volume': volume[0].text if volume else None,
                '_issue': issue[0].text if issue else None,
                '_firstpage': firstpage[0].text if firstpage else None,
                '_lastpage': lastpage[0].text if lastpage else None,
                '_doi': doi[0].text if doi else None,
                '_pdf_url': self.url_prefix + pdf_url[0].text if pdf_url else None,
                '_html_url': self.url_prefix + html_url[0].text if html_url else None
                }
        meta = MetaData(metadata)
        return [meta]
