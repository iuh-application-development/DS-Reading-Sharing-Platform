from google import genai
from google.genai import types
from flask import current_app
import json
import os

class AIAssistantError(Exception):
    """Custom exception for AI Assistant errors"""
    pass

class AIAssistant:
    def __init__(self):
        api_key = current_app.config.get('GOOGLE_API_KEY')
        if not api_key:
            raise AIAssistantError("Google API key not configured")
            
        try:
            # Khởi tạo client với API key
            self.client = genai.Client(api_key=api_key)
            # Sử dụng model experimental version
            self.model = "gemini-2.5-pro-preview-03-25"
            
        except Exception as e:
            current_app.logger.error(f"Failed to initialize Gemini API: {str(e)}")
            raise AIAssistantError(f"Failed to initialize Gemini API: {str(e)}")
        
    def validate_api_key(self):
        """Validate Google API key"""
        try:
            # Thử một yêu cầu đơn giản
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text="Hello")]
                )
            ]
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents
            )
            return True
        except Exception as e:
            current_app.logger.error(f"Google API key validation failed: {str(e)}")
            raise AIAssistantError(f"Invalid Google API key: {str(e)}")
            
    def get_writing_suggestions(self, content, task_type):
        """Get AI suggestions for writing tasks"""
        if not self.validate_api_key():
            raise AIAssistantError("Invalid Google API key")
            
        try:
            if not content:
                raise AIAssistantError("Content is required")
                
            if task_type not in ["title", "structure", "tags", "improve", "summarize"]:
                raise AIAssistantError("Invalid task type")
                
            if task_type == "title":
                prompt = f"""Given this content, suggest 3 engaging titles in Vietnamese:
                Content: {content}
                Format the response as a JSON array of strings."""
                
            elif task_type == "structure":
                prompt = f"""Analyze this content and suggest an improved structure in Vietnamese:
                Content: {content}
                Format the response as a JSON with sections and suggestions."""
                
            elif task_type == "tags":
                prompt = f"""Suggest relevant tags in Vietnamese for this content:
                Content: {content}
                Format the response as a JSON array of strings."""
                
            elif task_type == "improve":
                prompt = f"""Review and suggest improvements in Vietnamese for this content:
                Content: {content}
                Format the response as a JSON with suggestions for clarity, engagement, and grammar."""
                
            elif task_type == "summarize":
                prompt = f"""Create a concise summary in Vietnamese of this content:
                Content: {content}
                Format the response as a JSON with a summary field."""

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            ]
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents
            )
            return json.loads(response.text)
            
        except json.JSONDecodeError:
            current_app.logger.error("Failed to parse AI response as JSON")
            raise AIAssistantError("Invalid response format from AI")
        except Exception as e:
            current_app.logger.error(f"AI Assistant error: {str(e)}")
            raise AIAssistantError(f"Failed to get AI suggestions: {str(e)}")
            
    def get_chat_response(self, message, context=None):
        """Get a conversational response from the AI assistant"""
        if not self.validate_api_key():
            raise AIAssistantError("Invalid Google API key")
            
        try:
            # Tạo prompt với context nếu có
            system_prompt = """Bạn là một trợ lý AI thân thiện và hữu ích. Bạn có thể:
            1. Trả lời các câu hỏi về nhiều chủ đề
            2. Giúp đỡ trong việc viết và chỉnh sửa nội dung
            3. Đưa ra gợi ý và tư vấn
            4. Thảo luận về các vấn đề xã hội, công nghệ, khoa học, v.v.
            5. Hỗ trợ học tập và nghiên cứu
            
            Hãy trả lời một cách tự nhiên, thân thiện và hữu ích. Sử dụng Markdown để định dạng câu trả lời cho dễ đọc."""
            
            prompt = f"{system_prompt}\n\n"
            if context:
                prompt += f"Context: {context}\n\n"
            prompt += f"User: {message}"
                
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            ]
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents
            )
            return response.text
            
        except Exception as e:
            current_app.logger.error(f"AI Chat error: {str(e)}")
            raise AIAssistantError(f"Failed to get chat response: {str(e)}")