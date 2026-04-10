from __future__ import annotations

import json
import os
from typing import Any

from .pricing_engine import calculate_margin, calculate_price_gap, calculate_reference_price
from .schemas import DecisionUpdate, RecommendationRecord, SKURecord
from .simulation import summarize_simulation


OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
OPENAI_MODEL_ENV = "OPENAI_PRICING_MODEL"
DEFAULT_OPENAI_MODEL = "gpt-5-mini"


class LLMPricingAgent:
    def __init__(self) -> None:
        self.model = os.getenv(OPENAI_MODEL_ENV, DEFAULT_OPENAI_MODEL)

    def is_configured(self) -> bool:
        return bool(os.getenv(OPENAI_API_KEY_ENV))

    def answer_question(
        self,
        *,
        record: SKURecord,
        recommendation: RecommendationRecord,
        question: str,
        previous_response_id: str | None,
        pricing_state,
    ) -> tuple[str, str | None, DecisionUpdate | None]:
        if not self.is_configured():
            raise RuntimeError(
                f"{OPENAI_API_KEY_ENV} is not configured. Set it to enable LLM-backed pricing chat."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "The OpenAI Python SDK is not installed. Add `openai` to the backend environment to enable LLM chat."
            ) from exc

        client = OpenAI()
        tools = [self._apply_override_tool_schema()]
        response = client.responses.create(
            model=self.model,
            previous_response_id=previous_response_id,
            input=self._build_initial_input(record, recommendation, question, pricing_state),
            tools=tools,
        )

        decision_update: DecisionUpdate | None = None

        for _ in range(4):
            function_calls = [item for item in response.output if getattr(item, "type", "") == "function_call"]
            if not function_calls:
                break

            tool_outputs = []
            for call in function_calls:
                if call.name != "apply_decision_override":
                    continue

                arguments = json.loads(call.arguments or "{}")
                decision_update = pricing_state.apply_decision_override(
                    sku=record.sku,
                    recommendation=arguments.get("recommendation", "hold"),
                    suggested_price=float(arguments.get("suggested_price", recommendation.suggested_price)),
                    rationale=str(arguments.get("rationale", "")).strip() or "Updated from LLM chat.",
                    next_steps=[str(step) for step in arguments.get("next_steps", []) if str(step).strip()],
                )
                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": json.dumps(decision_update.model_dump(mode="json")),
                    }
                )

            if not tool_outputs:
                break

            response = client.responses.create(
                model=self.model,
                previous_response_id=response.id,
                input=tool_outputs,
                tools=tools,
            )

        answer = (response.output_text or "").strip()
        if not answer:
            answer = "I reviewed the SKU context but could not produce a final answer."

        return answer, response.id, decision_update

    def _build_initial_input(
        self,
        record: SKURecord,
        recommendation: RecommendationRecord,
        question: str,
        pricing_state,
    ) -> list[dict[str, Any]]:
        return [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "You are a senior retail pricing analyst. Use the provided workbook-derived SKU context as "
                            "the source of truth. Explain studies, compare the current app decision to the workbook "
                            "signals, and if the user explicitly asks to change, override, revise, or replace the "
                            "decision or next steps, call the apply_decision_override tool. "
                            "Do not invent workbook fields that are not in context. Be concrete and commercial."
                        ),
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": self._build_context(record, recommendation, pricing_state),
                    },
                    {
                        "type": "input_text",
                        "text": f"User question: {question}",
                    },
                ],
            },
        ]

    def _build_context(self, record: SKURecord, recommendation: RecommendationRecord, pricing_state) -> str:
        reference_price = calculate_reference_price(record)
        price_gap = calculate_price_gap(record, reference_price)
        current_margin = round(calculate_margin(record) * 100, 2)
        suggested_simulation = summarize_simulation(record, recommendation.suggested_price)
        similar = pricing_state.vector_store.similar_recommendations(recommendation.reason, limit=3)
        similar_lines = [
            f"- SKU {match['sku']}: {match['reason']}"
            for match in similar
            if match.get("sku") != record.sku and match.get("reason")
        ]

        context = [
            f"SKU: {record.sku}",
            f"Product: {record.product_name}",
            f"Category: {record.category}",
            f"Brand: {record.brand}",
            f"Pack size: {record.pack_size}",
            f"Current price: {record.tawfeer_price:.2f}",
            f"Cost: {record.cost:.2f}",
            f"Margin floor: {record.margin_floor * 100:.2f}%",
            f"Current margin: {current_margin:.2f}%",
            f"KVI flag: {record.kvi_flag}",
            f"Promo flag: {record.promo_flag}",
            f"Carrefour price: {record.carrefour_price:.2f}",
            f"Spinneys price: {record.spinneys_price:.2f}",
            f"MetroMart price: {record.metromart_price:.2f}",
            f"Reference price: {reference_price:.2f}",
            f"Price gap: {price_gap:.2f}%",
            f"Units sold last week: {record.units_sold_last_week}",
            f"Inventory level: {record.inventory_level}",
            f"Stock cover: {record.stock_cover if record.stock_cover is not None else 'N/A'}",
            f"Inventory interpretation: {record.inventory_interpretation or 'N/A'}",
            f"Workbook margin flag: {record.source_margin_flag or 'N/A'}",
            f"Workbook pricing flag: {record.source_pricing_flag or 'N/A'}",
            f"Workbook recommended action: {record.source_recommended_action or 'N/A'}",
            f"Workbook recommended price: {record.source_recommended_price if record.source_recommended_price is not None else 'N/A'}",
            f"Current app recommendation reason: {recommendation.reason}",
            f"Current app suggested price: {recommendation.suggested_price:.2f}",
            f"Current app confidence: {recommendation.confidence:.2f}",
            (
                "Current app simulation: "
                f"volume {suggested_simulation['expected_volume_change']:.2f}%, "
                f"revenue {suggested_simulation['expected_revenue_impact']:.2f}, "
                f"margin {suggested_simulation['expected_margin_impact']:.2f}, "
                f"projected margin {suggested_simulation['projected_margin_percent']:.2f}%"
            ),
        ]

        if similar_lines:
            context.append("Similar recommendation examples:")
            context.extend(similar_lines)

        return "\n".join(context)

    @staticmethod
    def _apply_override_tool_schema() -> dict[str, Any]:
        return {
            "type": "function",
            "name": "apply_decision_override",
            "description": (
                "Apply a new pricing decision for the current SKU when the user explicitly asks to change or revise "
                "the recommendation or plan."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "recommendation": {
                        "type": "string",
                        "enum": ["increase", "decrease", "hold"],
                    },
                    "suggested_price": {"type": "number"},
                    "rationale": {"type": "string"},
                    "next_steps": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["recommendation", "suggested_price", "rationale"],
                "additionalProperties": False,
            },
        }
