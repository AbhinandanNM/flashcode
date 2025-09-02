# CodeCrafts MVP 🚀

A comprehensive gamified programming learning platform that makes coding education engaging and effective through interactive lessons, real-time code execution, and social learning features.

## 🌟 Features

### Core Learning Features
- **Interactive Coding Lessons**: Step-by-step programming tutorials with theory and practice
- **Multiple Question Types**: MCQ, fill-in-the-blank, code challenges, and flashcards
- **Real-time Code Execution**: Execute Python code directly in the browser with instant feedback
- **Code Validation**: Automated testing against predefined test cases
- **Progress Tracking**: Comprehensive learning progress with detailed analytics

### Gamification System
- **XP & Leveling**: Earn experience points and level up through learning activities
- **Achievement System**: Unlock badges and achievements for various milestones
- **Daily Streaks**: Maintain learning streaks with bonus rewards
- **Leaderboards**: Compete with other learners globally and locally

### Social Learning
- **Coding Duels**: Real-time competitive programming challenges between users
- **Community Features**: Share progress and compete with friends
- **Collaborative Learning**: Learn together through social interactions

### Advanced Features
- **Spaced Repetition**: Intelligent flashcard system for optimal retention
- **Adaptive Learning**: Personalized learning paths based on performance
- **Mobile Responsive**: Fully optimized for mobile and tablet devices
- **Offline Support**: Continue learning even without internet connection

## 🏗️ Architecture

### Tech Stack

**Frontend**
- **React 18** with TypeScript for type-safe development
- **TailwindCSS** for responsive and modern UI design
- **Monaco Editor** for advanced code editing experience
- **React Router** for client-side navigation
- **Context API** for state management

**Backend**
- **FastAPI** for high-performance REST API
- **SQLAlchemy** for database ORM and migrations
- **PostgreSQL** for reliable data storage
- **Redis** for caching and session management
- **JWT** for secure authentication

**Infrastructure**
- **Docker & Docker Compose** for containerization
- **Nginx** for reverse proxy and load balancing
- **Let's Encrypt** for SSL certificate management
- **Judge0** for secure code execution

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │   FastAPI       │    │  PostgreSQL     │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│  (Database)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │     Redis       │    │     Judge0      │
         └──────────────►│   (Cache)       │    │ (Code Exec)     │
                        └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Node.js** 18+ and **npm** (for local development)
- **Python** 3.9+ and **pip** (for local development)
- **Git** for version control

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/codecrafts-mvp.git
   cd codecrafts-mvp
   ```

2. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker (Recommended)**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development Setup

**Backend Development**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Development**
```bash
cd frontend
npm install
npm start
```

**Database Setup**
```bash
# Run migrations
cd backend
alembic upgrade head

# Seed sample data
python populate_sample_lesson.py
```

## 🧪 Testing

### Comprehensive Test Suite

We maintain high code quality with extensive testing:

**Run All Tests**
```bash
# Complete test suite
./scripts/run_all_tests.sh

# Backend tests only
./scripts/run_all_tests.sh --backend-only

# Frontend tests only
./scripts/run_all_tests.sh --frontend-only

# Integration tests only
./scripts/run_all_tests.sh --integration-only
```

**Individual Test Suites**
```bash
# Backend unit tests
cd backend && python -m pytest

# Frontend unit tests
cd frontend && npm test

# Integration tests
python3 scripts/integration_test.py

# Feature validation
python3 scripts/validate_features.py
```

**Test Coverage**
- Backend: 85%+ line coverage
- Frontend: 80%+ line coverage
- Integration: Complete user workflow coverage

### Test Types

- **Unit Tests**: Individual component and function testing
- **Integration Tests**: Service layer and API integration
- **End-to-End Tests**: Complete user workflow validation
- **Performance Tests**: Load testing and optimization
- **Security Tests**: Authentication and input validation

## 📦 Deployment

### Production Deployment

**Quick Production Deploy**
```bash
# Copy production environment
cp .env.production .env
# Edit .env with your production values

# Deploy to production
./scripts/deploy.sh
```

**Manual Production Setup**
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Setup SSL certificates
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  --email your-email@domain.com --agree-tos --no-eff-email \
  -d your-domain.com
```

**Environment Configuration**
- See `DEPLOYMENT.md` for detailed production setup
- Configure environment variables in `.env`
- Set up SSL certificates with Let's Encrypt
- Configure monitoring and logging

### Scaling Considerations

- **Horizontal Scaling**: Load balancer + multiple app instances
- **Database Scaling**: Read replicas and connection pooling
- **Caching Strategy**: Redis cluster for distributed caching
- **CDN Integration**: Static asset delivery optimization

## 📚 Documentation

### Developer Documentation
- **[API Documentation](http://localhost:8000/docs)**: Interactive API documentation
- **[Testing Guide](TESTING.md)**: Comprehensive testing documentation
- **[Deployment Guide](DEPLOYMENT.md)**: Production deployment instructions
- **[Validation Checklist](VALIDATION_CHECKLIST.md)**: Complete validation procedures

### User Documentation
- **Getting Started Guide**: New user onboarding
- **Feature Tutorials**: Step-by-step feature guides
- **FAQ**: Common questions and troubleshooting

## 🔧 Development

### Project Structure

```
codecrafts-mvp/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API service layer
│   │   ├── contexts/       # React context providers
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   └── package.json        # Frontend dependencies
├── backend/                 # FastAPI backend application
│   ├── routers/            # API route handlers
│   ├── services/           # Business logic layer
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   ├── auth.py             # Authentication logic
│   └── main.py             # Application entry point
├── scripts/                # Deployment and utility scripts
├── nginx/                  # Nginx configuration
├── docker-compose.yml      # Development environment
├── docker-compose.prod.yml # Production environment
└── README.md              # This file
```

### Development Workflow

1. **Feature Development**
   - Create feature branch from `main`
   - Implement feature with tests
   - Run test suite locally
   - Submit pull request

2. **Code Quality**
   - ESLint and Prettier for frontend
   - Black and isort for backend
   - Type checking with TypeScript/mypy
   - Pre-commit hooks for quality gates

3. **Testing Strategy**
   - Write tests alongside feature development
   - Maintain high test coverage
   - Run integration tests before deployment
   - Validate features with end-to-end tests

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite
5. Submit a pull request

## 🔒 Security

### Security Features
- **JWT Authentication**: Secure token-based authentication
- **Password Security**: Bcrypt hashing with salt
- **Input Validation**: Comprehensive server-side validation
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Input sanitization and CSP headers
- **Code Execution Security**: Sandboxed execution environment

### Security Best Practices
- Regular security updates
- Dependency vulnerability scanning
- SSL/TLS encryption
- Rate limiting and DDoS protection
- Secure headers configuration

## 📊 Performance

### Performance Optimizations
- **Frontend**: Code splitting, lazy loading, caching
- **Backend**: Database indexing, query optimization, caching
- **Infrastructure**: CDN, load balancing, compression

### Performance Metrics
- **Page Load Time**: <3 seconds initial load
- **API Response Time**: <500ms for most endpoints
- **Code Execution**: <30 seconds timeout with resource limits
- **Database Queries**: <100ms for simple queries

## 🌍 Browser Support

### Supported Browsers
- **Chrome** 90+
- **Firefox** 88+
- **Safari** 14+
- **Edge** 90+

### Mobile Support
- **iOS Safari** 14+
- **Chrome Mobile** 90+
- **Samsung Internet** 13+

## 📈 Roadmap

### Phase 1 (Current - MVP)
- ✅ Core learning platform
- ✅ Gamification system
- ✅ Code execution
- ✅ User authentication
- ✅ Basic social features

### Phase 2 (Next Release)
- 🔄 Advanced analytics dashboard
- 🔄 Multi-language support (JavaScript, Java, C++)
- 🔄 Advanced code editor features
- 🔄 Instructor dashboard
- 🔄 Course creation tools

### Phase 3 (Future)
- 📋 AI-powered personalized learning
- 📋 Advanced collaboration features
- 📋 Mobile native applications
- 📋 Enterprise features
- 📋 Advanced analytics and reporting

## 🤝 Support

### Getting Help
- **Documentation**: Check the docs in this repository
- **Issues**: Report bugs and feature requests on GitHub
- **Community**: Join our Discord server for discussions
- **Email**: Contact support@codecrafts.app

### Troubleshooting
- Check the logs: `docker-compose logs -f`
- Verify environment configuration
- Run health checks: `curl http://localhost:8000/health`
- Review the troubleshooting section in `DEPLOYMENT.md`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Judge0** for secure code execution
- **Monaco Editor** for the code editing experience
- **FastAPI** for the excellent Python web framework
- **React** team for the amazing frontend framework
- **TailwindCSS** for the utility-first CSS framework

---

**Built with ❤️ by the CodeCrafts Team**

*Making programming education accessible, engaging, and effective for everyone.*