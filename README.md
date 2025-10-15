# 📄 Document Q&A Bot - AI-Powered PDF Analysis Tool

A sophisticated Q&A chatbot that provides **context-aware answers exclusively from uploaded PDF documents**. Built with Streamlit, LangChain, and Groq API for fast, accurate document analysis.

## 🎯 Project Overview

This is an intelligent document analysis system that allows users to upload PDF files and ask questions about their content. The bot ensures **100% document-focused responses** with zero general knowledge contamination.

## ✨ Key Features

### 🔒 **Strict Document-Only Responses**
- **Multi-layer validation** prevents general knowledge responses
- **Source verification** ensures every answer comes from uploaded document
- **Pattern detection** blocks generic AI responses
- **Context enforcement** maintains document focus

### 🧠 **Smart Conversation Management**
- **Session-based isolation** - each PDF upload creates a fresh session
- **Conversation memory** - remembers context within current document session
- **Greeting handling** - responds to greetings while guiding to document questions
- **Memory cleanup** - clears history when new documents are uploaded

### 🛡️ **Content Validation System**
- **Basic safety validation** - blocks harmful/inappropriate content
- **Context enforcement** - ensures responses are document-based only
- **Output quality validation** - validates response relevance to document

### 📁 **Multi-PDF Support**
- **Complete isolation** between different PDF uploads
- **Automatic cleanup** of previous document data
- **Fresh embeddings** for each new document
- **No cross-contamination** between files

### 🔍 **Advanced Text Extraction with OCR Fallback**
- **Dual extraction methods** - standard text extraction + PaddleOCR fallback
- **Smart fallback system** - automatically tries OCR if standard extraction fails
- **Image-based PDF support** - handles scanned documents and image-only PDFs
- **Real-time processing feedback** - shows extraction progress in the UI
- **Detailed extraction results** - per-page analysis and confidence scoring
- **Intelligent error handling** - clear explanations when extraction fails

### 🚀 **Performance Features**
- **FAISS vector search** for fast document retrieval
- **Chunked processing** for large documents
- **Efficient embeddings** using HuggingFace models
- **Groq API integration** for fast LLM responses

## 🛠️ Technical Architecture

```
📁 qabot/
├── app.py                    # Main Streamlit application
├── .env                      # Environment configuration
├── requirements.txt          # Python dependencies
├── src/
│   ├── config.py            # Configuration settings
│   ├── pdf_parser.py        # PDF text extraction (PyMuPDF + OCR fallback)
│   ├── vector_store.py      # FAISS vector operations
│   ├── embeddings.py        # HuggingFace embeddings
│   ├── qa_chain.py          # Document-focused QA pipeline
│   ├── guardrail.py         # Content validation system
│   └── memory_store.py      # Conversation memory management
├── data/                    # Auto-generated storage
│   ├── uploads/            # Temporary PDF storage
│   └── faiss_index/        # Vector embeddings
└── venv/                   # Virtual environment
```

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8 or higher (used Python 3.12.7)
- Groq API key (free at [console.groq.com](https://console.groq.com))

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/ChandekarDhruvin/QA-PDF.git

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. OCR Support (Automatic)
The system includes **PaddleOCR** for automatic fallback when PDFs don't have extractable text. 

**Features:**
- ✅ **No external dependencies** - No need to install Tesseract or other OCR software
- ✅ **Automatic model download** - Models download automatically on first use
- ✅ **Real-time feedback** - Shows OCR progress in the Streamlit interface
- ✅ **Confidence filtering** - Only includes high-confidence text recognition
- ✅ **Per-page analysis** - Detailed results for each page processed

**First Run:** The system will download OCR models (~150MB) automatically. Subsequent runs will be faster as models are cached locally.

## ⚙️ Windows Long Path Error Fix (for PaddleOCR Installation)

If you encounter this error during installation:

```
ERROR: Could not install packages due to an OSError: [Errno 2] No such file or directory ...
HINT: This error might have occurred since this system does not have Windows Long Path support enabled.
```

It’s a **Windows system limitation**, not a code issue.
By default, Windows restricts file paths to 260 characters — libraries like **PaddleOCR**, **PaddleX**, and **ModelScope** often exceed this length.
Follow the steps below to permanently fix it 👇

### 🩵 Option 1 — Enable Long Paths via PowerShell (Recommended)

Run this in **PowerShell as Administrator**:

```powershell
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1
```

Then **restart your PC** and reinstall:

```bash
pip install paddleocr paddlex modelscope --upgrade --no-cache-dir
```

### 🩶 Option 2 — Edit Registry (Works on Windows Home too)

1. Press **Win + R**, type `regedit`, and press **Enter**
2. Navigate to:

   ```
   HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem
   ```
3. Find or create a **DWORD (32-bit) Value** named:

   ```
   LongPathsEnabled
   ```
4. Double-click it and set its **Value data** to `1`
5. Click **OK**, close the Registry Editor
6. **Restart your computer**
7. Reinstall:

   ```bash
   pip install paddleocr paddlex modelscope --upgrade --no-cache-dir
   ```

💡 **Tip:** Once enabled, you’ll never face this issue again — PaddleOCR and similar large dependencies will install smoothly.

---
### 4. Configure Environment
Create or update `.env` file with your settings:
```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=meta-llama/llama-4-maverick-17b-128e-instruct
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 5. Run the Application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 How to Use

### Step-by-Step Usage

1. **🌐 Open the App**: Navigate to `http://localhost:8501`
2. **📤 Upload PDF**: Use the sidebar file uploader to select your PDF
3. **⏳ Wait for Processing**: System extracts and indexes document content
   - **Text-based PDFs**: Fast extraction using PyMuPDF
   - **Image-based PDFs**: Automatic OCR fallback with PaddleOCR
   - **Real-time feedback**: Watch the extraction progress in the interface
4. **💬 Start Asking**: Type questions about your document in the chat
5. **✅ Get Answers**: Receive responses based only on document content

### 🔍 Understanding the Extraction Process

The system uses a **two-step extraction process**:

1. **Standard Text Extraction** (Fast)
   - Extracts embedded text from PDF files
   - Works with text-based PDFs created from Word, Google Docs, etc.
   - Completes in seconds

2. **OCR Fallback** (Thorough)
   - Activates when standard extraction finds minimal text
   - Converts PDF pages to images and reads text using AI
   - Shows detailed progress: page conversion, OCR processing, confidence scoring
   - Takes longer but handles scanned documents and image-only PDFs

⚠️ Currently, standard text extraction works for text-based PDFs. OCR fallback for scanned or image-only PDFs is under development and not yet functional.
### Example Interactions

#### ✅ **Successful Document Questions**
```
User: "What is the main topic of this document?"
Bot: "Based on the document, the main topic is [specific content from PDF]..."

User: "Can you summarize the key findings?"
Bot: "According to the document, the key findings include: [content from PDF]..."

User: "What does the document say about [specific topic]?"
Bot: "[Relevant information extracted from the PDF]"
```

#### 👋 **Greeting Handling**
```
User: "Hi"
Bot: "Hello! I'm here to help you with questions about 'your-document.pdf'. What would you like to know?"

User: "Good morning"
Bot: "Good morning! I've processed your document and I'm ready to answer questions about it."
```

#### ❌ **Blocked General Knowledge**
```
User: "What is machine learning?" (general question)
Bot: "I cannot find this information in the uploaded document."

User: "What's the weather today?"
Bot: "I cannot find this information in the uploaded document."
```

## 🔧 Configuration Options

### Environment Variables
- `GROQ_API_KEY`: Your Groq API key for LLM access
- `MODEL_NAME`: Groq model to use (default: llama-4-maverick)
- `MAX_CHUNK_SIZE`: Text chunk size for processing (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `EMBEDDING_MODEL`: HuggingFace model for embeddings

### Customizable Features
- **Chunk sizes** for different document types
- **Validation strictness** levels
- **Response length** limits
- **Memory window** size

## 🧪 Testing the System

### Basic Functionality Test
1. Upload a PDF document
2. Ask a specific question about the content
3. Verify the response comes from the document
4. Upload a different PDF
5. Confirm previous conversation is cleared


## 🔍 Key Components Explained

### 1. **PDF Processing** (`pdf_parser.py`)
- **Dual extraction system**: PyMuPDF + PaddleOCR fallback
- **Smart detection**: Automatically chooses best extraction method
- **Real-time feedback**: Shows processing progress in UI
- **Detailed analysis**: Per-page results and confidence scoring
- **Error handling**: Clear explanations when extraction fails

### 2. **Vector Storage** (`vector_store.py`)
- FAISS for fast similarity search
- Session-based isolation
- Automatic cleanup between documents

### 3. **QA Chain** (`qa_chain.py`)
- Custom conversational chain
- Memory-aware responses
- Document-focused prompting

### 4. **Guardrails** (`guardrail.py`)
- Safety validation
- Context relevance checking
- Output quality control

### 5. **Memory Management** (`memory_store.py`)
- Conversation history tracking
- Session isolation
- Memory cleanup


## 🔐 Security Features

- **Input sanitization** for malicious content
- **API key protection** via environment variables
- **Safe file handling** with temporary storage
- **Content filtering** for inappropriate requests
- **Session isolation** prevents data leakage


## 🎯 Use Cases

Perfect for:
- 📄 **Research Analysis**: Academic papers, studies, reports
- 📚 **Educational Support**: Textbooks, course materials
- 📋 **Business Intelligence**: Contracts, policies, procedures
- 🔬 **Technical Documentation**: API docs, manuals, specifications
- 📖 **Legal Documents**: Contracts, agreements, regulations


## 📝 Dependencies

### Core Libraries
- **streamlit**: Web interface
- **langchain**: LLM orchestration
- **faiss-cpu**: Vector search
- **pymupdf**: PDF processing
- **sentence-transformers**: Text embeddings
- **groq**: Fast LLM API
- **python-dotenv**: Environment management

### OCR Libraries
- **paddleocr**: Robust OCR text extraction (no external dependencies)
- **paddlepaddle**: Deep learning framework for PaddleOCR
- **pdf2image**: PDF to image conversion
- **Pillow**: Image processing


---

**Remember**: This bot is designed as a **document-focused assistant**, not a general AI chatbot. It will politely redirect any attempt to get general knowledge back to the uploaded document content, ensuring reliable and accurate document-based responses every time.
