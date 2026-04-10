# VAI Pricing Agent

Local pricing intelligence application with:

- React frontend built with Vite and Tailwind
- FastAPI backend
- Local ChromaDB persistent vector store
- Sample CSV-backed SKU dataset for local development

## Project Structure

```text
backend/
  app/
  data/
  .venv/
frontend/
  src/
```

## Backend Setup

Use Python `3.11` or `3.12` for the backend. Python `3.14` is too new for the current `chromadb` dependency chain and will fail during install.

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Dataset Configuration

The backend now supports:

- legacy flat CSV schema (`backend/data/skus.csv`)
- pilot workbook schema from Excel (`Raw Data` sheet inside an `.xlsx` payload)
- updated pilot workbook schema from Excel (`Pricing Engine V1` sheet)
- normalized pilot CSV exports such as `backend/data/pricing_agent_pilot_dataset_improved_recalc.csv`

If a workbook matching `pricing_agent_pilot_strategy*.xlsx` exists in the project root or `backend/data/`,
the backend now prefers that workbook automatically. The current preferred dataset is:

- `pricing_agent_pilot_strategy_Final March 15 version.xlsx`
- `pricing_agent_pilot_strategy_Final March 17 working file.xlsx`

To force the backend to use your new dataset:

```bash
export PRICING_DATASET_PATH="/Users/omar/Documents/vs code/vai - pricing agent/backend/data/pricing_agent_pilot_dataset_improved_recalc.csv"
```

To regenerate the normalized CSV from the latest workbook:

```bash
python3 backend/scripts/convert_pricing_workbook.py \
  "/Users/omar/Downloads/pricing_agent_pilot_dataset_improved_recalc.xlsx" \
  "backend/data/pricing_agent_pilot_dataset_improved_recalc.csv" \
  "backend/data/pricing_agent_pilot_dataset - jad.csv"
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Running `npm run dev` inside `frontend/` now starts both services:

- Vite frontend on `http://127.0.0.1:5173`
- FastAPI backend on `http://127.0.0.1:8000`

If you want to run either service separately:

```bash
cd frontend
npm run dev:frontend
```

```bash
cd frontend
npm run dev:backend
```

## Root Commands

You can also run from the project root now:

```bash
npm run install:frontend
```

```bash
cd backend
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
npm run install:frontend
npm run dev
```

## API

- `GET /api/dashboard`
- `GET /api/skus`
- `GET /api/skus/{id}`
- `POST /api/simulate`
- `POST /api/run-agent`

## Security Notes

- Backend is bound to `127.0.0.1`
- CORS is restricted to the local Vite origin
- Basic security headers are enabled
- Lightweight in-process rate limiting is enabled
- Simulation input is validated server-side
