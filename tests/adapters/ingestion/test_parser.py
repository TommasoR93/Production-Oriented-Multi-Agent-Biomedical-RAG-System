from src.app.adapters.ingestion.parser import parser_pubmed

def test_parser_pubmed():
    pmids = """<?xml version="1.0" encoding="UTF-8"?>
<PubmedArticleSet>
    <PubmedArticle>
        <MedlineCitation>
            <PMID>12345678</PMID>
            <Article>
                <Journal>
                    <Title>Nature Medicine</Title>
                    <JournalIssue>
                        <PubDate>
                            <Year>2024</Year>
                        </PubDate>
                    </JournalIssue>
                </Journal>
                <ArticleTitle>Test Article</ArticleTitle>
                <Abstract>
                    <AbstractText>This is a test abstract.</AbstractText>
                </Abstract>
                <AuthorList>
                    <Author>
                        <ForeName>John</ForeName>
                        <LastName>Doe</LastName>
                    </Author>
                </AuthorList>
            </Article>
        </MedlineCitation>
        <PubmedData>
            <ArticleIdList>
                <ArticleId IdType="doi">10.1000/test123</ArticleId>
            </ArticleIdList>
        </PubmedData>
    </PubmedArticle>
</PubmedArticleSet>
"""
    document_test = parser_pubmed(pmids)
    assert document_test[0].pmid == "12345678"
    assert document_test[0].title == "Test Article"
    assert document_test[0].abstract == "This is a test abstract."
    assert document_test[0].authors == ["John Doe"]
    assert document_test[0].journal == "Nature Medicine"
    assert document_test[0].publication_year == 2024
    assert document_test[0].doi == "10.1000/test123"
    assert document_test[0].source == "PubMed"