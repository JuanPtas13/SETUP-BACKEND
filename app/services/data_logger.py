import h5py
import numpy as np
from datetime import datetime
import os

class DataLogger:
    def __init__(self, file_path=None):
        """Inicializa el logger con archivo HDF5 en la carpeta recordings"""
        if file_path is None:
            # Guardar en la carpeta recordings con estructura de carpetas
            base_dir = os.path.join(os.getcwd(), "recordings")
            os.makedirs(base_dir, exist_ok=True)
            self.file_path = os.path.join(base_dir, "datos_entrenamiento.h5")
        else:
            self.file_path = file_path
        
        # Crear subcarpetas para organización
        manos_dir = os.path.join(os.path.dirname(self.file_path), "manos")
        caras_dir = os.path.join(os.path.dirname(self.file_path), "caras")
        os.makedirs(manos_dir, exist_ok=True)
        os.makedirs(caras_dir, exist_ok=True)

    def _get_current_group_name(self, prefix, label):
        """Genera nombre de grupo con timestamp + label"""
        return f"{prefix}_{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def save(self, data, data_type="hands", label="normal"):
        """
        Guarda datos serializados en el archivo HDF5 con nombres en español.
        
        Args:
            data: Lista de diccionarios con datos serializados
            data_type: 'hands' o 'faces'
            label: etiqueta de emoción ('feliz', 'normal', etc.)
        """
        if not data:
            return False

        try:
            with h5py.File(self.file_path, 'a') as hdf:
                group_name = self._get_current_group_name(data_type, label)
                group = hdf.create_group(group_name)

                # Guardamos la etiqueta como atributo
                group.attrs['etiqueta'] = label  
                group.attrs['tipo_datos'] = data_type
                group.attrs['timestamp'] = datetime.now().isoformat()

                if data_type == "hands":
                    for i, mano in enumerate(data):
                        # Guardar landmarks con nombres en español
                        landmarks_array = []
                        for punto in mano:
                            landmarks_array.append([
                                punto['x'],  # coordenada_x
                                punto['y'],  # coordenada_y
                                punto['z']   # coordenada_z
                            ])
                        
                        dataset = group.create_dataset(
                            f"mano_{i}", 
                            data=np.array(landmarks_array)
                        )
                        # Agregar descripción en español
                        dataset.attrs['descripcion'] = f"Landmarks de mano {i} para etiqueta '{label}'"
                        dataset.attrs['columnas'] = ['coordenada_x', 'coordenada_y', 'coordenada_z']
                        
                elif data_type == "faces":
                    for i, cara in enumerate(data):
                        # Guardar datos de cara con nombres en español
                        dataset = group.create_dataset(
                            f"cara_{i}", 
                            data=np.array([
                                cara['xmin'],      # x_minimo
                                cara['ymin'],      # y_minimo
                                cara['width'],     # ancho
                                cara['height'],    # alto
                                cara['score']      # puntuacion_confianza
                            ])
                        )
                        # Agregar descripción en español
                        dataset.attrs['descripcion'] = f"Datos de detección de cara {i} para etiqueta '{label}'"
                        dataset.attrs['columnas'] = ['x_minimo', 'y_minimo', 'ancho', 'alto', 'puntuacion_confianza']
                
                print(f"✅ Datos guardados exitosamente en: {self.file_path}")
                print(f"   Grupo: {group_name}")
                print(f"   Tipo: {data_type}")
                print(f"   Etiqueta: {label}")
                print(f"   Total de elementos: {len(data)}")
                
                return True
        except Exception as e:
            print(f"❌ Error al guardar datos: {e}")
            return False


class RecordingState:
    """
    Controla el estado de grabación (manos o cara, y etiqueta).
    Útil para integrarlo con WebSocket.
    """
    def __init__(self):
        self.recording = False
        self.label = "normal"
        self.data_type = "hands"  # "hands" o "faces"

    def start(self, label="normal", data_type="hands"):
        self.recording = True
        self.label = label
        self.data_type = data_type

    def stop(self):
        self.recording = False
                                                                                                                