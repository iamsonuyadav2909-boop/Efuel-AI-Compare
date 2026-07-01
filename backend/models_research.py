"""
Pydantic schemas for the AI Research Engine (core workflow).
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid


class SourceRef(BaseModel):
    title: str = ''
    url: str = ''
    domain: str = ''
    trust_score: float = 0.0


class SpecItem(BaseModel):
    name: str
    value: str
    unit: Optional[str] = ''


class ScoreBreakdown(BaseModel):
    technical_quality: float = 0
    reliability: float = 0
    brand_reputation: float = 0
    industrial_usage: float = 0
    warranty: float = 0
    certification: float = 0
    performance: float = 0
    availability: float = 0
    compatibility: float = 0


class ProductResult(BaseModel):
    rank: int
    name: str
    brand: str
    engineering_score: float = 0
    score_breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    specifications: List[SpecItem] = Field(default_factory=list)
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    engineering_notes: str = ''
    compatibility: List[str] = Field(default_factory=list)
    industrial_applications: List[str] = Field(default_factory=list)
    alternatives: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    source_urls: List[str] = Field(default_factory=list)
    image_url: Optional[str] = None
    ai_recommendation: str = ''
    estimated_price_range: str = ''


class ResearchResult(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str
    category: str = ''
    summary: str = ''
    products: List[ProductResult] = Field(default_factory=list)
    top_recommendation: str = ''
    best_value: str = ''
    confidence: float = 0.0
    data_source_mode: str = 'no_data'  # 'live_search' (only successful mode) | 'no_data'
    no_data: bool = False
    message: str = ''  # populated ONLY when no_data=True with the exact strict error string
    search_provider_used: str = ''  # 'exa' | 'tavily' | ''
    last_crawl_time: Optional[str] = None
    sources: List[SourceRef] = Field(default_factory=list)
    query_hash: str = ''
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=200)
    force_refresh: bool = False
