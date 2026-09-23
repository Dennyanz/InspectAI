import os

MODEL_PATH = os.getenv("INSPECTAI_MODEL_PATH", "vision_ai/models/inspectai_epi.pt")
CONFIDENCE_THRESHOLD = float(os.getenv("INSPECTAI_CONFIDENCE", 0.50))

# D:\InspectAI\vision_ai\config\ai_config.py

MODEL_PATH = "vision_ai/models/inspectai_epi.pt"
CONFIDENCE_THRESHOLD = 0.40  # Reduzi um pouco para ficar mais sensível a detecções

CLASSES_LABELS = {
    0: "boots",
    1: "gloves",
    2: "goggles",
    3: "helmet",
    4: "no-boots",
    5: "no-gloves",
    6: "no-goggles",
    7: "no-helmet",
    8: "no-vest",
    9: "vest"
}