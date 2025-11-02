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

# Load environment variables from .env file (only if file exists)
try:
    load_dotenv()
except:
    pass  # .env file doesn't exist in Vercel, that's fine

# Configure Gemini API - check both possible environment variable names
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    print("🚀 Gemini API initialized successfully")
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
    language: str = "english"  # Add language parameter

class StudentResponseRequest(BaseModel):
    scenario: Dict[str, Any]
    teacherMessage: str
    chatHistory: List[Dict[str, str]]
    language: str = "english"  # Add language parameter

class EvaluationRequest(BaseModel):
    scenario: Dict[str, Any]
    selectedMisconception: int
    intervention: str
    chatHistory: List[Dict[str, str]]
    selectedStrategy: Optional[str] = None  # Add strategy parameter
    language: str = "english"  # Add language parameter

class QuestionGenerationRequest(BaseModel):
    gradeLevel: str
    subject: str
    learningOutcomes: str
    concepts: str
    language: str = "english"  # Add language parameter

# Gemini AI service
class GeminiService:
    def __init__(self):
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Gemini model only when needed"""
        try:
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                # Try different model names in order of preference
                # gemini-1.5-flash is faster and more widely available
                # gemini-1.5-pro may not be available in all regions/API versions
                model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
                
                for model_name in model_names:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        print(f"🚀 Gemini API model initialized successfully with {model_name}")
                        return
                    except Exception as model_error:
                        print(f"⚠️  Failed to initialize {model_name}: {model_error}")
                        continue
                
                # If all models fail, raise error
                raise Exception("Could not initialize any Gemini model")
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
    
    def _get_language_prefix(self, language: str) -> str:
        """Get language-specific prompt prefix"""
        if language == "traditional_chinese":
            return """
            **[繁體中文模式]** 你扮演一位AI教學助手，你必須以繁體中文回答所有問題。
            
            重要指示：
            1. 回答主體必須使用繁體中文（台灣文），不可使用其他語言
            2. 不要使用拼音或簡體字
            3. 保持專業的教學語調
            4. 確保所有回覆都是繁體中文
            
            """
        return ""  # Default to English (no prefix needed)
    
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
    
    def generate_question(self, grade_level: str, subject: str, learning_outcomes: str, concepts: str, language: str = "english") -> Dict[str, Any]:
        """Generate a practice question based on learning outcomes and concepts"""
        
        self._check_api_available()
        
        language_prefix = self._get_language_prefix(language)
        
        # Translate labels based on language
        if language == "traditional_chinese":
            question_template = """
            為 {grade_level} {subject} 課程生成一個高質量的練習問題。
            
            學習成果：{learning_outcomes}
            關鍵概念：{concepts}
            
            創建一個問題，要求：
            1. 是開放式的，鼓勵學生思考
            2. 允許多種方法或解釋
            3. 可以揭示關於概念的常見誤解
            4. 適合 {grade_level} 年級水平
            5. 與指定的學習成果相關
            
            問題應該設計來幫助教師診斷學生理解並識別誤解。
            
            以這個JSON格式回覆：
            {{
                "question": "練習問題",
                "rationale": "為什麼這個問題對揭示誤解有效",
                "expectedMisconceptions": ["常見誤解1", "常見誤解2", "常見誤解3"]
            }}
            
            僅回覆有效的JSON，不要其他文字或markdown格式。
            """
        else:
            question_template = """
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
        
        prompt = language_prefix + question_template.format(
            grade_level=grade_level,
            subject=subject,
            learning_outcomes=learning_outcomes,
            concepts=concepts
        )
        
        print(f"🔄 Calling Gemini API for question generation...")
        if self.model is None:
            raise HTTPException(status_code=503, detail="AI service unavailable")
        response = self.model.generate_content(prompt)
        print(f"✅ Gemini API response received")
        
        # Clean and parse the JSON response
        clean_text = self._clean_json_response(response.text)
        question_data = json.loads(clean_text)
        return question_data
    
    def generate_scenario(self, grade_level: str, subject: str, learning_outcomes: str, concepts: str, question: Optional[str], persona: StudentPersona, language: str = "english") -> Dict[str, Any]:
        """Generate a complete teaching scenario with student profile and misconceptions"""
        
        self._check_api_available()
        
        if not question:
            raise ValueError("Question is required for scenario generation")
        
        language_prefix = self._get_language_prefix(language)
        
        # Build persona description for AI
        if language == "traditional_chinese":
            persona_description = f"""
            學生特徵：
            - 概念準備度：{persona.conceptual_readiness}/10 (先前知識強度)
            - 後設認知意識：{persona.metacognitive_awareness}/10 (識別自己理解/困惑的能力)
            - 堅持度：{persona.persistence}/10 (克服困難的意願)
            - 溝通風格：{persona.communication_style} (偏好{persona.communication_style}解釋)
            - 信心水平：{persona.confidence_level}/10 (分享思考和提問的意願)
            
            行為指導：
            - 如果信心低 (1-3)：學生猶豫不決，尋求確認，說「我想可能...」
            - 如果信心高 (8-10)：學生自信，明確表達意見
            - 如果堅持度低 (1-3)：學生容易放棄，經常說「我不知道」
            - 如果堅持度高 (8-10)：學生持續嘗試，提出後續問題
            - 如果後設認知意識低 (1-3)：學生不認識自己的錯誤或困惑
            - 如果後設認知意識高 (8-10)：學生會說「我對...感到困惑」或「我想我明白但是...」
            - 如果溝通風格是「視覺」：學生要求圖片/圖表，描述空間關係
            - 如果溝通風格是「動手」：學生想要嘗試事物，提及實際例子
            - 如果溝通風格是「口語」：學生偏好解釋，詢問定義
            """
            
            scenario_template = """
            為 {grade_level} {subject} 課程創建一個現實的教學情境。
            
            學習成果：{learning_outcomes}
            關鍵概念：{concepts}
            練習問題：{question}
            
            {persona_description}
            
            生成一個會對這個具體問題回應現實誤解的學生。
            學生應該有清晰、邏輯性（但不正確）的理解，導致錯誤答案。
            
            以這個JSON格式生成回應：
            {{
                "student": {{
                    "name": "現實的名字",
                    "background": "反映學生人格特徵的簡短背景",
                    "performanceLevel": "掙扎/平均/優秀",
                    "actualMisconception": "這個學生對概念的具體誤解",
                    "initialResponse": "學生如何回應練習問題 - 應顯示他們的誤解和人格特徵"
                }},
                "misconceptionOptions": [
                    "正確的誤解（這個學生的實際問題）",
                    "似是而非但不正確的誤解1",
                    "似是而非但不正確的誤解2",
                    "似是而非但不正確的誤解3"
                ],
                "correctMisconceptionIndex": 0,
                "topic": "討論的具體主題",
                "difficulty": "初級/中級/進階",
                "persona": {{
                    "conceptual_readiness": {persona.conceptual_readiness},
                    "metacognitive_awareness": {persona.metacognitive_awareness},
                    "persistence": {persona.persistence},
                    "communication_style": "{persona.communication_style}",
                    "confidence_level": {persona.confidence_level}
                }},
                "practiceQuestion": "{question}"
            }}
            
            確保學生的初始回應直接回答練習問題並揭示他們的誤解。
            回應也應該清楚地反映他們的人格特徵。
            
            僅回覆有效的JSON，不要其他文字或markdown格式。
            """
        else:
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
            
            scenario_template = """
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
        
        prompt = language_prefix + scenario_template.format(
            grade_level=grade_level,
            subject=subject,
            learning_outcomes=learning_outcomes,
            concepts=concepts,
            question=question,
            persona_description=persona_description,
            persona=persona
        )
        
        print(f"🔄 Calling Gemini API for scenario generation with question...")
        if self.model is None:
            raise HTTPException(status_code=503, detail="AI service unavailable")
        response = self.model.generate_content(prompt)
        print(f"✅ Gemini API response received")
        
        # Clean and parse the JSON response
        clean_text = self._clean_json_response(response.text)
        scenario_data = json.loads(clean_text)
        return scenario_data
    
    def generate_student_response(self, scenario: Dict[str, Any], teacher_message: str, chat_history: List[Dict[str, str]], language: str = "english") -> str:
        """Generate student response based on their misconception and persona"""
        
        self._check_api_available()
        
        student = scenario.get('student', {})
        misconception = student.get('actualMisconception', '')
        persona = scenario.get('persona', {})
        practice_question = scenario.get('practiceQuestion', '')
        
        language_prefix = self._get_language_prefix(language)
        
        # Build context from chat history
        context = ""
        for msg in chat_history[-6:]:  # Last 6 messages for context
            context += f"{msg['sender'].title()}: {msg['message']}\n"
        
        # Build persona behavior guidance
        if language == "traditional_chinese":
            persona_guidance = f"""
            要維持的人格特徵：
            - 概念準備度：{persona.get('conceptual_readiness', 5)}/10
            - 後設認知意識：{persona.get('metacognitive_awareness', 5)}/10  
            - 堅持度：{persona.get('persistence', 5)}/10
            - 溝通風格：{persona.get('communication_style', 'verbal')}
            - 信心水平：{persona.get('confidence_level', 5)}/10
            
            行為一致性：
            - 信心 {persona.get('confidence_level', 5)}/10：{"猶豫不決，使用「可能」、「我想」，尋求確認" if persona.get('confidence_level', 5) <= 3 else "自信並清楚表達意見" if persona.get('confidence_level', 5) >= 8 else "表現中等信心"}
            - 堅持度 {persona.get('persistence', 5)}/10：{"容易放棄，經常說「我不知道」" if persona.get('persistence', 5) <= 3 else "持續嘗試，提出後續問題" if persona.get('persistence', 5) >= 8 else "表現平均堅持度"}
            - 後設認知 {persona.get('metacognitive_awareness', 5)}/10：{"不認識自己的錯誤或困惑" if persona.get('metacognitive_awareness', 5) <= 3 else "會說「我對...感到困惑」或「我想我明白但是...」" if persona.get('metacognitive_awareness', 5) >= 8 else "表現中等後設認知意識"}
            - 溝通：{f"要求圖表/圖片，描述空間關係" if persona.get('communication_style') == 'visual' else f"想要嘗試事物，提及實際例子" if persona.get('communication_style') == 'hands_on' else "偏好口語解釋，詢問定義"}
            """
            
            response_template = """
            你正在扮演 {student_name}，他是一個在 {topic} 方面表現{performance_level}的學生。

            你的背景：{background}
            你的具體誤解：{misconception}
            原始練習問題：{practice_question}
            
            {persona_guidance}

            最近的對話：
            {context}

            老師剛剛問：「{teacher_message}」

            重要回應指導：
            1. 你的回應應該是有推理的，從你的角度來說是邏輯性的
            2. 展示你的思考過程 - 解釋為什麼你認為某事是正確的
            3. 你的誤解應該導致一致的、邏輯性的（但錯誤的）推理
            4. 不要只是給出隨機的錯誤答案 - 給出基於你的誤解而有意義的答案
            5. 在整個過程中保持你的人格特徵
            6. 如果老師要求你解釋，逐步展示你的推理
            7. 如果問及原始問題，請參考你基於誤解的理解
            
            像這個學生一樣回應，展示你基於誤解的推理和人格特徵。
            保持對話性和適合{difficulty}難度的年齡。
            
            僅回覆學生的回應，不要其他文字或格式。
            """
        else:
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
            - Metacognitive {persona.get('metacognitive_awareness', 5)}/10: {"Don't recognize own mistakes or confusion" if persona.get('metacognitive_awareness', 5) <= 3 else "Say things like 'I'm confused about...' or 'I think I understand but...'" if persona.get('metacognitive_awareness', 5) >= 8 else "Show moderate metacognitive awareness"}
            - Communication: {f"Ask for diagrams/pictures, describe spatial relationships" if persona.get('communication_style') == 'visual' else f"Want to try things, mention physical examples" if persona.get('communication_style') == 'hands_on' else "Prefer verbal explanations, ask for definitions"}
            """
            
            response_template = """
            You are roleplaying as {student_name} who is {performance_level} in {topic}.

            Your Background: {background}
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
            Keep responses conversational and age-appropriate for {difficulty} level.
            
            Return ONLY the student's response, no other text or formatting.
            """
        
        prompt = language_prefix + response_template.format(
            student_name=student.get('name', 'a student'),
            performance_level=student.get('performanceLevel', 'average'),
            topic=scenario.get('topic', 'this subject'),
            background=student.get('background', ''),
            misconception=misconception,
            practice_question=practice_question,
            persona_guidance=persona_guidance,
            context=context,
            teacher_message=teacher_message,
            difficulty=scenario.get('difficulty', 'intermediate')
        )
        
        print(f"🔄 Calling Gemini API for reasoned student response...")
        if self.model is None:
            raise HTTPException(status_code=503, detail="AI service unavailable")
        response = self.model.generate_content(prompt)
        print(f"✅ Gemini API response received")
        
        return response.text.strip()
    
    def evaluate_session(self, scenario: Dict[str, Any], selected_misconception: int, intervention: str, chat_history: List[Dict[str, str]], selected_strategy: Optional[str] = None, language: str = "english") -> Dict[str, Any]:
        """Evaluate the teacher's diagnosis and intervention"""
        
        self._check_api_available()
        
        correct_index = scenario.get('correctMisconceptionIndex', 0)
        correct_diagnosis = selected_misconception == correct_index
        
        # Count teacher questions
        teacher_questions = len([msg for msg in chat_history if msg['sender'] == 'teacher'])
        
        language_prefix = self._get_language_prefix(language)
        
        # Build evaluation prompt
        chat_text = ""
        for msg in chat_history:
            chat_text += f"{msg['sender'].title()}: {msg['message']}\n"
        
        strategy_context = f"Selected Teaching Strategy: {selected_strategy}" if selected_strategy else "No specific strategy selected"
        
        if language == "traditional_chinese":
            # Handle conditional text outside the template
            correct_diagnosis_text = "是" if correct_diagnosis else "否"
            evaluation_template = """
            評估這次教學會話：
            
            學生的實際誤解：{actual_misconception}
            教師的診斷：{teacher_diagnosis}
            正確診斷：{correct_diagnosis_text}
            
            教師的介入：{intervention}
            {strategy_context}
            
            聊天記錄：
            {chat_text}
            
            以這個JSON格式提供評估：
            {{
                "correctDiagnosis": {correct_diagnosis_json},
                "score": 85,
                "questioningScore": 8,
                "correctMisconception": "學生的實際誤解",
                "feedback": "對教師表現的詳細反饋，包括問題質量、診斷準確性和介入有效性",
                "improvements": ["具體建議1", "具體建議2", "具體建議3"]
            }}
            
            根據以下標準評分0-100分：
            - 診斷準確性（35分）
            - 問題質量（30分）
            - 介入有效性（25分）
            - 教學策略運用（10分）
            
            問題評分（1-10分）基於：
            - 揭示學生思維的探索性問題
            - 從一般到具體的發展
            - 避免誘導性問題
            - 鼓勵學生推理
            
            在評估中考慮所使用的教學策略（如有）。
            
            僅回覆有效的JSON，不要其他文字或markdown格式。
            """
        else:
            correct_diagnosis_text = "YES" if correct_diagnosis else "NO"
            evaluation_template = """
            Evaluate this teaching session:
            
            Student's Actual Misconception: {actual_misconception}
            Teacher's Diagnosis: {teacher_diagnosis}
            Correct Diagnosis: {correct_diagnosis_text}
            
            Teacher's Intervention: {intervention}
            {strategy_context}
            
            Chat History:
            {chat_text}
            
            Provide evaluation in this JSON format:
            {{
                "correctDiagnosis": {correct_diagnosis_json},
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
        
        prompt = language_prefix + evaluation_template.format(
            actual_misconception=scenario['student']['actualMisconception'],
            teacher_diagnosis=scenario['misconceptionOptions'][selected_misconception],
            correct_diagnosis_text=correct_diagnosis_text,
            intervention=intervention,
            strategy_context=strategy_context,
            chat_text=chat_text,
            correct_diagnosis_json=str(correct_diagnosis).lower()
        )
        
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
            request.concepts,
            request.language
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
            request.studentPersona,
            request.language
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
            request.chatHistory,
            request.language
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
            request.selectedStrategy,
            request.language
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