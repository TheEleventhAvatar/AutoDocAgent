# AutoDoc Agent

AI-powered document automation system that extracts structured data from messy documents and automatically fills enterprise templates.

## 🚀 Features

- **Multi-format Document Processing**: Support for PDFs, images, Word documents, and text files
- **AI Data Extraction**: Uses OpenAI and LangChain to extract structured information
- **Semantic Field Matching**: Intelligent mapping between template fields and extracted data
- **Autonomous Workflow**: Automatically processes multiple documents and fills compatible forms
- **Document Classification**: Automatically identifies document types (invoice, resume, KYC, etc.)
- **Template Support**: Works with PDF forms and Excel templates
- **Modern Web Interface**: Built with Next.js and TailwindCSS

## 🏗️ Architecture

```
AutoDocAgent/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main API server
│   ├── extractor.py        # Document text extraction
│   ├── ai_agent.py         # AI-powered data extraction
│   ├── field_mapper.py     # Semantic field matching
│   ├── form_filler.py      # Template filling logic
│   ├── document_classifier.py # Document type classification
│   └── agent_loop.py       # Autonomous workflow engine
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App pages
│   │   └── components/    # React components
├── sample_documents/       # Sample documents for testing
├── sample_templates/       # Sample form templates
├── uploads/               # Uploaded documents
└── outputs/               # Generated documents
```

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**
- **FastAPI** - Web framework
- **OpenAI API** - AI data extraction
- **LangChain** - AI orchestration
- **sentence-transformers** - Semantic similarity
- **pdfplumber** - PDF text extraction
- **pytesseract** - OCR for images
- **openpyxl** - Excel processing
- **pypdf** - PDF form filling

### Frontend
- **Next.js 14** - React framework
- **TailwindCSS** - Styling
- **TypeScript** - Type safety
- **Lucide React** - Icons
- **React Dropzone** - File uploads
- **Axios** - HTTP client

## 📋 Prerequisites

1. **Python 3.8+**
2. **Node.js 18+**
3. **Tesseract OCR** (for image processing)
   - Windows: Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - Mac: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`
4. **OpenAI API Key** - Set as environment variable

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd AutoDocAgent
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY="your-openai-api-key"
# Or create .env file:
echo "OPENAI_API_KEY=your-openai-api-key" > .env
```

### 3. Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# or with yarn
yarn install
```

### 4. Start the Applications

```bash
# Start backend (in backend directory)
uvicorn main:app --reload --port 8000

# Start frontend (in frontend directory, new terminal)
npm run dev
```

### 5. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📖 Usage

### Basic Workflow

1. **Upload Documents**: Drag and drop multiple documents (PDFs, images, Word, text files)
2. **Automatic Processing**: The system extracts text and classifies document types
3. **AI Extraction**: Structured data is extracted using AI models
4. **Select Templates**: Choose form templates to fill
5. **Generate Documents**: Download completed forms automatically

### Autonomous Processing

Use the "Auto Process" button to:
- Analyze all uploaded documents
- Extract and merge data from multiple sources
- Automatically fill all compatible templates
- Generate missing field reports

### Supported Document Types

- **Resumes**: Extract personal info, experience, education
- **Invoices**: Extract vendor details, amounts, dates
- **KYC Forms**: Extract identity verification data
- **Bank Statements**: Extract account information and transactions
- **ID Cards**: Extract personal identification details

### Template Types

- **KYC Forms**: Know Your Customer applications
- **HR Onboarding**: Employee onboarding documents
- **Tax Forms**: Tax declaration and filing
- **Bank Account**: Account opening applications

## 🔧 API Endpoints

### Document Management
- `POST /upload` - Upload multiple documents
- `GET /uploads` - List uploaded files
- `DELETE /cleanup` - Clean up temporary files

### Data Processing
- `POST /extract` - Extract data from single document
- `POST /process-batch` - Process multiple documents
- `POST /autonomous-process` - Run autonomous workflow

### Template Management
- `GET /templates` - List available templates
- `POST /fill-form` - Fill specific template
- `GET /download/{filename}` - Download generated document

## 🧪 Testing

### Run Test Script

```bash
cd backend
python test_script.py
```

### Manual Testing

1. Upload sample documents from `sample_documents/`
2. Try different template combinations
3. Test autonomous processing with multiple documents
4. Verify field mapping accuracy

## 📁 Sample Files

The project includes sample documents for testing:

- `sample_documents/sample_resume.txt` - Sample resume
- `sample_documents/sample_invoice.txt` - Sample invoice
- `sample_documents/sample_kyc.txt` - Sample KYC form
- `sample_documents/sample_bank_statement.txt` - Sample bank statement

And sample templates:

- `sample_templates/KYC_Form.xlsx` - KYC application
- `sample_templates/HR_Onboarding.xlsx` - HR onboarding
- `sample_templates/Tax_Form.xlsx` - Tax declaration
- `sample_templates/Bank_Account_Form.pdf` - Bank account form

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your-openai-api-key
LOG_LEVEL=INFO
UPLOAD_DIR=../uploads
OUTPUT_DIR=../outputs
TEMPLATE_DIR=../sample_templates
```

### Custom Templates

Add your own templates to the `sample_templates/` directory:
- Excel templates should have headers in the first row
- PDF templates should contain fillable form fields
- Supported formats: `.xlsx`, `.xls`, `.pdf`

## 🚀 Production Deployment

### Backend (Docker)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend (Docker)

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Setup

- Set up proper file storage (S3, etc.)
- Configure database for user management
- Set up Redis for caching
- Configure monitoring and logging
- Set up SSL certificates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

1. **Tesseract not found**: Install Tesseract OCR and ensure it's in your PATH
2. **OpenAI API errors**: Check your API key and billing status
3. **PDF extraction fails**: Some PDFs may be scanned images - ensure OCR is working
4. **Memory issues**: Large documents may require more RAM

### Debug Mode

Enable debug logging by setting:
```env
LOG_LEVEL=DEBUG
```

### Performance Tips

- Process documents in batches for better performance
- Use GPU acceleration for sentence transformers if available
- Cache embeddings for frequently used templates
- Optimize PDF size before processing

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the sample files for expected formats

---

**AutoDoc Agent** - Transforming document automation with AI 🚀
