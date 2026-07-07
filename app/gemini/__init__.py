import httpx
import json
from typing import Dict, Any
from app.core.logging import logger
from app.core.exceptions import DiagnosisException

class GeminiClientError(DiagnosisException):
    """Exception raised for errors during Gemini API communications."""
    pass


class GeminiClientWrapper:
    """
    Integrates with the official Google Generative Language API via raw HTTP
    calls using httpx, utilizing structured JSON generation formats.
    """
    def __init__(self, api_key: str, default_model: str = "gemini-1.5-pro") -> None:
        self.api_key = api_key
        self.default_model = default_model

    async def generate_explanation(self, system_instruction: str, prompt: str, timeout_seconds: float = 30.0) -> str:
        """
        Sends a structured prompt request to the Gemini API and parses the response text.
        
        Args:
            system_instruction: Guiding persona/system role constraints.
            prompt: User-facing or analytical context prompt.
            timeout_seconds: Timeout limit for the HTTP request.
            
        Returns:
            AI-generated structured JSON response string.
        """
        if not self.api_key:
            raise GeminiClientError("Gemini API key is not configured. Please set GEMINI_API_KEY in your environment.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.default_model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        # Build payload following Google Gemini structured API specs
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "systemInstruction": {
                "parts": [
                    {
                        "text": system_instruction
                    }
                ]
            },
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2
            }
        }

        try:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                logger.debug(f"Sending generateContent call to model: {self.default_model}")
                response = await client.post(url, headers=headers, json=payload)
                
                # Check for HTTP errors
                if response.status_code == 429:
                    logger.warning("Gemini API rate limit hit (429).")
                    raise GeminiClientError("Gemini API Rate Limit exceeded.")
                response.raise_for_status()
                
                res_data = response.json()
                
                # Extract text output from candidate payload structure
                candidates = res_data.get("candidates", [])
                if not candidates:
                    raise GeminiClientError("Gemini returned empty candidate choices.")
                
                candidate = candidates[0]
                content = candidate.get("content", {})
                parts = content.get("parts", [])
                if not parts:
                    raise GeminiClientError("Gemini content parts structure is empty.")
                
                text_out = parts[0].get("text", "")
                if not text_out:
                    raise GeminiClientError("Gemini text content field is empty.")
                
                # Clean up any markdown code blocks returned despite instructions
                cleaned_text = text_out.strip()
                if cleaned_text.startswith("```"):
                    # Strip ```json ... ``` or ``` ... ```
                    lines = cleaned_text.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    cleaned_text = "\n".join(lines).strip()
                
                return cleaned_text

        except httpx.TimeoutException as e:
            logger.error(f"Gemini API request timed out: {e}")
            raise GeminiClientError("Gemini API request timed out.")
        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API returned error code {e.response.status_code}: {e.response.text}")
            raise GeminiClientError(f"Gemini API returned error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error calling Gemini API: {e}")
            raise GeminiClientError(f"Failed to communicate with Gemini API: {e}")
