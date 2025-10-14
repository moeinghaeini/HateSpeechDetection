# 🚀 Open-Source Data Engineering Architecture
## Hate Speech Detection Platform - Complete Open-Source Solution

**Project:** Mappa dell'Intolleranza 2024  
**Architecture:** Open-Source Data Engineering Stack  
**Approach:** End-to-End Open-Source Data Pipeline  

---

## 🏗️ Complete Open-Source Architecture Diagram

```mermaid
graph TB
    subgraph "🌐 Data Sources & Ingestion"
        A1["`**Twitter API v2**
        📱 Real-time social media data
        • Tweepy Python library
        • Rate limiting & error handling
        • Italian language filtering`"]
        A2["`**Facebook Graph API**
        📘 Facebook posts & comments
        • Requests library
        • OAuth authentication
        • Community group analysis`"]
        A3["`**Instagram Basic Display**
        📷 Visual content analysis
        • Instagram API client
        • Caption text extraction
        • Hashtag monitoring`"]
        A4["`**Manual Data Uploads**
        📁 File-based ingestion
        • CSV, Excel, JSON support
        • Pandas data processing
        • Data validation`"]
        A5["`**Web Scraping**
        🕷️ Additional data sources
        • BeautifulSoup4
        • Scrapy framework
        • Selenium automation`"]
    end
    
    subgraph "📥 Data Ingestion Layer"
        B1["`**Apache Kafka**
        🌊 Distributed streaming platform
        • Real-time data streaming
        • Topic-based messaging
        • Fault-tolerant design
        • Horizontal scaling`"]
        B2["`**Redis**
        ⚡ In-memory data store
        • Message queuing
        • Caching layer
        • Session management
        • Rate limiting`"]
        B3["`**Apache Airflow**
        🔄 Workflow orchestration
        • DAG-based scheduling
        • Task dependency management
        • Error handling & retries
        • Monitoring & alerting`"]
    end
    
    subgraph "🔄 Data Processing Layer"
        C1["`**Apache Spark**
        ⚡ Distributed processing engine
        • Batch & streaming processing
        • SQL, Python, Scala support
        • Machine learning integration
        • Fault tolerance`"]
        C2["`**Apache Beam**
        🌊 Unified batch/streaming
        • Portable data pipelines
        • Multiple runner support
        • Complex event processing
        • Data validation`"]
        C3["`**Celery**
        🐍 Distributed task queue
        • Asynchronous processing
        • Worker management
        • Task scheduling
        • Result backend`"]
        C4["`**Dask**
        📊 Parallel computing
        • NumPy/Pandas scaling
        • Distributed arrays
        • Task scheduling
        • Memory optimization`"]
    end
    
    subgraph "🤖 AI/ML & NLP Layer"
        D1["`**Hugging Face Transformers**
        🤗 Pre-trained models
        • BERT, RoBERTa, XLM-R
        • Custom model training
        • Model hub integration
        • Pipeline APIs`"]
        D2["`**spaCy**
        📝 Industrial NLP library
        • Named entity recognition
        • Part-of-speech tagging
        • Dependency parsing
        • Custom models`"]
        D3["`**NLTK**
        📚 Natural language toolkit
        • Text preprocessing
        • Sentiment analysis
        • Language detection
        • Corpus management`"]
        D4["`**scikit-learn**
        🔬 Machine learning library
        • Classification algorithms
        • Feature extraction
        • Model evaluation
        • Pipeline management`"]
        D5["`**OpenAI API Integration**
        🧠 GPT models via API
        • GPT-4o integration
        • Custom prompts
        • Response parsing
        • Cost optimization`"]
        D6["`**Google AI Integration**
        🔮 Gemini models via API
        • Multimodal processing
        • Text generation
        • Model comparison
        • API management`"]
    end
    
    subgraph "💾 Data Storage Layer"
        E1["`**PostgreSQL**
        🗃️ Primary relational database
        • ACID compliance
        • JSON support
        • Full-text search
        • Replication & clustering`"]
        E2["`**MongoDB**
        🍃 Document database
        • Flexible schema
        • Horizontal scaling
        • Aggregation pipelines
        • GridFS for files`"]
        E3["`**Apache Cassandra**
        📊 Distributed NoSQL
        • High availability
        • Linear scalability
        • Time-series data
        • Multi-datacenter`"]
        E4["`**MinIO**
        🗄️ S3-compatible storage
        • Object storage
        • Data lake architecture
        • Versioning & lifecycle
        • Multi-tenant support`"]
        E5["`**Elasticsearch**
        🔍 Search & analytics engine
        • Full-text search
        • Real-time analytics
        • Kibana integration
        • Log aggregation`"]
    end
    
    subgraph "📊 Analytics & BI Layer"
        F1["`**Apache Superset**
        📈 Business intelligence platform
        • Interactive dashboards
        • SQL query interface
        • Data visualization
        • User management`"]
        F2["`**Grafana**
        📊 Monitoring & observability
        • Real-time dashboards
        • Alerting system
        • Data source integration
        • Custom panels`"]
        F3["`**Jupyter Notebooks**
        📓 Interactive development
        • Data exploration
        • Model development
        • Documentation
        • Collaboration`"]
        F4["`**Apache Zeppelin**
        🦓 Notebook platform
        • Multi-language support
        • Spark integration
        • Data visualization
        • Collaborative features`"]
    end
    
    subgraph "🌐 API & Web Layer"
        G1["`**FastAPI**
        ⚡ Modern web framework
        • Automatic API docs
        • Type hints
        • Async support
        • High performance`"]
        G2["`**Flask**
        🌶️ Lightweight web framework
        • RESTful APIs
        • Template engine
        • Extensions ecosystem
        • Microservices ready`"]
        G3["`**Streamlit**
        💻 Data app framework
        • Rapid prototyping
        • Interactive widgets
        • Real-time updates
        • Easy deployment`"]
        G4["`**Dash**
        📊 Analytical web apps
        • Plotly integration
        • Reactive programming
        • Component library
        • Enterprise features`"]
    end
    
    subgraph "🔒 Security & Monitoring"
        H1["`**Apache Ranger**
        🛡️ Security framework
        • Access control
        • Data governance
        • Audit logging
        • Policy management`"]
        H2["`**Prometheus**
        📊 Metrics collection
        • Time-series database
        • Alerting rules
        • Service discovery
        • Exporters ecosystem`"]
        H3["`**Grafana Loki**
        📝 Log aggregation
        • Log parsing
        • Label indexing
        • Query language
        • Grafana integration`"]
        H4["`**Jaeger**
        🔍 Distributed tracing
        • Request tracking
        • Performance analysis
        • Service maps
        • Error debugging`"]
    end
    
    subgraph "🐳 Container & Orchestration"
        I1["`**Docker**
        🐳 Containerization
        • Application packaging
        • Environment consistency
        • Resource isolation
        • Easy deployment`"]
        I2["`**Kubernetes**
        ☸️ Container orchestration
        • Auto-scaling
        • Service discovery
        • Load balancing
        • Rolling updates`"]
        I3["`**Docker Compose**
        🔧 Multi-container apps
        • Development environment
        • Service dependencies
        • Network configuration
        • Volume management`"]
    end
    
    %% Data Flow Connections
    A1 --> B1
    A2 --> B1
    A3 --> B1
    A4 --> B2
    A5 --> B1
    
    B1 --> C1
    B2 --> C3
    B3 --> C1
    
    C1 --> C2
    C2 --> C4
    C3 --> C1
    
    C1 --> D1
    C2 --> D2
    C3 --> D3
    C4 --> D4
    C1 --> D5
    C2 --> D6
    
    D1 --> E1
    D2 --> E2
    D3 --> E3
    D4 --> E4
    D5 --> E1
    D6 --> E2
    
    E1 --> F1
    E2 --> F2
    E3 --> F3
    E4 --> F4
    E5 --> F1
    
    F1 --> G1
    F2 --> G2
    F3 --> G3
    F4 --> G4
    
    G1 --> H1
    G2 --> H2
    G3 --> H3
    G4 --> H4
    
    %% Container connections
    I1 -.-> C1
    I1 -.-> D1
    I1 -.-> E1
    I2 -.-> C1
    I2 -.-> D1
    I2 -.-> E1
    I3 -.-> G1
    I3 -.-> G2
```

---

## 🔄 Data Pipeline Flow Diagram

```mermaid
flowchart LR
    subgraph "📥 Data Ingestion Pipeline"
        A1["`**Social Media APIs**
        📱 Twitter, Facebook, Instagram
        • Real-time data collection
        • Rate limiting & error handling`"] --> B1["`**Apache Kafka**
        🌊 Message streaming
        • Topic partitioning
        • Fault tolerance`"]
        A2["`**File Uploads**
        📁 CSV, Excel, JSON
        • Batch processing
        • Data validation`"] --> B2["`**Redis Queue**
        ⚡ Task queuing
        • Priority handling
        • Retry mechanisms`"]
        A3["`**Web Scraping**
        🕷️ Additional sources
        • Scheduled collection
        • Content extraction`"] --> B3["`**Apache Airflow**
        🔄 Workflow orchestration
        • DAG scheduling
        • Dependency management`"]
    end
    
    subgraph "🔄 Data Processing Pipeline"
        B1 --> C1["`**Apache Spark**
        ⚡ Stream processing
        • Real-time classification
        • Data transformation`"]
        B2 --> C2["`**Celery Workers**
        🐍 Async processing
        • Task distribution
        • Result collection`"]
        B3 --> C3["`**Apache Beam**
        🌊 Batch processing
        • ETL operations
        • Data validation`"]
        C1 --> C4["`**Data Quality Checks**
        ✅ Validation pipeline
        • Completeness checks
        • Accuracy validation
        • Consistency monitoring`"]
        C2 --> C4
        C3 --> C4
    end
    
    subgraph "🤖 AI/ML Processing Pipeline"
        C4 --> D1["`**Text Preprocessing**
        📝 NLP pipeline
        • Tokenization
        • Cleaning & normalization
        • Feature extraction`"]
        D1 --> D2["`**Model Ensemble**
        🧠 Multi-model voting
        • BERT classification
        • GPT-4o analysis
        • Gemini processing
        • Confidence scoring`"]
        D2 --> D3["`**Result Aggregation**
        📊 Ensemble voting
        • Weighted scoring
        • Consensus building
        • Quality assessment`"]
    end
    
    subgraph "💾 Data Storage Pipeline"
        D3 --> E1["`**PostgreSQL**
        🗃️ Structured data
        • Classification results
        • User management
        • Audit logs`"]
        D3 --> E2["`**MongoDB**
        🍃 Document storage
        • Raw posts
        • Metadata
        • Analytics data`"]
        D3 --> E3["`**MinIO**
        🗄️ Object storage
        • File backups
        • Model artifacts
        • Data lake`"]
        D3 --> E4["`**Elasticsearch**
        🔍 Search index
        • Full-text search
        • Analytics queries
        • Real-time dashboards`"]
    end
    
    subgraph "📊 Analytics Pipeline"
        E1 --> F1["`**Apache Superset**
        📈 BI dashboards
        • Interactive visualizations
        • Custom reports
        • User dashboards`"]
        E2 --> F2["`**Grafana**
        📊 Monitoring dashboards
        • Real-time metrics
        • Alerting system
        • Performance monitoring`"]
        E3 --> F3["`**Jupyter Notebooks**
        📓 Data exploration
        • Ad-hoc analysis
        • Model development
        • Research notebooks`"]
        E4 --> F4["`**Custom Analytics**
        🔬 Advanced analytics
        • Trend analysis
        • Pattern detection
        • Predictive modeling`"]
    end
    
    subgraph "🌐 Presentation Pipeline"
        F1 --> G1["`**FastAPI Backend**
        ⚡ RESTful APIs
        • Data endpoints
        • Authentication
        • Rate limiting`"]
        F2 --> G1
        F3 --> G2["`**Streamlit Frontend**
        💻 Interactive app
        • Real-time dashboards
        • User interface
        • Data visualization`"]
        F4 --> G2
        G1 --> G2
    end
```

---

## 🛠️ Technology Stack Details

### **Data Ingestion & Streaming**
- **Apache Kafka**: Distributed streaming platform for real-time data
- **Redis**: In-memory data store for caching and queuing
- **Apache Airflow**: Workflow orchestration and scheduling
- **Tweepy**: Python library for Twitter API integration
- **Requests**: HTTP library for API interactions

### **Data Processing & Analytics**
- **Apache Spark**: Distributed processing engine for big data
- **Apache Beam**: Unified batch and streaming data processing
- **Celery**: Distributed task queue for asynchronous processing
- **Dask**: Parallel computing library for scaling Python
- **Pandas**: Data manipulation and analysis library

### **AI/ML & NLP**
- **Hugging Face Transformers**: Pre-trained transformer models
- **spaCy**: Industrial-strength natural language processing
- **NLTK**: Natural language toolkit for text processing
- **scikit-learn**: Machine learning library for Python
- **OpenAI API**: GPT models integration
- **Google AI**: Gemini models integration

### **Data Storage**
- **PostgreSQL**: Primary relational database
- **MongoDB**: Document-oriented database
- **Apache Cassandra**: Distributed NoSQL database
- **MinIO**: S3-compatible object storage
- **Elasticsearch**: Search and analytics engine

### **Analytics & Visualization**
- **Apache Superset**: Business intelligence platform
- **Grafana**: Monitoring and observability platform
- **Jupyter Notebooks**: Interactive development environment
- **Apache Zeppelin**: Multi-purpose notebook platform
- **Plotly**: Interactive visualization library

### **Web & API Development**
- **FastAPI**: Modern web framework for APIs
- **Flask**: Lightweight web framework
- **Streamlit**: Data app framework
- **Dash**: Analytical web applications
- **Gunicorn**: Python WSGI HTTP server

### **Security & Monitoring**
- **Apache Ranger**: Security framework for data governance
- **Prometheus**: Metrics collection and monitoring
- **Grafana Loki**: Log aggregation system
- **Jaeger**: Distributed tracing system
- **Sentry**: Error tracking and monitoring

### **Container & Orchestration**
- **Docker**: Containerization platform
- **Kubernetes**: Container orchestration
- **Docker Compose**: Multi-container application management
- **Helm**: Kubernetes package manager

---

