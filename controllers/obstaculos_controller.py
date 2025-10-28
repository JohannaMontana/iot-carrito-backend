from flask import Blueprint, request, jsonify
from flask_socketio import SocketIO, emit
from database.db_connection import db
import pymysql
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ObstaculosController:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.blueprint = Blueprint('obstaculos', __name__)
        self._register_routes()

    def _register_routes(self):
        @self.blueprint.route('/api/obstaculo', methods=['POST'])
        def detectar_obstaculo():
            """Simular detección de obstáculo"""
            try:
                data = request.json
                dispositivo_id = data.get('dispositivo_id', 1)
                status_clave = data.get('status_clave', 1)

                connection = db.get_connection()
                with connection.cursor() as cursor:
                    cursor.callproc('sp_agregar_logica_obstaculo',
                                    [dispositivo_id, status_clave])
                    result = cursor.fetchone()
                    connection.commit()

                # Emitir alerta en tiempo real
                self.socketio.emit('alerta_obstaculo', {
                    'dispositivo_id': dispositivo_id,
                    'tipo_obstaculo': status_clave,
                    'timestamp': datetime.now().isoformat(),
                    'mensaje': 'Obstáculo detectado y evadido automáticamente',
                    'severidad': 'alta' if status_clave in [1, 4] else 'media'
                })

                return jsonify({
                    'success': True,
                    'message': result['mensaje'],
                    'alerta_generada': True
                })

            except Exception as e:
                logger.error(f"Error en obstáculo: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.blueprint.route('/api/reanudar', methods=['POST'])
        def reanudar_ejecucion():
            """Reanudar ejecución después de obstáculo"""
            try:
                data = request.json
                dispositivo_id = data.get('dispositivo_id', 1)

                connection = db.get_connection()
                with connection.cursor() as cursor:
                    cursor.callproc('sp_reanudar_ejecucion', [dispositivo_id])
                    result = cursor.fetchall()  # Puede devolver múltiples resultados
                    connection.commit()

                self.socketio.emit('ejecucion_reanudada', {
                    'dispositivo_id': dispositivo_id,
                    'timestamp': datetime.now().isoformat(),
                    'mensaje': 'Ejecución reanudada después de obstáculo'
                })

                return jsonify({
                    'success': True,
                    'message': 'Ejecución reanudada correctamente',
                    'resultados': result
                })

            except Exception as e:
                logger.error(f"Error reanudando: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.blueprint.route('/api/obstaculos/resolver/<int:obstaculo_id>', methods=['POST'])
        def resolver_obstaculo(obstaculo_id):
            """Marcar obstáculo como resuelto manualmente"""
            try:
                connection = db.get_connection()
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE obstaculos 
                        SET resuelto = TRUE 
                        WHERE obstaculo_id = %s
                    """, (obstaculo_id,))
                    connection.commit()

                self.socketio.emit('obstaculo_resuelto', {
                    'obstaculo_id': obstaculo_id,
                    'timestamp': datetime.now().isoformat(),
                    'mensaje': 'Obstáculo marcado como resuelto'
                })

                return jsonify({
                    'success': True,
                    'message': f'Obstáculo {obstaculo_id} marcado como resuelto'
                })

            except Exception as e:
                logger.error(f"Error resolviendo obstáculo: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.blueprint.route('/api/obstaculos/estadisticas')
        def estadisticas_obstaculos():
            """Obtener estadísticas de obstáculos"""
            try:
                connection = db.get_connection()
                with connection.cursor() as cursor:
                    # Total de obstáculos por tipo
                    cursor.execute("""
                        SELECT 
                            ro.status_texto,
                            COUNT(*) as cantidad,
                            AVG(CASE WHEN o.resuelto = TRUE THEN 1 ELSE 0 END) as tasa_resolucion
                        FROM obstaculos o
                        JOIN referencia_obstaculos ro ON o.status_clave = ro.status_clave
                        WHERE o.dispositivo_id = 1
                        GROUP BY ro.status_texto
                        ORDER BY cantidad DESC
                    """)
                    obstaculos_por_tipo = cursor.fetchall()

                    # Obstáculos por día (última semana)
                    cursor.execute("""
                        SELECT 
                            DATE(fecha_hora) as fecha,
                            COUNT(*) as obstaculos
                        FROM obstaculos 
                        WHERE dispositivo_id = 1 
                        AND fecha_hora >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                        GROUP BY DATE(fecha_hora)
                        ORDER BY fecha
                    """)
                    obstaculos_por_dia = cursor.fetchall()

                return jsonify({
                    'obstaculos_por_tipo': obstaculos_por_tipo,
                    'obstaculos_por_dia': obstaculos_por_dia,
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f"Error obteniendo estadísticas: {e}")
                return jsonify({'error': str(e)}), 500