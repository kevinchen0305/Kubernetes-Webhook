from pydantic import BaseModel
from typing import Any

class Patch(BaseModel):
    op: str
    path: str
    value: Any
