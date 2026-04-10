from __future__ import annotations

from statistics import mean

from .schemas import SKUListItem, SKURecord


def calculate_reference_price(record: SKURecord) -> float:
    if record.kvi_flag and record.lowest_market_price is not None and record.lowest_market_price > 0:
        return round(record.lowest_market_price, 2)

    if record.average_market_price is not None and record.average_market_price > 0:
        return round(record.average_market_price, 2)

    prices = [record.carrefour_price, record.spinneys_price, record.metromart_price]
    valid_prices = [price for price in prices if price > 0]
    if not valid_prices:
        return round(record.tawfeer_price, 2)
    return round(mean(valid_prices), 2)


def calculate_margin(record: SKURecord, price: float | None = None) -> float:
    effective_price = price if price is not None else record.tawfeer_price
    if effective_price == 0:
        return 0.0
    return round((effective_price - record.cost) / effective_price, 4)


def calculate_price_gap(record: SKURecord, reference_price: float | None = None) -> float:
    ref_price = reference_price if reference_price is not None else calculate_reference_price(record)
    if ref_price == 0:
        return 0.0
    return round(((record.tawfeer_price - ref_price) / ref_price) * 100, 2)


def build_list_item(
    record: SKURecord,
    recommendation: str,
    suggested_price: float,
    confidence: float,
    ai_explainer: str,
) -> SKUListItem:
    reference_price = calculate_reference_price(record)
    margin = calculate_margin(record)
    margin_violation = margin < record.margin_floor
    return SKUListItem(
        sku=record.sku,
        product_name=record.product_name,
        tawfeer_price=round(record.tawfeer_price, 2),
        reference_price=reference_price,
        price_gap=calculate_price_gap(record, reference_price),
        margin=round(margin * 100, 2),
        recommendation=recommendation,
        suggested_price=round(suggested_price, 2),
        confidence=round(confidence, 2),
        kvi_flag=record.kvi_flag,
        margin_violation=margin_violation,
        ai_explainer=ai_explainer,
    )
