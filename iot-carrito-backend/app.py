from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from config import Config
from database.db_connection import db
import logging
from datetime import datetime
import json

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración Flask
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


# ==================== RUTAS DE API ====================

@app.route('/')
def index():
    """Página principal - Todos los endpoints"""
    return jsonify({
        'message': '🚀 Backend IoT Carrito - API COMPLETA funcionando',
        'version': '2.0',
        'endpoints': {
            # Movimientos
            'movimiento_agregar': '/api/movimiento (POST)',
            'movimiento_ultimo': '/api/ultimo-movimiento (GET)',
            'movimientos_historial': '/api/ultimos-10-movimientos (GET)',

            # Secuencias DEMO
            'secuencia_ejecutar': '/api/secuencia (POST)',
            'secuencias_listar': '/api/secuencias (GET)',
            'secuencia_crear': '/api/crear-secuencia (POST)',
            'secuencias_historial': '/api/ultimas-20-secuencias (GET)',

            # Obstáculos
            'obstaculo_detectar': '/api/obstaculo (POST)',
            'obstaculo_ultimo': '/api/ultimo-obstaculo (GET)',
            'obstaculos_historial': '/api/ultimos-10-obstaculos (GET)',
            'ejecucion_reanudar': '/api/reanudar (POST)',
            'movimiento_detener': '/api/detener (POST)',

            # Monitoreo
            'estado_actual': '/api/estado-actual (GET)',
            'metricas_sistema': '/api/metricas (GET)',
            'alertas_historial': '/api/alertas (GET)',
            'estadisticas_obstaculos': '/api/estadisticas-obstaculos (GET)',

            # Salud
            'health_check': '/health (GET)'
        }
    })


@app.route('/health')
def health_check():
    """Endpoint de salud"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'IoT Carrito Backend - API Completa',
        'database': 'connected'
    })


# ==================== MOVIMIENTOS ====================

@app.route('/api/movimiento', methods=['POST'])
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

        socketio.emit('movimiento_agregado', {
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


@app.route('/api/ultimo-movimiento')
def ultimo_movimiento():
    """Obtener el último movimiento"""
    try:
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.callproc('sp_ultimo_estatus_movimiento', [1])
            resultado = cursor.fetchone()

        return jsonify({'ultimo_movimiento': resultado})

    except Exception as e:
        logger.error(f"Error obteniendo último movimiento: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ultimos-10-movimientos')
def ultimos_10_movimientos():
    """Obtener últimos 10 movimientos"""
    try:
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.callproc('sp_ultimos_10_estatus_movimientos', [1])
            movimientos = cursor.fetchall()

        return jsonify({
            'total_movimientos': len(movimientos),
            'movimientos': movimientos
        })

    except Exception as e:
        logger.error(f"Error obteniendo movimientos: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== SECUENCIAS DEMO ====================

@app.route('/api/secuencia', methods=['POST'])
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

        socketio.emit('secuencia_iniciada', {
            'secuencia_id': secuencia_id,
            'timestamp': datetime.now().isoformat(),
            'mensaje': 'Secuencia DEMO iniciada'
        })

        return jsonify({'success': True, 'message': result['mensaje']})

    except Exception as e:
        logger.error(f"Error ejecutando secuencia: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/secuencias')
def listar_secuencias():
    """Listar todas las secuencias disponibles"""
    try:
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.callproc('sp_ultimas_20_secuencias_demo', [1])
            secuencias = cursor.fetchall()

        return jsonify({
            'total_secuencias': len(secuencias),
            'secuencias': secuencias
        })

    except Exception as e:
        logger.error(f"Error listando secuencias: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/crear-secuencia', methods=['POST'])
def crear_secuencia():
    """Crear nueva secuencia personalizada"""
    try:
        data = request.json
        nombre = data.get('nombre_secuencia')
        movimientos = data.get('movimientos')  # JSON array
        descripcion = data.get('descripcion', '')
        creador = data.get('creador', 'Usuario')

        # Convertir movimientos a JSON si es string
        if isinstance(movimientos, str):
            movimientos = json.loads(movimientos)

        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.callproc('sp_agregar_secuencia_demo',
                            [1, nombre, json.dumps(movimientos)])
            result = cursor.fetchone()
            connection.commit()

        return jsonify({'success': True, 'message': result['mensaje']})

    except Exception as e:
        logger.error(f"Error creando secuencia: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ultimas-20-secuencias')
def ultimas_20_secuencias():
    """Obtener últimas 20 secuencias"""
    try:
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.callproc('sp_ultimas_20_secuencias_demo', [1])
            secuencias = cursor.fetchall()

        return jsonify({'secuencias': secuencias})

    except Exception as e:
        logger.error(f"Error obteniendo secuencias: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== OBSTÁCULOS ====================

@app.route('/api/obstaculo', methods=['POST'])
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

        socketio.emit('alerta_obstaculo', {
            'dispositivo_id': dispositivo_id,
            'tipo_obstaculo': status_clave,
            'timestamp': datetime.now().isoformat(),
            'mensaje': 'Obstáculo detectado y evadido automáticamente',
            'severidad': 'alta'
        })

        return jsonify({
            'success': True,
            'message': result['mensaje'],
            'alerta_generada': True
        })

    except Exception as e:
        logger.error(f"Error en obstáculo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ultimo-obstaculo')
def ultimo_obstaculo():
    """Obtener el último obstáculo detectado"""
    try:
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.callproc('sp_ultimo_estatus_obstaculo', [1])
            resultado = cursor.fetchone()

        return jsonify({'ultimo_obstaculo': resultado})

    except Exception as e:
        logger.error(f"Error obteniendo último obstáculo: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ultimos-10-obstaculos')
def ultimos_10_obstaculos():
    """Obtener últimos 10 obstáculos"""
    try:
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.callproc('sp_ultimos_10_estatus_obstaculos', [1])
            obstaculos = cursor.fetchall()

        return jsonify({
            'total_obstaculos': len(obstaculos),
            'obstaculos': obstaculos
        })

    except Exception as e:
        logger.error(f"Error obteniendo obstáculos: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reanudar', methods=['POST'])
def reanudar_ejecucion():
    """Reanudar ejecución después de obstáculo"""
    try:
        data = request.json
        dispositivo_id = data.get('dispositivo_id', 1)

        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.callproc('sp_reanudar_ejecucion', [dispositivo_id])
            resultados = cursor.fetchall()
            connection.commit()

        socketio.emit('ejecucion_reanudada', {
            'dispositivo_id': dispositivo_id,
            'timestamp': datetime.now().isoformat(),
            'mensaje': 'Ejecución reanudada exitosamente'
        })

        return jsonify({
            'success': True,
            'message': 'Ejecución reanudada',
            'resultados': resultados
        })

    except Exception as e:
        logger.error(f"Error reanudando ejecución: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/detener', methods=['POST'])
def detener_movimiento():
    """Detener movimiento actual"""
    try:
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.callproc('sp_agregar_estatus_movimiento', [1, 3, 1])  # Status 3 = Detener
            result = cursor.fetchone()
            connection.commit()

        socketio.emit('movimiento_detenido', {
            'timestamp': datetime.now().isoformat(),
            'mensaje': 'Movimiento detenido manualmente'
        })

        return jsonify({'success': True, 'message': result['mensaje']})

    except Exception as e:
        logger.error(f"Error deteniendo movimiento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== MONITOREO Y ESTADÍSTICAS ====================

@app.route('/api/estado-actual')
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


@app.route('/api/metricas')
def obtener_metricas():
    """Obtener métricas del sistema"""
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

            # Actividad reciente
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


@app.route('/api/alertas')
def obtener_alertas():
    """Obtener historial de alertas/obstáculos"""
    try:
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.callproc('sp_ultimos_10_estatus_obstaculos', [1])
            alertas = cursor.fetchall()

        return jsonify({
            'total_alertas': len(alertas),
            'alertas': alertas
        })

    except Exception as e:
        logger.error(f"Error obteniendo alertas: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/estadisticas-obstaculos')
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

            # Obstáculos por día
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


# ==================== WEB SOCKETS ====================

@socketio.on('connect')
def handle_connect():
    logger.info(f'Cliente conectado: {request.sid}')
    emit('connection_established', {
        'status': 'connected',
        'client_id': request.sid,
        'timestamp': datetime.now().isoformat()
    })


@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f'Cliente desconectado: {request.sid}')


@socketio.on('solicitar_actualizacion')
def handle_actualizacion(data):
    """Cliente solicita actualización de estado"""
    emit('estado_actualizado', {
        'timestamp': datetime.now().isoformat(),
        'mensaje': 'Estado actualizado por solicitud'
    })


# ==================== INICIALIZACIÓN ====================

if __name__ == '__main__':
    logger.info("🚀 Iniciando servidor IoT Carrito - API COMPLETA en puerto 5500...")
    logger.info("📊 Todos los endpoints disponibles en: http://localhost:5500")
    logger.info("❤️  Health Check: http://localhost:5500/health")

    socketio.run(
        app,
        host='0.0.0.0',
        port=5500,
        debug=True,
        allow_unsafe_werkzeug=True
    )