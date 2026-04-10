from __future__ import annotations

import math

from .pricing_engine import calculate_margin, calculate_reference_price
from .schemas import SKURecord, SimulationResponse


def estimate_demand_elasticity(record: SKURecord, proposed_price: float) -> float:
    price_gap = _projected_price_gap(record, proposed_price)
    stock_cover = record.stock_cover if record.stock_cover is not None else (
        record.inventory_level / max(record.units_sold_last_week, 1)
    )
    inventory_note = (record.inventory_interpretation or "").lower()

    elasticity = -1.1 if record.kvi_flag else -0.75

    if record.promo_flag:
        elasticity -= 0.15

    if stock_cover < 1.2 or "understock" in inventory_note:
        elasticity += 0.18
    elif stock_cover > 3 or "overstock" in inventory_note or "high stock" in inventory_note:
        elasticity -= 0.12

    if proposed_price > record.tawfeer_price and price_gap > 3:
        elasticity -= 0.2
    elif proposed_price < record.tawfeer_price and price_gap > 5:
        elasticity += 0.1

    if record.source_pricing_flag:
        source_flag = record.source_pricing_flag.lower()
        if "too expensive" in source_flag or "overpriced" in source_flag:
            elasticity -= 0.15
        elif "too cheap" in source_flag or "underpriced" in source_flag:
            elasticity += 0.08

    return round(min(max(elasticity, -2.0), -0.3), 2)


def simulate_price_change(record: SKURecord, proposed_price: float) -> SimulationResponse:
    current_price = record.tawfeer_price
    price_delta_pct = _price_delta_pct(current_price, proposed_price)

    demand_elasticity = estimate_demand_elasticity(record, proposed_price)
    expected_volume_change = round(price_delta_pct * demand_elasticity * 100, 2)
    expected_volume_change = max(min(expected_volume_change, 60.0), -60.0)

    current_units = float(record.units_sold_last_week)
    projected_units = max(current_units * (1 + (expected_volume_change / 100)), 0.0)

    current_revenue = current_units * current_price
    projected_revenue = projected_units * proposed_price
    expected_revenue_impact = round(projected_revenue - current_revenue, 2)

    current_margin_value = current_units * (current_price - record.cost)
    projected_margin_value = projected_units * (proposed_price - record.cost)
    expected_margin_impact = round(projected_margin_value - current_margin_value, 2)

    return SimulationResponse(
        sku=record.sku,
        current_price=round(current_price, 2),
        proposed_price=round(proposed_price, 2),
        expected_volume_change=expected_volume_change,
        expected_units_sold=float(math.ceil(projected_units)),
        expected_revenue_impact=expected_revenue_impact,
        expected_margin_impact=expected_margin_impact,
        projected_margin_percent=round(calculate_margin(record, proposed_price) * 100, 2),
    )


def summarize_simulation(record: SKURecord, proposed_price: float) -> dict[str, float]:
    result = simulate_price_change(record, proposed_price)
    return {
        "expected_volume_change": result.expected_volume_change,
        "expected_units_sold": result.expected_units_sold,
        "expected_revenue_impact": result.expected_revenue_impact,
        "expected_margin_impact": result.expected_margin_impact,
        "projected_margin_percent": round(calculate_margin(record, proposed_price) * 100, 2),
        "projected_price_gap": round(_projected_price_gap(record, proposed_price), 2),
        "demand_elasticity": estimate_demand_elasticity(record, proposed_price),
    }


def _projected_price_gap(record: SKURecord, proposed_price: float) -> float:
    reference_price = calculate_reference_price(record)
    if reference_price <= 0:
        return 0.0
    return ((proposed_price - reference_price) / reference_price) * 100


def _price_delta_pct(current_price: float, proposed_price: float) -> float:
    if current_price <= 0:
        return 0.0
    return (proposed_price - current_price) / current_price
