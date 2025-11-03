from typing import List, Optional
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Extra


class Pokemon(BaseModel):
    Nombre: Optional[str] = None
    Tipo: Optional[str] = None
    Pais: Optional[str] = None
    Total: Optional[int] = None

    class Config:
        extra = Extra.allow


app = FastAPI()


# Load CSV at startup (relative to this file)
CSV_PATH = Path(__file__).parent / "pokedex_enriquecida.csv"
try:
    df = pd.read_csv(CSV_PATH)
except Exception:
    df = pd.DataFrame()


@app.get("/health")
def health():
    return {"status": "ok", "rows": len(df)}


@app.get("/types", response_model=List[str])
def get_types():
    if df.empty:
        return []
    if 'Tipo' not in df.columns:
        return []
    types = df['Tipo'].dropna().unique().tolist()
    return sorted(types)


@app.get("/countries", response_model=List[str])
def get_countries():
    if df.empty:
        return []
    if 'Pais' in df.columns:
        countries = df['Pais'].dropna().unique().tolist()
    elif 'País' in df.columns:
        countries = df['País'].dropna().unique().tolist()
    else:
        countries = []
    return sorted(countries)


@app.get("/pokemon", response_model=List[Pokemon])
def get_pokemon(
    tipo: Optional[str] = Query(None, description="Filtrar por Tipo exacto"),
    pais: Optional[str] = Query(None, description="Filtrar por País exacto"),
    min_total: Optional[int] = Query(None),
    max_total: Optional[int] = Query(None),
    limit: Optional[int] = Query(500),
):
    if df.empty:
        raise HTTPException(status_code=500, detail="CSV no cargado")

    q = df.copy()

    if tipo:
        if 'Tipo' in q.columns:
            q = q[q['Tipo'] == tipo]

    if pais:
        # account for 'Pais' or 'País'
        if 'Pais' in q.columns:
            q = q[q['Pais'] == pais]
        elif 'País' in q.columns:
            q = q[q['País'] == pais]

    if min_total is not None and 'Total' in q.columns:
        q = q[q['Total'] >= min_total]

    if max_total is not None and 'Total' in q.columns:
        q = q[q['Total'] <= max_total]

    # limit rows
    q = q.head(limit)

    # convert column names to API-friendly names
    q = q.rename(columns={
        'Sp. Atk': 'Sp_Atk',
        'Sp. Def': 'Sp_Def',
        'País': 'Pais'
    })

    # ensure JSON serializable
    records = q.to_dict(orient='records')
    return records
