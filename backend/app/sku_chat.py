from __future__ import annotations

from .pricing_engine import calculate_margin, calculate_price_gap, calculate_reference_price
from .schemas import RecommendationRecord, SKURecord
from .simulation import summarize_simulation


def answer_sku_question(record: SKURecord, recommendation: RecommendationRecord, question: str) -> str:
    normalized = " ".join(question.lower().split())
    reference_price = calculate_reference_price(record)
    current_margin = calculate_margin(record) * 100
    margin_floor = record.margin_floor * 100
    price_gap = calculate_price_gap(record, reference_price)
    direction = _recommendation_direction(record.tawfeer_price, recommendation.suggested_price)
    simulation = summarize_simulation(record, recommendation.suggested_price)

    if any(term in normalized for term in ["why", "reason", "rationale", "explain", "obtained"]):
        return _format_bullets(
            [
                f"Strategy: `{direction}`.",
                f"Why: {recommendation.reason}.",
                f"Current price: ${record.tawfeer_price:.2f}.",
                f"Suggested price: ${recommendation.suggested_price:.2f}.",
                f"Confidence: {recommendation.confidence * 100:.0f}%.",
            ]
        )

    if any(term in normalized for term in ["margin", "gm", "profit", "floor"]):
        return _format_bullets(
            [
                f"Current margin: {current_margin:.2f}%.",
                f"Margin floor: {margin_floor:.2f}%.",
                f"Projected margin at ${recommendation.suggested_price:.2f}: {simulation['projected_margin_percent']:.2f}%.",
            ]
        )

    if any(term in normalized for term in ["market", "competitor", "benchmark", "gap", "reference"]):
        return _format_bullets(
            [
                f"Market reference price: ${reference_price:.2f}.",
                f"Tawfeer is {abs(price_gap):.2f}% {'above' if price_gap >= 0 else 'below'} the market reference.",
                f"Carrefour price: ${record.carrefour_price:.2f}.",
                f"Spinneys price: ${record.spinneys_price:.2f}.",
                f"MetroMart price: ${record.metromart_price:.2f}.",
            ]
        )

    if any(term in normalized for term in ["inventory", "stock", "cover", "units sold", "demand", "volume"]):
        stock_cover = record.stock_cover if record.stock_cover is not None else (
            record.inventory_level / max(record.units_sold_last_week, 1)
        )
        return _format_bullets(
            [
                f"Inventory level: {record.inventory_level}.",
                f"Units sold last week: {record.units_sold_last_week}.",
                f"Stock cover: {stock_cover:.2f}.",
                f"Inventory interpretation: {record.inventory_interpretation or 'No special inventory note'}.",
            ]
        )

    if any(term in normalized for term in ["simulate", "impact", "if", "change price", "new price", "suggested price"]):
        return _format_bullets(
            [
                f"Simulation price: ${recommendation.suggested_price:.2f}.",
                f"Expected volume change: {simulation['expected_volume_change']:.2f}%.",
                f"Expected revenue impact: ${simulation['expected_revenue_impact']:.2f}.",
                f"Expected margin impact: ${simulation['expected_margin_impact']:.2f}.",
            ]
        )

    if any(term in normalized for term in ["increase", "decrease", "hold", "recommendation", "action", "next step"]):
        return _format_bullets(
            [
                f"Recommendation: `{direction}`.",
                f"Move from ${record.tawfeer_price:.2f} to ${recommendation.suggested_price:.2f}.",
                f"Main driver: {recommendation.reason}.",
            ]
        )

    return _format_bullets(
        [
            f"SKU: {record.product_name} ({record.sku}).",
            f"Recommended action: `{direction}` from ${record.tawfeer_price:.2f} to ${recommendation.suggested_price:.2f}.",
            "Decision basis: margin, market position, and inventory context.",
            "You can ask about margin, competitors, inventory, simulation impact, or why this strategy was chosen.",
        ]
    )


def _recommendation_direction(current_price: float, suggested_price: float) -> str:
    if suggested_price > current_price:
        return "increase"
    if suggested_price < current_price:
        return "decrease"
    return "hold"


def _format_bullets(items: list[str]) -> str:
    cleaned = [item.strip() for item in items if item and item.strip()]
    return "\n".join(f"- {item}" for item in cleaned)
