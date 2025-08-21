import os
import h5py
import numpy as np
from datetime import datetime

class DataLogger:
    def __init__(self, base_dir="training_data", file_prefix="training_data"):
        """
        Inicializa el logger y crea la carpeta de destino si no existe.
        - base_dir: carpeta base dentro de app (ejemplo: 'app/saved_data')
        - file_prefix: prefijo del archivo (ejemplo: 'training_data')
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.save_dir = os.path.join(current_dir, '..', base_dir)
        os.makedirs(self.save_dir, exist_ok=True)
        self.file_prefix = file_prefix

    def save(self, data, data_type="hands", label="normal"):
        """
        Guarda cada sesión en un archivo .h5 diferente por etiqueta.
        """
        if not data:
            return False

        # Nombre de archivo por etiqueta
        file_name = f"{self.file_prefix}_{label}.h5"
        file_path = os.path.join(self.save_dir, file_name)

        try:
            group_name = f"{data_type}_{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with h5py.File(file_path, 'a') as hdf:
                group = hdf.create_group(group_name)
                group.attrs['etiqueta'] = label
                group.attrs['tipo_datos'] = data_type
                group.attrs['timestamp'] = datetime.now().isoformat()

                if data_type == "hands":
                    for i, mano in enumerate(data):
                        landmarks_array = [[p['x'], p['y'], p['z']] for p in mano]
                        dataset = group.create_dataset(f"mano_{i}", data=np.array(landmarks_array))
                        dataset.attrs['columnas'] = ['coordenada_x', 'coordenada_y', 'coordenada_z']

                elif data_type == "faces":
                    for i, cara in enumerate(data):
                        dataset = group.create_dataset(f"cara_{i}", data=np.array([
                            cara['xmin'], cara['ymin'], cara['width'], cara['height'], cara['score']
                        ]))
                        dataset.attrs['columnas'] = ['x_minimo', 'y_minimo', 'ancho', 'alto', 'puntuacion_confianza']

            print(f"✅ Datos guardados en grupo: {group_name} en archivo: {file_name}")
            return True

        except Exception as e:
            print(f"❌ Error al guardar datos: {e}")
            return False

    def list_files(self):
        """Devuelve la lista de archivos .h5 en la carpeta"""
        try:
            return [f for f in os.listdir(self.save_dir) if f.endswith(".h5")]
        except:
            return []

    def get_file_path(self, filename=None):
        """Obtiene la ruta completa de un archivo .h5 por etiqueta"""
        if filename:
            return os.path.join(self.save_dir, filename)
        return self.save_dir
