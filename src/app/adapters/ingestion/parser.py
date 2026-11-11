import xml.etree.ElementTree as ET
from src.app.models.domain import Document

def parser_pubmed(pmids) -> list[Document]:
    """Parsing function for PubMed API articles."""
    root = ET.fromstring(pmids)
    source = "PubMed"
    documents = []

    for article in root.findall(".//PubmedArticle"):

        pmid = article.findtext(".//MedlineCitation/PMID")

        title_element = article.find(".//ArticleTitle")
        title = "".join(title_element.itertext()).strip() if title_element is not None else ""

        abstract = "\n".join(
            "".join(el.itertext()).strip()
            for el in article.findall(".//AbstractText")
        )

        authors = [
            f"{a.findtext('ForeName', '')} {a.findtext('LastName', '')}".strip()
            for a in article.findall(".//AuthorList/Author")
        ]

        journal = article.findtext(".//Journal/Title", "")

        year = article.findtext(".//PubDate/Year")
        publication_year = int(year) if year else None

        doi = article.findtext(".//ArticleId[@IdType='doi']")

        documents.append(
                Document(
                    pmid=pmid,
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    journal=journal,
                    publication_year=publication_year,
                    doi=doi,
                    source=source
                )
        )
    return documents