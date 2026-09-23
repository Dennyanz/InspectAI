import cv2
import threading
import time
import requests
from ultralytics import YOLO

URL_BACKEND = "http://localhost:5000/enviar_vital"

# Caminho absoluto fixado para evitar qualquer erro de diretório no Windows
MODELO_PATH = r"C:\InspectAI\backend\models\inspectai.pt"

class VideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
                break
            self.grabbed, self.frame = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.stream.release()

try:
    model = YOLO(MODELO_PATH)
    print("🤖 Modelo YOLO (inspectai.pt) carregado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao carregar o modelo YOLO no caminho {MODELO_PATH}: {e}")
    exit()

print("🎥 Iniciando captura de vídeo paralela por Threads...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

frame_count = 0
SKIP_FRAMES = 3

while True:
    frame = vs.read()
    if frame is None:
        break

    frame_count += 1
    if frame_count % SKIP_FRAMES == 0:
        results = model(frame, verbose=False)
        capacete_detectado = False
        colete_detectado = False
        pessoa_detectada = False

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                label = model.names[cls].lower()
                if "person" in label or "operario" in label:
                    pessoa_detectada = True
                if "helmet" in label or "capacete" in label:
                    capacete_detectado = True
                if "vest" in label or "colete" in label:
                    colete_detectado = True

        if pessoa_detectada:
            if not capacete_detectado or not colete_detectado:
                try:
                    requests.post(URL_BACKEND, json={
                        "status": "INCONFORMIDADE",
                        "operador_id": "Operario Sem EPI",
                        "bpm": 0
                    }, timeout=1)
                except:
                    pass

    cv2.putText(frame, "InspectAI - Visao Computacional Ativa", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.imshow("Monitoramento de Seguranca - Camara 01", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vs.stop()
cv2.destroyAllWindows()
