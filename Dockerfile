# 1. Choix de l'image de base (Python 3.12 slim)
FROM python:3.12-slim

# 2. Répertoire de travail dans le conteneur
WORKDIR /app

# 3. Copie uniquement les dépendances et installe-les d'abord
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copie le reste du code
COPY . .

# 5. Expose le port (celui sur lequel uvicorn écoute)
EXPOSE 8000

# 6. Point d’entrée pour lancer l’app
CMD ["uvicorn", "ocr_api:app", "--host", "0.0.0.0", "--port", "8000"]
