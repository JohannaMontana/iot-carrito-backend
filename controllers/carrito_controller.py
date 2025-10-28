from flask import Blueprint, request, jsonify
from flask_socketio import SocketIO, emit
from database.db_connection import db
import pymysql
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CarritoController:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.blueprint = Blueprint('carrito', __name__)
        self._register_routes()

    def _register_routes(self):
        @self.blueprint.route('/api/movimiento', methods=['POST'])
        def agregar_movimiento():
            """Agregar movimiento manual al carrito"""
            try:
                data = request.json
                dispositivo_id = data.get('dispositivo_id', 1)
                status_clave = data.get('status_clave')
                duracion = data.get('duracion_segundos', 5)

                connection = db.get_connection()
                with connection.cursor() as cursor:
                    cursor.callproc('sp_agregar_estatus_movimiento',
                                    [dispositivo_id, status_clave, duracion])
                    result = cursor.fetchone()
                    connection.commit()

                # Emitir actualización en tiempo real
                self.socketio.emit('movimiento_agregado', {
                    'dispositivo_id': dispositivo_id,
                    'status_clave': status_clave,
                    'duracion': duracion,
                    'timestamp': datetime.now().isoformat(),
                    'tipo': 'manual'
                })

                return jsonify({'success': True, 'message': result['mensaje']})

            except Exception as e:
                logger.error(f"Error en movimiento: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.blueprint.route('/api/secuencia', methods=['POST'])
        def ejecutar_secuencia():
            """Ejecutar secuencia DEMO"""
            try:
                data = request.json
                secuencia_id = data.get('secuencia_id')

                connection = db.get_connection()
                with connection.cursor() as cursor:
                    cursor.callproc('sp_repetir_secuencia_demo', [secuencia_id])
                    result = cursor.fetchone()
                    connection.commit()

                self.socketio.emit('secuencia_iniciada', {
                    'secuencia_id': secuencia_id,
                    'timestamp': datetime.now().isoformat()
                })

                return jsonify({'success': True, 'message': result['mensaje']})

            except Exception as e:
                logger.error(f"Error en secuencia: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.blueprint.route('/api/secuencias', methods=['GET'])
        def obtener_secuencias():
            """Obtener todas las secuencias disponibles"""
            try:
                connection = db.get_connection()
                with connection.cursor() as cursor:
                    cursor.callproc('sp_ultimas_20_secuencias_demo', [1])
                    secuencias = cursor.fetchall()

                return jsonify({'secuencias': secuencias})

            except Exception as e:
                logger.error(f"Error obteniendo secuencias: {e}")
                return jsonify({'error': str(e)}), 500

        @self.blueprint.route('/api/detener', methods=['POST'])
        def detener_movimiento():
            """Detener movimiento actual"""
            try:
                connection = db.get_connection()
                with connection.cursor() as cursor:
                    cursor.callproc('sp_agregar_estatus_movimiento', [1, 3, 1])
                    result = cursor.fetchone()
                    connection.commit()

                self.socketio.emit('movimiento_detenido', {
                    'timestamp': datetime.now().isoformat(),
                    'mensaje': 'Movimiento detenido'
                })

                return jsonify({'success': True, 'message': result['mensaje']})

            except Exception as e:
                logger.error(f"Error deteniendo movimiento: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500