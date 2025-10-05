# AI-Enhanced Quiz Generator

A comprehensive quiz generation system that leverages AI APIs, advanced data structures, and dynamic programming to create personalized learning experiences.

## 🎯 Overview

This project demonstrates the integration of multiple computer science concepts:
- **Tree Data Structures** for hierarchical question organization
- **Queue (Deque) Management** for optimized question sequencing  
- **Dynamic Programming** for adaptive difficulty optimization
- **AI Integration** with OpenAI/Gemini APIs for content generation
- **Full-Stack Architecture** with FastAPI backend and React frontend

## 🏗️ Architecture

### Backend Components
```
backend/
├── main.py                 # FastAPI application entry point
├── routers/               # API route handlers
│   ├── auth.py           # Authentication endpoints
│   ├── quiz.py           # Quiz management endpoints
│   └── analytics.py      # Performance analytics
├── services/             # Business logic services
│   └── ai_service.py     # AI question generation
├── models/               # Data models and schemas
│   ├── user.py          # User data models
│   ├── question.py      # Question data models
│   └── quiz.py          # Quiz session models
├── utils/                # Core algorithms
│   ├── tree_structure.py # Hierarchical question organization
│   ├── queue_manager.py  # Question sequencing with deque
│   └── dynamic_programming.py # Adaptive difficulty optimization
├── database/             # Database connectivity
│   └── connection.py     # MongoDB connection management
└── tests/                # Unit tests
    ├── test_tree_structure.py
    ├── test_queue_manager.py
    ├── test_dynamic_programming.py
    └── test_ai_service.py
```

### Frontend Components
```
src/
├── components/           # React components
│   ├── Auth/            # Authentication components
│   ├── Dashboard/       # Main dashboard
│   ├── Quiz/            # Quiz creation and session
│   ├── Analytics/       # Performance visualization
│   └── Layout/          # Application layout
├── contexts/            # React context providers
│   ├── AuthContext.tsx  # User authentication state
│   └── QuizContext.tsx  # Quiz session management
├── services/            # API integration
│   └── api.ts           # API client and endpoints
└── hooks/               # Custom React hooks
```

## 🚀 Key Features

### 1. AI-Powered Question Generation
- **OpenAI Integration**: Automatically generates questions from any text content
- **Multiple Question Types**: Supports multiple choice, true/false, and short answer
- **Difficulty Assessment**: AI evaluates and assigns appropriate difficulty levels
- **Mock Mode**: Generates sample questions when no API key is provided

### 2. Tree-Based Question Organization
```python
# Hierarchical structure: Subject → Topic → Difficulty → Questions
Structure: Root
├── Mathematics
│   ├── Algebra
│   │   ├── Beginner: [Q1, Q2, ...]
│   │   ├── Intermediate: [Q3, Q4, ...]
│   │   └── Advanced: [Q5, Q6, ...]
│   └── Calculus
│       ├── Intermediate: [Q7, Q8, ...]
│       └── Advanced: [Q9, Q10, ...]
└── Physics
    └── Mechanics: [...]
```

### 3. Queue-Based Question Sequencing
- **Deque Implementation**: Efficient O(1) insertion/removal at both ends
- **Adaptive Reordering**: Dynamic difficulty adjustment based on performance
- **Priority Insertion**: High-priority questions jump to front of queue
- **Performance Tracking**: Records answer accuracy and timing

### 4. Dynamic Programming Optimization
- **Difficulty Transition Matrix**: Optimizes learning progression
- **Performance Analysis**: Tracks user performance patterns
- **Memoization**: Caches optimal difficulty transitions
- **Trend Analysis**: Considers performance history for predictions

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB 4.4+
- Git

### Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd ai-quiz-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start MongoDB (if running locally)
mongod --dbpath ./data/db

# Run the FastAPI server
cd backend
python main.py
```

### Frontend Setup
```bash
# Install Node.js dependencies
npm install

# Start the React development server
npm run dev
```

### Database Setup
```bash
# The application will automatically create necessary collections
# MongoDB connection is configured in backend/database/connection.py
```

## 🎮 Usage

### 1. Creating a Quiz
1. **Login/Register**: Create an account or use demo credentials
2. **Upload Content**: Paste study material or upload text files
3. **Configure Quiz**: Set question count, difficulty preferences
4. **AI Generation**: Provide OpenAI API key for AI questions (optional)
5. **Start Quiz**: Begin the adaptive quiz session

### 2. Taking a Quiz
1. **Question Display**: View AI-generated questions with multiple choice options
2. **Answer Submission**: Select answers and receive immediate feedback
3. **Adaptive Difficulty**: Questions adjust based on your performance
4. **Progress Tracking**: Monitor completion and accuracy in real-time

### 3. Analytics Dashboard
- **Performance Metrics**: View accuracy, timing, and progress trends
- **Difficulty Analysis**: See performance breakdown by difficulty level
- **Learning Insights**: Get personalized recommendations for improvement

## 🧪 Testing

### Running Unit Tests
```bash
# Run all tests
cd backend
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_tree_structure.py -v
python -m pytest tests/test_queue_manager.py -v
python -m pytest tests/test_dynamic_programming.py -v
python -m pytest tests/test_ai_service.py -v

# Run with coverage
python -m pytest tests/ --cov=backend --cov-report=html
```

### Test Coverage
- **Tree Structure**: 95%+ coverage of hierarchical organization
- **Queue Manager**: 90%+ coverage of deque operations and adaptive logic
- **Dynamic Programming**: 85%+ coverage of optimization algorithms
- **AI Service**: 80%+ coverage including mock mode functionality

## 🔌 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/verify-token` - Verify JWT token

### Quiz Management Endpoints
- `POST /api/quiz/generate-quiz` - Create new AI-generated quiz
- `GET /api/quiz/quiz/{id}/next-question` - Get next question in sequence
- `POST /api/quiz/quiz/{id}/submit-answer` - Submit answer and get feedback
- `GET /api/quiz/quiz/{id}/stats` - Get quiz performance statistics
- `DELETE /api/quiz/quiz/{id}/session` - End quiz session

### Question Search Endpoints
- `GET /api/quiz/questions/tree-structure` - Get hierarchical question organization
- `GET /api/quiz/questions/search` - Search questions by criteria

## 🧠 Algorithm Details

### Tree Structure Implementation
```python
class QuestionNode:
    def __init__(self, value, node_type):
        self.value = value
        self.node_type = node_type  # 'subject', 'topic', 'difficulty', 'question'
        self.children = {}
        self.questions = []

class QuestionTree:
    def add_question(self, question):
        # Navigate: Subject → Topic → Difficulty
        # Create intermediate nodes if needed
        # Add question to appropriate leaf node
```

### Queue Management with Deque
```python
from collections import deque

class QuestionQueue:
    def __init__(self, adaptive_mode=True):
        self.queue = deque()
        self.adaptive_mode = adaptive_mode
        
    def add_questions(self, questions, randomize=True):
        # O(1) append operations
        # Optional randomization for variety
        
    def get_next_question(self):
        # O(1) popleft operation
        # Apply adaptive reordering if enabled
```

### Dynamic Programming Optimization
```python
class DifficultyOptimizer:
    def get_optimal_next_difficulty(self, current_difficulty, performance_score):
        # Use memoization for repeated calculations
        # Consider transition costs between difficulty levels
        # Optimize for learning efficiency
        
    def optimize_quiz_difficulty_sequence(self, question_count, starting_difficulty):
        # Generate optimal progression for entire quiz
        # Balance challenge with achievability
```

## 🤝 Contributing

### Development Workflow
1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Write tests** for new functionality
4. **Implement feature** with proper documentation
5. **Run test suite**: `pytest tests/ -v`
6. **Submit pull request** with detailed description

### Code Style
- **Python**: Follow PEP 8 guidelines
- **TypeScript/React**: Use ESLint and Prettier
- **Documentation**: Include docstrings and comments
- **Testing**: Maintain >80% test coverage

## 📈 Performance Considerations

### Backend Optimization
- **Database Indexing**: Optimized queries for question retrieval
- **Connection Pooling**: Efficient MongoDB connection management
- **Async Operations**: Non-blocking I/O with FastAPI
- **Caching**: Memoization in DP algorithms

### Frontend Optimization
- **Code Splitting**: Lazy loading of components
- **State Management**: Efficient React context usage
- **Bundle Optimization**: Tree shaking and minification
- **Performance Monitoring**: Real-time metrics tracking

## 🔒 Security

### Authentication
- **JWT Tokens**: Secure authentication with proper expiration
- **Password Hashing**: bcrypt for secure password storage
- **CORS Configuration**: Properly configured cross-origin requests

### Data Protection
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Prevention**: Parameterized queries
- **API Rate Limiting**: Protection against abuse

## 🌟 Future Enhancements

### Planned Features
- **Multi-language Support**: I18n implementation
- **Real-time Collaboration**: Multiple users taking quizzes together
- **Advanced Analytics**: Machine learning insights
- **Mobile Application**: React Native implementation
- **Voice Integration**: Speech-to-text for questions

### Scalability Improvements
- **Microservices Architecture**: Service decomposition
- **Container Deployment**: Docker and Kubernetes
- **CDN Integration**: Static asset optimization
- **Load Balancing**: Horizontal scaling support

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Development Team** - Initial work and implementation
- **Contributors** - See contributors list for additional contributors

## 🙏 Acknowledgments

- **OpenAI** for providing the AI API for question generation
- **FastAPI** for the excellent async web framework
- **React** team for the frontend framework
- **MongoDB** for the flexible document database
- **Open Source Community** for inspiration and tools

---

For detailed API documentation, visit `/docs` when the server is running.
For questions and support, please open an issue in the repository.