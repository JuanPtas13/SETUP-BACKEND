import h5py
import numpy as np
from datetime import datetime
import os

class DataLogger:
    def __init__(self, file_path="training_data.h5"):
        """Inicializa el logger con un archivo HDF5"""
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
    def _get_current_group_name(self, prefix, label):
        """Genera nombre de grupo con timestamp + label"""
        return f"{prefix}_{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def save(self, data, data_type="hands", label="normal"):
        """
        Guarda datos serializados en el archivo HDF5.
        
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
                group.attrs['label'] = label  

                if data_type == "hands":
                    for i, hand in enumerate(data):
                        group.create_dataset(f"hand_{i}", 
                                          data=np.array([[lm['x'], lm['y'], lm['z']] for lm in hand]))
                elif data_type == "faces":
                    for i, face in enumerate(data):
                        group.create_dataset(f"face_{i}", 
                                          data=np.array([
                                              face['xmin'],
                                              face['ymin'],
                                              face['width'],
                                              face['height'],
                                              face['score']
                                          ]))
                return True
        except Exception as e:
            print(f"Error al guardar datos: {e}")
            return False
