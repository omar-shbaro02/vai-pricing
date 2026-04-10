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
        return (
            f"The strategy is `{direction}` because {recommendation.reason}. "
            f"Current price is ${record.tawfeer_price:.2f}, the suggested price is ${recommendation.suggested_price:.2f}, "
            f"and confidence is {recommendation.confidence * 100:.0f}%."
        )

    if any(term in normalized for term in ["margin", "gm", "profit", "floor"]):
        return (
            f"Current margin is {current_margin:.2f}% and the configured floor is {margin_floor:.2f}%. "
            f"At the suggested price of ${recommendation.suggested_price:.2f}, the projected margin is "
            f"{simulation['projected_margin_percent']:.2f}%."
        )

    if any(term in normalized for term in ["market", "competitor", "benchmark", "gap", "reference"]):
        return (
            f"The market reference price is ${reference_price:.2f}. "
            f"Tawfeer is currently {price_gap:.2f}% {'above' if price_gap >= 0 else 'below'} that reference. "
            f"Competitor prices are Carrefour ${record.carrefour_price:.2f}, Spinneys ${record.spinneys_price:.2f}, "
            f"and MetroMart ${record.metromart_price:.2f}."
        )

    if any(term in normalized for term in ["inventory", "stock", "cover", "units sold", "demand", "volume"]):
        stock_cover = record.stock_cover if record.stock_cover is not None else (
            record.inventory_level / max(record.units_sold_last_week, 1)
        )
        return (
            f"Inventory level is {record.inventory_level}, units sold last week were {record.units_sold_last_week}, "
            f"and stock cover is {stock_cover:.2f}. "
            f"Inventory interpretation is: {record.inventory_interpretation or 'No special inventory note'}."
        )

    if any(term in normalized for term in ["simulate", "impact", "if", "change price", "new price", "suggested price"]):
        return (
            f"Using the suggested price of ${recommendation.suggested_price:.2f}, the current simulation projects "
            f"{simulation['expected_volume_change']:.2f}% volume change, "
            f"${simulation['expected_revenue_impact']:.2f} revenue impact, and "
            f"${simulation['expected_margin_impact']:.2f} margin impact."
        )

    if any(term in normalized for term in ["increase", "decrease", "hold", "recommendation", "action", "next step"]):
        return (
            f"The current recommendation is to `{direction}`. "
            f"Move from ${record.tawfeer_price:.2f} to ${recommendation.suggested_price:.2f}. "
            f"The main driver is: {recommendation.reason}."
        )

    return (
        f"For {record.product_name} ({record.sku}), the recommended action is to `{direction}` from "
        f"${record.tawfeer_price:.2f} to ${recommendation.suggested_price:.2f}. "
        f"This is based on margin, market position, and inventory context. "
        f"You can ask about margin, competitors, inventory, simulation impact, or why this strategy was chosen."
    )


def _recommendation_direction(current_price: float, suggested_price: float) -> str:
    if suggested_price > current_price:
        return "increase"
    if suggested_price < current_price:
        return "decrease"
    return "hold"
