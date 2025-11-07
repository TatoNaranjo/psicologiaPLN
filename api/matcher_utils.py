import spacy
import json
import numpy as np
from spacy.matcher import Matcher
from pathlib import Path


pln = spacy.load("es_core_news_md")
with open(Path(__file__).resolve().parent / "corpus.json", "r", encoding="utf-8") as f:
    corpus = json.load(f)

# Diccionario de intensificadores clínicos
INTENSIFICADORES = {
    "constante", "persistente", "severo", "leve", "grave", "crónico",
    "agudo", "excesivo", "frecuente", "raro", "recurrente",
    "intermitente", "prolongado", "temporal", "incesante"
}

def build_corpus_embeddings():
    embeddings = []
    for item in corpus:
        doc = pln(item["texto_completo"])
        embeddings.append({
            "codigo": item["codigo"],
            "titulo": item["titulo"],
            "texto_completo": item["texto_completo"],
            "vector": doc.vector  # embedding medio de spaCy
        })
    return embeddings


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def buscar_mas_similar(texto_usuario, top_k=3):
    doc = pln(texto_usuario)
    user_vec = doc.vector

    resultados = []
    for item in corpus_embeddings:
        sim = cosine_similarity(user_vec, item["vector"])
        resultados.append((item, sim))

    # ordenar de mayor a menor similitud
    resultados = sorted(resultados, key=lambda x: x[1], reverse=True)[:top_k]

    return resultados

corpus_embeddings = build_corpus_embeddings()
def extraer_patrones(texto: str):
    doc = pln(texto)
    matcher = Matcher(pln.vocab)

    # Patrón: sustantivo + intensificador
    patron_sintoma_int = [
        {"POS": "NOUN"},
        {"LEMMA": {"IN": list(INTENSIFICADORES)}, "OP": "?"}
    ]

    # Registrar patrón
    matcher.add("SINTOMA_INT", [patron_sintoma_int])

    resultados = []
    for match_id, start, end in matcher(doc):
        span = doc[start:end]
        sintoma = span[0].lemma_.lower()

        intensificador = None
        if len(span) > 1 and span[1].lemma_.lower() in INTENSIFICADORES:
            intensificador = span[1].lemma_.lower()

        resultados.append({"sintoma": sintoma, "intensidad": intensificador})

    return resultados
