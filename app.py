from flask import Flask, render_template, request, jsonify, session
import subprocess
import threading
import os
import signal
import psutil
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Diccionario para almacenar los procesos activos
active_attacks = {}

class AttackThread(threading.Thread):
    def __init__(self, ip, port, attack_id):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.attack_id = attack_id
        self.process = None
        self.start_time = datetime.now()
        
    def run(self):
        try:
            # Ejecutar el script de ataque
            self.process = subprocess.Popen(
                ['python', 'attack_script.py', self.ip, str(self.port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.process.wait()
        except Exception as e:
            print(f"Error en ataque {self.attack_id}: {e}")
    
    def stop(self):
        if self.process:
            # Matar el proceso y sus hijos
            parent = psutil.Process(self.process.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_attack', methods=['POST'])
def start_attack():
    try:
        ip = request.form['ip']
        port = request.form['port']
        
        # Validar IP y puerto
        if not ip or not port:
            return jsonify({'success': False, 'error': 'IP y Puerto son requeridos'})
        
        # Generar ID único para el ataque
        attack_id = f"{ip}:{port}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Crear y iniciar el hilo de ataque
        attack_thread = AttackThread(ip, port, attack_id)
        attack_thread.start()
        
        # Guardar el hilo en el diccionario de ataques activos
        active_attacks[attack_id] = {
            'thread': attack_thread,
            'ip': ip,
            'port': port,
            'start_time': attack_thread.start_time,
            'status': 'running'
        }
        
        return jsonify({
            'success': True, 
            'message': f'Ataque iniciado a {ip}:{port}',
            'attack_id': attack_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/stop_attack', methods=['POST'])
def stop_attack():
    try:
        attack_id = request.form['attack_id']
        
        if attack_id in active_attacks:
            active_attacks[attack_id]['thread'].stop()
            active_attacks[attack_id]['status'] = 'stopped'
            del active_attacks[attack_id]
            return jsonify({'success': True, 'message': 'Ataque detenido'})
        else:
            return jsonify({'success': False, 'error': 'Ataque no encontrado'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/stop_all', methods=['POST'])
def stop_all():
    try:
        for attack_id in list(active_attacks.keys()):
            active_attacks[attack_id]['thread'].stop()
            del active_attacks[attack_id]
        
        return jsonify({'success': True, 'message': 'Todos los ataques detenidos'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_active_attacks')
def get_active_attacks():
    attacks = []
    for attack_id, attack_info in active_attacks.items():
        attacks.append({
            'id': attack_id,
            'ip': attack_info['ip'],
            'port': attack_info['port'],
            'start_time': attack_info['start_time'].strftime('%Y-%m-%d %H:%M:%S'),
            'duration': str(datetime.now() - attack_info['start_time']).split('.')[0]
        })
    
    return jsonify({'success': True, 'attacks': attacks})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)