from __future__ import annotations

from datetime import datetime, UTC

from .pricing_engine import calculate_margin, calculate_price_gap, calculate_reference_price
from .schemas import RecommendationRecord, SKURecord
from .simulation import summarize_simulation


def generate_recommendation(record: SKURecord) -> RecommendationRecord:
    reference_price = calculate_reference_price(record)
    current_margin = calculate_margin(record)
    current_price_gap = calculate_price_gap(record, reference_price)
    current_summary = summarize_simulation(record, record.tawfeer_price)
    stock_cover = record.stock_cover if record.stock_cover is not None else (
        record.inventory_level / max(record.units_sold_last_week, 1)
    )
    inventory_note = (record.inventory_interpretation or "").lower()

    min_allowed_price = max(record.cost / max(1 - record.margin_floor, 0.01), record.cost * 1.005)
    max_step_up = 1.08 if record.kvi_flag else 1.12
    max_step_down = 0.94 if record.kvi_flag else 0.88
    max_allowed_price = max(record.tawfeer_price * max_step_up, min_allowed_price)
    min_candidate_price = max(record.tawfeer_price * max_step_down, record.cost * 1.005)

    candidates = {
        round(record.tawfeer_price, 2),
        round(min_allowed_price, 2),
        round(max_allowed_price, 2),
        round(reference_price, 2),
        round(reference_price * 0.99, 2),
        round(reference_price * 1.01, 2),
    }

    if record.source_recommended_price is not None:
        candidates.add(round(record.source_recommended_price, 2))

    for pct in range(-8, 9):
        if pct == 0:
            continue
        candidates.add(round(record.tawfeer_price * (1 + (pct / 100)), 2))

    candidate_scores: list[tuple[float, float, dict[str, float]]] = []
    for candidate_price in sorted(candidates):
        if candidate_price <= 0:
            continue
        if candidate_price < min_candidate_price or candidate_price > max_allowed_price:
            continue
        summary = summarize_simulation(record, candidate_price)
        score = _score_candidate(
            record=record,
            candidate_price=candidate_price,
            summary=summary,
            stock_cover=stock_cover,
        )
        candidate_scores.append((score, round(candidate_price, 2), summary))

    best_score, best_price, best_summary = max(candidate_scores, key=lambda item: item[0], default=(0.0, record.tawfeer_price, current_summary))
    current_score = _score_candidate(
        record=record,
        candidate_price=record.tawfeer_price,
        summary=current_summary,
        stock_cover=stock_cover,
    )

    improvement = best_score - current_score
    price_move_pct = abs((best_price - record.tawfeer_price) / max(record.tawfeer_price, 0.01)) * 100
    acceptable_gap = 2.0 if record.kvi_flag else 5.0

    should_hold = improvement < 8 or price_move_pct < 0.75
    if (
        best_price > record.tawfeer_price
        and best_summary["expected_revenue_impact"] < 0
        and current_margin >= record.margin_floor
        and current_price_gap >= -acceptable_gap
    ):
        should_hold = True
    if (
        best_price < record.tawfeer_price
        and best_summary["expected_margin_impact"] < 0
        and current_price_gap <= acceptable_gap
    ):
        should_hold = True
    if current_margin < record.margin_floor and best_price <= record.tawfeer_price:
        should_hold = False
        best_price = max(best_price, round(min_allowed_price, 2))
        best_summary = summarize_simulation(record, best_price)
    elif should_hold:
        best_price = round(record.tawfeer_price, 2)
        best_summary = current_summary

    recommendation = "hold"
    if best_price > record.tawfeer_price + 0.009:
        recommendation = "increase"
    elif best_price < record.tawfeer_price - 0.009:
        recommendation = "decrease"

    reasons: list[str] = []
    projected_margin = calculate_margin(record, best_price)
    projected_gap = best_summary["projected_price_gap"]

    if recommendation == "increase":
        if current_margin < record.margin_floor:
            reasons.append("Price increase lifts margin toward the configured floor")
        if best_summary["expected_margin_impact"] > 0:
            reasons.append("Expected gross profit improves at the recommended price")
        if best_summary["expected_revenue_impact"] >= 0:
            reasons.append("Projected revenue remains stable to positive after the increase")
        else:
            reasons.append("Revenue softens modestly, but the move improves unit economics")
    elif recommendation == "decrease":
        if current_price_gap > 2:
            reasons.append("Price decrease closes the gap to market and supports demand")
        if best_summary["expected_revenue_impact"] > 0:
            reasons.append("Projected revenue improves from stronger expected sell-through")
        if best_summary["expected_margin_impact"] >= 0:
            reasons.append("Margin dollars are preserved despite the lower shelf price")
        else:
            reasons.append("The lower price is justified by a better demand outlook")
    else:
        reasons.append("Current price already balances margin, demand, and market position best")

    if projected_margin < record.margin_floor:
        reasons.append("Further change is constrained by the margin floor")

    if record.kvi_flag and abs(projected_gap) <= 2:
        reasons.append("Recommendation keeps the KVI close to market benchmark")
    elif not record.kvi_flag and abs(projected_gap) <= 4:
        reasons.append("Recommendation keeps the SKU within an acceptable market band")

    if stock_cover < 1.2 or "understock" in inventory_note:
        reasons.append("Tight stock cover favors smaller and more disciplined price moves")
    elif stock_cover > 3 or "overstock" in inventory_note or "high stock" in inventory_note:
        reasons.append("High stock cover supports a more demand-oriented recommendation")

    if record.source_recommended_price is not None and recommendation != "hold":
        source_distance = abs(best_price - record.source_recommended_price)
        if source_distance <= max(record.tawfeer_price * 0.03, 0.05):
            reasons.append("Recommended price is aligned with the workbook signal")

    confidence = _confidence_for_choice(
        record=record,
        recommendation=recommendation,
        improvement=improvement,
        projected_margin=projected_margin,
        projected_gap=projected_gap,
        best_summary=best_summary,
    )

    return RecommendationRecord(
        sku=record.sku,
        suggested_price=round(best_price, 2),
        reason=". ".join(dict.fromkeys(reasons)),
        confidence=round(confidence, 2),
        timestamp=datetime.now(UTC),
    )


def _score_candidate(
    *,
    record: SKURecord,
    candidate_price: float,
    summary: dict[str, float],
    stock_cover: float,
) -> float:
    projected_margin = calculate_margin(record, candidate_price)
    projected_gap = summary["projected_price_gap"]
    revenue_impact = summary["expected_revenue_impact"]
    margin_impact = summary["expected_margin_impact"]
    current_price = record.tawfeer_price
    current_gap = calculate_price_gap(record)
    move_pct = abs((candidate_price - current_price) / max(current_price, 0.01)) * 100
    source_flag = record.source_pricing_flag.lower()

    score = margin_impact + (0.5 * revenue_impact)

    if projected_margin < record.margin_floor:
        score -= (record.margin_floor - projected_margin) * max(record.units_sold_last_week, 1) * 12
    else:
        score += (projected_margin - record.margin_floor) * max(record.units_sold_last_week, 1) * 2.5

    acceptable_gap = 2.0 if record.kvi_flag else 5.0
    if abs(projected_gap) > acceptable_gap:
        score -= (abs(projected_gap) - acceptable_gap) * 8
    score -= abs(projected_gap) * (2.6 if record.kvi_flag else 1.6)

    if abs(projected_gap) < abs(current_gap):
        score += (abs(current_gap) - abs(projected_gap)) * 6

    if candidate_price > current_price and revenue_impact < 0:
        score -= abs(revenue_impact) * (0.7 if projected_margin >= record.margin_floor else 0.28)

    if candidate_price < current_price and margin_impact < 0:
        penalty_weight = 0.35
        if current_gap > acceptable_gap and projected_margin >= record.margin_floor and revenue_impact >= 0:
            penalty_weight = 0.12
        score -= abs(margin_impact) * penalty_weight

    if current_gap > acceptable_gap and candidate_price > current_price:
        score -= 45
    if current_gap < -acceptable_gap and candidate_price < current_price:
        score -= 20

    if candidate_price < current_price and current_gap > acceptable_gap and projected_margin >= record.margin_floor:
        score += (current_gap - max(projected_gap, 0)) * 22
        if revenue_impact > 0:
            score += revenue_impact * 0.45

    if ("too expensive" in source_flag or "overpriced" in source_flag) and candidate_price > current_price:
        score -= 55
    if ("too cheap" in source_flag or "underpriced" in source_flag) and candidate_price < current_price:
        score -= 30

    if stock_cover < 1.2 and candidate_price < current_price:
        score -= 18
    elif stock_cover > 3 and candidate_price > current_price:
        score -= 10

    score -= move_pct * (1.2 if record.kvi_flag else 0.8)
    return round(score, 4)


def _confidence_for_choice(
    *,
    record: SKURecord,
    recommendation: str,
    improvement: float,
    projected_margin: float,
    projected_gap: float,
    best_summary: dict[str, float],
) -> float:
    confidence = 0.62

    if recommendation == "hold":
        confidence += 0.08
    else:
        confidence += min(improvement / 120, 0.18)

    if projected_margin >= record.margin_floor:
        confidence += 0.06

    acceptable_gap = 2.0 if record.kvi_flag else 5.0
    if abs(projected_gap) <= acceptable_gap:
        confidence += 0.05

    if recommendation == "increase" and best_summary["expected_revenue_impact"] >= 0:
        confidence += 0.04
    if recommendation == "decrease" and best_summary["expected_margin_impact"] >= 0:
        confidence += 0.04

    if recommendation != "hold" and abs(best_summary["expected_volume_change"]) > 18:
        confidence -= 0.05

    return min(max(confidence, 0.5), 0.95)
