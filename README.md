# TeachWise - AI Teaching Simulator

A simplified AI-powered teaching practice platform that helps educators diagnose and address student misconceptions through realistic classroom simulations.

## Features

🎯 **Simple Setup**: Teachers input grade level, subject, learning outcomes, and key concepts  
🔑 **User-Provided API Keys**: Secure, no server-side API key setup required  
🤖 **AI Student Simulation**: Realistic student responses with authentic misconceptions  
💬 **Interactive Chat**: Natural conversation interface for diagnostic questioning  
🔍 **Misconception Detection**: Multiple choice diagnosis with expert feedback  
📊 **Progress Tracking**: Session analytics stored locally  
💡 **Intervention Strategies**: Guided practice for addressing misconceptions  

## Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key (users provide their own)

### Installation

1. **Clone and setup**:
```bash
git clone <your-repo>
cd teachwise
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the app**:
```bash
python3 start.py
```

4. **Open your browser**: Navigate to `http://localhost:8000`

5. **Get API key**: Visit [Google AI Studio](https://aistudio.google.com/app/apikey) to get your free API key

6. **Enter API key**: Paste your API key in the app to start using AI features

## How It Works

### 1. Setup Your Scenario
- Enter your Google Gemini API key (secure and never stored)
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

## Security & Privacy

- **No server-side API keys**: Users provide their own Google Gemini API keys
- **Session-only storage**: API keys are only used during the session and never stored
- **Local data**: All progress tracking stored locally in your browser
- **No external dependencies**: Self-contained application

## Development

The app is designed to be simple and self-contained:
- All frontend code in `index.html`
- All backend logic in `simple_app.py`
- No complex database or external services
- Gemini AI handles all intelligent features

## License

MIT 