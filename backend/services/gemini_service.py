from google import genai
from google.genai import errors
from exceptions.custom import ExternalServiceException, ConfigurationException
from config.settings import settings
from core.logging import logger
import re

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        
        if not self.api_key:
            raise ConfigurationException("GEMINI_API_KEY is missing.")
            
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini SDK: {str(e)}")
            raise ExternalServiceException("Failed to initialize Google GenAI SDK.")

    def test_connection(self) -> bool:
        """
        Tests the connection and validates the API key by requesting a tiny generation.
        """
        try:
            # A minimal request to verify the key and model
            response = self.client.models.generate_content(
                model=self.model,
                contents="ping",
                config={"max_output_tokens": 1}
            )
            return True
        except errors.APIError as e:
            logger.error(f"Gemini API Error during connection test: {str(e)}")
            raise ConfigurationException("Invalid API Key or Model.")
        except Exception as e:
            logger.error(f"Unexpected Error during connection test: {str(e)}")
            raise ExternalServiceException("Failed to connect to Gemini API.")

    def generate_rtl(self, prompt: str) -> str:
        """
        Generates RTL code from the prompt and handles SDK exceptions.
        """
        try:
            # We enforce a timeout context if supported by SDK, but SDK handles it via HTTP requests
            # The exact parameter for timeout depends on the underlying SDK HTTP client.
            # We will use default timeouts but wrap in general exception handling.
            
            logger.info(f"Sending prompt to {self.model}")
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if not response or not response.text:
                raise ExternalServiceException("Received empty response from Gemini.")
                
            # Extract Verilog code from Markdown blocks
            raw_text = response.text
            match = re.search(r"```verilog\n(.*?)```", raw_text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            # If no markdown block found, just return the text
            return raw_text.strip()
            
        except errors.APIError as e:
            logger.error(f"Gemini API Error: {str(e)}")
            # Handle specific status codes if present in error message/code
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str:
                raise ExternalServiceException("Quota Exceeded.")
            elif "not found" in error_str or "404" in error_str:
                raise ConfigurationException("Invalid Model.")
            else:
                raise ExternalServiceException("Gemini API Error.")
        except Exception as e:
            error_str = str(e).lower()
            logger.error(f"Gemini SDK Error: {str(e)}")
            if "timeout" in error_str:
                raise ExternalServiceException("Request Timeout.")
            elif "connection" in error_str or "network" in error_str:
                raise ExternalServiceException("Network Failure.")
                
            raise ExternalServiceException("An unexpected error occurred while calling Gemini.")

gemini_service = GeminiService()
