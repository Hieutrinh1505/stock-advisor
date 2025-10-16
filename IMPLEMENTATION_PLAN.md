# Stock Advisor AI Agent - Implementation Plan

## Project Overview

An AI-powered stock advisor that provides:
- Real-time stock summaries using RAG (Retrieval-Augmented Generation)
- Buy/sell recommendations based on comprehensive analysis
- Portfolio suggestions based on risk profiles (passive/aggressive)
- Price predictions using statistical and ML models

---

## Tech Stack

### Core Technologies
- **Backend**: Python, FastAPI
- **Object Storage**: MinIO (S3-compatible)
- **Vector Database**: Milvus
- **Database**: PostgreSQL
- **Caching**: Redis
- **AI/ML**: LangChain, Ollama, Claude/GPT-4
- **Message Queue**: RabbitMQ (simplified from Kafka for MVP)
- **Frontend**: React (Future Phase)
- **Infrastructure**: Docker Compose → AWS (Production)
- **CI/CD**: GitHub Actions

### Key Libraries
- **Data**: pandas, numpy, polygon-py, pyarrow
- **ML**: scikit-learn, sentence-transformers
- **Finance**: yfinance, ta-lib
- **AI**: langchain, anthropic, openai, pymilvus
- **Storage**: boto3, minio
- **API**: fastapi, pydantic, sqlalchemy
- **Testing**: pytest, pytest-asyncio

---

## Implementation Approach: POC → MVP → Production

### POC (Proof of Concept) - Weeks 1-2 ⭐ CURRENT FOCUS
**Goal**: Validate core RAG architecture with real stock data

**Scope**:
- Data ingestion from Polygon API to MinIO
- Vector database setup with Milvus
- Basic RAG pipeline for stock summaries
- Simple API endpoint to test the flow

**Success Criteria**:
- Successfully store historical stock data in MinIO (Parquet format)
- Generate embeddings and store in Milvus
- Retrieve relevant context and generate stock summaries via RAG
- Validate latency < 3 seconds for queries

### MVP (Minimum Viable Product) - Weeks 3-6
**Goal**: Production-ready API with core features

**Scope**:
- Complete FastAPI backend
- Authentication & user management
- Real-time data pipeline (simplified)
- Stock analysis endpoints
- Basic portfolio tracking
- Caching layer with Redis

**Success Criteria**:
- Full REST API documented
- User registration/login working
- 5 core stock analysis features live
- API response time < 500ms
- Basic error handling and logging

### Production - Weeks 7-12
**Goal**: Scalable, monitored system with advanced features

**Scope**:
- ML prediction models
- Advanced portfolio optimization
- React frontend
- AWS deployment
- CI/CD pipeline
- Monitoring & alerts

---

## Development Phases

### 🎯 Phase 1: POC - MinIO & Milvus RAG (Weeks 1-2) ⭐ CURRENT FOCUS

#### 1.1 Environment Setup
**Tasks:**
- [x] Initialize project structure
- [x] Set up MinIO storage client
- [ ] Create docker-compose.yml for local services
- [ ] Set up logging framework (structlog)
- [ ] Configure environment variables

**Docker Services:**
```yaml
- MinIO (S3-compatible storage)
- Milvus (vector database)
- Etcd (Milvus metadata)
- PostgreSQL (metadata only)
```

#### 1.2 Data Ingestion to MinIO
**Goal**: Store historical stock data in Parquet format on MinIO

**Data Structure:**
```
stocks/
├── history/
│   ├── AAPL_2024.parquet
│   ├── GOOGL_2024.parquet
│   └── MSFT_2024.parquet
├── fundamentals/
│   └── quarterly_2024.parquet
└── news/
    ├── 2024-10/
    └── 2024-11/
```

**Tasks:**
- [x] Implement S3Storage class for MinIO operations
- [ ] Create data fetcher for Polygon API (OHLCV data)
- [ ] Implement Parquet writer with PyArrow
- [ ] Build batch upload functionality
- [ ] Add data validation with Pydantic models
- [ ] Create script to backfill 1 year of data for top 50 stocks
- [ ] Implement retry logic for failed uploads
- [ ] Add progress tracking and logging

**Deliverable**: MinIO bucket with historical stock data in Parquet format

#### 1.3 Milvus Vector Database Setup
**Goal**: Store embeddings for RAG retrieval

**Collection Schema:**
```python
stock_knowledge:
  - id: int64 (primary key)
  - symbol: varchar(10)
  - date: int64 (timestamp)
  - content: varchar (original text)
  - content_type: varchar (price_action, news, fundamental)
  - embedding: float_vector(384)  # sentence-transformers
  - metadata: json
```

**Tasks:**
- [ ] Set up Milvus standalone via Docker
- [ ] Create collection schema for stock data
- [ ] Implement MilvusClient wrapper class
- [ ] Add index for fast similarity search (HNSW)
- [ ] Test connection and basic CRUD operations

#### 1.4 Document Processing & Embedding Pipeline
**Goal**: Transform stock data into searchable embeddings

**Processing Flow:**
```
Parquet Data → Text Chunks → Embeddings → Milvus
```

**Tasks:**
- [ ] Install sentence-transformers (all-MiniLM-L6-v2)
- [ ] Create text chunking strategy for stock data:
  - Daily price action summaries
  - Technical indicator descriptions
  - News article segments
- [ ] Implement batch embedding generation
- [ ] Build ingestion pipeline: MinIO → Process → Milvus
- [ ] Add metadata (symbol, date, data_type) to vectors
- [ ] Create embedding job runner
- [ ] Test retrieval accuracy with sample queries

**Deliverable**: Milvus collection populated with stock embeddings

#### 1.5 Basic RAG Implementation
**Goal**: Query stock data and generate AI summaries

**Components:**
1. Retriever: Search Milvus for relevant context
2. Generator: Use Ollama/Claude for response
3. Chain: LangChain to connect retriever + generator

**Tasks:**
- [ ] Install LangChain and Ollama (llama3.2)
- [ ] Create Milvus retriever wrapper for LangChain
- [ ] Implement prompt templates for stock queries
- [ ] Build RAG chain: query → retrieve → generate
- [ ] Test with sample questions:
  - "Summarize AAPL performance last month"
  - "What's the trend for GOOGL?"
  - "Compare MSFT and AAPL recent movements"
- [ ] Measure response latency
- [ ] Add context window management
- [ ] Implement source citation in responses

**Deliverable**: Working RAG system answering stock queries

#### 1.6 Simple API for Testing
**Goal**: FastAPI endpoint to validate POC

**Endpoints:**
```
POST /api/v1/query
  - Input: { "question": "string", "symbols": ["AAPL"] }
  - Output: { "answer": "string", "sources": [], "latency_ms": 0 }

GET /api/v1/stocks/{symbol}/context
  - Returns: Available context chunks for a symbol
```

**Tasks:**
- [ ] Create minimal FastAPI app
- [ ] Implement query endpoint with RAG
- [ ] Add health check endpoint
- [ ] Create simple request validation
- [ ] Add CORS for local testing
- [ ] Write basic integration test
- [ ] Document API with OpenAPI

**Deliverable**: Testable API demonstrating end-to-end flow

---

### 📦 Phase 2: MVP Backend (Weeks 3-6)

#### 2.1 Database Layer (PostgreSQL)
**Schema Design:**
```sql
-- User management
users (id, email, password_hash, created_at, risk_profile)
user_watchlists (user_id, symbol, added_at)

-- Stock metadata
stocks (symbol, name, sector, industry, last_updated)

-- Query cache
query_cache (query_hash, response, symbols, created_at, ttl)
```

**Tasks:**
- [ ] Set up PostgreSQL with Docker
- [ ] Create Alembic migrations
- [ ] Implement SQLAlchemy models
- [ ] Add connection pooling
- [ ] Create indexes for performance

#### 2.2 Complete FastAPI Backend
**Core Endpoints:**
```
Authentication:
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh

Stock Analysis:
GET  /api/v1/stocks/search?q={query}
GET  /api/v1/stocks/{symbol}/summary
POST /api/v1/stocks/analyze (batch analysis)
GET  /api/v1/stocks/{symbol}/history

RAG Queries:
POST /api/v1/ai/query
POST /api/v1/ai/compare (compare multiple stocks)

User Features:
POST /api/v1/watchlist/add
GET  /api/v1/watchlist
```

**Tasks:**
- [ ] Implement JWT authentication
- [ ] Create all CRUD endpoints
- [ ] Add request validation with Pydantic
- [ ] Implement rate limiting (Redis)
- [ ] Add comprehensive error handling
- [ ] Create API documentation
- [ ] Write integration tests

#### 2.3 Enhanced RAG Features
**Improvements:**
- Multi-document retrieval from Milvus
- Re-ranking for better context
- Query expansion for better retrieval
- Response streaming for better UX

**Tasks:**
- [ ] Implement hybrid search (semantic + keyword)
- [ ] Add re-ranking with cross-encoder
- [ ] Create query expansion logic
- [ ] Implement response streaming
- [ ] Add conversation memory (Redis)
- [ ] Create fallback: Ollama → Claude
- [ ] Add response quality metrics

#### 2.4 Data Pipeline Enhancement
**Goal**: Automated daily data updates

**Components:**
- Scheduled jobs for data fetching
- News aggregation (optional)
- Technical indicators calculation

**Tasks:**
- [ ] Set up APScheduler for cron jobs
- [ ] Create daily stock data updater
- [ ] Implement incremental data loading
- [ ] Add technical indicators (RSI, MACD, MA)
- [ ] Store processed data in MinIO
- [ ] Update Milvus embeddings daily
- [ ] Add job monitoring and alerts

#### 2.5 Caching & Performance
**Strategy:**
- Redis for query caching (5-minute TTL)
- In-memory cache for stock metadata
- Response compression

**Tasks:**
- [ ] Set up Redis with Docker
- [ ] Implement caching decorators
- [ ] Cache expensive operations:
  - RAG responses (query hash based)
  - Stock summaries (5 min TTL)
  - User watchlists (1 min TTL)
- [ ] Add cache invalidation logic
- [ ] Implement response compression
- [ ] Monitor cache hit rates

---

### 🚀 Phase 3: Production & Advanced Features (Weeks 7-12)

#### 3.1 Machine Learning Models (Optional)
**Simple Prediction Models:**
- Prophet for trend forecasting
- Linear regression for baseline
- Basic LSTM for price prediction

**Tasks:**
- [ ] Implement feature engineering
- [ ] Build Prophet model trainer
- [ ] Create simple LSTM model
- [ ] Add model evaluation metrics
- [ ] Store predictions in PostgreSQL
- [ ] Expose prediction API endpoint

#### 3.2 Frontend Development (React)
**Pages:**
- Landing page with search
- Stock detail page with charts
- AI chat interface
- User dashboard

**Tasks:**
- [ ] Initialize React app (Vite + TypeScript)
- [ ] Set up TailwindCSS
- [ ] Create stock search component
- [ ] Build AI chat interface
- [ ] Add authentication UI
- [ ] Implement real-time charts (Chart.js)
- [ ] Create responsive layout

#### 3.3 Infrastructure & Deployment
**Docker Compose Setup:**
```yaml
services:
  - FastAPI backend
  - MinIO
  - Milvus (standalone)
  - PostgreSQL
  - Redis
  - Nginx (reverse proxy)
```

**Tasks:**
- [ ] Create production docker-compose.yml
- [ ] Write Dockerfiles with multi-stage builds
- [ ] Configure Nginx for reverse proxy
- [ ] Add health checks to all services
- [ ] Set up volume persistence
- [ ] Configure environment variables
- [ ] Add SSL certificates (Let's Encrypt)

**AWS Deployment (Optional):**
- [ ] Set up EC2 instance (or ECS)
- [ ] Configure S3 for backups
- [ ] Set up CloudWatch logging
- [ ] Configure auto-scaling
- [ ] Add monitoring with Grafana

#### 3.4 CI/CD Pipeline
**Tasks:**
- [ ] Create GitHub Actions workflow:
  - Linting (Black, isort)
  - Unit tests (pytest)
  - Build Docker images
  - Push to registry
  - Deploy to staging
- [ ] Add pre-commit hooks
- [ ] Set up automated testing
- [ ] Configure deployment approvals

#### 3.5 Monitoring & Observability
**Tasks:**
- [ ] Set up application logging (structlog)
- [ ] Add Prometheus metrics
- [ ] Create Grafana dashboards:
  - API latency
  - RAG query performance
  - Cache hit rates
  - Milvus search latency
- [ ] Set up error tracking (Sentry)
- [ ] Configure alerts for critical issues

---

## System Architecture (Simplified for POC/MVP)

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (Phase 3)                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           React App (Vite + TypeScript)                │ │
│  │  - Stock Search   - AI Chat   - Watchlist              │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────▼──────────────────────────────────┐
│                       API LAYER                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         FastAPI Backend (Python 3.12+)                 │ │
│  │  - REST API    - Auth/JWT    - Rate Limiting           │ │
│  │  - Scheduled Jobs (APScheduler)                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────┬────────────────────┬────────────────┬─────────────┘
          │                    │                │
┌─────────▼────────┐  ┌────────▼─────────┐  ┌──▼──────────┐
│   STORAGE        │  │   VECTOR DB      │  │   CACHE     │
│  ┌────────────┐  │  │  ┌───────────┐   │  │ ┌─────────┐ │
│  │   MinIO    │  │  │  │  Milvus   │   │  │ │  Redis  │ │
│  │ (S3-compat)│  │  │  │           │   │  │ │         │ │
│  │            │  │  │  │ - Vectors │   │  │ │ - Query │ │
│  │ Parquet    │  │  │  │ - HNSW    │   │  │ │   Cache │ │
│  │  Files:    │  │  │  │   Index   │   │  │ │ - User  │ │
│  │ - History  │  │  │  └───────────┘   │  │ │   Data  │ │
│  │ - Technical│  │  │                  │  │ └─────────┘ │
│  └────────────┘  │  └──────────────────┘  └─────────────┘
└──────────────────┘
          │
┌─────────▼────────┐  ┌──────────────────┐  ┌─────────────┐
│   RAG LAYER      │  │   METADATA       │  │   AI/LLM    │
│  ┌────────────┐  │  │  ┌───────────┐   │  │ ┌─────────┐ │
│  │ LangChain  │  │  │  │PostgreSQL │   │  │ │ Ollama  │ │
│  │            │  │  │  │           │   │  │ │ (local) │ │
│  │ - Retriever│  │  │  │ - Users   │   │  │ │    ↓    │ │
│  │ - Chain    │  │  │  │ - Stocks  │   │  │ │ Claude  │ │
│  │ - Prompts  │  │  │  │ - Cache   │   │  │ │(fallback│ │
│  └────────────┘  │  │  └───────────┘   │  │ └─────────┘ │
└──────────────────┘  └──────────────────┘  └─────────────┘

┌──────────────────────────────────────────────────────────────┐
│                  EMBEDDING MODEL                              │
│              sentence-transformers/all-MiniLM-L6-v2          │
│                      (384 dimensions)                         │
└──────────────────────────────────────────────────────────────┘

Data Flow:
Polygon API → Parquet → MinIO → Process → Embeddings → Milvus
                                                  ↓
User Query → RAG (retrieve from Milvus) → LLM → Response
```

---

## Learning Resources (Prioritized for POC/MVP)

### Essential for POC (Weeks 1-2) ⭐
1. **MinIO & S3 Storage**
   - [MinIO Python Client Documentation](https://min.io/docs/minio/linux/developers/python/minio-py.html)
   - [boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3.html)
   - [PyArrow Parquet Guide](https://arrow.apache.org/docs/python/parquet.html)

2. **Milvus Vector Database**
   - [Milvus Documentation](https://milvus.io/docs)
   - [PyMilvus SDK](https://milvus.io/docs/install-pymilvus.md)
   - [Milvus Bootcamp](https://github.com/milvus-io/bootcamp)
   - [Understanding Vector Indexing (HNSW)](https://milvus.io/docs/index.md)

3. **LangChain & RAG**
   - [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
   - [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
   - [LangChain Milvus Integration](https://python.langchain.com/docs/integrations/vectorstores/milvus)
   - [RAG from Scratch - Video Series](https://www.youtube.com/playlist?list=PLfaIDFEXuae2LXbO1_PKyVJiQ23ZztA0x)

4. **Sentence Transformers**
   - [Sentence-Transformers Documentation](https://www.sbert.net/)
   - [Pretrained Models](https://www.sbert.net/docs/pretrained_models.html)
   - [Semantic Search Tutorial](https://www.sbert.net/examples/applications/semantic-search/README.html)

### Important for MVP (Weeks 3-6)
5. **FastAPI**
   - [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
   - [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
   - [JWT Authentication Tutorial](https://testdriven.io/blog/fastapi-jwt-auth/)

6. **PostgreSQL & SQLAlchemy**
   - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
   - [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
   - [FastAPI with Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)

7. **Redis & Caching**
   - [Redis Python Client](https://redis-py.readthedocs.io/)
   - [Caching Strategies](https://redis.io/docs/manual/patterns/)

8. **Polygon API**
   - [Polygon.io Documentation](https://polygon.io/docs/stocks/getting-started)
   - [polygon-py Library](https://github.com/polygon-io/client-python)

### Nice to Have (Production Phase)
9. **Docker & Docker Compose**
   - [Docker Documentation](https://docs.docker.com/get-started/)
   - [Docker Compose for Python](https://docs.docker.com/compose/gettingstarted/)

10. **Testing**
    - [pytest Documentation](https://docs.pytest.org/)
    - [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)

---

## Development Guidelines

### Code Quality
- Follow PEP 8 style guide (Black formatter)
- Type hints for functions
- Concise docstrings
- Environment variables for secrets
- Logging with structlog

### Git Workflow
- Feature branches: `feature/description`
- Commit messages: Clear and descriptive
- Keep commits focused and small

---

## Key Milestones

### POC Phase (Weeks 1-2) ⭐
- **Week 1 End**: MinIO operational with stock data, Milvus setup complete
- **Week 2 End**: Working RAG system with API endpoint, latency < 3 seconds

### MVP Phase (Weeks 3-6)
- **Week 4**: Complete API with authentication
- **Week 6**: Caching layer, scheduled jobs, 5 core features live

### Production Phase (Weeks 7-12)
- **Week 9**: Frontend deployed
- **Week 12**: AWS deployment with monitoring

---

## Success Criteria

### POC Success Metrics (Week 2 Target)
- ✅ MinIO contains 1 year of historical data for 50 stocks
- ✅ Milvus collection has 10,000+ embeddings
- ✅ RAG query latency < 3 seconds
- ✅ API successfully answers 3 test questions
- ✅ Response quality is coherent and relevant

### MVP Success Metrics (Week 6 Target)
- API response time < 500ms (p95)
- 5 core stock analysis endpoints working
- User authentication functional
- Cache hit rate > 60%
- Daily data updates working

---

## Next Steps for Week 1

1. ✅ MinIO storage client created
2. [ ] Set up docker-compose.yml (MinIO, Milvus, PostgreSQL, Etcd)
3. [ ] Create Polygon API data fetcher
4. [ ] Implement Parquet writer
5. [ ] Upload 1 year of data for 10 test stocks (AAPL, GOOGL, MSFT, AMZN, NVDA, TSLA, META, NFLX, AMD, INTC)
6. [ ] Set up Milvus collection
7. [ ] Create embedding pipeline

---

**Last Updated**: 2025-10-16
**Version**: 2.0 - POC/MVP Focused

---

## Quick Start Commands

```bash
# Start all services
docker-compose up -d

# Run data ingestion
python scripts/fetch_stock_data.py

# Generate embeddings
python scripts/generate_embeddings.py

# Test RAG
python scripts/test_rag.py

# Start API
uvicorn app.main:app --reload
```
