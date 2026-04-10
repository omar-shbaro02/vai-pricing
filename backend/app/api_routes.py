from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from .data_loader import load_sku_records, resolve_dataset_path
from .decision_engine import generate_recommendation
from .llm_pricing_agent import LLMPricingAgent
from .pricing_engine import build_list_item, calculate_margin, calculate_price_gap, calculate_reference_price
from .schemas import (
    AgentReviewAction,
    AgentReviewResponse,
    AgentReviewSelectedSKU,
    DashboardResponse,
    DecisionUpdate,
    RecommendationRecord,
    RunAgentResponse,
    SKUChatRequest,
    SKUChatResponse,
    SKUDetailResponse,
    SKUListItem,
    SimulateRequest,
    SimulationResponse,
)
from .simulation import simulate_price_change, summarize_simulation
from .sku_chat import answer_sku_question
from .vector_store import VectorStore


router = APIRouter(prefix="/api")


class PricingState:
    def __init__(self) -> None:
        self.vector_store = VectorStore(Path(__file__).resolve().parents[1] / "chroma")
        self.llm_agent = LLMPricingAgent()
        self.dataset_path: Path | None = None
        self.dataset_mtime_ns: int | None = None
        self.records = []
        self.record_index = {}
        self.base_recommendations = {}
        self.decision_overrides: dict[str, DecisionUpdate] = {}
        self.refresh(force=True)

    def refresh(self, force: bool = False) -> None:
        dataset_path = resolve_dataset_path()
        dataset_mtime_ns = dataset_path.stat().st_mtime_ns

        if not force and self.dataset_path == dataset_path and self.dataset_mtime_ns == dataset_mtime_ns:
            return

        records = load_sku_records(dataset_path)
        recommendations = {record.sku: generate_recommendation(record) for record in records}

        self.dataset_path = dataset_path
        self.dataset_mtime_ns = dataset_mtime_ns
        self.records = records
        self.record_index = {record.sku: record for record in records}
        self.base_recommendations = recommendations
        self.decision_overrides = {
            sku: override for sku, override in self.decision_overrides.items() if sku in self.record_index
        }
        self.vector_store.seed_skus(records)
        self.vector_store.upsert_recommendations(
            [self.get_recommendation(record.sku) for record in records]
        )

    def get_recommendation(self, sku: str) -> RecommendationRecord:
        override = self.decision_overrides.get(sku)
        if override is None:
            return self.base_recommendations[sku]

        return RecommendationRecord(
            sku=override.sku,
            suggested_price=override.suggested_price,
            reason=override.rationale,
            confidence=0.95,
            timestamp=override.applied_at,
        )

    def apply_decision_override(
        self,
        *,
        sku: str,
        recommendation: str,
        suggested_price: float,
        rationale: str,
        next_steps: list[str] | None = None,
    ) -> DecisionUpdate:
        record = self.record_index[sku]
        base = self.base_recommendations[sku]
        if recommendation == "hold":
            suggested_price = record.tawfeer_price

        override = DecisionUpdate(
            sku=sku,
            recommendation=recommendation,
            suggested_price=round(float(suggested_price), 2),
            rationale=rationale.strip(),
            next_steps=next_steps or [
                f"Review the override from ${record.tawfeer_price:.2f} to ${round(float(suggested_price), 2):.2f}.",
                "Validate the change against category and commercial priorities.",
            ],
            applied_at=datetime.now(UTC),
        )
        self.decision_overrides[sku] = override
        self.vector_store.upsert_recommendations([self.get_recommendation(sku)])
        return override


state = PricingState()


def _state() -> PricingState:
    state.refresh()
    return state


def _recommendation_direction(pricing_state: PricingState, record_sku: str, current_price: float) -> str:
    suggested_price = pricing_state.get_recommendation(record_sku).suggested_price
    if suggested_price > current_price:
        return "increase"
    if suggested_price < current_price:
        return "decrease"
    return "hold"


def _resolved_stock_cover(record) -> float | None:
    if record.stock_cover is not None:
        return record.stock_cover
    if record.units_sold_last_week <= 0:
        return None
    return round(record.inventory_level / record.units_sold_last_week, 2)


def _build_item(pricing_state: PricingState, record) -> SKUListItem:
    recommendation_record = pricing_state.get_recommendation(record.sku)
    direction = _recommendation_direction(pricing_state, record.sku, record.tawfeer_price)
    explainer = _build_sku_explainer(record, direction, recommendation_record)
    return build_list_item(
        record,
        recommendation=direction,
        suggested_price=recommendation_record.suggested_price,
        confidence=recommendation_record.confidence,
        ai_explainer=explainer,
    )


def _build_sku_explainer(record, direction: str, recommendation_record) -> str:
    reference_price = calculate_reference_price(record)
    price_gap = calculate_price_gap(record, reference_price)
    current_margin = calculate_margin(record) * 100
    margin_floor = record.margin_floor * 100
    inventory_note = record.inventory_interpretation or "Inventory is stable"
    reason = recommendation_record.reason.rstrip(".")

    if direction == "increase":
        return (
            f"Increase toward ${recommendation_record.suggested_price:.2f} because {reason}. "
            f"Current margin is {current_margin:.2f}% versus a {margin_floor:.2f}% floor. {inventory_note}."
        )
    if direction == "decrease":
        return (
            f"Decrease toward ${recommendation_record.suggested_price:.2f} because {reason}. "
            f"This SKU is {abs(price_gap):.2f}% above the market reference at ${reference_price:.2f}. {inventory_note}."
        )
    return (
        f"Hold at ${record.tawfeer_price:.2f} because {reason}. "
        f"Margin is {current_margin:.2f}% against a {margin_floor:.2f}% floor, with market reference at ${reference_price:.2f}."
    )


def _apply_filters(
    items: list[SKUListItem],
    *,
    kvis_only: bool,
    increases_only: bool,
    decreases_only: bool,
    margin_violations_only: bool,
) -> list[SKUListItem]:
    filtered = items
    if kvis_only:
        filtered = [item for item in filtered if item.kvi_flag]
    if increases_only:
        filtered = [item for item in filtered if item.recommendation == "increase"]
    if decreases_only:
        filtered = [item for item in filtered if item.recommendation == "decrease"]
    if margin_violations_only:
        filtered = [item for item in filtered if item.margin_violation]
    return filtered


def _priority_for_item(item: SKUListItem) -> str:
    if item.margin_violation or abs(item.price_gap) >= 6:
        return "high"
    if item.recommendation != "hold" or abs(item.price_gap) >= 3:
        return "medium"
    return "low"


def _action_copy(item: SKUListItem, reason: str) -> str:
    if item.recommendation == "increase":
        return (
            f"Move from ${item.tawfeer_price:.2f} to ${item.suggested_price:.2f} to recover margin"
            if item.margin_violation
            else f"Test an increase toward ${item.suggested_price:.2f} while staying close to market"
        )
    if item.recommendation == "decrease":
        return f"Reduce to ${item.suggested_price:.2f} to close the market gap and protect traffic"
    return f"Hold at ${item.tawfeer_price:.2f}; current guardrails are acceptable"


def _portfolio_review(
    pricing_state: PricingState,
    items: list[SKUListItem],
) -> tuple[str, str, str, dict[str, int], list[AgentReviewAction]]:
    total = len(items)
    increases = sum(1 for item in items if item.recommendation == "increase")
    decreases = sum(1 for item in items if item.recommendation == "decrease")
    holds = total - increases - decreases
    violations = sum(1 for item in items if item.margin_violation)
    kvis = sum(1 for item in items if item.kvi_flag)
    large_gaps = sum(1 for item in items if abs(item.price_gap) >= 3)

    if total == 0:
        return (
            "No SKUs match the current filters.",
            "Clear or relax one or more filters to generate a pricing review.",
            "There is no execution recommendation until SKUs are visible.",
            {
                "total": 0,
                "increase": 0,
                "decrease": 0,
                "hold": 0,
                "margin_violations": 0,
                "kvis": 0,
            },
            [],
        )

    overview = (
        f"The current plan covers {total} SKUs: {decreases} need price decreases, "
        f"{increases} need increases, and {holds} can stay on hold."
    )
    portfolio_review = (
        f"{violations} SKUs are below margin floor, {large_gaps} are meaningfully off market, "
        f"and {kvis} KVIs require tighter price discipline."
    )
    execution_note = (
        "Prioritize high-severity items first, especially margin violations and KVIs priced above market."
    )

    ranked_items = sorted(
        items,
        key=lambda item: (
            0 if item.margin_violation else 1,
            0 if item.recommendation != "hold" else 1,
            -abs(item.price_gap),
            -item.confidence,
        ),
    )[:6]

    focus_actions = []
    for item in ranked_items:
        reason = pricing_state.get_recommendation(item.sku).reason
        focus_actions.append(
            AgentReviewAction(
                sku=item.sku,
                product_name=item.product_name,
                recommendation=item.recommendation,
                current_price=item.tawfeer_price,
                suggested_price=item.suggested_price,
                price_gap=item.price_gap,
                margin=item.margin,
                confidence=item.confidence,
                why=reason,
                action=_action_copy(item, reason),
                priority=_priority_for_item(item),
            )
        )

    return (
        overview,
        portfolio_review,
        execution_note,
        {
            "total": total,
            "increase": increases,
            "decrease": decreases,
            "hold": holds,
            "margin_violations": violations,
            "kvis": kvis,
        },
        focus_actions,
    )


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard() -> DashboardResponse:
    pricing_state = _state()
    items = [_build_item(pricing_state, record) for record in pricing_state.records]

    flagged = [
        item
        for item in items
        if item.recommendation != "hold" or item.margin_violation or abs(item.price_gap) >= 3
    ]
    overpriced_count = sum(1 for item in items if item.price_gap > 0)
    avg_margin = sum(item.margin for item in items) / len(items)
    kvi_items = [item for item in items if item.kvi_flag]
    kvi_compliance = 100.0
    if kvi_items:
        compliant = sum(1 for item in kvi_items if item.price_gap <= 2)
        kvi_compliance = round((compliant / len(kvi_items)) * 100, 2)

    return DashboardResponse(
        total_skus_analyzed=len(items),
        recommended_price_changes=sum(1 for item in items if item.recommendation != "hold"),
        overpriced_percentage=round((overpriced_count / len(items)) * 100, 2),
        average_margin=round(avg_margin, 2),
        kvi_compliance_score=kvi_compliance,
        flagged_skus=flagged[:5],
    )


@router.get("/skus", response_model=list[SKUListItem])
def get_skus(
    kvis_only: bool = Query(False),
    increases_only: bool = Query(False),
    decreases_only: bool = Query(False),
    margin_violations_only: bool = Query(False),
) -> list[SKUListItem]:
    pricing_state = _state()
    items = [_build_item(pricing_state, record) for record in pricing_state.records]
    return _apply_filters(
        items,
        kvis_only=kvis_only,
        increases_only=increases_only,
        decreases_only=decreases_only,
        margin_violations_only=margin_violations_only,
    )


@router.get("/agent-review", response_model=AgentReviewResponse)
def get_agent_review(
    sku_id: str | None = Query(None),
    kvis_only: bool = Query(False),
    increases_only: bool = Query(False),
    decreases_only: bool = Query(False),
    margin_violations_only: bool = Query(False),
) -> AgentReviewResponse:
    pricing_state = _state()
    items = [_build_item(pricing_state, record) for record in pricing_state.records]
    filtered_items = _apply_filters(
        items,
        kvis_only=kvis_only,
        increases_only=increases_only,
        decreases_only=decreases_only,
        margin_violations_only=margin_violations_only,
    )
    overview, portfolio_review, execution_note, totals, focus_actions = _portfolio_review(
        pricing_state,
        filtered_items,
    )

    selected_sku = None
    if sku_id is not None:
        record = pricing_state.record_index.get(sku_id)
        if not record:
            raise HTTPException(status_code=404, detail="SKU not found")
        item = next((candidate for candidate in items if candidate.sku == sku_id), None)
        if item is None:
            raise HTTPException(status_code=404, detail="SKU not found")

        recommendation = pricing_state.get_recommendation(sku_id)
        override = pricing_state.decision_overrides.get(sku_id)
        selected_sku = AgentReviewSelectedSKU(
          sku=item.sku,
          product_name=item.product_name,
          recommendation=item.recommendation,
          current_price=item.tawfeer_price,
          suggested_price=item.suggested_price,
          margin=item.margin,
          margin_floor=round(record.margin_floor * 100, 2),
          price_gap=item.price_gap,
          confidence=item.confidence,
          summary=item.ai_explainer,
          next_steps=override.next_steps if override else [
              _action_copy(item, recommendation.reason),
              f"Confidence is {(item.confidence * 100):.0f}%, so use this as the leading scenario for review.",
              recommendation.reason,
          ],
        )

    return AgentReviewResponse(
        overview=overview,
        portfolio_review=portfolio_review,
        execution_note=execution_note,
        totals=totals,
        focus_actions=focus_actions,
        selected_sku=selected_sku,
    )


@router.get("/skus/{sku_id}", response_model=SKUDetailResponse)
def get_sku_detail(sku_id: str) -> SKUDetailResponse:
    pricing_state = _state()
    record = pricing_state.record_index.get(sku_id)
    if not record:
        raise HTTPException(status_code=404, detail="SKU not found")

    recommendation_record = pricing_state.get_recommendation(sku_id)
    suggested_price = recommendation_record.suggested_price
    direction = _recommendation_direction(pricing_state, sku_id, record.tawfeer_price)

    explanation = pricing_state.vector_store.get_reason_context(sku_id, recommendation_record.reason)
    return SKUDetailResponse(
        sku=record.sku,
        product_name=record.product_name,
        category=record.category,
        pack_size=record.pack_size,
        current_price=round(record.tawfeer_price, 2),
        all_competitor_prices={
            "carrefour": record.carrefour_price,
            "spinneys": record.spinneys_price,
            "metromart": record.metromart_price,
        },
        reference_price=calculate_reference_price(record),
        price_gap=calculate_price_gap(record),
        margin=round(calculate_margin(record) * 100, 2),
        margin_floor=round(record.margin_floor * 100, 2),
        inventory=record.inventory_level,
        stock_cover=_resolved_stock_cover(record),
        inventory_interpretation=record.inventory_interpretation,
        units_sold_last_week=record.units_sold_last_week,
        recommendation=direction,
        suggested_price=suggested_price,
        confidence=recommendation_record.confidence,
        kvi_flag=record.kvi_flag,
        promo_flag=record.promo_flag,
        decision_explanation=explanation,
        simulation_impact=summarize_simulation(record, suggested_price),
    )


@router.post("/simulate", response_model=SimulationResponse)
def simulate(request: SimulateRequest) -> SimulationResponse:
    pricing_state = _state()
    record = pricing_state.record_index.get(request.sku)
    if not record:
        raise HTTPException(status_code=404, detail="SKU not found")
    return simulate_price_change(record, request.proposed_price)


@router.post("/skus/{sku_id}/chat", response_model=SKUChatResponse)
def chat_about_sku(sku_id: str, request: SKUChatRequest) -> SKUChatResponse:
    pricing_state = _state()
    record = pricing_state.record_index.get(sku_id)
    if not record:
        raise HTTPException(status_code=404, detail="SKU not found")

    recommendation = pricing_state.get_recommendation(sku_id)

    try:
        answer, response_id, decision_update = pricing_state.llm_agent.answer_question(
            record=record,
            recommendation=recommendation,
            question=request.question,
            previous_response_id=request.previous_response_id,
            pricing_state=pricing_state,
        )
        return SKUChatResponse(
            sku=sku_id,
            question=request.question,
            answer=answer,
            response_id=response_id,
            used_llm=True,
            decision_update=decision_update,
        )
    except RuntimeError as exc:
        answer = answer_sku_question(record, recommendation, request.question)
        return SKUChatResponse(
            sku=sku_id,
            question=request.question,
            answer=f"{answer}\n\nLLM pricing chat is not active: {exc}",
            used_llm=False,
        )


@router.post("/run-agent", response_model=RunAgentResponse)
def run_agent() -> RunAgentResponse:
    state.refresh(force=True)
    return RunAgentResponse(
        processed=len(state.records),
        updated_recommendations=len(state.base_recommendations),
        timestamp=datetime.now(UTC),
    )
