from pydantic import BaseModel, Field

class Document(BaseModel):
    pmid: str = Field(description="Unique ID PubMed identifier of the article")
    title: str = Field(description="Title of the scientific article")
    abstract: str = Field(description="Abstract describing the studies and its findinds")
    authors: list[str] = Field(description="List of authors of the article")
    journal: str = Field(description="Name of the journal in which the article was published")
    publication_year: int | None = Field(description="Year when the article was published")
    doi: str | None = Field(description="Digital object identifier of the article")
    source: str = Field(description="Source of the article")