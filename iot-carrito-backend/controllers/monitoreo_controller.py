from flask import Blueprint, jsonify
from flask_socketio import SocketIO, emit
from database.db_connection import db
import pymysql
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MonitoreoController:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.blueprint = Blueprint('monitoreo', __name__)
        self._register_routes()

    def _register_routes(self):
        @self.blueprint.route('/api/estado-actual')
        def estado_actual():
            """Obtener estado actual completo del carrito"""
            try:
                connection = db.get_connection()
                with connection.cursor() as cursor:
                    # Último movimiento
                    cursor.callproc('sp_ultimo_estatus_movimiento', [1])
                    ultimo_movimiento = cursor.fetchone()

                    # Último obstáculo
                    cursor.callproc('sp_ultimo_estatus_obstaculo', [1])
                    ultimo_obstaculo = cursor.fetchone()

                    # Últimos movimientos
                    cursor.callproc('sp_ultimos_10_estatus_movimientos', [1])
                    movimientos_recientes = cursor.fetchall()

                    # Estadísticas básicas
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_movimientos,
                            COUNT(DISTINCT DATE(fecha_hora)) as dias_activo,
                            AVG(duracion_segundos) as duracion_promedio
                        FROM operaciones_movimiento 
                        WHERE dispositivo_id = 1
                    """)
                    estadisticas = cursor.fetchone()

                return jsonify({
                    'ultimo_movimiento': ultimo_movimiento,
                    'ultimo_obstaculo': ultimo_obstaculo,
                    'movimientos_recientes': movimientos_recientes,
                    'estadisticas': estadisticas,
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f"Error obteniendo estado: {e}")
                return jsonify({'error': str(e)}), 500

        @self.blueprint.route('/api/alertas')
        def obtener_alertas():
            """Obtener historial de alertas/obstáculos"""
            try:
                connection = db.get_connection()
                with connection.cursor() as cursor:
                    cursor.callproc('sp_ultimos_10_estatus_obstaculos', [1])
                    alertas = cursor.fetchall()

                return jsonify({'alertas': alertas})

            except Exception as e:
                logger.error(f"Error obteniendo alertas: {e}")
                return jsonify({'error': str(e)}), 500

        @self.blueprint.route('/api/metricas')
        def obtener_metricas():
            """Obtener métricas para dashboard"""
            try:
                connection = db.get_connection()
                with connection.cursor() as cursor:
                    # Movimientos por tipo
                    cursor.execute("""
                        SELECT 
                            rm.status_texto,
                            COUNT(*) as cantidad,
                            AVG(om.duracion_segundos) as duracion_promedio
                        FROM operaciones_movimiento om
                        JOIN referencia_movimientos rm ON om.status_clave = rm.status_clave
                        WHERE om.dispositivo_id = 1
                        GROUP BY rm.status_texto
                        ORDER BY cantidad DESC
                    """)
                    movimientos_por_tipo = cursor.fetchall()

                    # Actividad por hora (últimas 24h)
                    cursor.execute("""
                        SELECT 
                            HOUR(fecha_hora) as hora,
                            COUNT(*) as movimientos
                        FROM operaciones_movimiento 
                        WHERE dispositivo_id = 1 
                        AND fecha_hora >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                        GROUP BY HOUR(fecha_hora)
                        ORDER BY hora
                    """)
                    actividad_por_hora = cursor.fetchall()

                return jsonify({
                    'movimientos_por_tipo': movimientos_por_tipo,
                    'actividad_por_hora': actividad_por_hora,
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f"Error obteniendo métricas: {e}")
                return jsonify({'error': str(e)}), 500

        @self.blueprint.route('/api/dispositivos')
        def obtener_dispositivos():
            """Obtener información de dispositivos"""
            try:
                connection = db.get_connection()
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM dispositivos WHERE activo = TRUE
                    """)
                    dispositivos = cursor.fetchall()

                return jsonify({'dispositivos': dispositivos})

            except Exception as e:
                logger.error(f"Error obteniendo dispositivos: {e}")
                return jsonify({'error': str(e)}), 500