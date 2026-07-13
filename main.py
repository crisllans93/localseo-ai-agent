import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from groq import Groq  # <-- Cambiado a Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LocalSEO AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar el cliente de Groq con su modelo gratuito
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class SEORequest(BaseModel):
    business_name: str
    business_type: str
    city: str

@app.post("/api/generate-seo")
async def generate_seo(data: SEORequest):
    try:
        prompt = f"""
        Eres un consultor experto en SEO Local y Copywriting. Genera una micro-estrategia optimizada para el siguiente negocio:
        Nombre del Negocio: {data.business_name}
        Tipo de Negocio: {data.business_type}
        Ciudad/Ubicación: {data.city}

        Debes responder EXCLUSIVAMENTE con un objeto JSON estricto (sin bloques de código markdown, sin texto antes ni después) con la siguiente estructura exacta:
        {{
            "keywords": ["Palabra clave local 1", "Palabra clave local 2", "Palabra clave local 3"],
            "google_posts": [
                {{"titulo": "Post 1: Lanzamiento / Promoción", "contenido": "Texto optimizado para Google Business Profile con emojis..."}},
                {{"titulo": "Post 2: Autoridad / Confianza", "contenido": "Texto persuasivo enfocado en calidad..."}}
            ]
        }}
        """

        # Usamos el modelo llama-3.3-70b que es excelente y gratis en Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Eres un servicio API automatizado que solo devuelve JSON estricto sin formato markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result_json = json.loads(response.choices[0].message.content)
        return result_json

    except Exception as e:
        print("\n❌ ERROR DETECTADO EN GROQ:", str(e), "\n")
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/", StaticFiles(directory="static", html=True), name="static")