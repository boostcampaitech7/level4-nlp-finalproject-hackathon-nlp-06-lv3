from typing import TypedDict


class SimilarityEntry(TypedDict):
    mail_id: str
    similarity_score: float


class SimilarityDict(TypedDict):
    """
    {
        메일 ID: [
            (Top 1 메일 ID, 유사도),
            ...
        ],
        ...
    }
    """

    mail_id: list[SimilarityEntry]
