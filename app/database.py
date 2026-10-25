import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "clima_criminal.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reportes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_delito TEXT NOT NULL,
        tipo_personalizado TEXT,
        descripcion TEXT,
        nivel_gravedad INTEGER DEFAULT 5,
        modo_ubicacion TEXT DEFAULT 'exacta',
        latitud REAL NOT NULL,
        longitud REAL NOT NULL,
        sector TEXT NOT NULL,
        municipio TEXT DEFAULT 'Santo Domingo Este',
        referencia_publica TEXT,
        franja_horaria TEXT NOT NULL,
        fecha_reporte TEXT NOT NULL,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sector ON reportes(sector)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tipo ON reportes(tipo_delito)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fecha ON reportes(fecha_reporte)")
    conn.commit()
    
    # Check if we should seed calibration data
    cursor.execute("SELECT COUNT(*) FROM reportes")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_calibration_data(conn)
    conn.close()

def seed_calibration_data(conn):
    cursor = conn.cursor()
    now = datetime.now()
    
    # Lista de incidentes calibrados representativos de Santo Domingo Este y Gran SD
    incidentes_semilla = [
        # Los Mina (Zona activa)
        {
            "tipo_delito": "Despojo en motocicleta",
            "tipo_personalizado": None,
            "descripcion": "Dos individuos en pasola blanca despojaron de celular y mochila a un joven que salía del trabajo.",
            "gravedad": 8,
            "modo": "exacta",
            "lat": 18.5085,
            "lon": -69.8654,
            "sector": "Los Mina",
            "municipio": "Santo Domingo Este",
            "ref": "Av. San Vicente de Paúl casi esquina Marco del Rosario",
            "franja": "Noche",
            "dias_atras": 1
        },
        {
            "tipo_delito": "Atraco a mano armada",
            "tipo_personalizado": None,
            "descripcion": "Asalto con arma de fuego a transeúnte mientras esperaba transporte.",
            "gravedad": 9,
            "modo": "exacta",
            "lat": 18.5120,
            "lon": -69.8690,
            "sector": "Los Mina",
            "municipio": "Santo Domingo Este",
            "ref": "Próximo a la estación del Metro Rosa Duarte",
            "franja": "Madrugada",
            "dias_atras": 2
        },
        {
            "tipo_delito": "Otro",
            "tipo_personalizado": "Robo con cizalla en local",
            "descripcion": "Rompieron candados con una cizalla grande en horas de la madrugada y sustrajeron mercancía.",
            "gravedad": 6,
            "modo": "protegida",
            "lat": 18.5030,
            "lon": -69.8620,
            "sector": "Los Mina",
            "municipio": "Santo Domingo Este",
            "ref": "Zona comercial Katanga",
            "franja": "Madrugada",
            "dias_atras": 3
        },
        
        # Ensanche Ozama
        {
            "tipo_delito": "Robo de vehículo/accesorios",
            "tipo_personalizado": None,
            "descripcion": "Desmantelaron retrovisores y batería de un Honda Civic estacionado frente a una vivienda.",
            "gravedad": 5,
            "modo": "exacta",
            "lat": 18.4912,
            "lon": -69.8710,
            "sector": "Ensanche Ozama",
            "municipio": "Santo Domingo Este",
            "ref": "Calle Octavio Mejía Ricart",
            "franja": "Noche",
            "dias_atras": 1
        },
        {
            "tipo_delito": "Despojo en motocicleta",
            "tipo_personalizado": None,
            "descripcion": "Sujeto en motocicleta Suzuki AX100 arrebató cartera a una señora.",
            "gravedad": 7,
            "modo": "exacta",
            "lat": 18.4875,
            "lon": -69.8665,
            "sector": "Ensanche Ozama",
            "municipio": "Santo Domingo Este",
            "ref": "Calle Masonería cerca del parque",
            "franja": "Tarde",
            "dias_atras": 2
        },

        # Alma Rosa I y II
        {
            "tipo_delito": "Robo de vehículo/accesorios",
            "tipo_personalizado": "Robo de retrovisores",
            "descripcion": "Robaron retrovisores de dos vehículos Toyota Corolla en la misma cuadra.",
            "gravedad": 5,
            "modo": "exacta",
            "lat": 18.4860,
            "lon": -69.8550,
            "sector": "Alma Rosa I",
            "municipio": "Santo Domingo Este",
            "ref": "Calle Costa Rica",
            "franja": "Madrugada",
            "dias_atras": 0
        },
        {
            "tipo_delito": "Atraco a mano armada",
            "tipo_personalizado": None,
            "descripcion": "Dos asaltantes encañonaron a una pareja que llegaba a su residencia y les quitaron pertenencias.",
            "gravedad": 9,
            "modo": "protegida",
            "lat": 18.4970,
            "lon": -69.8450,
            "sector": "Alma Rosa II",
            "municipio": "Santo Domingo Este",
            "ref": "Cerca de la Av. San Vicente de Paúl",
            "franja": "Noche",
            "dias_atras": 3
        },

        # Villa Duarte / Maquiteria
        {
            "tipo_delito": "Despojo en motocicleta",
            "tipo_personalizado": None,
            "descripcion": "Atraco al paso en motocicleta, despojaron de celular a estudiante.",
            "gravedad": 7,
            "modo": "exacta",
            "lat": 18.4810,
            "lon": -69.8790,
            "sector": "Villa Duarte / Maquiteria",
            "municipio": "Santo Domingo Este",
            "ref": "Av. Real cerca del puente flotante",
            "franja": "Tarde",
            "dias_atras": 1
        },
        {
            "tipo_delito": "Hurto simple",
            "tipo_personalizado": None,
            "descripcion": "Sustracción de bomba de agua del patio sin violencia.",
            "gravedad": 4,
            "modo": "protegida",
            "lat": 18.4760,
            "lon": -69.8730,
            "sector": "Villa Duarte / Maquiteria",
            "municipio": "Santo Domingo Este",
            "ref": "Sector Calero",
            "franja": "Madrugada",
            "dias_atras": 4
        },

        # Invivienda / Hainamosa
        {
            "tipo_delito": "Atraco a mano armada",
            "tipo_personalizado": None,
            "descripcion": "Atraco colectivo en parada de carros públicos, pistola en mano.",
            "gravedad": 9,
            "modo": "exacta",
            "lat": 18.5190,
            "lon": -69.8080,
            "sector": "Invivienda",
            "municipio": "Santo Domingo Este",
            "ref": "Av. Pedro Mir frente a la manzana 4700",
            "franja": "Noche",
            "dias_atras": 1
        },
        {
            "tipo_delito": "Despojo en motocicleta",
            "tipo_personalizado": None,
            "descripcion": "Motoristas armados interceptaron a repartidor de delivery.",
            "gravedad": 8,
            "modo": "exacta",
            "lat": 18.5165,
            "lon": -69.8020,
            "sector": "Invivienda",
            "municipio": "Santo Domingo Este",
            "ref": "Cerca del parque de Invivienda",
            "franja": "Noche",
            "dias_atras": 2
        },
        {
            "tipo_delito": "Otro",
            "tipo_personalizado": "Estafa y despojo en vía pública",
            "descripcion": "Sujetos fingiendo ser mecánicos pincharon goma y luego intentaron extorsionar.",
            "gravedad": 5,
            "modo": "exacta",
            "lat": 18.5310,
            "lon": -69.7920,
            "sector": "Hainamosa / El Tamarindo",
            "municipio": "Santo Domingo Este",
            "ref": "Carretera Mella km 11",
            "franja": "Tarde",
            "dias_atras": 5
        },

        # Villa Faro / Mendoza
        {
            "tipo_delito": "Despojo en motocicleta",
            "tipo_personalizado": None,
            "descripcion": "Dos motorizados interceptaron a una mujer saliendo del banco.",
            "gravedad": 8,
            "modo": "exacta",
            "lat": 18.5090,
            "lon": -69.8390,
            "sector": "Villa Faro",
            "municipio": "Santo Domingo Este",
            "ref": "Carretera de Mendoza con 4 de Agosto",
            "franja": "Mañana",
            "dias_atras": 2
        },
        {
            "tipo_delito": "Robo a vivienda/negocio",
            "tipo_personalizado": None,
            "descripcion": "Entraron por la verja trasera de un colmado y se llevaron dinero en efectivo y licores.",
            "gravedad": 7,
            "modo": "protegida",
            "lat": 18.5150,
            "lon": -69.8210,
            "sector": "Mendoza / Ralma",
            "municipio": "Santo Domingo Este",
            "ref": "Sector Ralma",
            "franja": "Madrugada",
            "dias_atras": 3
        },

        # Los Frailes / Las Américas
        {
            "tipo_delito": "Atraco a mano armada",
            "tipo_personalizado": None,
            "descripcion": "Atraco en el puente peatonal de Las Américas a varias personas a punta de pistola.",
            "gravedad": 9,
            "modo": "exacta",
            "lat": 18.4715,
            "lon": -69.8010,
            "sector": "Los Frailes (I y II)",
            "municipio": "Santo Domingo Este",
            "ref": "Autopista Las Américas km 10",
            "franja": "Noche",
            "dias_atras": 1
        },
        {
            "tipo_delito": "Robo de vehículo/accesorios",
            "tipo_personalizado": "Robo de camioneta",
            "descripcion": "Se llevaron una camioneta Hilux estacionada en calle residencial.",
            "gravedad": 8,
            "modo": "exacta",
            "lat": 18.4830,
            "lon": -69.7890,
            "sector": "Brisas del Este",
            "municipio": "Santo Domingo Este",
            "ref": "Calle Hípica",
            "franja": "Madrugada",
            "dias_atras": 4
        },

        # Cancino / Charles de Gaulle
        {
            "tipo_delito": "Despojo en motocicleta",
            "tipo_personalizado": None,
            "descripcion": "Atraco a pasajero mientras bajaba de guagua de la Charles.",
            "gravedad": 7,
            "modo": "exacta",
            "lat": 18.5260,
            "lon": -69.8430,
            "sector": "Cancino / Lucerna / Charles",
            "municipio": "Santo Domingo Este",
            "ref": "Av. Charles de Gaulle frente a multicentro",
            "franja": "Tarde",
            "dias_atras": 0
        },

        # El Almirante
        {
            "tipo_delito": "Atraco a mano armada",
            "tipo_personalizado": None,
            "descripcion": "Atraco en la banca de lotería por sujetos en jeepeta.",
            "gravedad": 9,
            "modo": "exacta",
            "lat": 18.5360,
            "lon": -69.7830,
            "sector": "El Almirante",
            "municipio": "Santo Domingo Este",
            "ref": "Av. Las Carreras",
            "franja": "Noche",
            "dias_atras": 2
        },

        # Distrito Nacional (Comparativa)
        {
            "tipo_delito": "Hurto simple",
            "tipo_personalizado": None,
            "descripcion": "Carterismo a turista mientras caminaba por la zona peatonal.",
            "gravedad": 3,
            "modo": "exacta",
            "lat": 18.4735,
            "lon": -69.8870,
            "sector": "Ciudad Colonial / Gazcue",
            "municipio": "Distrito Nacional",
            "ref": "Calle El Conde",
            "franja": "Tarde",
            "dias_atras": 1
        },
        {
            "tipo_delito": "Despojo en motocicleta",
            "tipo_personalizado": None,
            "descripcion": "Atraco a persona en la parada del metro Los Taínos.",
            "gravedad": 8,
            "modo": "exacta",
            "lat": 18.5010,
            "lon": -69.9120,
            "sector": "Cristo Rey / Capotillo",
            "municipio": "Distrito Nacional",
            "ref": "Av. Nicolás de Ovando",
            "franja": "Noche",
            "dias_atras": 2
        }
    ]

    for item in incidentes_semilla:
        fecha_calculada = (now - timedelta(days=item["dias_atras"])).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO reportes (
            tipo_delito, tipo_personalizado, descripcion, nivel_gravedad,
            modo_ubicacion, latitud, longitud, sector, municipio,
            referencia_publica, franja_horaria, fecha_reporte
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["tipo_delito"],
            item["tipo_personalizado"],
            item["descripcion"],
            item["gravedad"],
            item["modo"],
            item["lat"],
            item["lon"],
            item["sector"],
            item["municipio"],
            item["ref"],
            item["franja"],
            fecha_calculada
        ))
    
    conn.commit()
