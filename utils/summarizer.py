import os
import re
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

def _clean_points(raw):
    points = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^\s*(?:[-*•]|\d+[\.\)])\s*", "", line)
        if line:
            points.append(line)
    return points

def _gemini_request(prompt, retries=5):
    if not API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY is missing. Add it to the .env file."
        )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + MODEL
        + ":generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    last_error = None

    for attempt in range(retries):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=120
            )

            # SUCCESS
            if response.status_code == 200:
                data = response.json()

                candidates = data.get("candidates", [])

                if not candidates:
                    raise RuntimeError(
                        "Gemini returned no candidates."
                    )

                parts = candidates[0].get(
                    "content", {}
                ).get("parts", [])

                text_parts = []

                for part in parts:
                    if part.get("text"):
                        text_parts.append(part["text"])

                result = "\n".join(text_parts).strip()

                if result:
                    return result

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            # TEMPORARY SERVER BUSY
            if response.status_code == 503:
                last_error = response.text

                wait_time = min(
                    30,
                    5 * (2 ** attempt)
                )

                print(
                    "Gemini is temporarily busy (503). "
                    "Retrying in {} seconds...".format(wait_time)
                )

                time.sleep(wait_time)
                continue

            # RATE LIMIT
            if response.status_code == 429:
                last_error = response.text

                wait_time = min(
                    30,
                    5 * (2 ** attempt)
                )

                print(
                    "Gemini rate limit reached (429). "
                    "Retrying in {} seconds...".format(wait_time)
                )

                time.sleep(wait_time)
                continue

            # AUTHENTICATION / MODEL / REQUEST ERRORS
            if response.status_code in (400, 401, 403, 404):
                raise RuntimeError(
                    "Gemini API error {}: {}".format(
                        response.status_code,
                        response.text
                    )
                )

            # OTHER API ERRORS
            raise RuntimeError(
                "Gemini API error {}: {}".format(
                    response.status_code,
                    response.text
                )
            )

        except requests.RequestException as exc:
            last_error = str(exc)

            wait_time = min(
                30,
                5 * (2 ** attempt)
            )

            print(
                "Network error. "
                "Retrying in {} seconds...".format(wait_time)
            )

            time.sleep(wait_time)

    raise RuntimeError(
        "Gemini is temporarily unavailable after {} attempts. "
        "Please try again later. {}".format(
            retries,
            last_error
        )
    )
    if not API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY is missing. Add it to the .env file."
        )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + MODEL
        + ":generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    last_error = None

    for attempt in range(retries):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()

                candidates = data.get("candidates", [])

                if not candidates:
                    raise RuntimeError(
                        "Gemini returned no candidates."
                    )

                parts = candidates[0].get("content", {}).get("parts", [])

                text_parts = []

                for part in parts:
                    if part.get("text"):
                        text_parts.append(part["text"])

                result = "\n".join(text_parts).strip()

                if result:
                    return result

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            # Temporary server overload
            if response.status_code == 503:
                wait_time = min(30, 5 * (2 ** attempt))

                print(
                    "Gemini is temporarily busy (503). "
                    "Retrying in {} seconds...".format(wait_time)
                )

                time.sleep(wait_time)
                last_error = response.text
                continue

            # Rate limit
            if response.status_code == 429:
                wait_time = min(30, 5 * (2 ** attempt))

                print(
                    "Gemini rate limit reached (429). "
                    "Retrying in {} seconds...".format(wait_time)
                )

                time.sleep(wait_time)
                last_error = response.text
                continue

            # Authentication / request errors
            if response.status_code in (400, 401, 403, 404):
                raise RuntimeError(
                    "Gemini API error {}: {}".format(
                        response.status_code,
                        response.text
                    )
                )

            raise RuntimeError(
                "Gemini API error {}: {}".format(
                    response.status_code,
                    response.text
                )
            )

        except requests.RequestException as exc:
            last_error = str(exc)

            wwait_time = min(30, 5 * (2 ** attempt))

            print(
                "Network error. Retrying in {} seconds...".format(
                    wait_time
                )
            )

            time.sleep(wait_time)

    raise RuntimeError(
        "Gemini is temporarily unavailable after {} attempts. "
        "Please try again later.\n{}".format(
            retries,
            last_error
        )
    )
def _chunk_text(text, max_chars=7000):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + max_chars, length)
        if end < length:
            split_at = text.rfind(". ", start, end)
            if split_at > start + max_chars // 2:
                end = split_at + 1
        chunks.append(text[start:end].strip())
        start = end

    return chunks

def generate_summary(text):
    """
    Returns a list of point-wise English summary strings.
    Uses Google Gemini through the REST API, so it works without
    the google-generativeai Python package.
    """
    if not text or not text.strip():
        return ["No readable text was found in the PDF."]

    chunks = _chunk_text(text)
    if not chunks:
        return ["No readable text was found in the PDF."]

    all_points = []

    for i, chunk in enumerate(chunks):
        prompt = f"""
You are an academic learning assistant.

Summarize ONLY the information present in the supplied document text.
Do not invent facts. Preserve important technical terms, definitions,
steps, examples, and key relationships.

Return ONLY concise bullet points.
Do not write an introduction such as "Here is a summary".
Use approximately 6-10 useful points for this section.
Each point should be a complete, easy-to-understand sentence.

Document section {i + 1} of {len(chunks)}:
{chunk}
"""
        raw = _gemini_request(prompt)
        all_points.extend(_clean_points(raw))

    # If a very long document produced many repeated points, do a final
    # consolidation pass. This is still Gemini and keeps the output readable.
    if len(all_points) > 18:
        combined = "\n".join("- " + p for p in all_points)
        final_prompt = f"""
You are an academic summarizer. Consolidate the following section summaries
into 10-15 high-value bullet points. Keep all important concepts and do not
invent information. Return ONLY bullet points.

{combined}
"""
        try:
            final_raw = _gemini_request(final_prompt)
            final_points = _clean_points(final_raw)
            if final_points:
                return final_points
        except Exception:
            # Preserve usable chunk summaries if the consolidation call fails.
            pass

    return all_points or ["No summary was generated."]
