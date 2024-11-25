import yt_dlp
import vlc
import os
import time

def download_video(url, output_path):
    """
    Faz o download do vídeo usando yt-dlp e salva no diretório especificado.
    Retorna o caminho completo do arquivo baixado.
    """
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),  # Salva o vídeo com o título e a extensão
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Baixa o vídeo
            result = ydl.extract_info(url, download=True)
            
            # O nome do arquivo gerado é obtido através do 'prepare_filename'
            video_filename = ydl.prepare_filename(result)  # Pega o caminho do arquivo com o nome do vídeo
            print(f"Vídeo baixado com sucesso para {video_filename}")
            
            return video_filename  # Retorna o caminho do arquivo baixado
    except Exception as e:
        print(f"Erro ao baixar o vídeo: {e}")
        return None

def play_video(video_path):
    """
    Reproduz o vídeo usando a biblioteca VLC.
    """
    try:
        # Criação do objeto de player VLC
        player = vlc.MediaPlayer(video_path)
        player.play()
        
        # Aguardar enquanto o vídeo está sendo reproduzido
        while player.is_playing():
            time.sleep(1)  # Aguardar o término da reprodução
        print("Vídeo terminado.")
    except Exception as e:
        print(f"Erro ao tentar reproduzir o vídeo: {e}")

if __name__ == "__main__":
    # URL do vídeo que deseja baixar e reproduzir
    url = "https://www.youtube.com/watch?v=-J_w9K6DgRo"  #URL do vídeo desejado

    # Diretório onde o script está sendo executado (diretório de backend)
    current_dir = os.getcwd()  # Obtém o diretório atual de execução do script (backend)
    
    # Caminho do diretório de download, dentro do próprio diretório do projeto
    output_path = os.path.join(current_dir, 'downloads')  # Pasta 'downloads' dentro do diretório do backend

    # Verificar e criar o diretório 'downloads' se não existir
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Passo 1: Baixar o vídeo
    video_filename = download_video(url, output_path)

    # Passo 2: Se o vídeo foi baixado com sucesso, reproduza-o
    if video_filename:
        play_video(video_filename)
