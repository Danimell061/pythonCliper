import cv2 # Manipulação de vídeo
import numpy as np # Manipulação de arrays
import collections # Fila de frames
import time # Tempo
import datetime # Data e hora
import mss # Captura de tela

# Pre-Definicoes
SEGUNDOS = 30
FPS = 30
TECLA_CLIPAR = 'c'
TECLA_SAIR = 'q'

# Salvar o clipe em um arquivo
def salvar_clip(frames_comprimidos, fps, resolucao):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = f"clipe_tela_{timestamp}.avi"
    print(f"\n[INFO] Salvando clipe como '{nome_arquivo}'...")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    saida = cv2.VideoWriter(nome_arquivo, fourcc, fps, resolucao)

    for frame_comprimido in frames_comprimidos:
        #Descomprime o frame JPEG antes de escrever no vídeo
        frame = cv2.imdecode(np.frombuffer(frame_comprimido, np.uint8), cv2.IMREAD_COLOR)
        saida.write(frame)

    saida.release()
    print(f"[INFO] Clipe salvo com sucesso!")

# Captura de tela
with mss.mss() as sct: # uso do with para evitar vazamento de dados
    # monitor = {"top": 0, "left": 0, "width": 500, "height": 500}
    monitor = sct.monitors[2]
    largura = monitor["width"]
    altura = monitor["height"]
    resolucao = (largura, altura)

    tamanho_max_buffer = SEGUNDOS * FPS
    fila_frames = collections.deque(maxlen=tamanho_max_buffer) # Fila que armazena os frames (Ela apaga os mais antigos quando cheia e coloca o novo no lugar)

    print("-- [INFO] Iniciando Sistema de Clipes de Tela --")
    print(f"Duração do clipe: {SEGUNDOS} segundos")
    print(f"Resolução: {largura}x{altura} @ {FPS} FPS")
    print(f"\n>>> Pressione '{TECLA_CLIPAR.upper()}' para salvar os últimos {SEGUNDOS} segundos.")
    print(f">>> Pressione '{TECLA_SAIR.upper()}' para sair.")

    # Controla o tempo para manter o FPS desejado
    tempo_por_frame = 1.0 / FPS

    while True:
        frame_start_time = time.time() # Tempo inicial do loop
        img_mss = sct.grab(monitor) # Captura a tela e retorna uma imagem
        frame = np.array(img_mss) # Converte a imagem capturada para um array
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR) # Converte o formato de cor de BGRA para BGR

        # Comprimindo o Frame
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90] #90% de qualidade
        _, buffer_jpeg = cv2.imencode('.jpg', frame, encode_param)

        # Adiciona na fila como bytes
        fila_frames.append(buffer_jpeg)

        # App para captura de tela
        preview_frame = cv2.resize(frame, (int(largura / 2), int(altura / 2)))
        cv2.imshow('Tela Ao Vivo (Preview)', preview_frame)

        tecla = cv2.waitKey(1)

        if tecla == ord(TECLA_SAIR):
            cv2.destroyAllWindows()
            print("\n-- [AVISO] PROGRAMA ENCERRADO --")
            break

        elif tecla == ord(TECLA_CLIPAR):
            if len(fila_frames) >= tamanho_max_buffer:
                salvar_clip(list(fila_frames), FPS, resolucao)
            else:
                print(f"\n[AVISO] Aguarde o buffer encher. Ainda não há {SEGUNDOS} segundos de vídeo gravados.")

        # Calcula quanto tempo a captura e o processamento levaram
        elapsed_time = time.time() - frame_start_time
        # Calcular o tempo restante para pausar (se necessário)
        sleep_time = tempo_por_frame - elapsed_time
        if sleep_time > 0:
            time.sleep(sleep_time)