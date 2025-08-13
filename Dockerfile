# Imagen base
FROM python:3.10

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

# Establecer el directorio de trabajo
WORKDIR /app
ENV PYTHONPATH=/app

# Copiar archivos al contenedor
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Ejecutar la app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


