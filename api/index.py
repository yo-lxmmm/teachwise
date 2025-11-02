from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, Any, Optional

# Add the parent directory to Python path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Import your existing TeachWise functionality
# Note: Environment variables should be available at import time in Vercel
import os
print(f"🔍 DEBUG: Environment check at import - GOOGLE_API_KEY present: {bool(os.getenv('GOOGLE_API_KEY'))}")
print(f"🔍 DEBUG: Environment check at import - GEMINI_API_KEY present: {bool(os.getenv('GEMINI_API_KEY'))}")

try:
    from simple_app import gemini_service
    print("✅ Successfully imported TeachWise gemini_service")
    print(f"🔍 DEBUG: gemini_service.model status: {gemini_service.model is not None}")
    TEACHWISE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Failed to import TeachWise functionality: {e}")
    import traceback
    print(f"❌ DEBUG: Full import traceback:\n{traceback.format_exc()}")
    TEACHWISE_AVAILABLE = False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '':
            # Serve HTML
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                html_path = str(parent_dir / 'index.html')
                with open(html_path, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            except FileNotFoundError:
                self.wfile.write(b"<h1>TeachWise</h1><p>Frontend not found</p>")
        else:
            # API endpoints
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            if path == '/health':
                # Check API key availability
                api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                api_key_status = "available" if api_key else "missing"
                api_key_preview = api_key[:10] + "..." if api_key and len(api_key) > 10 else "not_set"
                
                # Check if gemini service is available and initialized
                ai_ready = False
                model_info = None
                if TEACHWISE_AVAILABLE:
                    try:
                        ai_ready = gemini_service.model is not None
                        if gemini_service.model:
                            # Try to get model info
                            model_info = str(type(gemini_service.model))
                    except Exception as e:
                        ai_ready = False
                        model_info = f"Error checking model: {str(e)}"
                
                response_data = {
                    "status": "healthy",
                    "version": "2.0", 
                    "api_key": api_key_status,
                    "api_key_preview": api_key_preview,
                    "ai_ready": ai_ready,
                    "teachwise_available": TEACHWISE_AVAILABLE,
                    "model_info": model_info,
                    "environment_vars": {
                        "GOOGLE_API_KEY_set": bool(os.getenv("GOOGLE_API_KEY")),
                        "GEMINI_API_KEY_set": bool(os.getenv("GEMINI_API_KEY"))
                    }
                }
            else:
                response_data = {"message": "TeachWise API", "path": path}
            
            self.wfile.write(json.dumps(response_data).encode())
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Read POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        
        try:
            request_data = json.loads(post_data)
        except:
            request_data = {}
        
        # Set headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Route API calls using your existing TeachWise functionality
        if path == '/api/generate-question':
            if not TEACHWISE_AVAILABLE:
                response_data = {"error": "TeachWise service not available - check server logs"}
                self.wfile.write(json.dumps(response_data).encode())
                return
            
            if gemini_service.model is None:
                response_data = {
                    "error": "AI service unavailable - GOOGLE_API_KEY environment variable not set in Vercel",
                    "help": "Please set GOOGLE_API_KEY in Vercel project settings > Environment Variables"
                }
                self.wfile.write(json.dumps(response_data).encode())
                return
                
            try:
                grade_level = request_data.get("gradeLevel", "5th grade")
                subject = request_data.get("subject", "Math")
                learning_outcomes = request_data.get("learningOutcomes", "Basic understanding")
                concepts = request_data.get("concepts", "Basic concepts")
                language = request_data.get("language", "english")
                
                response_data = gemini_service.generate_question(grade_level, subject, learning_outcomes, concepts, language)
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"❌ Question generation error: {error_trace}")
                response_data = {
                    "error": f"Question generation failed: {str(e)}",
                    "details": error_trace if os.getenv("DEBUG") else None
                }
                
        elif path == '/api/generate-scenario':
            if not TEACHWISE_AVAILABLE:
                response_data = {"error": "TeachWise service not available - check server logs"}
                self.wfile.write(json.dumps(response_data).encode())
                return
            
            if gemini_service.model is None:
                response_data = {
                    "error": "AI service unavailable - GOOGLE_API_KEY environment variable not set in Vercel",
                    "help": "Please set GOOGLE_API_KEY in Vercel project settings > Environment Variables"
                }
                self.wfile.write(json.dumps(response_data).encode())
                return
                
            try:
                grade_level = request_data.get("gradeLevel", "5th grade")
                subject = request_data.get("subject", "Math")
                learning_outcomes = request_data.get("learningOutcomes", "Basic understanding")
                concepts = request_data.get("concepts", "Basic concepts")
                question = request_data.get("question", "")
                language = request_data.get("language", "english")
                
                # Create student persona from request
                student_persona_data = request_data.get("studentPersona", {})
                from simple_app import StudentPersona
                student_persona = StudentPersona(**student_persona_data)
                
                response_data = gemini_service.generate_scenario(grade_level, subject, learning_outcomes, concepts, question, student_persona, language)
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"❌ Scenario generation error: {error_trace}")
                response_data = {
                    "error": f"Scenario generation failed: {str(e)}",
                    "details": error_trace if os.getenv("DEBUG") else None
                }
                
        elif path == '/api/student-response':
            if not TEACHWISE_AVAILABLE:
                response_data = {"error": "TeachWise service not available - check server logs"}
                self.wfile.write(json.dumps(response_data).encode())
                return
            
            if gemini_service.model is None:
                response_data = {
                    "error": "AI service unavailable - GOOGLE_API_KEY environment variable not set in Vercel",
                    "help": "Please set GOOGLE_API_KEY in Vercel project settings > Environment Variables"
                }
                self.wfile.write(json.dumps(response_data).encode())
                return
                
            try:
                scenario = request_data.get("scenario", {})
                teacher_message = request_data.get("teacherMessage", "")
                chat_history = request_data.get("chatHistory", [])
                language = request_data.get("language", "english")
                
                student_response = gemini_service.generate_student_response(scenario, teacher_message, chat_history, language)
                response_data = {"response": student_response}
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"❌ Student response error: {error_trace}")
                response_data = {
                    "error": f"Student response failed: {str(e)}",
                    "details": error_trace if os.getenv("DEBUG") else None
                }
                
        elif path == '/api/evaluate-session':
            if not TEACHWISE_AVAILABLE:
                response_data = {"error": "TeachWise service not available - check server logs"}
                self.wfile.write(json.dumps(response_data).encode())
                return
            
            if gemini_service.model is None:
                response_data = {
                    "error": "AI service unavailable - GOOGLE_API_KEY environment variable not set in Vercel",
                    "help": "Please set GOOGLE_API_KEY in Vercel project settings > Environment Variables"
                }
                self.wfile.write(json.dumps(response_data).encode())
                return
                
            try:
                scenario = request_data.get("scenario", {})
                selected_misconception = request_data.get("selectedMisconception", 0)
                intervention = request_data.get("intervention", "")
                chat_history = request_data.get("chatHistory", [])
                selected_strategy = request_data.get("selectedStrategy")
                language = request_data.get("language", "english")
                
                response_data = gemini_service.evaluate_session(scenario, selected_misconception, intervention, chat_history, selected_strategy, language)
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"❌ Session evaluation error: {error_trace}")
                response_data = {
                    "error": f"Session evaluation failed: {str(e)}",
                    "details": error_trace if os.getenv("DEBUG") else None
                }
        else:
            response_data = {
                "error": "API endpoint not found",
                "path": path,
                "available_endpoints": ["/api/generate-question", "/api/generate-scenario", "/api/student-response", "/api/evaluate-session"]
            }
        
        self.wfile.write(json.dumps(response_data).encode())
        
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
