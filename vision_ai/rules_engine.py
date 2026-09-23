# D:\InspectAI\vision_ai\rules_engine.py

class IndustrialRulesEngine:
    @staticmethod
    def evaluate(detections: dict, area: str = "Geral") -> tuple[str, str]:
        """
        Analisa as detecções da IA e retorna: (Status do Evento, Nível de Risco)
        """
        # Regra 1: Alerta Crítico - Flagrante de pessoa Sem Capacete
        if detections.get("no-helmet", 0) > 0:
            return "MISSING_HELMET", "HIGH"
            
        # Regra 2: Alerta Crítico - Flagrante de pessoa Sem Colete
        if detections.get("no-vest", 0) > 0:
            return "MISSING_VEST", "HIGH"
            
        # Regra 3: Alerta de Segurança - Sem Óculos de Proteção
        if detections.get("no-goggles", 0) > 0:
            return "MISSING_GOGGLES", "MEDIUM"

        # Regra 4: Se detectar os EPIs corretos na área
        if detections.get("helmet", 0) > 0 or detections.get("vest", 0) > 0:
            return "NORMAL", "LOW"

        # Padrão caso a câmera esteja vazia ou monitorando apenas o cenário
        return "NORMAL", "LOW"