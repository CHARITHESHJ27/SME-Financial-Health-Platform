# SME Financial Health Platform

A comprehensive AI-powered financial health assessment platform for Small and Medium Enterprises (SMEs) that analyzes financial statements, cash flow patterns, and business metrics to provide actionable insights and recommendations.

## Features

### Core Capabilities
- AI-Powered Analysis: Uses OpenAI GPT for intelligent financial insights
- Comprehensive Assessment: Evaluates creditworthiness, identifies risks, suggests optimizations
- Industry Benchmarking: Compares performance against industry standards
- Multi-format Support: Handles CSV, XLSX, and PDF financial data
- Multilingual Support: English and Hindi language support
- Real-time Dashboard: Interactive visualizations and metrics

### Advanced Features
- Financial Forecasting: 12-month predictive analysis
- Cost Optimization: AI-driven cost reduction recommendations
- Risk Assessment: Comprehensive risk analysis and mitigation strategies
- GST Integration: Mock GST compliance checking and tax optimization (Design-ready for Account Aggregator integration)
- Credit Scoring: Advanced credit scoring algorithm (0-100) with industry benchmarking
- Working Capital Analysis: Cash flow and liquidity optimization
- Rate Limiting: API protection with configurable limits
- Input Validation: Comprehensive business rule validation
- Banking API Integration: Architecture ready for Account Aggregator (AA) framework
- Multilingual Support: English primary, Hindi-ready architecture

## Architecture

```
sme-financial-health-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes (controllers)
│   │   ├── services/       # Business logic layer
│   │   ├── core/           # Domain logic
│   │   ├── models/         # Database models & requests
│   │   └── auth.py         # Authentication & security
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── charts/         # Chart components
│   │   └── config/         # Configuration
│   └── package.json
├── data/                   # Sample data and benchmarks
├── scripts/                # Utility scripts
└── ARCHITECTURE.md         # Detailed architecture docs
```

### Service Layer Architecture

- CompanyService: Company operations and business rules
- FinancialAssessmentService: Financial analysis coordination
- FileProcessingService: File upload and data extraction
- ValidationService: Input validation and business constraints
- LLMService: AI-powered insights and recommendations

## Technology Stack

### Backend
- Framework: FastAPI (Python)
- Database: PostgreSQL
- AI/ML: OpenAI GPT-4, pandas, scikit-learn
- Authentication: JWT tokens
- File Processing: pandas, openpyxl

### Frontend
- Framework: React.js
- UI Library: Ant Design
- Charts: Chart.js, Recharts
- State Management: React Hooks
- Internationalization: react-i18next

### Infrastructure
- Containerization: Docker
- Database: PostgreSQL
- Security: Encryption at rest and in transit

## Quick Start

### Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd sme-financial-health-platform

# One-command setup and start
./start.sh setup    # Install all dependencies
./start.sh start    # Start both servers
```

### Manual Setup

#### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+ (optional, SQLite used by default)
- Docker (optional)

#### Backend Setup

1. Set up Python environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and other settings
```

3. Start Backend Server
```bash
cd app
python main.py
# Server runs on http://localhost:8000
```

#### Frontend Setup

1. Install dependencies
```bash
cd frontend
npm install
```

2. Start Development Server
```bash
npm start
# Frontend runs on http://localhost:3000
```

### Docker Setup (Alternative)

```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Testing the Platform

```bash
# Run basic functionality tests
python test_platform.py
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs - Interactive API documentation
- **ReDoc**: http://localhost:8000/redoc - Alternative documentation format

### API Features

- Comprehensive Documentation: All endpoints fully documented with examples
- Interactive Testing: Test API endpoints directly from Swagger UI
- Request/Response Schemas: Detailed parameter and response documentation
- Rate Limiting Info: Clear rate limit specifications for each endpoint
- Error Handling: Documented error responses and status codes
- Authentication: JWT token-based security documentation

### Key Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| POST | `/api/v1/companies/` | Register new company | 10/hour |
| POST | `/api/v1/companies/{id}/assess` | Financial assessment | 100/hour |
| POST | `/api/v1/upload-financial-data/{id}` | Upload financial data | 5/hour |
| GET | `/api/v1/companies/{id}/dashboard` | Dashboard data | 100/hour |
| GET | `/api/v1/companies/{id}/forecast` | Financial forecast | 100/hour |
| GET | `/api/v1/industries/benchmarks/{type}` | Industry benchmarks | 100/hour |
| GET | `/api/v1/companies/{id}/gst-compliance` | GST compliance | 100/hour |

### Response Formats

All API responses follow consistent JSON format:

```json
{
  "status": "success|error",
  "data": {...},
  "message": "Description",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Codes

- 400: Bad Request - Invalid input data
- 404: Not Found - Resource doesn't exist
- 429: Too Many Requests - Rate limit exceeded
- 500: Internal Server Error - Server-side error

## Usage Examples

### 1. Company Registration
```python
import requests

company_data = {
    "name": "Tech Solutions Pvt Ltd",
    "industry": "services",
    "gst_number": "27AABCU9603R1ZX",
    "language_preference": "english"
}

response = requests.post("http://localhost:8000/api/v1/companies/", json=company_data)
company_id = response.json()["id"]
```

### 2. Financial Assessment
```python
financial_data = {
    "revenue": 2500000,
    "total_expenses": 1800000,
    "current_assets": 1200000,
    "current_liabilities": 600000,
    "total_assets": 2900000,
    "total_debt": 800000,
    "revenue_growth_rate": 0.15
}

assessment = requests.post(
    f"http://localhost:8000/api/v1/companies/{company_id}/assess",
    json=financial_data
)
```

### 3. File Upload
```python
files = {'file': open('financial_data.csv', 'rb')}
response = requests.post(
    f"http://localhost:8000/api/v1/upload-financial-data/{company_id}",
    files=files
)
```

## Sample Data

The platform includes sample data for testing:

- Retail Sample: `data/sample_csv/retail_sample.csv`
- GST Data: `data/gst_mock/gst_return.json`
- Industry Benchmarks: `data/benchmarks/industry_avg.csv`

## Security Features

- Data Encryption: All financial data encrypted at rest and in transit
- JWT Authentication: Secure API access with token-based auth
- Input Validation: Comprehensive business rule validation
- Rate Limiting: API protection against abuse (configurable limits)
- SQL Injection Protection: Parameterized queries via SQLAlchemy ORM
- CORS Configuration: Secure cross-origin requests
- File Upload Security: Size and type validation (10MB limit)
- Environment-based Config: Secure configuration management

## Code Quality & Architecture

- Clean Architecture: Separation of concerns with service layer
- Dependency Injection: Testable and maintainable code structure
- Type Hints: Full Python type annotations
- Error Handling: Comprehensive exception handling
- Logging: Structured logging for monitoring
- Testing: Core functionality tests included
- Documentation: Comprehensive docstrings and comments

## Multilingual Support

The platform supports multiple languages:
- English: Default language
- Hindi: Regional language support
- Extensible: Easy to add more languages

## Industry Support

Supported business types:
- Manufacturing
- Retail
- Services
- Agriculture
- Logistics
- E-commerce

Each industry has specific:
- Benchmark ratios
- Risk assessment criteria
- Optimization recommendations
- Growth strategies

## Testing

### Quick Functionality Test
```bash
# Test core platform functionality
python test_platform.py
```

### Backend Tests
```bash
cd backend
pytest tests/  # When test suite is implemented
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Development Scripts

### Start Script Commands
```bash
./start.sh setup     # Install all dependencies
./start.sh start     # Start both servers
./start.sh backend   # Start only backend
./start.sh frontend  # Start only frontend
./start.sh stop      # Stop all servers
./start.sh clean     # Clean up environment
./start.sh help      # Show all commands
```

## Project Structure

```
sme-financial-health-platform/
├── backend/
│   ├── app/
│   │   ├── api/routes.py           # HTTP endpoints
│   │   ├── services/               # Business logic layer
│   │   │   ├── company_service.py      # Company operations
│   │   │   ├── financial_assessment_service.py
│   │   │   ├── file_processing_service.py
│   │   │   ├── validation_service.py   # Input validation
│   │   │   └── llm_service.py          # AI integration
│   │   ├── core/                   # Domain logic
│   │   │   ├── financial_engine.py     # Financial calculations
│   │   │   ├── scoring.py              # Credit scoring
│   │   │   └── benchmarks.py           # Industry benchmarks
│   │   ├── models/
│   │   │   ├── schemas.py              # Database models
│   │   │   └── requests.py             # Request DTOs
│   │   ├── auth.py                 # Authentication
│   │   ├── database.py             # Database config
│   │   └── main.py                 # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── charts/
│   │   └── config/
│   └── package.json
├── data/                       # Sample data
├── scripts/                    # Utility scripts
├── test_platform.py            # Basic functionality tests
├── start.sh                    # Development automation
├── docker-compose.yml          # Container orchestration
├── ARCHITECTURE.md             # Detailed architecture
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines
- Follow the service layer architecture
- Add comprehensive input validation
- Include error handling and logging
- Write tests for new functionality
- Update documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Email: support@sme-financial-health.com
- Architecture docs: `ARCHITECTURE.md`

## Deployment

### Production Deployment

1. Environment Setup
```bash
# Set production environment variables
export ENVIRONMENT=production
export DATABASE_URL=postgresql://user:pass@host:port/db
export OPENAI_API_KEY=your-openai-key
```

2. Build and Deploy
```bash
# Build frontend
cd frontend && npm run build

# Deploy with Docker
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling Considerations

- Database: Use PostgreSQL with read replicas
- Caching: Implement Redis for session management
- Load Balancing: Use Nginx or AWS ALB
- Monitoring: Implement logging and monitoring

## Roadmap

### Phase 1 
- Core financial analysis with 20+ ratios
- Credit scoring algorithm (0-100)
- Industry benchmarking (6 industries)
- File upload support (CSV, XLSX, PDF)
- AI-powered insights and recommendations
- Professional service layer architecture
- Comprehensive input validation
- Rate limiting and security features

### Phase 2 (Next)
- Real banking API integration
- Advanced ML models for predictions
- Mobile app development
- Advanced reporting and analytics
- User authentication system
- Multi-tenant architecture

### Phase 3 (Future)
- Automated bookkeeping integration
- Tax filing automation
- Investor reporting dashboard
- Real-time financial monitoring
- Advanced AI recommendations
- Enterprise features

---

**Built for SME financial empowerment with enterprise-grade architecture**
