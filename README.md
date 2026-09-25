InspectAI - Monitoramento Operacional e Telemetria Inteligente

Ecossistema integrado de Internet das Coisas (IoT), visão computacional e backend em nuvem para segurança ocupacional e prevenção proativa de acidentes em ambientes industriais.



 Visão Geral

O InspectAI atua na resposta rápida a emergências e na eliminação de pontos cegos operacionais ao combinar telemetria física via dispositivo vestível (*wearable*) com processamento central em Python e modelos de redes neurais.



Arquitetura Tecnológica

1. Dispositivo Vestível (Edge & Hardware)
Controlador Central: ESP32 gerenciando conexões sem fio e rotinas de telemetria.
Cinemática: Sensor inercial MPU-6050 para detecção de quedas bruscas e impactos severos.
Biometria: Sensor óptico MAX30102 para aferição contínua de batimentos cardíacos e saturação de oxigênio.
Comunicação: Transmissão em tempo real de pacotes via Wi-Fi (MQTT/WebSockets).

2. Backend & Inteligência Artificial
API de Telemetria (`api_telemetria.py`): Ingestão contínua de sinais vitais e notificações de alerta.
Persistência Relacional: Modelagem de dados estruturada em SQLite/SQL (`inspectai.db`) com consultas otimizadas.
Visão Computacional (Vision AI): Inferência com modelos YOLOv8 (`.pt` e `.onnx`) para detecção de conformidade de EPIs e monitoramento de áreas de risco.

3. Painel de Controle (Dashboard)
* Central de monitoramento em tempo real com alertas visuais imediatos em caso de quedas mecânicas ou anomalias biométricas.



Como Executar

Pré-requisitos
Python 3.9+ instalado
Git

Instalação
1. Clone o repositório:
   ```bash
   git clone [https://github.com/Dennyanz/InspectAI.git](https://github.com/Dennyanz/InspectAI.git)
   cd InspectAI
