from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Dispositivo:
    dispositivo_id: int
    nombre_dispositivo: str
    ip_address: str
    pais: str
    ciudad: str
    longitud: float
    latitud: float
    fecha_registro: datetime
    activo: bool = True

@dataclass
class Movimiento:
    operacion_id: int
    dispositivo_id: int
    status_clave: int
    fecha_hora: datetime
    duracion_segundos: int
    tipo_ejecucion: str  # 'manual' o 'automatica'
    secuencia_id: Optional[int] = None
    ejecucion_id: Optional[int] = None
    estado: str = 'pendiente'  # pendiente, ejecutando, completado, interrumpido, reanudado
    tiempo_ejecutado: int = 0
    fecha_interrupcion: Optional[datetime] = None

@dataclass
class Obstaculo:
    obstaculo_id: int
    dispositivo_id: int
    status_clave: int
    fecha_hora: datetime
    movimiento_interrumpido_id: Optional[int] = None
    ejecucion_interrumpida_id: Optional[int] = None
    resuelto: bool = False

@dataclass
class SecuenciaDemo:
    secuencia_id: int
    dispositivo_id: int
    nombre_secuencia: str
    descripcion: Optional[str] = None
    movimientos: Dict[str, Any] = None
    intervalo_entre_movimientos: int = 1
    fecha_creacion: datetime = None
    activa: bool = True
    es_predefinida: bool = False
    creador: str = 'Usuario'

@dataclass
class EjecucionSecuencia:
    ejecucion_id: int
    secuencia_id: int
    dispositivo_id: int
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    estado: str = 'pendiente'  # pendiente, ejecutando, pausada, completada, cancelada
    total_movimientos: int = 0
    movimiento_actual: int = 1
    movimientos_completados: int = 0

class MovimientoStatus:
    ADELANTE = 1
    ATRAS = 2
    DETENER = 3
    VUELTA_ADELANTE_DERECHA = 4
    VUELTA_ADELANTE_IZQUIERDA = 5
    VUELTA_ATRAS_DERECHA = 6
    VUELTA_ATRAS_IZQUIERDA = 7
    GIRO_90_DERECHA = 8
    GIRO_90_IZQUIERDA = 9
    GIRO_360_DERECHA = 10
    GIRO_360_IZQUIERDA = 11

class ObstaculoStatus:
    ADELANTE = 1
    ADELANTE_IZQUIERDA = 2
    ADELANTE_DERECHA = 3
    ADELANTE_IZQUIERDA_DERECHA = 4
    RETROCEDE = 5