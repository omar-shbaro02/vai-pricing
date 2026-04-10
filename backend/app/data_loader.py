from __future__ import annotations

import csv
import os
import re
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree as ET

from .schemas import SKURecord


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_CSV_PATH = DATA_DIR / "skus.csv"
DEFAULT_PILOT_DATASET_PATH = DATA_DIR / "pricing_agent_pilot_dataset_improved_recalc.csv"
DEFAULT_RETAIL_DATASET_PATH = DATA_DIR / "retail_final_dataset.xlsx"
STRATEGY_WORKBOOK_PATTERNS = [
    "pricing_agent_pilot_strategy*.xlsx",
]
DATASET_PATH_ENV = "PRICING_DATASET_PATH"
XML_NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
SUPPORTED_WORKBOOK_SHEETS = ("NEW (2)", "NEW", "FromJAD", "Raw Data", "Pricing Engine V1")


def ensure_sample_csv(path: Path = DEFAULT_CSV_PATH) -> Path:
    if path.exists():
        return path

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sample_rows = [
        {
            "sku": "SKU-1001",
            "product_name": "Tawfeer Olive Oil",
            "category": "Pantry",
            "pack_size": "750ml",
            "tawfeer_price": 8.99,
            "cost": 6.10,
            "margin_floor": 0.22,
            "kvi_flag": True,
            "promo_flag": False,
            "carrefour_price": 8.49,
            "spinneys_price": 8.79,
            "metromart_price": 8.65,
            "units_sold_last_week": 330,
            "inventory_level": 810,
            "store_count": 12,
            "last_price_change_date": "2026-02-14",
        },
        {
            "sku": "SKU-1002",
            "product_name": "Greek Yogurt Plain",
            "category": "Dairy",
            "pack_size": "500g",
            "tawfeer_price": 3.59,
            "cost": 2.15,
            "margin_floor": 0.25,
            "kvi_flag": True,
            "promo_flag": False,
            "carrefour_price": 3.79,
            "spinneys_price": 3.69,
            "metromart_price": 3.89,
            "units_sold_last_week": 490,
            "inventory_level": 650,
            "store_count": 15,
            "last_price_change_date": "2026-02-05",
        },
        {
            "sku": "SKU-1003",
            "product_name": "Premium Basmati Rice",
            "category": "Staples",
            "pack_size": "5kg",
            "tawfeer_price": 12.5,
            "cost": 9.4,
            "margin_floor": 0.18,
            "kvi_flag": False,
            "promo_flag": True,
            "carrefour_price": 11.9,
            "spinneys_price": 12.2,
            "metromart_price": 11.8,
            "units_sold_last_week": 150,
            "inventory_level": 420,
            "store_count": 10,
            "last_price_change_date": "2026-01-29",
        },
        {
            "sku": "SKU-1004",
            "product_name": "Whole Bean Coffee",
            "category": "Beverages",
            "pack_size": "1kg",
            "tawfeer_price": 15.99,
            "cost": 10.9,
            "margin_floor": 0.2,
            "kvi_flag": False,
            "promo_flag": False,
            "carrefour_price": 16.49,
            "spinneys_price": 16.29,
            "metromart_price": 16.99,
            "units_sold_last_week": 110,
            "inventory_level": 280,
            "store_count": 8,
            "last_price_change_date": "2026-02-20",
        },
        {
            "sku": "SKU-1005",
            "product_name": "Baby Wipes Sensitive",
            "category": "Baby Care",
            "pack_size": "72ct",
            "tawfeer_price": 4.99,
            "cost": 3.6,
            "margin_floor": 0.2,
            "kvi_flag": True,
            "promo_flag": False,
            "carrefour_price": 4.79,
            "spinneys_price": 4.89,
            "metromart_price": 5.19,
            "units_sold_last_week": 370,
            "inventory_level": 520,
            "store_count": 14,
            "last_price_change_date": "2026-02-10",
        },
        {
            "sku": "SKU-1006",
            "product_name": "Dishwashing Liquid Lemon",
            "category": "Home Care",
            "pack_size": "1L",
            "tawfeer_price": 2.85,
            "cost": 1.65,
            "margin_floor": 0.24,
            "kvi_flag": False,
            "promo_flag": True,
            "carrefour_price": 2.99,
            "spinneys_price": 3.05,
            "metromart_price": 2.95,
            "units_sold_last_week": 280,
            "inventory_level": 720,
            "store_count": 11,
            "last_price_change_date": "2026-02-01",
        },
        {
            "sku": "SKU-1007",
            "product_name": "Fresh Orange Juice",
            "category": "Chilled Drinks",
            "pack_size": "1.5L",
            "tawfeer_price": 5.29,
            "cost": 3.25,
            "margin_floor": 0.22,
            "kvi_flag": True,
            "promo_flag": False,
            "carrefour_price": 5.49,
            "spinneys_price": 5.59,
            "metromart_price": 5.39,
            "units_sold_last_week": 430,
            "inventory_level": 390,
            "store_count": 13,
            "last_price_change_date": "2026-02-24",
        },
        {
            "sku": "SKU-1008",
            "product_name": "Multigrain Bread",
            "category": "Bakery",
            "pack_size": "600g",
            "tawfeer_price": 2.19,
            "cost": 1.42,
            "margin_floor": 0.2,
            "kvi_flag": True,
            "promo_flag": False,
            "carrefour_price": 2.29,
            "spinneys_price": 2.39,
            "metromart_price": 2.35,
            "units_sold_last_week": 510,
            "inventory_level": 240,
            "store_count": 16,
            "last_price_change_date": "2026-02-18",
        },
    ]

    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(sample_rows[0].keys()))
        writer.writeheader()
        writer.writerows(sample_rows)

    return path


def _to_bool(value: str | None) -> bool:
    if value is None:
        return False
    return str(value).strip().lower() in {"true", "yes", "y", "1"}


def _to_float(value: str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).strip()
    if not text or text.lower() in {"n/a", "none", "no price recommendation"}:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def _to_optional_float(value: str | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"n/a", "none", "no price recommendation"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _to_int(value: str | None, default: int = 0) -> int:
    return int(round(_to_float(value, float(default))))


def _excel_serial_to_date(value: str | None) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        return text
    try:
        serial = float(text)
    except ValueError:
        return text
    epoch = datetime(1899, 12, 30)
    return (epoch + timedelta(days=serial)).date().isoformat()


def _normalize_header(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return normalized.strip("_")


def _is_xlsx_payload(path: Path) -> bool:
    if path.suffix.lower() == ".xlsx":
        return True
    with path.open("rb") as file:
        return file.read(2) == b"PK"


def _load_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for si in root.findall("a:si", XML_NS):
        texts = [part.text or "" for part in si.findall(".//a:t", XML_NS)]
        strings.append("".join(texts))
    return strings


def _extract_sheet_rows(archive: zipfile.ZipFile, sheet_name: str) -> list[dict[str, str]]:
    rels_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    rid_to_target = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels_root.findall("{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
    }
    workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
    sheet_target = None
    for sheet in workbook_root.findall("a:sheets/a:sheet", XML_NS):
        if sheet.attrib.get("name", "").strip().lower() == sheet_name.strip().lower():
            relation_id = sheet.attrib.get(
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            )
            if relation_id:
                sheet_target = _normalize_zip_path(rid_to_target[relation_id])
            break
    if not sheet_target:
        raise ValueError(f"Sheet '{sheet_name}' not found in workbook")

    shared_strings = _load_shared_strings(archive)
    sheet_root = ET.fromstring(archive.read(sheet_target))
    rows = sheet_root.findall("a:sheetData/a:row", XML_NS)

    table_rows: list[dict[str, str]] = []
    headers: dict[int, str] = {}
    for row in rows:
        values_by_index: dict[int, str] = {}
        for cell in row.findall("a:c", XML_NS):
            cell_ref = cell.attrib.get("r", "")
            col_letters = "".join(ch for ch in cell_ref if ch.isalpha())
            col_index = 0
            for letter in col_letters:
                col_index = col_index * 26 + (ord(letter) - ord("A") + 1)
            col_index -= 1

            cell_type = cell.attrib.get("t")
            value_node = cell.find("a:v", XML_NS)
            if value_node is None:
                cell_value = ""
            elif cell_type == "s":
                cell_value = shared_strings[int(value_node.text or 0)]
            else:
                cell_value = value_node.text or ""
            values_by_index[col_index] = cell_value.strip()

        if not values_by_index:
            continue

        row_number = int(row.attrib.get("r", "0"))
        if row_number == 1:
            headers = {index: _normalize_header(text) for index, text in values_by_index.items()}
            continue

        mapped_row = {}
        for index, header in headers.items():
            if header:
                mapped_row[header] = values_by_index.get(index, "")

        if any(mapped_row.values()):
            table_rows.append(mapped_row)

    return table_rows


def _normalize_zip_path(target: str) -> str:
    cleaned = target.replace("\\", "/").lstrip("/")
    if cleaned.startswith("xl/"):
        return cleaned
    return f"xl/{cleaned}"


def _list_sheet_names(archive: zipfile.ZipFile) -> list[str]:
    workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
    return [sheet.attrib.get("name", "").strip() for sheet in workbook_root.findall("a:sheets/a:sheet", XML_NS)]


def _extract_supported_workbook_rows(archive: zipfile.ZipFile) -> list[dict[str, str]]:
    available_sheets = _list_sheet_names(archive)
    for sheet_name in SUPPORTED_WORKBOOK_SHEETS:
        if any(candidate.lower() == sheet_name.lower() for candidate in available_sheets):
            return _extract_sheet_rows(archive, sheet_name)
    raise ValueError(
        "Workbook does not contain a supported pricing data sheet. "
        f"Expected one of: {', '.join(SUPPORTED_WORKBOOK_SHEETS)}"
    )


def _map_raw_dataset_row(row: dict[str, str]) -> SKURecord:
    source_recommended_price = _to_optional_float(row.get("recommended_price"))
    if source_recommended_price is None:
        source_recommended_price = _to_optional_float(row.get("margin_safe_min_price"))

    inventory_interpretation = str(
        row.get("inventory_interpreation")
        or row.get("inventory_interpretation")
        or ""
    ).strip()

    source_pricing_flag = str(
        row.get("pricing_flag")
        or row.get("price_positioning")
        or ""
    ).strip()

    source_recommended_action = str(
        row.get("recommended_action")
        or row.get("recommended_pricing_action")
        or row.get("action")
        or ""
    ).strip()

    average_market_price = _to_optional_float(row.get("average_market_price"))
    if average_market_price is None:
        average_market_price = _to_optional_float(row.get("avg_market_price"))

    stock_cover = _to_optional_float(row.get("stock_cover"))
    if stock_cover is None:
        stock_cover = _to_optional_float(row.get("stock_cover_week"))

    return SKURecord(
        sku=str(row.get("sku", "")).strip(),
        product_name=str(row.get("product_name", "")).strip(),
        category=str(row.get("category", "")).strip() or "Unknown",
        subcategory=str(row.get("subcategory", "")).strip(),
        brand=str(row.get("brand", "")).strip(),
        pack_size=str(row.get("pack_size", "")).strip() or "N/A",
        tawfeer_price=_to_float(row.get("tawfeer_price")),
        cost=_to_float(row.get("cost")),
        margin_floor=_to_float(row.get("margin_floor"), 0.15),
        kvi_flag=_to_bool(row.get("kvi_flag")),
        promo_flag=_to_bool(row.get("promo_flag")),
        carrefour_price=_to_float(row.get("carrefour_price")),
        spinneys_price=_to_float(row.get("spinneys_price")),
        metromart_price=_to_float(row.get("metromart_price")),
        units_sold_last_week=_to_int(row.get("units_sold_last_week")),
        inventory_level=_to_int(row.get("inventory_level")),
        store_count=max(1, _to_int(row.get("store_count"), 1)),
        last_price_change_date=_excel_serial_to_date(row.get("last_price_change_date")),
        lowest_market_price=_to_optional_float(row.get("lowest_market_price")),
        average_market_price=average_market_price,
        stock_cover=stock_cover,
        inventory_interpretation=inventory_interpretation,
        source_margin_flag=str(row.get("margin_flag", "")).strip(),
        source_pricing_flag=source_pricing_flag,
        source_recommended_action=source_recommended_action,
        source_recommended_price=source_recommended_price,
    )


def _map_legacy_row(row: dict[str, str]) -> SKURecord:
    return SKURecord(
        sku=row["sku"],
        product_name=row["product_name"],
        category=row["category"],
        pack_size=row["pack_size"],
        tawfeer_price=float(row["tawfeer_price"]),
        cost=float(row["cost"]),
        margin_floor=float(row["margin_floor"]),
        kvi_flag=row["kvi_flag"].lower() == "true",
        promo_flag=row["promo_flag"].lower() == "true",
        carrefour_price=float(row["carrefour_price"]),
        spinneys_price=float(row["spinneys_price"]),
        metromart_price=float(row["metromart_price"]),
        units_sold_last_week=int(row["units_sold_last_week"]),
        inventory_level=int(row["inventory_level"]),
        store_count=int(row["store_count"]),
        last_price_change_date=row["last_price_change_date"],
    )


def resolve_dataset_path(path: Path | None = None) -> Path:
    env_path = os.getenv(DATASET_PATH_ENV)
    if env_path:
        candidate = Path(env_path).expanduser()
        if candidate.exists():
            return candidate

    if path and path.exists():
        return path

    if DEFAULT_RETAIL_DATASET_PATH.exists():
        return DEFAULT_RETAIL_DATASET_PATH

    strategy_candidates: list[Path] = []
    for directory in (DATA_DIR, PROJECT_DIR):
        for pattern in STRATEGY_WORKBOOK_PATTERNS:
            strategy_candidates.extend(sorted(directory.glob(pattern)))
    if strategy_candidates:
        return max(strategy_candidates, key=lambda candidate: candidate.stat().st_mtime)

    if DEFAULT_PILOT_DATASET_PATH.exists():
        return DEFAULT_PILOT_DATASET_PATH

    return ensure_sample_csv(DEFAULT_CSV_PATH)


def load_sku_records(path: Path | None = None) -> list[SKURecord]:
    source_path = resolve_dataset_path(path)

    if _is_xlsx_payload(source_path):
        with zipfile.ZipFile(source_path) as archive:
            rows = _extract_supported_workbook_rows(archive)
        return [
            _map_raw_dataset_row(row)
            for row in rows
            if row.get("sku") and row.get("product_name") and _to_float(row.get("tawfeer_price")) > 0
        ]

    with source_path.open("r", newline="", encoding="utf-8") as csvfile:
        rows = csv.DictReader(csvfile)
        if rows.fieldnames and "Product_Name" in rows.fieldnames:
            return [
                _map_raw_dataset_row({_normalize_header(k): v for k, v in row.items()})
                for row in rows
                if row.get("SKU")
            ]
        return [_map_legacy_row(row) for row in rows]
