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


# ---- Admin: Brands ----

class BrandCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    website: str = ''
    logo_url: str = ''


class BrandUpdate(BaseModel):
    website: Optional[str] = None
    logo_url: Optional[str] = None


# ---- Admin: Products ----

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=160)
    brand: str = Field(..., min_length=1, max_length=120)
    category: str = ''
    specifications: List[dict] = Field(default_factory=list)
    estimated_price_range: str = ''
    engineering_notes: str = ''


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    estimated_price_range: Optional[str] = None
    engineering_notes: Optional[str] = None


# ---- Admin: Documents ----

class DocumentMetadataUpdate(BaseModel):
    title: Optional[str] = None
    doc_type: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    product_name: Optional[str] = None
    product_id: Optional[str] = None


# ---- Admin: API Integrations ----

class IntegrationKeyUpdate(BaseModel):
    api_key: str = Field(..., min_length=3)
    enabled: bool = True


class IntegrationToggle(BaseModel):
    enabled: bool


# ---- Admin: System Settings ----

class SystemSettingsUpdate(BaseModel):
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    research_rate_limit_per_min: Optional[int] = None
