# NeuralRAG v1.0
## Retrieval-Augmented Generation App
---
## 🚀 Setup and Usage Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn
- Git

### Quick Start

1. **Clone the Repository**
```bash
git clone <repository-url>
cd rag-implementation/rag-v1.0
```

2. **Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Navigate to server directory and start Flask API
cd server
python run.py
```
Server will be running on `http://127.0.0.1:5000`

3. **Frontend Setup**
```bash
# In a new terminal, navigate to frontend
cd frontend
npm install
npm start
```
React app will open on `http://localhost:3000`

---

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │────│   Flask Server   │────│   AI Pipeline   │
│   (React)       │    │   (REST + WS)    │    │   (RAG Core)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   UI/UX Layer   │    │   API Gateway    │    │ Hybrid Search   │
│ • Terminal UI   │    │ • CORS Support   │    │ • ChromaDB      │
│ • WebSocket     │    │ • Error Handling │    │ • BM25 Search   │
│ • Real-time     │    │ • Session Mgmt   │    │ • Score Fusion  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Directory Structure

#### `/data` - Raw Scientific Documents
- **Purpose**: Storage for raw scientific papers and documents
- **Formats**: PDF, EPUB files
- **Scale**: 100+ documents from arXiv and Project Gutenberg

#### `/preprocessing` - Document Processing Pipeline
- **Purpose**: Normalization, chunking, and text processing
- **Components**:
  - `batch_pdf_processor.py` - PDF extraction and processing
  - `batch_multi_format_processor.py` - Multi-format document handler
  - `parallel_processor.py` - Concurrent processing for scale
  - `chunking/` - Smart chunking strategies with overlap
  - `normalization/` - Text cleaning and standardization
  - `processed_chunks/` - Output storage for processed documents

#### `/hybrid_search` - Retrieval Engine
- **Purpose**: Semantic and lexical search implementation
- **Components**:
  - `hybrid_search.py` - Main search orchestration
  - `chroma/` - Vector database setup and operations
  - `lexical_matching/` - BM25 implementation
  - **Search Strategy**: Weighted combination (50% semantic, 50% lexical)
  - **Features**: Metadata filtering, confidence scoring

#### `/server` - API Backend
- **Purpose**: REST API and WebSocket server
- **Framework**: Flask with Socket.IO
- **Features**:
  - RESTful endpoints for querying
  - WebSockets
  - CORS

#### `/frontend` - User Interface
- **Purpose**: Interactive web interface for RAG system
- **Framework**: React with TypeScript

### Data Flow

```
1. User Query → Frontend Interface
2. Query → WebSocket/REST API → Flask Server
3. Query Processing → AI Pipeline (ai.py)
4. Hybrid Search → ChromaDB + BM25 → Result Fusion
5. LLM Generation → OpenRouter API → Response
6. Response → Frontend → User Display
```

---

## 🧠 Technical Decisions

### Key Design Choices and Trade-offs

Openrouter - free & different models
Llamaindex over langchain - no ui bottleneck

ChromaDB was selected for its ease of setup, built-in similarity search capabilities, and excellent scalability for prototype-to-production transitions without complex configuration


50/50 weighted combination of semantic (ChromaDB) and lexical (BM25) as a solid starting point for both contextual understanding and exact keyword matching, providing comprehensive retrieval coverage

---

## Scaling Strategy

#### Database Migration Strategy
- **100x Scale**: **Elasticsearch** with **dense_vector** fields for enterprise-grade search infrastructure
- **Data Partitioning**: Implement document sharding by domain/topic for parallel processing

#### Infrastructure Optimization
- **Container Orchestration**: Deploy with **Docker + Kubernetes** for auto-scaling based on request volume

- **Query Routing Agent**: Classify queries by complexity and route to specialized processing pipelines




