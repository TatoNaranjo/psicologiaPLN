# psicologiaPLN :brain:

## By: TatoNaranjo | Santiago Naranjo Herrera & Daniel Steven Hincapié Cetina

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![spaCy](https://img.shields.io/badge/spaCy-%2309A3D5.svg?style=for-the-badge&logo=spacy&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-%23000000.svg?style=for-the-badge&logo=ollama&logoColor=white)

## Tabla de Contenidos :page_with_curl:
- [Qué es psicologiaPLN](#qué-es-psicologiapln)
- [Dependencias](#dependencias)
- [Pasos de Instalación](#pasos-de-instalación)
- [Notas Adicionales](#notas-adicionales)
- [Licencia](#licencia)
- [Contacto](#contacto)

## Qué es psicologiaPLN? :book:
`psicologiaPLN` es un proyecto de backend que expone una API REST construida con **Django** y **Django Rest Framework**. Su propósito es servir como el "cerebro" para un asistente de chat capaz de analizar viñetas clínicas.

Utiliza un enfoque de **Generación Aumentada por Recuperación (RAG)**. Cuando recibe una viñeta, usa **spaCy** para vectorizar el texto y buscar diagnósticos similares en un corpus (`corpus.json`). Luego, pasa esta información contextual a un Modelo de Lenguaje Grande (LLM) local servido a través de **Ollama** para generar un análisis clínico fundamentado.

Este repositorio fue creado en 2025 para un proyecto universitario y de exploración personal en IA local.

## Dependencias :warning:
Para correr este proyecto, necesitarás:
* Python (3.10+)
* Un gestor de paquetes de Python (como `pip` y `venv`)
* [Ollama](https://ollama.com/) para servir el LLM local.
* Un modelo de Ollama descargado (`phi3:3.8b`)
* Un modelo de spaCy (`es_core_news_md`)

Las dependencias de Python están listadas en `requirements.txt` (si no existe, puedes crearlo con las librerías usadas: `django`, `djangorestframework`, `django-cors-headers`, `spacy`, `requests`, `numpy`).

## Pasos de Instalación :checkered_flag:

1.  **Clona el repositorio**
    ```bash
    git clone [https://github.com/TatoNaranjo/psicologiaPLN](https://github.com/TatoNaranjo/psicologiaPLN)
    cd psicologiaPLN
    ```

2.  **Crea y activa un entorno virtual**
    ```bash
    # En macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    
    # En Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instala las dependencias de Python**
    ```bash
    pip install -r requirements.txt 
    ```
    *(Si no tienes `requirements.txt`, instala manualmente: `pip install django djangorestframework django-cors-headers spacy requests numpy`)*

4.  **Descarga el modelo de spaCy**
    ```bash
    python -m spacy download es_core_news_md
    ```

5.  **(Terminal Aparte) Inicia el servidor de Ollama**
    * Asegúrate de tener Ollama instalado.
    * Ejecuta el modelo que especificaste en `views.py` (ej. `phi3:3.8b`) para mantenerlo "caliente".
    ```bash
    ollama run phi3:3.8b
    ```
    * **No cierres esta terminal.**

6.  **(Terminal Aparte) Inicia el servidor de Django**
    ```bash
    python manage.py runserver
    ```
    * El servidor de la API estará corriendo en `http://localhost:8000`.

## Notas adicionales :construction:
-   Este proyecto es **solo el backend**. Necesita un frontend (como [PLNVinetas-FrontEnd](https://github.com/TatoNaranjo/PLNVinetas-FrontEnd)) para interactuar con él.
-   Asegúrate de que el `MODEL_NAME` en `api/views.py` coincida *exactamente* con el nombre de un modelo que tengas en `ollama list`.
-   La configuración de CORS en `settings.py` está ajustada para `http://localhost:5173` (el puerto por defecto de Vite).

## Licencia :door:
Este proyecto está licenciado bajo la [Licencia MIT](https://opensource.org/licenses/MIT).

## Contacto :computer:
Para preguntas o comentarios, puedes contactarme a través de mi [correo electrónico](mailto:naranjosa2004@gmail.com).
