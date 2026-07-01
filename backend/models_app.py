"""
Pydantic schemas for application features: Favorites, Documents, BOM, Chat, Compare.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class FavoriteCreate(BaseModel):
    product_name: str
    brand: str
    category: str = ''
    engineering_score: float = 0
    query: str = ''


class DocumentCreate(BaseModel):
    title: str
    url: str
    doc_type: str = 'reference'  # datasheet | catalogue | manual | certificate | reference
    category: str = ''
    brand: str = ''
    product_name: str = ''


class BOMGenerateRequest(BaseModel):
    project_name: str = Field(..., min_length=2, max_length=120)
    requirement: str = Field(..., min_length=3, max_length=300)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None


class CompareRequest(BaseModel):
    products: List[dict] = Field(..., min_length=2, max_length=4)
    query_category: str = ''
