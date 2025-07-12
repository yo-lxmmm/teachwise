from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
import random
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API - only if API key is available
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("⚠️  Warning: GOOGLE_API_KEY not found. AI features will be disabled.")

app = FastAPI(
    title="TeachWise - Simple AI Teaching Simulator",
    description="Streamlined AI-powered teaching practice platform",
    version="2.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class StudentPersona(BaseModel):
    conceptual_readiness: int = 5  # 1-10, prior knowledge strength
    metacognitive_awareness: int = 5  # 1-10, ability to self-monitor understanding  
    persistence: int = 5  # 1-10, willingness to work through difficulty
    communication_style: str = "verbal"  # "verbal", "visual", "hands_on"
    confidence_level: int = 5  # 1-10, affects willingness to share thinking

class ScenarioRequest(BaseModel):
    gradeLevel: str
    subject: str
    learningOutcomes: str
    concepts: str
    question: Optional[str] = None  # Add question parameter
    studentPersona: StudentPersona = StudentPersona()

class StudentResponseRequest(BaseModel):
    scenario: Dict[str, Any]
    teacherMessage: str
    chatHistory: List[Dict[str, str]]

class EvaluationRequest(BaseModel):
    scenario: Dict[str, Any]
    selectedMisconception: int
    intervention: str
    chatHistory: List[Dict[str, str]]
    selectedStrategy: Optional[str] = None  # Add strategy parameter

class QuestionGenerationRequest(BaseModel):
    gradeLevel: str
    subject: str
    learningOutcomes: str
    concepts: str

# Gemini AI service
class GeminiService:
    def __init__(self):
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Gemini model only when needed"""
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                self.model = genai.GenerativeModel('gemini-1.5-pro')
                print("🚀 Gemini API initialized successfully")
            else:
                print("⚠️  Gemini API not initialized - no API key found")
        except Exception as e:
            print(f"❌ Error initializing Gemini API: {e}")
            self.model = None
    
    def _check_api_available(self):
        """Check if API is available before making calls"""
        if not self.model:
            raise HTTPException(
                status_code=503, 
                detail="AI service unavailable. Please check your GOOGLE_API_KEY environment variable."
            )
    
    def _clean_json_response(self, text: str) -> str:
        """Clean JSON response by removing markdown code blocks"""
        # Remove ```json and ``` if present
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:]  # Remove ```json
        elif text.startswith('```'):
            text = text[3:]   # Remove ```
        
        if text.endswith('```'):
            text = text[:-3]  # Remove closing ```
        
        return text.strip()
    
    def generate_question(self, grade_level: str, subject: str, learning_outcomes: str, concepts: str) -> Dict[str, Any]:
        """Generate a practice question based on learning outcomes and concepts"""
        
        self._check_api_available()
        
        prompt = f"""
        Generate a high-quality practice question for a {grade_level} {subject} class.
        
        Learning Outcomes: {learning_outcomes}
        Key Concepts: {concepts}
        
        Create a question that:
        1. Is open-ended and encourages student thinking
        2. Allows for multiple approaches or explanations
        3. Can reveal common misconceptions about the concepts
        4. Is age-appropriate for {grade_level} level
        5. Connects to the specified learning outcomes
        
        The question should be designed to help teachers diagnose student understanding and identify misconceptions.
        
        Return response in this JSON format:
        {{
            "question": "the practice question",
            "rationale": "why this question is effective for revealing misconceptions",
            "expectedMisconceptions": ["common misconception 1", "common misconception 2", "common misconception 3"]
        }}
        
        Return ONLY valid JSON, no other text or markdown formatting.
        """
        
        print(f"🔄 Calling Gemini API for question generation...")
        if self.model is None:
            raise HTTPException(status_code=503, detail="AI service unavailable")
        response = self.model.generate_content(prompt)
        print(f"✅ Gemini API response received")
        
        # Clean and parse the JSON response
        clean_text = self._clean_json_response(response.text)
        question_data = json.loads(clean_text)
        return question_data
    
    def generate_scenario(self, grade_level: str, subject: str, learning_outcomes: str, concepts: str, question: Optional[str], persona: StudentPersona) -> Dict[str, Any]:
        """Generate a complete teaching scenario with student profile and misconceptions"""
        
        self._check_api_available()
        
        if not question:
            raise ValueError("Question is required for scenario generation")
        
        # Build persona description for AI
        persona_description = f"""
        Student Characteristics:
        - Conceptual Readiness: {persona.conceptual_readiness}/10 (prior knowledge strength)
        - Metacognitive Awareness: {persona.metacognitive_awareness}/10 (ability to recognize own understanding/confusion)
        - Persistence: {persona.persistence}/10 (willingness to work through difficulty)
        - Communication Style: {persona.communication_style} (prefers {persona.communication_style} explanations)
        - Confidence Level: {persona.confidence_level}/10 (willingness to share thinking and ask questions)
        
        Behavioral Guidelines:
        - If confidence is low (1-3): Student is hesitant, asks for validation, says "I think maybe..." 
        - If confidence is high (8-10): Student is assertive, states opinions confidently
        - If persistence is low (1-3): Student gives up quickly, says "I don't know" often
        - If persistence is high (8-10): Student keeps trying, asks follow-up questions
        - If metacognitive awareness is low (1-3): Student doesn't recognize their mistakes or confusion
        - If metacognitive awareness is high (8-10): Student says things like "I'm confused about..." or "I think I understand but..."
        - If communication style is "visual": Student asks for pictures/diagrams, describes spatial relationships
        - If communication style is "hands_on": Student wants to try things, mentions physical examples
        - If communication style is "verbal": Student prefers explanations, asks for definitions
        """
        
        prompt = f"""
        Create a realistic teaching scenario for a {grade_level} {subject} class.
        
        Learning Outcomes: {learning_outcomes}
        Key Concepts: {concepts}
        Practice Question: {question}
        
        {persona_description}
        
        Generate a student who will respond to this specific question with a realistic misconception.
        The student should have a clear, logical (but incorrect) understanding that leads to their wrong answer.
        
        Generate a response in this JSON format:
        {{
            "student": {{
                "name": "realistic first name",
                "background": "brief background that reflects the student's persona characteristics",
                "performanceLevel": "struggling/average/advanced",
                "actualMisconception": "the specific misconception this student has about the concepts",
                "initialResponse": "how the student responds to the practice question - should show their misconception and persona traits"
            }},
            "misconceptionOptions": [
                "The correct misconception (this student's actual issue)",
                "Plausible but incorrect misconception 1",
                "Plausible but incorrect misconception 2", 
                "Plausible but incorrect misconception 3"
            ],
            "correctMisconceptionIndex": 0,
            "topic": "specific topic being discussed",
            "difficulty": "beginner/intermediate/advanced",
            "persona": {{
                "conceptual_readiness": {persona.conceptual_readiness},
                "metacognitive_awareness": {persona.metacognitive_awareness},
                "persistence": {persona.persistence},
                "communication_style": "{persona.communication_style}",
                "confidence_level": {persona.confidence_level}
            }},
            "practiceQuestion": "{question}"
        }}
        
        Make sure the student's initial response directly addresses the practice question and reveals their misconception.
        The response should also clearly reflect their persona characteristics.
        
        Return ONLY valid JSON, no other text or markdown formatting.
        """
        
        print(f"🔄 Calling Gemini API for scenario generation with question...")
        if self.model is None:
            raise HTTPException(status_code=503, detail="AI service unavailable")
        response = self.model.generate_content(prompt)
        print(f"✅ Gemini API response received")
        
        # Clean and parse the JSON response
        clean_text = self._clean_json_response(response.text)
        scenario_data = json.loads(clean_text)
        return scenario_data
    
    def generate_student_response(self, scenario: Dict[str, Any], teacher_message: str, chat_history: List[Dict[str, str]]) -> str:
        """Generate student response based on their misconception and persona"""
        
        self._check_api_available()
        
        student = scenario.get('student', {})
        misconception = student.get('actualMisconception', '')
        persona = scenario.get('persona', {})
        practice_question = scenario.get('practiceQuestion', '')
        
        # Build context from chat history
        context = ""
        for msg in chat_history[-6:]:  # Last 6 messages for context
            context += f"{msg['sender'].title()}: {msg['message']}\n"
        
        # Build persona behavior guidance
        persona_guidance = f"""
        PERSONA CHARACTERISTICS TO MAINTAIN:
        - Conceptual Readiness: {persona.get('conceptual_readiness', 5)}/10
        - Metacognitive Awareness: {persona.get('metacognitive_awareness', 5)}/10  
        - Persistence: {persona.get('persistence', 5)}/10
        - Communication Style: {persona.get('communication_style', 'verbal')}
        - Confidence Level: {persona.get('confidence_level', 5)}/10
        
        BEHAVIORAL CONSISTENCY:
        - Confidence {persona.get('confidence_level', 5)}/10: {"Be hesitant, use 'maybe', 'I think', ask for validation" if persona.get('confidence_level', 5) <= 3 else "Be assertive and state opinions clearly" if persona.get('confidence_level', 5) >= 8 else "Show moderate confidence"}
        - Persistence {persona.get('persistence', 5)}/10: {"Give up quickly, say 'I don't know' often" if persona.get('persistence', 5) <= 3 else "Keep trying, ask follow-up questions" if persona.get('persistence', 5) >= 8 else "Show average persistence"}
        - Metacognitive {persona.get('metacognitive_awareness', 5)}/10: {"Don't recognize mistakes or confusion" if persona.get('metacognitive_awareness', 5) <= 3 else "Explicitly state confusion: 'I'm confused about...', 'I think I understand but...'" if persona.get('metacognitive_awareness', 5) >= 8 else "Show some self-awareness"}
        - Communication: {f"Ask for diagrams/pictures, describe spatial relationships" if persona.get('communication_style') == 'visual' else f"Want to try things, mention physical examples" if persona.get('communication_style') == 'hands_on' else "Prefer verbal explanations, ask for definitions"}
        """
        
        prompt = f"""
        You are roleplaying as {student.get('name', 'a student')} who is {student.get('performanceLevel', 'average')} in {scenario.get('topic', 'this subject')}.

        Your Background: {student.get('background', '')}
        Your Specific Misconception: {misconception}
        Original Practice Question: {practice_question}
        
        {persona_guidance}

        Recent conversation:
        {context}

        The teacher just asked: "{teacher_message}"

        IMPORTANT RESPONSE GUIDELINES:
        1. Your responses should be REASONED and logical from your perspective
        2. Show your thinking process - explain WHY you think something is correct
        3. Your misconception should lead to consistent, logical (but wrong) reasoning
        4. Don't just give random wrong answers - give answers that make sense given your misconception
        5. Stay true to your persona characteristics throughout
        6. If the teacher asks you to explain, show your reasoning step by step
        7. If asked about the original question, refer back to your misconception-based understanding
        
        Respond as this student would, showing both your misconception-based reasoning AND your persona traits.
        Keep responses conversational and age-appropriate for {scenario.get('difficulty', 'intermediate')} level.
        
        Return ONLY the student's response, no other text or formatting.
        """
        
        print(f"🔄 Calling Gemini API for reasoned student response...")
        if self.model is None:
            raise HTTPException(status_code=503, detail="AI service unavailable")
        response = self.model.generate_content(prompt)
        print(f"✅ Gemini API response received")
        
        return response.text.strip()
    
    def evaluate_session(self, scenario: Dict[str, Any], selected_misconception: int, intervention: str, chat_history: List[Dict[str, str]], selected_strategy: Optional[str] = None) -> Dict[str, Any]:
        """Evaluate the teacher's diagnosis and intervention"""
        
        self._check_api_available()
        
        correct_index = scenario.get('correctMisconceptionIndex', 0)
        correct_diagnosis = selected_misconception == correct_index
        
        # Count teacher questions
        teacher_questions = len([msg for msg in chat_history if msg['sender'] == 'teacher'])
        
        # Build evaluation prompt
        chat_text = ""
        for msg in chat_history:
            chat_text += f"{msg['sender'].title()}: {msg['message']}\n"
        
        strategy_context = f"Selected Teaching Strategy: {selected_strategy}" if selected_strategy else "No specific strategy selected"
        
        prompt = f"""
        Evaluate this teaching session:
        
        Student's Actual Misconception: {scenario['student']['actualMisconception']}
        Teacher's Diagnosis: {scenario['misconceptionOptions'][selected_misconception]}
        Correct Diagnosis: {"YES" if correct_diagnosis else "NO"}
        
        Teacher's Intervention: {intervention}
        {strategy_context}
        
        Chat History:
        {chat_text}
        
        Provide evaluation in this JSON format:
        {{
            "correctDiagnosis": {str(correct_diagnosis).lower()},
            "score": 85,
            "questioningScore": 8,
            "correctMisconception": "the student's actual misconception",
            "feedback": "detailed feedback on the teacher's performance, including question quality, diagnostic accuracy, and intervention effectiveness",
            "improvements": ["specific suggestion 1", "specific suggestion 2", "specific suggestion 3"]
        }}
        
        Score the session 0-100 based on:
        - Diagnostic accuracy (35 points)
        - Quality of questioning (30 points) 
        - Intervention effectiveness (25 points)
        - Use of teaching strategies (10 points)
        
        Questioning score (1-10) based on:
        - Probing questions that reveal student thinking
        - Progression from general to specific
        - Avoiding leading questions
        - Encouraging student reasoning
        
        Consider the teaching strategy used (if any) in your evaluation.
        
        Return ONLY valid JSON, no other text or markdown formatting.
        """
        
        print(f"🔄 Calling Gemini API for session evaluation...")
        if self.model is None:
            raise HTTPException(status_code=503, detail="AI service unavailable")
        response = self.model.generate_content(prompt)
        print(f"✅ Gemini API response received")
        
        # Clean and parse the JSON response
        clean_text = self._clean_json_response(response.text)
        evaluation = json.loads(clean_text)
        return evaluation

# Initialize services
gemini_service = GeminiService()

# API Routes
@app.get("/")
async def serve_frontend():
    """Serve the main frontend"""
    return FileResponse("index.html")

@app.post("/api/generate-question")
async def generate_question(request: QuestionGenerationRequest):
    """Generate a practice question based on learning outcomes and concepts"""
    try:
        question_data = gemini_service.generate_question(
            request.gradeLevel,
            request.subject,
            request.learningOutcomes,
            request.concepts
        )
        return question_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate question: {str(e)}")

@app.post("/api/generate-scenario")
async def generate_scenario(request: ScenarioRequest):
    """Generate a new teaching scenario"""
    try:
        if not request.question:
            raise HTTPException(status_code=400, detail="Question is required for scenario generation")
        
        scenario = gemini_service.generate_scenario(
            request.gradeLevel,
            request.subject,
            request.learningOutcomes,
            request.concepts,
            request.question,
            request.studentPersona
        )
        return scenario
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate scenario: {str(e)}")

@app.post("/api/student-response")
async def get_student_response(request: StudentResponseRequest):
    """Get AI student response to teacher's question"""
    try:
        response = gemini_service.generate_student_response(
            request.scenario,
            request.teacherMessage,
            request.chatHistory
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate student response: {str(e)}")

@app.post("/api/evaluate-session")
async def evaluate_session(request: EvaluationRequest):
    """Evaluate the teacher's diagnosis and intervention"""
    try:
        evaluation = gemini_service.evaluate_session(
            request.scenario,
            request.selectedMisconception,
            request.intervention,
            request.chatHistory,
            request.selectedStrategy
        )
        return evaluation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate session: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_key_status = "available" if os.getenv("GOOGLE_API_KEY") else "missing"
    return {
        "status": "healthy",
        "version": "2.0",
        "api_key": api_key_status,
        "features": ["Teaching Simulation", "AI Student Responses", "Session Evaluation"]
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify deployment"""
    return {
        "message": "TeachWise API is running!",
        "timestamp": "2024-01-01T00:00:00Z",
        "environment": "production"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 