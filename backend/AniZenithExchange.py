from pydantic import BaseModel
from typing import List, Dict

# Class to Model a typical AniZenith Request
class AniZenithRequest(BaseModel):
    messages: List[Dict[str, str]]
    use_local: bool


# Class to Model a typical AniZenith Response
class AniZenithResponse(BaseModel):
    messages: List[Dict[str, str]]