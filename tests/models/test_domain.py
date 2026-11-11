from src.app.models.domain import Document

def test_Document():
    document = Document(
        pmid = "40159341",
        title = "Cardiac Arrest During Long-Distance Running Races.",
        abstract = "More than 29 million participants completed marathons and half-marathons in the US between 2010-2023",
        authors = ["Jonathan H Kim"],
        journal = "JAMA",
        publication_year = 2025,
        doi = "10.1001/jama.2025.3026",
        source = "PubMed"
    )

    assert document.pmid == "40159341"
    assert document.title == "Cardiac Arrest During Long-Distance Running Races."
    assert document.abstract == "More than 29 million participants completed marathons and half-marathons in the US between 2010-2023"
    assert document.authors == ["Jonathan H Kim"]
    assert document.journal == "JAMA"
    assert document.publication_year == 2025
    assert document.doi == "10.1001/jama.2025.3026"
    assert document.source == "PubMed"
    