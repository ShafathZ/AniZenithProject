from typing import List

from backend.mongo.AniZenithVectorSearchResult import AniZenithVectorSearchResult


class AniZenithReranker:

    def __init__(self):
        pass

    def rerank(self, user_query: str, results: List[AniZenithVectorSearchResult], limit=5):
        # TODO: Add to this this framework
        return results