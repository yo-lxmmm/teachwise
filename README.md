# TeachWise - AI Teaching Simulator

A simplified AI-powered teaching practice platform that helps educators diagnose and address student misconceptions through realistic classroom simulations.

## Features

🎯 **Simple Setup**: Teachers input grade level, subject, learning outcomes, and key concepts  
🤖 **AI Student Simulation**: Realistic student responses with authentic misconceptions  
💬 **Interactive Chat**: Natural conversation interface for diagnostic questioning  
🔍 **Misconception Detection**: Multiple choice diagnosis with expert feedback  
📊 **Progress Tracking**: Session analytics stored locally  
💡 **Intervention Strategies**: Guided practice for addressing misconceptions  

## Quick Start

### Prerequisites
- Python 3.8+
- Gemini API key

### Installation

1. **Clone and setup**:
```bash
git clone <your-repo>
cd teachbetter
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment**:
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

4. **Run the app**:
```bash
python simple_app.py
```

5. **Open your browser**: Navigate to `http://localhost:8000`

## How It Works

### 1. Setup Your Scenario
- Select grade level (K-5, 6-8, 9-12, College)
- Enter subject area
- Define learning outcomes
- List key concepts

### 2. Teaching Simulation
- AI generates a realistic student with specific misconceptions
- Chat with the student to understand their thinking
- Ask diagnostic questions to identify the root issue

### 3. Diagnosis & Intervention
- Select the misconception you've identified
- Provide your intervention strategy
- Get expert feedback on your teaching approach

### 4. Progress Tracking
- View session completion statistics
- Track diagnostic accuracy over time
- Monitor improvement in teaching skills

## Architecture

- **Frontend**: Single-page HTML application with vanilla JavaScript
- **Backend**: FastAPI with Gemini AI integration
- **Storage**: LocalStorage for session data
- **AI**: Google Gemini Pro for all AI interactions

## API Endpoints

- `GET /` - Serve frontend
- `POST /api/generate-scenario` - Create new teaching scenario
- `POST /api/student-response` - Get AI student response
- `POST /api/evaluate-session` - Evaluate teacher performance
- `GET /health` - Health check

## Environment Variables

- `GEMINI_API_KEY` - Required for AI functionality

## Development

The app is designed to be simple and self-contained:
- All frontend code in `index.html`
- All backend logic in `simple_app.py`
- No complex database or external services
- Gemini AI handles all intelligent features

## License

MIT 