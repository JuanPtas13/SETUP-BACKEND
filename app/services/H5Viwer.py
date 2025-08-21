import h5py

class H5Viewer:
    def __init__(self, file_path):
        self.file_path = file_path

    def listar_contenido(self):
        """
        Devuelve un diccionario con la estructura del archivo H5.
        """
        contenido = {}
        try:
            with h5py.File(self.file_path, 'r') as hdf:
                def recorrer_grupo(grupo):
                    resultado = {}
                    for key in grupo.keys():
                        item = grupo[key]
                        if isinstance(item, h5py.Group):
                            resultado[key] = recorrer_grupo(item)
                        elif isinstance(item, h5py.Dataset):
                            # Solo muestra la forma y tipo de datos, no los datos completos
                            resultado[key] = {
                                "shape": item.shape,
                                "dtype": str(item.dtype),
                                "attrs": {k: str(v) for k, v in item.attrs.items()}
                            }
                    return resultado
                contenido = recorrer_grupo(hdf)
        except Exception as e:
            contenido = {"error": str(e)}
        return contenido
