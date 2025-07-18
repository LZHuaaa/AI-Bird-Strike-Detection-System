# 🐦 Avian Intel Bridge - Bird Strike Detection System

## 🌟 Overview
The Avian Intelligence Bridge is a cutting-edge bird detection and communication analysis system designed for airport safety. It combines multiple AI models to identify, analyze, and interpret bird behavior in real time, with a special focus on high-risk species in airport environments.

<img width="898" height="559" alt="image" src="https://github.com/user-attachments/assets/cc59abdd-8062-4515-8208-27efdc110ab7" />

<p align="center"><em>Real-world incident highlighting the dangers of bird strikes</em></p>

## 🚀 Key Features

### 🎤 Audio Analysis & Detection
- Real-time bird call monitoring and recording
- Advanced audio feature extraction using librosa
- Audio segment storage and playback capabilities
- Comprehensive spectral and temporal analysis

### 🤖 AI-Powered Analysis
- Species identification with BirdNET
- Audio classification using Hugging Face transformers
- Emotional state recognition in bird calls
- Behavioral pattern analysis and prediction
- Real-time threat assessment
- Strategic response generation

### 🧠 Communication Analysis
- Call type classification (territorial, feeding, social, warning, mating)
- Flock behavior detection
- Emotional state analysis (calm, alert, agitated, focused, panicked)
- Communication pattern interpretation
- Group coordination detection

### 🎯 Risk Assessment
- Enhanced risk scoring system
- Real-time threat level evaluation
- Behavioral intent prediction
- Environmental context analysis
- Historical pattern analysis

### 📊 Strategic Response System
- AI-powered decision engine
- Automated response recommendations
- Predator sound deployment system
- Dynamic threat level assessment
- Success metrics calculation

### 🌐 Data Management
- Comprehensive bird species database
- Historical detection tracking
- Environmental condition monitoring
- Runway risk assessment
- Weather data integration

## 🤖 AI Models Used

### 1. Audio Classification Models
- **MIT/ast-finetuned-audioset-10-10-0.4593**
  - Purpose: General audio classification
  - Features: Multi-label audio event detection

### 2. Speech Emotion Recognition
- **ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition**
  - Purpose: Emotional content analysis in bird calls
  - Features: Advanced emotion detection

### 3. Species Identification
- **BirdNET Analyzer**
  - Purpose: Bird species identification
  - Features: High-accuracy species detection

### 4. Custom Neural Networks
- **EfficientNet-B0**
  - Purpose: Bird call classification
  - Features: Optimized for audio spectrograms

### 5. Natural Language Generation
- **Google Gemini API**
  - Purpose: Call interpretation and bird information
  - Features: Natural language explanations and descriptions

## 🎯 High-Risk Species Monitoring
Special monitoring for Malaysian airport high-risk species:
- House Crow (Corvus splendens)
- Large-billed Crow (Corvus macrorhynchos)
- White-bellied Sea Eagle (Haliaeetus leucogaster)
- Javan Myna (Acridotheres javanicus)

## 🛠 Installation

```sh
# Step 1: Clone the repository using the project's Git URL.  
git clone https://github.com/LZHuaaa/Avian-Intel-Bridge-New.git

# Step 2: Navigate to the project directory.  
cd Avian-Intel-Bridge-New

# Step 3: Install frontend dependencies.  
npm install

# Step 4: Set up backend using Python 3.11⚠️.  
# ⚠️ Make sure you have Python 3.11 installed: https://www.python.org/downloads/](https://www.python.org/downloads/release/python-3110/

# 4.1 Create a virtual environment  
py -3.11 -m venv .venv

# 4.2 Activate the virtual environment  
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 4.3 Install backend dependencies  
pip install -r requirements.txt

# 4.4 Initialize and start the backend  
cd backend  
python db.py  
python seed_data.py  
python app.py

# Step 5: Start frontend (in a new terminal from project root).  
npm run dev

```

## 📊 System Architecture

### 🎨 Frontend
- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **Styling**:
  - Tailwind CSS for utility-first styling
  - shadcn/ui for component library
  - Lucide React for icons
  - Custom HSL-based design system
- **State Management**:
  - React Query for server state
  - React Context for app state
- **Data Visualization**:
  - Recharts for charts and graphs
  - Leaflet for maps
- **Real-time Communication**: WebSocket for live updates

### 🔧 Backend
- **Framework**: FastAPI
- **Real-time Processing**: 
  - WebSocket server
  - Async/await for non-blocking operations
- **Database**: SQLAlchemy ORM
- **Audio Processing**:
  - librosa for audio analysis
  - PyAudio for real-time audio capture
  - scipy.signal for signal processing

### 🤖 AI Models
- **Audio Classification**:
  - MIT/ast-finetuned-audioset-10-10-0.4593 [https://huggingface.co/MIT/ast-finetuned-audioset-10-10-0.4593]
  - wav2vec2-lg-xlsr for emotion recognition [https://huggingface.co/facebook/wav2vec2-large-xlsr-53]
- **Species Identification**: BirdNET Analyzer [https://github.com/birdnet-team/BirdNET-Analyzer]
- **Neural Networks**: 
  - PyTorch
  - Hugging Face Transformers [https://huggingface.co/MIT/ast-finetuned-audioset-10-10-0.4593]
  - EfficientNet-B0 for custom classification [https://huggingface.co/facebook/wav2vec2-base-960h]
- **Language Models**: Google Gemini API

### 📡 APIs & Services
- **External APIs**:
  - Google Generative AI (Gemini)
  - Weather data services
- **Internal Services**:
  - Strategic Response System
  - Risk Assessment Service
  - Audio Monitoring Service
  - Bird Translation Service
 
<img width="799" height="455" alt="image" src="https://github.com/user-attachments/assets/76c88301-be78-4d1e-9420-9f05100c73b3" />

