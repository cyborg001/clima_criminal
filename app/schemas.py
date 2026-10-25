from pydantic import BaseModel, Field
from typing import Optional

class ReporteCreate(BaseModel):
    tipo_delito: str = Field(..., description="Categoría estándar o 'Otro'")
    tipo_personalizado: Optional[str] = Field(None, description="Delito personalizado si es 'Otro'")
    descripcion: Optional[str] = Field(None, description="Descripción del hecho (sin nombres personales)")
    modo_ubicacion: str = Field("exacta", description="'exacta' para calle/esquina o 'protegida' para zona aproximada")
    latitud: float = Field(..., description="Latitud")
    longitud: float = Field(..., description="Longitud")
    sector: str = Field(..., description="Nombre del sector o barrio")
    municipio: Optional[str] = Field("Santo Domingo Este", description="Municipio")
    referencia_publica: Optional[str] = Field(None, description="Referencia de calle o comercio público")
    franja_horaria: str = Field(..., description="Mañana, Tarde, Noche, Madrugada")
    fecha_reporte: Optional[str] = Field(None, description="Fecha del incidente (YYYY-MM-DD)")

class ReporteResponse(ReporteCreate):
    id: int
    nivel_gravedad: int
    creado_en: str
