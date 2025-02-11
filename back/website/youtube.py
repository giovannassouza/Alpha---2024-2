import yt_dlp
import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

def download_video(url, output_path):
    """
    Faz o download do vídeo usando yt-dlp e salva no diretório especificado.
    Retorna a URL de incorporação do vídeo.
    """
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),  # Salva o vídeo com o título e a extensão
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Baixa o vídeo
            result = ydl.extract_info(url, download=True)
            
            # O ID do vídeo no YouTube
            video_id = result['id']  # ID do vídeo para usar no link de incorporação
            print(f"Vídeo baixado com sucesso: {video_id}")
            
            return video_id  # Retorna o ID do vídeo baixado
    except Exception as e:
        print(f"Erro ao baixar o vídeo: {e}")
        return None

@app.route('/')
def home():
    """
    Home endpoint to check API status.
    ---
    tags:
      - Home
    responses:
      200:
        description: API is working.
    """
    return "API OK"

# Rota para baixar o vídeo
@app.route('/videos/download', methods=['POST'])
def api_download_video():
    """
    Endpoint to download a YouTube video.
    ---
    tags:
      - Videos
    parameters:
      - name: url
        in: body
        type: string
        required: true
        description: URL of the YouTube video to download.
    responses:
      200:
        description: Video downloaded successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Success message.
            embed_url:
              type: string
              description: URL to embed the downloaded video.
      400:
        description: URL not provided.
      500:
        description: Error downloading the video.
    """
    data = request.get_json()  # Obtém os dados JSON da requisição
    url = data.get('url')  # URL do vídeo
    if not url:
        return jsonify({'error': 'URL não fornecida'}), 400

    # Diretório de downloads
    current_dir = os.getcwd()
    output_path = os.path.join(current_dir, 'downloads')
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Baixa o vídeo e obtém o ID do vídeo
    video_id = download_video(url, output_path)
    
    if video_id:
        # Gera a URL de incorporação para o YouTube
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        return jsonify({'message': 'Vídeo baixado com sucesso', 'embed_url': embed_url}), 200
    else:
        return jsonify({'error': 'Erro ao baixar o vídeo'}), 500

# Rota para mostrar a interface do YouTube no Front-end
@app.route('/video', methods=['GET'])
def show_video():
    """
    Endpoint to show the video player interface.
    ---
    tags:
      - Videos
    parameters:
      - name: video_id
        in: query
        type: string
        required: true
        description: ID of the YouTube video to embed.
    responses:
      200:
        description: Video player interface.
      404:
        description: Video not found.
    """
    video_id = request.args.get('video_id')  # ID do vídeo passado como parâmetro
    if video_id:
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        return render_template('video_player.html', embed_url=embed_url)
    else:
        return "Vídeo não encontrado", 404

if __name__ == "__main__":
    app.run(debug=True)
