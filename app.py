from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, session, send_from_directory
import os
import requests
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'supersecretkey'

# Certifique-se de que a pasta de uploads existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Use variável de ambiente para armazenar a API key
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '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')
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_MODEL = "whisper-large-v3-turbo"

# Função para obter histórico
def obter_historico():
    historico = []
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        if file.endswith(('.mp3', '.wav', '.m4a')):
            txt_file = file.rsplit('.', 1)[0] + '.txt'
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], txt_file)):
                historico.append({'filename': file})
    return historico

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Processa a transcrição
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        data = {"model": GROQ_MODEL, "response_format": "text"}
        
        try:
            with open(filepath, "rb") as audio_file:
                files = {"file": (file.filename, audio_file, "audio/mpeg")}
                response = requests.post(GROQ_ENDPOINT, headers=headers, files=files, data=data)
        
            if response.status_code == 200:
                transcription_text = response.text.strip()
                
                # Salvar transcrição em txt
                txt_filename = file.filename.rsplit('.', 1)[0] + '.txt'
                txt_filepath = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
                with open(txt_filepath, 'w', encoding='utf-8') as f:
                    f.write(transcription_text)
                
                return redirect(url_for('result', filename=file.filename))
            else:
                return jsonify({"error": "Erro na transcrição."}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/result/<filename>')
def result(filename):
    txt_filename = filename.rsplit('.', 1)[0] + '.txt'
    txt_filepath = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
    
    if os.path.exists(txt_filepath):
        with open(txt_filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = 'Transcrição não encontrada.'
    
    history = obter_historico()
    return render_template('result.html', filename=filename, text=text, history=history)

@app.route('/get_transcription/<filename>')
def get_transcription(filename):
    txt_filename = filename.rsplit('.', 1)[0] + '.txt'
    txt_filepath = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
    if os.path.exists(txt_filepath):
        with open(txt_filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        return jsonify({'text': text})
    return jsonify({'error': 'Arquivo não encontrado.'}), 404

@app.route('/download_txt/<filename>')
def download_txt(filename):
    txt_filename = filename.rsplit('.', 1)[0] + '.txt'
    txt_filepath = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
    if os.path.exists(txt_filepath):
        return send_file(txt_filepath, as_attachment=True)
    return jsonify({'error': 'Arquivo não encontrado.'}), 404

# Servir arquivos de áudio da pasta uploads
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)