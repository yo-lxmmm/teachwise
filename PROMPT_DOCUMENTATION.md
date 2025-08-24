# TeachWise Prompt Engineering Documentation

## Overview

TeachWise is an AI-powered teaching simulator that uses sophisticated prompt engineering to create realistic educational scenarios. The system employs Google's Gemini AI to generate authentic student responses, evaluate teacher performance, and provide educational feedback.

## Architecture

The prompt system is organized into four main components:

1. **Question Generation** - Creates practice questions based on learning outcomes
2. **Scenario Generation** - Builds complete teaching scenarios with student personas
3. **Student Response Generation** - Simulates realistic student interactions
4. **Session Evaluation** - Assesses teacher performance and provides feedback

## Core Prompt Categories

### 1. Question Generation Prompts

**Purpose**: Generate practice questions that reveal student misconceptions

**Location**: `simple_app.py` - `generate_question()` method

**Key Features**:
- Grade-level appropriate content
- Open-ended questions that encourage thinking
- Designed to reveal common misconceptions
- Multilingual support (English/Traditional Chinese)

**Example Prompt Structure**:
```
Generate a high-quality practice question for a {grade_level} {subject} class.

Learning Outcomes: {learning_outcomes}
Key Concepts: {concepts}

Create a question that:
1. Is open-ended and encourages student thinking
2. Allows for multiple approaches or explanations
3. Can reveal common misconceptions about the concepts
4. Is age-appropriate for {grade_level} level
5. Connects to the specified learning outcomes

Return response in this JSON format:
{
    "question": "the practice question",
    "rationale": "why this question is effective for revealing misconceptions",
    "expectedMisconceptions": ["misconception 1", "misconception 2", "misconception 3"]
}
```

### 2. Scenario Generation Prompts

**Purpose**: Create realistic teaching scenarios with authentic student personas

**Location**: `simple_app.py` - `generate_scenario()` method

**Key Features**:
- Detailed student persona integration
- Realistic misconception modeling
- Multiple-choice diagnostic options
- Behavioral consistency guidelines

**Student Persona Parameters**:
- **Conceptual Readiness** (1-10): Prior knowledge strength
- **Metacognitive Awareness** (1-10): Self-monitoring ability
- **Persistence** (1-10): Willingness to work through difficulty
- **Communication Style**: verbal/visual/hands_on preferences
- **Confidence Level** (1-10): Willingness to share thinking

**Example Prompt Structure**:
```
Create a realistic teaching scenario for a {grade_level} {subject} class.

Learning Outcomes: {learning_outcomes}
Key Concepts: {concepts}
Practice Question: {question}

Student Characteristics:
- Conceptual Readiness: {persona.conceptual_readiness}/10
- Metacognitive Awareness: {persona.metacognitive_awareness}/10
- Persistence: {persona.persistence}/10
- Communication Style: {persona.communication_style}
- Confidence Level: {persona.confidence_level}/10

Behavioral Guidelines:
- If confidence is low (1-3): Student is hesitant, asks for validation
- If confidence is high (8-10): Student is assertive, states opinions confidently
- If persistence is low (1-3): Student gives up quickly, says "I don't know"
- If persistence is high (8-10): Student keeps trying, asks follow-up questions
- If metacognitive awareness is low (1-3): Student doesn't recognize mistakes
- If metacognitive awareness is high (8-10): Student recognizes confusion

Generate a response in this JSON format:
{
    "student": {
        "name": "realistic first name",
        "background": "brief background reflecting persona",
        "performanceLevel": "struggling/average/advanced",
        "actualMisconception": "specific misconception",
        "initialResponse": "response showing misconception and persona traits"
    },
    "misconceptionOptions": [
        "The correct misconception (student's actual issue)",
        "Plausible but incorrect misconception 1",
        "Plausible but incorrect misconception 2", 
        "Plausible but incorrect misconception 3"
    ],
    "correctMisconceptionIndex": 0
}
```

### 3. Student Response Generation Prompts

**Purpose**: Generate realistic student responses during conversations

**Location**: `simple_app.py` - `generate_student_response()` method

**Key Features**:
- Maintains persona consistency throughout conversation
- Shows logical reasoning based on misconceptions
- Integrates chat history for context
- Behavioral trait manifestation

**Response Guidelines**:
- Responses should be reasoned and logical from student's perspective
- Show thinking process and explain reasoning
- Maintain consistent misconception-based logic
- Display persona characteristics in communication style
- Age-appropriate language and complexity

**Example Prompt Structure**:
```
You are roleplaying as {student_name} who is {performance_level} in {topic}.

Your Background: {background}
Your Specific Misconception: {misconception}
Original Practice Question: {practice_question}

PERSONA CHARACTERISTICS TO MAINTAIN:
- Conceptual Readiness: {persona.conceptual_readiness}/10
- Metacognitive Awareness: {persona.metacognitive_awareness}/10  
- Persistence: {persona.persistence}/10
- Communication Style: {persona.communication_style}
- Confidence Level: {persona.confidence_level}/10

Recent conversation:
{context}

The teacher just asked: "{teacher_message}"

IMPORTANT RESPONSE GUIDELINES:
1. Your responses should be REASONED and logical from your perspective
2. Show your thinking process - explain WHY you think something is correct
3. Your misconception should lead to consistent, logical (but wrong) reasoning
4. Stay true to your persona characteristics throughout
5. If the teacher asks you to explain, show your reasoning step by step

Respond as this student would, showing both your misconception-based reasoning AND your persona traits.
```

### 4. Session Evaluation Prompts

**Purpose**: Assess teacher performance and provide constructive feedback

**Location**: `simple_app.py` - `evaluate_session()` method

**Key Features**:
- Comprehensive scoring rubric (0-100 points)
- Detailed feedback categories
- Specific improvement suggestions
- Teaching strategy assessment

**Scoring Breakdown**:
- **Diagnostic Accuracy** (35 points): Correct identification of misconception
- **Quality of Questioning** (30 points): Effective probing and reasoning encouragement
- **Intervention Effectiveness** (25 points): Appropriate teaching strategies
- **Use of Teaching Strategies** (10 points): Strategic approach application

**Example Prompt Structure**:
```
Evaluate this teaching session:

Student's Actual Misconception: {actual_misconception}
Teacher's Diagnosis: {teacher_diagnosis}
Correct Diagnosis: {correct_diagnosis}

Teacher's Intervention: {intervention}
Teaching Strategy Used: {strategy}

Chat History:
{chat_text}

Provide evaluation in this JSON format:
{
    "correctDiagnosis": true/false,
    "score": 85,
    "questioningScore": 8,
    "correctMisconception": "the student's actual misconception",
    "feedback": "detailed feedback on performance",
    "improvements": ["suggestion 1", "suggestion 2", "suggestion 3"]
}

Score the session 0-100 based on:
- Diagnostic accuracy (35 points)
- Quality of questioning (30 points) 
- Intervention effectiveness (25 points)
- Use of teaching strategies (10 points)
```

## Implementation Details

### Language Support

The system supports both English and Traditional Chinese through language-specific prompt prefixes:

```python
def _get_language_prefix(self, language: str) -> str:
    if language == "traditional_chinese":
        return """
        **[繁體中文模式]** 你扮演一位AI教學助手，你必須以繁體中文回答所有問題。
        
        重要指示：
        1. 回答主體必須使用繁體中文（台灣文），不可使用其他語言
        2. 不要使用拼音或簡體字
        3. 保持專業的教學語調
        4. 確保所有回覆都是繁體中文
        """
    return ""  # Default to English
```

### JSON Response Cleaning

The system includes robust JSON parsing with markdown cleaning:

```python
def _clean_json_response(self, text: str) -> str:
    text = text.strip()
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]
    
    if text.endswith('```'):
        text = text[:-3]
    
    return text.strip()
```

### Error Handling

Comprehensive error handling for API failures:

```python
def _check_api_available(self):
    if not self.model:
        raise HTTPException(
            status_code=503, 
            detail="AI service unavailable. Please check your GOOGLE_API_KEY environment variable."
        )
```

## Usage Workflow

### 1. Setup Phase
```javascript
// Frontend sends setup request
const response = await fetch('/api/generate-question', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        gradeLevel: 'K-5',
        subject: 'Mathematics',
        learningOutcomes: 'Students will understand place value',
        concepts: 'Place value, decimal system, number representation'
    })
});
```

### 2. Scenario Generation
```javascript
// Generate teaching scenario with student persona
const scenarioResponse = await fetch('/api/generate-scenario', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        gradeLevel: 'K-5',
        subject: 'Mathematics',
        learningOutcomes: 'Students will understand place value',
        concepts: 'Place value, decimal system',
        question: 'What is the value of 7 in 375?',
        studentPersona: {
            conceptual_readiness: 6,
            metacognitive_awareness: 4,
            persistence: 7,
            communication_style: 'verbal',
            confidence_level: 5
        }
    })
});
```

### 3. Interactive Chat
```javascript
// Get student response during conversation
const chatResponse = await fetch('/api/student-response', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        scenario: currentScenario,
        teacherMessage: 'Can you explain how you got that answer?',
        chatHistory: conversationHistory
    })
});
```

### 4. Session Evaluation
```javascript
// Evaluate teacher performance
const evaluationResponse = await fetch('/api/evaluate-session', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        scenario: currentScenario,
        selectedMisconception: 0,
        intervention: 'I would use visual aids to help the student...',
        chatHistory: conversationHistory
    })
});
```

## Best Practices

### 1. Prompt Design Principles
- **Specificity**: Use detailed, specific instructions
- **Context**: Provide comprehensive background information
- **Consistency**: Maintain character and behavioral consistency
- **Clarity**: Use clear, unambiguous language
- **Structure**: Organize prompts with clear sections and formatting

### 2. Persona Development
- **Realistic Traits**: Base personas on actual student characteristics
- **Behavioral Consistency**: Maintain traits throughout interactions
- **Logical Reasoning**: Ensure misconceptions lead to coherent (but incorrect) logic
- **Age Appropriateness**: Match language and complexity to grade level

### 3. Response Quality
- **Reasoning Display**: Show student thinking process
- **Misconception Consistency**: Maintain logical errors throughout
- **Natural Language**: Use conversational, age-appropriate communication
- **Contextual Awareness**: Reference previous conversation elements

### 4. Evaluation Criteria
- **Comprehensive Scoring**: Use multiple assessment dimensions
- **Constructive Feedback**: Provide specific, actionable suggestions
- **Professional Tone**: Maintain supportive, educational language
- **Evidence-Based**: Base feedback on conversation analysis

## Technical Configuration

### Environment Setup
```bash
# Required environment variables
export GOOGLE_API_KEY="your_gemini_api_key"

# Install dependencies
pip install -r requirements.txt

# Run application
python simple_app.py
```

### API Key Configuration
```python
# In simple_app.py
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("⚠️  Warning: GOOGLE_API_KEY not found. AI features will be disabled.")
```

## Deployment

### Local Development
```bash
python simple_app.py
# Access at http://localhost:8000
```

### Production Deployment (Vercel)
```bash
# Deploy to Vercel
vercel --prod

# Set environment variables in Vercel dashboard
GOOGLE_API_KEY="your_production_api_key"
```

## Future Enhancements

1. **Additional Persona Traits**: Expand student characteristics
2. **Subject-Specific Prompts**: Tailor prompts for different subjects
3. **Advanced Evaluation Metrics**: More sophisticated assessment criteria
4. **Multi-Turn Conversations**: Extended dialogue management
5. **Cultural Adaptation**: Region-specific educational contexts

## Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Ensure GOOGLE_API_KEY is set in environment
   - Verify API key has proper permissions
   - Check for key expiration

2. **JSON Parsing Errors**:
   - AI responses may include markdown formatting
   - Use `_clean_json_response()` method
   - Implement retry logic for malformed responses

3. **Persona Inconsistency**:
   - Ensure persona traits are clearly defined in prompts
   - Provide behavioral guidelines for each trait level
   - Reference persona characteristics in each response

4. **Response Quality**:
   - Adjust prompt specificity and context
   - Provide more detailed examples
   - Fine-tune behavioral guidelines

This documentation provides a comprehensive overview of how prompts are built and used in the TeachWise project, covering both the technical implementation and educational pedagogy principles behind the system. 