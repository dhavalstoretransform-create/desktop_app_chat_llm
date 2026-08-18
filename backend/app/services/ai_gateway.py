import time
import os
from typing import Dict, Any, Optional

from app.models.ai_model import AIModel

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class AIGateway:
    """
    Central gateway for communicating with various AI providers.
    """
    
    @staticmethod
    async def complete(model: AIModel, prompt: str, history: str = "") -> Dict[str, Any]:
        """
        Executes a chat completion request to the designated provider.
        
        Returns:
            Dict containing:
            - content: str
            - input_tokens: int
            - output_tokens: int
            - total_tokens: int
            - response_time_ms: int
        """
        if not model.provider or not model.provider.is_active:
            raise ValueError("AI Provider is missing or inactive")
        
        provider_code = model.provider.code.upper()
        
        start_time = time.perf_counter()
        
        try:
            if provider_code == "OPENAI":
                result = await AIGateway._call_openai(model, prompt, history)
            elif provider_code == "ANTHROPIC":
                result = await AIGateway._call_anthropic(model, prompt, history)
            elif provider_code == "GOOGLE" or provider_code == "GEMINI":
                result = await AIGateway._call_google(model, prompt, history)
            else:
                raise ValueError(f"Unsupported provider code: {provider_code}")
        except Exception as e:
            # Re-raise standard exception for higher layers to catch
            raise RuntimeError(f"AI Provider error: {str(e)}")
            
        end_time = time.perf_counter()
        result["response_time_ms"] = int((end_time - start_time) * 1000)
        
        return result

    @staticmethod
    async def _call_openai(model: AIModel, prompt: str, history: str = "") -> Dict[str, Any]:
        if not AsyncOpenAI:
            raise RuntimeError("OpenAI SDK is not installed")
            
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        client = AsyncOpenAI(api_key=api_key)
        
        messages = []
        if history:
            messages.append({"role": "system", "content": "Conversation history:\n" + history})
        messages.append({"role": "user", "content": prompt})
        
        response = await client.chat.completions.create(
            model=model.code,
            messages=messages,
        )
        
        return {
            "content": response.choices[0].message.content or "",
            "input_tokens": response.usage.prompt_tokens if response.usage else 0,
            "output_tokens": response.usage.completion_tokens if response.usage else 0,
            "total_tokens": response.usage.total_tokens if response.usage else 0,
        }

    @staticmethod
    async def _call_anthropic(model: AIModel, prompt: str, history: str = "") -> Dict[str, Any]:
        if not AsyncAnthropic:
            raise RuntimeError("Anthropic SDK is not installed")
            
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
            
        client = AsyncAnthropic(api_key=api_key)
        
        # Anthropic standardizes messages
        messages = [{"role": "user", "content": prompt}]
        
        response = await client.messages.create(
            model=model.code,
            messages=messages,
            system=history if history else None,
            max_tokens=model.max_output_tokens or 4096,
        )
        
        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text
                
        input_tokens = response.usage.input_tokens if hasattr(response.usage, "input_tokens") else 0
        output_tokens = response.usage.output_tokens if hasattr(response.usage, "output_tokens") else 0
        
        return {
            "content": content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        }

    @staticmethod
    async def _call_google(model: AIModel, prompt: str, history: str = "") -> Dict[str, Any]:
        if not genai:
            raise RuntimeError("Google Generative AI SDK is not installed")
            
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
            
        genai.configure(api_key=api_key)
        
        # Using the new google-generativeai API
        genai_model = genai.GenerativeModel(model.code)
        
        full_prompt = prompt
        if history:
            full_prompt = f"Context:\n{history}\n\nUser: {prompt}"
            
        # Call synchronously in a thread or async if supported (genai generate_content_async)
        response = await genai_model.generate_content_async(full_prompt)
        
        # Metadata tokens (if available)
        input_tokens = 0
        output_tokens = 0
        total_tokens = 0
        
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
            output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)
            total_tokens = getattr(response.usage_metadata, "total_token_count", 0)
        else:
            # Fallback estimation if no usage metadata available from older API formats
            input_tokens = len(full_prompt) // 4 + 1
            output_tokens = len(response.text) // 4 + 1
            total_tokens = input_tokens + output_tokens
        
        return {
            "content": response.text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }
