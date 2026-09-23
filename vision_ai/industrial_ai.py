import torch
try:
    torch.serialization.add_safe_globals([object])
except:
    pass
import os
import numpy as np
import cv2
import logging
import torch
import functools
from ultralytics import YOLO
from vision_ai.config.ai_config import MODEL_PATH, CONFIDENCE_THRESHOLD, CLASSES_LABELS

# Força o PyTorch a aceitar carregamentos completos do YOLO sem restrições de segurança
torch.load = functools.partial(torch.load, weights_only=False)

logger = logging.getLogger("InspectAI.IndustrialVisionAI")

class IndustrialVisionAI:
    def __init__(self):
        """
        Inicializa o modelo YOLOv8 com os pesos industriais configurados.
        """
        try:
            if os.path.exists(MODEL_PATH):
                logger.info(f"[VISION ENGINE] Carregando modelo customizado de: {MODEL_PATH}")
                self.model = YOLO(MODEL_PATH)
            else:
                logger.warning(f"Weights customizados '{MODEL_PATH}' não localizados. Inicializando Fallback YOLOv8n.")
                self.model = YOLO("yolov8n.pt")
                
            logger.info("[VISION ENGINE] Rede Neural carregada com sucesso.")
            
        except Exception as e:
            logger.critical(f"Falha de compilação da rede neural: {str(e)}")
            raise e

    def process_frame(self, frame):
        """
        Executa a inferência da rede neural em um frame de vídeo.
        """
        if self.model is None:
            return frame, {}

        # Executa a predição com os parâmetros configurados
        results = self.model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
        
        # Dicionário para contar as detecções do frame atual
        detections_count = {}
        
        # Se houver resultados, processa as caixas delimitadoras
        if results and len(results) > 0:
            result = results[0]
            boxes = result.boxes
            
            for box in boxes:
                # Obtém o ID da classe detectada
                class_id = int(box.cls[0].item())
                # Traduz o ID para o nome usando o nosso CLASSES_LABELS do ai_config.py
                class_name = CLASSES_LABELS.get(class_id, f"class_{class_id}")
                
                # Incrementa o contador de detecções
                detections_count[class_name] = detections_count.get(class_name, 0) + 1
                
                # Desenha a caixa e a etiqueta no frame para exibição visual
                xyxy = box.xyxy[0].tolist()
                p1, p2 = (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3]))
                
                # Define cores diferentes: verde para seguro (helmet, vest, etc) e vermelho para perigo (no-helmet, etc)
                color = (0, 0, 255) if "no-" in class_name else (0, 255, 0)
                
                cv2.rectangle(frame, p1, p2, color, 2)
                cv2.putText(frame, f"{class_name}", (p1[0], p1[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                            
        return frame, detections_count
