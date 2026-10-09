# MindMapBot - AI Learning Companion

## Features
- User registration and login using SQLite
- PDF upload and text extraction
- Point-wise English summarization using Google Gemini API
- English-to-Hindi translation
- English and Hindi text-to-speech
- Flashcards
- Automatic mind map generation
- Download English/Hindi summaries and mind map
- Gemini REST API integration (no google-generativeai SDK required)

## Python
Designed to work with Python 3.8.x.

## Setup

1. Open PowerShell in this folder.
2. Create/activate the virtual environment if needed:
   `python -m venv venv`
   `venv\Scripts\activate`
3. Install dependencies:
   `python -m pip install -r requirements.txt`
4. Copy `.env.example` to `.env`.
5. Put your Gemini API key in `.env`:
   `GOOGLE_API_KEY=YOUR_KEY`
6. Test:
   `python -m utils.test_summarizer`
7. Run:
   `streamlit run main.py`

## Important
Do NOT put your real API key in GitHub or share it in screenshots.
