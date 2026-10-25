from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import random
from datetime import datetime
from typing import Optional, List

from .database import get_connection, init_db
from .schemas import ReporteCreate

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEOJSON_PATH = os.path.join(BASE_DIR, "data", "sectores_gran_sd.geojson")

app = FastAPI(title="Clima Criminal - Gran Santo Domingo", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and Templates
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/sectores")
def get_sectores():
    if not os.path.exists(GEOJSON_PATH):
        raise HTTPException(status_code=404, detail="GeoJSON no encontrado")
    
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geojson = json.load(f)
    
    # Enriquecer cada sector con métricas de la base de datos
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT sector, COUNT(*) as total, AVG(nivel_gravedad) as avg_gravedad
        FROM reportes
        GROUP BY sector
    """)
    stats = {row["sector"]: {"total": row["total"], "gravedad": row["avg_gravedad"]} for row in cursor.fetchall()}
    conn.close()

    for feature in geojson["features"]:
        nombre = feature["properties"]["nombre"]
        sector_stat = stats.get(nombre, {"total": 0, "gravedad": 0})
        total = sector_stat["total"]
        gravedad = sector_stat["gravedad"] or 0
        
        # Determinar nivel de riesgo dinámico
        if total >= 3 or gravedad >= 8:
            nivel = "Crítico"
            color = "#ff3b30"
        elif total >= 2 or gravedad >= 6:
            nivel = "Alto"
            color = "#ff9500"
        elif total >= 1:
            nivel = "Moderado"
            color = "#ffcc00"
        else:
            nivel = "Bajo"
            color = "#34c759"
            
        feature["properties"]["total_incidentes"] = total
        feature["properties"]["nivel_riesgo"] = nivel
        feature["properties"]["color_riesgo"] = color

    return geojson

@app.get("/api/reportes")
def get_reportes(
    sector: Optional[str] = None,
    tipo_delito: Optional[str] = None,
    franja: Optional[str] = None,
    q: Optional[str] = None
):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM reportes WHERE 1=1"
    params = []
    
    if sector and sector != "Todos":
        query += " AND sector = ?"
        params.append(sector)
        
    if tipo_delito and tipo_delito != "Todos":
        query += " AND tipo_delito = ?"
        params.append(tipo_delito)
        
    if franja and franja != "Todas":
        query += " AND franja_horaria = ?"
        params.append(franja)
        
    if q and q.strip():
        palabra = f"%{q.strip()}%"
        query += " AND (descripcion LIKE ? OR tipo_personalizado LIKE ? OR referencia_publica LIKE ?)"
        params.extend([palabra, palabra, palabra])
        
    query += " ORDER BY fecha_reporte DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@app.post("/api/reportes/crear")
def crear_reporte(payload: ReporteCreate):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Calcular nivel de gravedad automático según tipología
    gravedad_map = {
        "Atraco a mano armada": 9,
        "Despojo en motocicleta": 8,
        "Robo a vivienda/negocio": 7,
        "Robo de vehículo/accesorios": 5,
        "Hurto simple": 3,
        "Otro": 5
    }
    gravedad = gravedad_map.get(payload.tipo_delito, 5)
    
    lat = payload.latitud
    lon = payload.longitud
    
    # Protección de privacidad espacial si el usuario eligió modo protegido
    if payload.modo_ubicacion == "protegida":
        # Desfase aleatorio de seguridad (~250-400 metros)
        offset_lat = random.uniform(-0.0025, 0.0025)
        offset_lon = random.uniform(-0.0025, 0.0025)
        lat += offset_lat
        lon += offset_lon
    
    fecha = payload.fecha_reporte or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
    INSERT INTO reportes (
        tipo_delito, tipo_personalizado, descripcion, nivel_gravedad,
        modo_ubicacion, latitud, longitud, sector, municipio,
        referencia_publica, franja_horaria, fecha_reporte
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.tipo_delito,
        payload.tipo_personalizado,
        payload.descripcion,
        gravedad,
        payload.modo_ubicacion,
        lat,
        lon,
        payload.sector,
        payload.municipio or "Santo Domingo Este",
        payload.referencia_publica,
        payload.franja_horaria,
        fecha
    ))
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    
    return {"status": "ok", "id": nuevo_id, "mensaje": "Reporte anónimo registrado exitosamente"}

@app.get("/api/estadisticas")
def get_estadisticas():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM reportes")
    total = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT sector, COUNT(*) as cantidad
        FROM reportes
        WHERE municipio = 'Santo Domingo Este'
        GROUP BY sector
        ORDER BY cantidad DESC
        LIMIT 3
    """)
    top_sectores_sde = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT tipo_delito, COUNT(*) as cantidad
        FROM reportes
        GROUP BY tipo_delito
        ORDER BY cantidad DESC
        LIMIT 1
    """)
    top_delito_row = cursor.fetchone()
    top_delito = dict(top_delito_row) if top_delito_row else {"tipo_delito": "N/A", "cantidad": 0}
    
    cursor.execute("""
        SELECT franja_horaria, COUNT(*) as cantidad
        FROM reportes
        GROUP BY franja_horaria
        ORDER BY cantidad DESC
        LIMIT 1
    """)
    top_franja_row = cursor.fetchone()
    top_franja = dict(top_franja_row) if top_franja_row else {"franja_horaria": "N/A", "cantidad": 0}
    
    conn.close()
    
    return {
        "total_reportes": total,
        "top_sectores_sde": top_sectores_sde,
        "delito_frecuente": top_delito["tipo_delito"],
        "horario_critico": top_franja["franja_horaria"]
    }
