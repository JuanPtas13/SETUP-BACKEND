#mantoene el estado de la grabacion 
class RecordingState:
    def __init__(self):
        self.recording = False
        self.label = None
        self.data_type = None  # "hands" o "faces"

    def start(self, label, data_type):
        self.recording = True
        self.label = label
        self.data_type = data_type
        print(f"[REC] Iniciando grabación: {data_type} - {label}")

    def stop(self):
        print(f"[REC] Finalizando grabación: {self.data_type} - {self.label}")
        self.recording = False
        self.label = None
        self.data_type = None
