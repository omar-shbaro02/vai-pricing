from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SKURecord(BaseModel):
    sku: str
    product_name: str
    category: str
    subcategory: str = ""
    brand: str = ""
    pack_size: str
    tawfeer_price: float = Field(ge=0)
    cost: float = Field(ge=0)
    margin_floor: float = Field(ge=0, le=1)
    kvi_flag: bool
    promo_flag: bool
    carrefour_price: float = Field(ge=0)
    spinneys_price: float = Field(ge=0)
    metromart_price: float = Field(ge=0)
    units_sold_last_week: int = Field(ge=0)
    inventory_level: int = Field(ge=0)
    store_count: int = Field(ge=1)
    last_price_change_date: str
    lowest_market_price: float | None = None
    average_market_price: float | None = None
    stock_cover: float | None = None
    inventory_interpretation: str = ""
    source_margin_flag: str = ""
    source_pricing_flag: str = ""
    source_recommended_action: str = ""
    source_recommended_price: float | None = None


class RecommendationRecord(BaseModel):
    sku: str
    suggested_price: float = Field(ge=0)
    reason: str = Field(min_length=10, max_length=500)
    confidence: float = Field(ge=0, le=1)
    timestamp: datetime


class DecisionUpdate(BaseModel):
    sku: str
    recommendation: Literal["increase", "decrease", "hold"]
    suggested_price: float = Field(ge=0)
    rationale: str = Field(min_length=5, max_length=1000)
    next_steps: list[str] = Field(default_factory=list)
    applied_at: datetime


class SKUListItem(BaseModel):
    sku: str
    product_name: str
    tawfeer_price: float
    reference_price: float
    price_gap: float
    margin: float
    recommendation: Literal["increase", "decrease", "hold"]
    suggested_price: float
    confidence: float
    kvi_flag: bool
    margin_violation: bool
    ai_explainer: str


class DashboardResponse(BaseModel):
    total_skus_analyzed: int
    recommended_price_changes: int
    overpriced_percentage: float
    average_margin: float
    kvi_compliance_score: float
    flagged_skus: list[SKUListItem]


class AgentReviewAction(BaseModel):
    sku: str
    product_name: str
    recommendation: Literal["increase", "decrease", "hold"]
    current_price: float
    suggested_price: float
    price_gap: float
    margin: float
    confidence: float
    why: str
    action: str
    priority: Literal["high", "medium", "low"]


class AgentReviewSelectedSKU(BaseModel):
    sku: str
    product_name: str
    recommendation: Literal["increase", "decrease", "hold"]
    current_price: float
    suggested_price: float
    margin: float
    margin_floor: float
    price_gap: float
    confidence: float
    summary: str
    next_steps: list[str]


class AgentReviewResponse(BaseModel):
    overview: str
    portfolio_review: str
    execution_note: str
    totals: dict[str, int]
    focus_actions: list[AgentReviewAction]
    selected_sku: AgentReviewSelectedSKU | None = None


class SKUDetailResponse(BaseModel):
    sku: str
    product_name: str
    category: str
    pack_size: str
    current_price: float
    all_competitor_prices: dict[str, float]
    reference_price: float
    price_gap: float
    margin: float
    margin_floor: float
    inventory: int
    stock_cover: float | None = None
    inventory_interpretation: str = ""
    units_sold_last_week: int
    recommendation: Literal["increase", "decrease", "hold"]
    suggested_price: float
    confidence: float
    kvi_flag: bool
    promo_flag: bool
    decision_explanation: str
    simulation_impact: dict[str, float]


class DashboardFlaggedResponse(BaseModel):
    items: list[SKUListItem]


class SimulateRequest(BaseModel):
    sku: str = Field(min_length=1, max_length=100)
    proposed_price: float = Field(gt=0, le=100000)


class SimulationResponse(BaseModel):
    sku: str
    current_price: float
    proposed_price: float
    expected_volume_change: float
    expected_units_sold: float
    expected_revenue_impact: float
    expected_margin_impact: float
    projected_margin_percent: float


class SKUChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    previous_response_id: str | None = None


class SKUChatResponse(BaseModel):
    sku: str
    question: str
    answer: str
    response_id: str | None = None
    used_llm: bool = False
    decision_update: DecisionUpdate | None = None


class RunAgentResponse(BaseModel):
    processed: int
    updated_recommendations: int
    timestamp: datetime
