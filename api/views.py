# /api/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests 
import spacy

from .matcher_utils import (
    extraer_patrones, 
    buscar_mas_similar,
    corpus_embeddings,
    INTENSIFICADORES as MATCHER_INTENSIFICADORES 
)

pln = spacy.load("es_core_news_md")

# CAMBIO 1: Volvemos al endpoint '/api/generate'
# Es más compatible con modelos que no son explícitamente de "chat".
OLLAMA_URL = "http://localhost:11434/api/generate" 
MODEL_NAME = "phi3:3.8b" # Mantenemos tu modelo

INTENSIFICADORES = {
    "constante", "persistente", "severo", "leve", "grave", "crónico", 
    "agudo", "excesivo", "frecuente", "raro", "recurrente", 
    "intermitente", "prolongado", "temporal", "incesante"
}

SYSTEM_PROMPT = """
Eres un asistente clínico experto en el DSM. Tu única función es ayudar a psicólogos a analizar viñetas clínicas.

REGLAS ESTRICTAS:
1.  Tu propósito es *exclusivamente* analizar viñetas clínicas.
2.  Si el usuario te saluda ("Hola", "¿Cómo estás?"), responde al saludo de forma breve, profesional y recuerda tu función ("Hola. Soy un asistente clínico listo para analizar tu viñeta.").
3.  Si el usuario te pregunta por cualquier otro tema (el clima, historia, chistes, etc.), debes *rehusarte amablemente*. Responde algo como: "Lo siento, mi única función es analizar viñetas clínicas. ¿Podrías proporcionarme una?"
4.  NUNCA te salgas de tu rol. Eres un profesional clínico, no un chat general.
"""

@api_view(["POST"])
def analizar_chat(request):
    """
    Maneja una conversación de chat, decidiendo si aplicar RAG o no.
    Usa el endpoint /api/generate de Ollama.
    """
    history = request.data.get("history", [])

    if not history:
        return Response({"error": "No se proporcionó historial de chat."})

    last_user_message = history[-1]["content"]

    contexto_rag = ""
    try:
        similares = buscar_mas_similar(last_user_message, top_k=3)
        if similares and similares[0][1] > 0.25:
            contexto_rag = "--- INICIO DEL CONTEXTO (Base de Conocimiento) ---\n"
            for item, score in similares:
                contexto_rag += f"Código: {item['codigo']}\n"
                contexto_rag += f"Título: {item['titulo']}\n"
                contexto_rag += f"Descripción: {item['texto_completo']}\n---\n"
            contexto_rag += "--- FIN DEL CONTEXTO ---\n"
            contexto_rag += "Basándote *única y exclusivamente* en el contexto anterior y la viñeta, proporciona tu análisis:"

    except Exception as e:
        print(f"Error en RAG: {e}")

    # --- CAMBIO 2: Construir un 'prompt' único desde el historial ---
    # El endpoint /api/generate no entiende 'messages', solo 'prompt'.
    # Usamos el formato ChatML que Phi-3 entiende.
    
    final_prompt = f"<|system|>\n{SYSTEM_PROMPT}<|end|>\n"
    
    # Añadimos el historial previo
    for msg in history[:-1]: # Todos excepto el último
        final_prompt += f"<|{msg['role']}|>\n{msg['content']}<|end|>\n"
        
    # Añadimos el contexto RAG (si existe) como un mensaje del sistema
    if contexto_rag:
        final_prompt += f"<|system|>\n{contexto_rag}<|end|>\n"
        
    # Añadimos el último mensaje del usuario
    final_prompt += f"<|user|>\n{last_user_message}<|end|>\n"
    
    # Le decimos al modelo que es su turno de hablar
    final_prompt += "<|assistant|>\n"


    # --- CAMBIO 3: Adaptar el 'data' para /api/generate ---
    data = {
        "model": MODEL_NAME,
        "prompt": final_prompt, # Usamos 'prompt', no 'messages'
        "stream": False 
    }

    try:
        response_ollama = requests.post(OLLAMA_URL, json=data)
        response_ollama.raise_for_status() 
        
        respuesta_json = response_ollama.json()
        print(f"DEBUG: Respuesta completa de Ollama: {respuesta_json}")

        # --- CAMBIO 4: Parsear la respuesta de /api/generate ---
        # La respuesta está en la clave 'response', no en 'message.content'
        respuesta_contenido = respuesta_json.get("response", "No se obtuvo respuesta del modelo.").strip()
        
        # Manejo del error 'done_reason: load' que vimos antes
        if not respuesta_contenido and respuesta_json.get("done_reason") == "load":
            return Response({"error": "El modelo se estaba cargando en memoria. Por favor, envía tu mensaje de nuevo."})

        if not respuesta_contenido:
            return Response({"respuesta": "El modelo no generó una respuesta."})

        return Response({"respuesta": respuesta_contenido})
        
    except requests.exceptions.ConnectionError:
        return Response({"error": f"No se pudo conectar a Ollama. ¿Ejecutaste 'ollama run {MODEL_NAME}'?"})
    except Exception as e:
        return Response({"error": f"Error en la llamada a Ollama: {str(e)}"})


# --- TUS OTRAS VISTAS (SIN CAMBIOS) ---
# Estas funciones están bien y no tienen conflicto.

@api_view(["POST"])
def analizar_texto(request):
    """Extrae palabras clave de la viñeta."""
    # ... (tu código original va aquí)
    texto = request.data.get("texto", "")
    doc = pln(texto)
    palabras_clave = []
    for token in doc:
        if token.pos_ in ["NOUN", "ADJ", "PROPN", "ADV"]:
            lema = token.lemma_.lower()
            if lema in INTENSIFICADORES or token.pos_ in ["NOUN", "PROPN"]:
                palabras_clave.append(lema)
    return Response({"palabras_clave": palabras_clave})


@api_view(["POST"])
def analizar_patrones(request):
    """Extrae síntomas con intensidad usando matcher_utils."""
    # ... (tu código original va aquí)
    texto = request.data.get("texto", "")
    patrones = extraer_patrones(texto)
    if not patrones:
        return Response({"respuesta": "No encontré síntomas relevantes en la viñeta."})
    frases = []
    for p in patrones:
        if p["intensidad"]:
            frases.append(f"{p['sintoma']} de manera {p['intensidad']}")
        else:
            frases.append(f"{p['sintoma']}")
    respuesta = "La viñeta que me pasaste presenta " + ", ".join(frases) + "."
    return Response({"respuesta": respuesta, "detalles": patrones})


@api_view(["POST"])
def analizar_similitud(request):
    """Busca diagnósticos similares según DSM."""
    texto = request.data.get("texto","")
    similares = buscar_mas_similar(texto)
    respuesta = []
    for item, score in similares:
        respuesta.append({
            "codigo": item["codigo"],
            "titulo": item["titulo"],
            "similitud": round(float(score), 3),
            "texto_completo": item["texto_completo"]
        })
    return Response({"entrada": texto, "posibles_diagnosticos": respuesta})


@api_view(["GET"])
def get_nlp_metrics(request):
    """
    Endpoint para obtener métricas y parámetros del sistema NLP.
    """
    try:
        # Métricas del modelo spaCy
        spacy_model = pln.meta["name"]
        spacy_version = pln.meta["version"]
        vector_dim = pln.vocab.vectors_length
        
        # Métricas del Corpus (RAG)
        corpus_size = len(corpus_embeddings)
        
        # Parámetros del LLM (definidos globalmente en este archivo)
        ollama_model = MODEL_NAME
        
        # Parámetros del Matcher
        intensifiers_count = len(MATCHER_INTENSIFICADORES)
        
        # Parámetros hardcodeados en la vista 'analizar_chat'
        rag_threshold = 0.25  # El umbral que definiste
        rag_top_k = 3         # El top_k que definiste
        
        metrics = {
            "spacy_model": f"{spacy_model} ({spacy_version})",
            "vector_dimensions": vector_dim,
            "knowledge_base_size": corpus_size,
            "llm_model": ollama_model,
            "rag_similarity_threshold": rag_threshold,
            "rag_top_k": rag_top_k,
            "clinical_intensifiers": intensifiers_count
        }
        return Response(metrics)
        
    except Exception as e:
        return Response({"error": f"Error al generar métricas: {str(e)}"}, status=500)