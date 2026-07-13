from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Client
import json
import os

# Configuración inicial
app = FastAPI()
client = Client(api_key=os.environ.get("GROQ_API_KEY"))

# Modelo de datos para la solicitud
class SEORequest(BaseModel):
    business_name: str
    business_type: str
    city: str

@app.post("/api/generate-seo")
async def generate_seo(data: SEORequest):
    try:
        # Prompt estructurado para forzar JSON estricto
        prompt = f"""
        Eres un consultor experto en SEO Local y ventas. Genera una estrategia para:
        Negocio: {data.business_name}
        Tipo: {data.business_type}
        Ubicación: {data.city}

        Responde EXCLUSIVAMENTE con un objeto JSON (sin formato markdown):
        {{
            "keywords": ["KW1", "KW2", "KW3"],
            "google_posts": [
                {{"titulo": "Título 1", "contenido": "Contenido 1"}},
                {{"titulo": "Título 2", "contenido": "Contenido 2"}}
            ],
            "sales_script": "Mensaje de prospección persuasivo, humano y corto para {data.business_name} en {data.city}."
        }}
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Eres un servicio API que solo devuelve JSON estricto."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        # Convertir respuesta a diccionario
        result_json = json.loads(response.choices[0].message.content)
        return result_json

    except Exception as e:
        print(f"Error en backend: {e}")
        return {"error": str(e)}

# Para servir los archivos estáticos (index.html)
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="static", html=True), name="static")