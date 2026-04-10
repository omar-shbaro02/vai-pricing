from __future__ import annotations

import csv
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


XML_NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RAW_DATA_HEADERS = [
    "SKU",
    "Product_Name",
    "Category",
    "subcategory",
    "Brand",
    "Pack_Size",
    "Tawfeer_Price",
    "Cost",
    "Margin_Floor",
    "calculation vs market price",
    "Margin Flag",
    "Pricing Flag",
    "Recommended action",
    "Recommended price",
    "Difference vs Lowest in the market",
    "New GM% after price recommendation",
    "KVI_Flag",
    "Promo_Flag",
    "Carrefour_Price",
    "Spinneys_Price",
    "MetroMart_Price",
    "Lowest market price",
    "average market price",
    "Units_Sold_Last_Week",
    "Inventory_Level",
    "Stock cover",
    "Inventory interpreation",
    "Store_Count",
    "Last_Price_Change_Date",
    "SKU_Type",
    "Target_GM",
    "Min_Allowed_Price",
    "Max_Allowed_Price",
    "Market_Anchor_Price",
    "Margin_Floor_Price",
    "Constraint_Reason",
    "Approval_Status",
]
SUPPORTED_SHEET_NAMES = ("Raw Data", "Pricing Engine V1")


def load_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for si in root.findall("a:si", XML_NS):
        strings.append("".join((node.text or "") for node in si.findall(".//a:t", XML_NS)))
    return strings


def load_sheet_rows(archive: zipfile.ZipFile, sheet_name: str) -> list[dict[str, str]]:
    shared_strings = load_shared_strings(archive)
    rels_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    rid_to_target = {
        rel.attrib["Id"]: rel.attrib["Target"].lstrip("/")
        for rel in rels_root.findall("{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
    }
    workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))

    target = None
    for sheet in workbook_root.findall("a:sheets/a:sheet", XML_NS):
        if sheet.attrib.get("name", "").strip().lower() == sheet_name.strip().lower():
            relation_id = sheet.attrib[
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            ]
            target = rid_to_target[relation_id]
            break

    if not target:
        raise ValueError(f"Sheet '{sheet_name}' not found")

    if not target.startswith("xl/"):
        target = f"xl/{target.lstrip('/')}"

    root = ET.fromstring(archive.read(target))
    rows = root.findall("a:sheetData/a:row", XML_NS)

    result: list[dict[str, str]] = []
    for row in rows:
        values: dict[str, str] = {}
        for cell in row.findall("a:c", XML_NS):
            ref = cell.attrib.get("r", "")
            value_node = cell.find("a:v", XML_NS)
            if value_node is None:
                text = ""
            elif cell.attrib.get("t") == "s":
                text = shared_strings[int(value_node.text or "0")]
            else:
                text = value_node.text or ""
            values[ref] = text.strip()
        if any(values.values()):
            result.append(values)
    return result


def workbook_has_sheet(archive: zipfile.ZipFile, sheet_name: str) -> bool:
    workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
    return any(
        sheet.attrib.get("name", "").strip().lower() == sheet_name.strip().lower()
        for sheet in workbook_root.findall("a:sheets/a:sheet", XML_NS)
    )


def load_primary_rows(archive: zipfile.ZipFile) -> list[dict[str, str]]:
    for sheet_name in SUPPORTED_SHEET_NAMES:
        if workbook_has_sheet(archive, sheet_name):
            return load_sheet_rows(archive, sheet_name)
    raise ValueError(f"Workbook does not contain any supported pricing data sheet: {SUPPORTED_SHEET_NAMES}")


def build_kvi_metadata(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    metadata: dict[str, dict[str, str]] = {}
    for row in rows:
        suffix = row_key_suffix(row)
        sku = row.get(f"A{suffix}", "").strip()
        if not sku:
            continue
        metadata[sku] = {
            "Product_Name": row.get(f"B{suffix}", ""),
            "Category": row.get(f"C{suffix}", ""),
            "subcategory": row.get(f"D{suffix}", ""),
            "Brand": row.get(f"E{suffix}", ""),
            "Pack_Size": row.get(f"F{suffix}", ""),
            "KVI_Flag": row.get(f"J{suffix}", "Yes"),
            "Promo_Flag": row.get(f"K{suffix}", "No"),
        }
    return metadata


def build_raw_metadata(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    metadata: dict[str, dict[str, str]] = {}
    for row in rows:
        suffix = row_key_suffix(row)
        sku = row.get(f"A{suffix}", "").strip()
        if not sku:
            continue
        metadata[sku] = {
            "Product_Name": row.get(f"B{suffix}", "").strip(),
            "Category": row.get(f"C{suffix}", "").strip(),
            "subcategory": row.get(f"D{suffix}", "").strip(),
            "Brand": row.get(f"E{suffix}", "").strip(),
            "Pack_Size": row.get(f"F{suffix}", "").strip(),
        }
    return metadata


def row_key_suffix(row: dict[str, str]) -> str:
    first_ref = next(iter(row.keys()))
    return "".join(ch for ch in first_ref if ch.isdigit())


def normalize_header(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return normalized.strip("_")


def sheet_rows_to_records(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if not rows:
        return []

    header_row = rows[0]
    header_suffix = row_key_suffix(header_row)
    headers: dict[str, str] = {}
    for cell_ref, value in header_row.items():
        col = "".join(ch for ch in cell_ref if ch.isalpha())
        headers[col] = normalize_header(value)

    records: list[dict[str, str]] = []
    for row in rows[1:]:
        row_suffix = row_key_suffix(row)
        if row_suffix == header_suffix:
            continue
        record: dict[str, str] = {}
        for cell_ref, value in row.items():
            col = "".join(ch for ch in cell_ref if ch.isalpha())
            header = headers.get(col)
            if header:
                record[header] = value
        if any(record.values()):
            records.append(record)
    return records


def normalize_raw_rows(
    raw_rows: list[dict[str, str]],
    kvi_metadata: dict[str, dict[str, str]],
    fallback_metadata: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for row in raw_rows:
        row_id = row_key_suffix(row)
        sku = row.get(f"A{row_id}", "").strip()
        if not sku:
            continue

        metadata = {**fallback_metadata.get(sku, {}), **kvi_metadata.get(sku, {})}
        sku_type = row.get(f"AG{row_id}", "").strip()
        product_name = row.get(f"B{row_id}", "").strip() or metadata.get("Product_Name") or f"SKU {sku}"
        category = row.get(f"C{row_id}", "").strip() or metadata.get("Category") or sku_type or "Unknown"
        subcategory = row.get(f"D{row_id}", "").strip() or metadata.get("subcategory", "")
        brand = row.get(f"E{row_id}", "").strip() or metadata.get("Brand", "")
        pack_size = row.get(f"F{row_id}", "").strip() or metadata.get("Pack_Size", "")
        kvi_flag = "Yes" if sku_type == "KVI" or metadata.get("KVI_Flag", "").lower() == "yes" else "No"
        promo_flag = metadata.get("Promo_Flag", "No") or "No"

        normalized.append(
            {
                "SKU": sku,
                "Product_Name": product_name,
                "Category": category,
                "subcategory": subcategory,
                "Brand": brand,
                "Pack_Size": pack_size,
                "Tawfeer_Price": row.get(f"G{row_id}", ""),
                "Cost": row.get(f"H{row_id}", ""),
                "Margin_Floor": row.get(f"I{row_id}", ""),
                "calculation vs market price": row.get(f"K{row_id}", ""),
                "Margin Flag": row.get(f"L{row_id}", ""),
                "Pricing Flag": row.get(f"M{row_id}", ""),
                "Recommended action": row.get(f"N{row_id}", ""),
                "Recommended price": row.get(f"O{row_id}", ""),
                "Difference vs Lowest in the market": row.get(f"P{row_id}", ""),
                "New GM% after price recommendation": row.get(f"Q{row_id}", ""),
                "KVI_Flag": kvi_flag,
                "Promo_Flag": promo_flag,
                "Carrefour_Price": row.get(f"V{row_id}", ""),
                "Spinneys_Price": row.get(f"W{row_id}", ""),
                "MetroMart_Price": row.get(f"X{row_id}", ""),
                "Lowest market price": row.get(f"Y{row_id}", ""),
                "average market price": row.get(f"Z{row_id}", ""),
                "Units_Sold_Last_Week": row.get(f"AA{row_id}", ""),
                "Inventory_Level": row.get(f"AB{row_id}", ""),
                "Stock cover": row.get(f"AC{row_id}", ""),
                "Inventory interpreation": row.get(f"AD{row_id}", ""),
                "Store_Count": row.get(f"AE{row_id}", ""),
                "Last_Price_Change_Date": row.get(f"AF{row_id}", ""),
                "SKU_Type": sku_type,
                "Target_GM": row.get(f"AH{row_id}", ""),
                "Min_Allowed_Price": row.get(f"AI{row_id}", ""),
                "Max_Allowed_Price": row.get(f"AJ{row_id}", ""),
                "Market_Anchor_Price": row.get(f"AL{row_id}", ""),
                "Margin_Floor_Price": row.get(f"AM{row_id}", ""),
                "Constraint_Reason": row.get(f"R{row_id}", ""),
                "Approval_Status": row.get(f"S{row_id}", ""),
            }
        )
    return normalized


def normalize_engine_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    records = sheet_rows_to_records(rows)
    normalized: list[dict[str, str]] = []
    for row in records:
        sku = row.get("sku", "").strip()
        if not sku or sku.lower() == "sku":
            continue

        normalized.append(
            {
                "SKU": sku,
                "Product_Name": row.get("product_name", ""),
                "Category": row.get("category", ""),
                "subcategory": row.get("subcategory", ""),
                "Brand": row.get("brand", ""),
                "Pack_Size": row.get("pack_size", ""),
                "Tawfeer_Price": row.get("tawfeer_price", ""),
                "Cost": row.get("cost", ""),
                "Margin_Floor": row.get("margin_floor", ""),
                "calculation vs market price": row.get("gap_vs_benchmark", ""),
                "Margin Flag": row.get("margin_flag", ""),
                "Pricing Flag": row.get("price_positioning", ""),
                "Recommended action": row.get("recommended_pricing_action", ""),
                "Recommended price": row.get("recommended_price", ""),
                "Difference vs Lowest in the market": row.get(
                    "difference_vs_lowest_in_the_market_average_market_price", ""
                ),
                "New GM% after price recommendation": row.get(
                    "new_gm_after_price_recommendation", ""
                ),
                "KVI_Flag": row.get("kvi_flag", ""),
                "Promo_Flag": row.get("promo_flag", ""),
                "Carrefour_Price": row.get("carrefour_price", ""),
                "Spinneys_Price": row.get("spinneys_price", ""),
                "MetroMart_Price": row.get("metromart_price", ""),
                "Lowest market price": row.get("lowest_market_price", ""),
                "average market price": row.get("average_market_price", ""),
                "Units_Sold_Last_Week": row.get("units_sold_last_week", ""),
                "Inventory_Level": row.get("inventory_level", ""),
                "Stock cover": row.get("stock_cover", ""),
                "Inventory interpreation": row.get("inventory_interpretation", ""),
                "Store_Count": row.get("store_count", ""),
                "Last_Price_Change_Date": row.get("last_price_change_date", ""),
                "SKU_Type": row.get("segment", ""),
                "Target_GM": row.get("target_gm", ""),
                "Min_Allowed_Price": row.get("margin_safe_min_price", ""),
                "Max_Allowed_Price": "",
                "Market_Anchor_Price": row.get("avg_market_price", ""),
                "Margin_Floor_Price": row.get("margin_safe_min_price", ""),
                "Constraint_Reason": row.get("rule_conflict", ""),
                "Approval_Status": row.get("action", ""),
            }
        )
    return normalized


def main() -> int:
    if len(sys.argv) not in {3, 4}:
        print("Usage: python convert_pricing_workbook.py <input.xlsx> <output.csv> [fallback_workbook]")
        return 1

    source = Path(sys.argv[1]).expanduser()
    destination = Path(sys.argv[2]).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fallback_source = Path(sys.argv[3]).expanduser() if len(sys.argv) == 4 else None

    with zipfile.ZipFile(source) as archive:
        primary_sheet = next(sheet for sheet in SUPPORTED_SHEET_NAMES if workbook_has_sheet(archive, sheet))
        raw_rows = load_sheet_rows(archive, primary_sheet)
        kvi_rows = load_sheet_rows(archive, "KVI LIst") if workbook_has_sheet(archive, "KVI LIst") else []

    fallback_metadata: dict[str, dict[str, str]] = {}
    if fallback_source and fallback_source.exists():
        with zipfile.ZipFile(fallback_source) as archive:
            fallback_metadata = build_raw_metadata(load_primary_rows(archive))

    if primary_sheet == "Pricing Engine V1":
        normalized = normalize_engine_rows(raw_rows)
    else:
        normalized = normalize_raw_rows(raw_rows, build_kvi_metadata(kvi_rows), fallback_metadata)

    with destination.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=RAW_DATA_HEADERS)
        writer.writeheader()
        writer.writerows(normalized)

    print(f"Wrote {len(normalized)} rows to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
