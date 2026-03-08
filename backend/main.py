from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Dict, Any
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from extractor import DocumentExtractor
from ai_agent import AIDataExtractor
from field_mapper import SemanticFieldMapper
from form_filler import FormFiller
from document_classifier import DocumentClassifier
from agent_loop import AutonomousAgent

app = FastAPI(title="AutoDoc Agent", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
extractor = DocumentExtractor()
ai_extractor = AIDataExtractor()
field_mapper = SemanticFieldMapper()
form_filler = FormFiller()
doc_classifier = DocumentClassifier()
agent = AutonomousAgent()

# Ensure directories exist
os.makedirs("../uploads", exist_ok=True)
os.makedirs("../outputs", exist_ok=True)

@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload multiple documents for processing"""
    uploaded_files = []
    
    for file in files:
        file_path = Path("../uploads") / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_files.append(str(file_path))
    
    return {"message": f"Uploaded {len(uploaded_files)} files", "files": uploaded_files}

@app.post("/extract")
async def extract_data(file_path: str):
    """Extract text and structured data from a document"""
    try:
        # Extract raw text
        text = extractor.extract_text(file_path)
        
        # Classify document type
        doc_type = doc_classifier.classify(text)
        
        # Extract structured data using AI
        structured_data = ai_extractor.extract_structured_data(text, doc_type)
        
        return {
            "document_type": doc_type,
            "extracted_text": text,
            "structured_data": structured_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-batch")
async def process_batch_documents(file_paths: List[str]):
    """Process multiple documents and merge extracted data"""
    try:
        all_data = {}
        document_types = {}
        
        for file_path in file_paths:
            # Extract text and classify
            text = extractor.extract_text(file_path)
            doc_type = doc_classifier.classify(text)
            document_types[file_path] = doc_type
            
            # Extract structured data
            structured_data = ai_extractor.extract_structured_data(text, doc_type)
            
            # Merge data (later documents override earlier ones)
            all_data.update(structured_data)
        
        return {
            "merged_data": all_data,
            "document_types": document_types,
            "total_documents": len(file_paths)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fill-form")
async def fill_form(template_path: str, data: Dict[str, Any]):
    """Fill a form template with extracted data"""
    try:
        # Map template fields to extracted data
        mapped_data = field_mapper.map_fields(template_path, data)
        
        # Fill the form
        output_path = form_filler.fill_template(template_path, mapped_data)
        
        return {
            "output_file": output_path,
            "mapped_fields": mapped_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/autonomous-process")
async def autonomous_process(file_paths: List[str], template_directory: str = "../sample_templates"):
    """Run the autonomous agent to process documents and fill available templates"""
    try:
        results = agent.run_autonomous_workflow(file_paths, template_directory)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download processed files"""
    file_path = Path("../outputs") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, filename=filename)

@app.get("/templates")
async def list_templates():
    """List available form templates"""
    template_dir = Path("../sample_templates")
    templates = []
    
    for file_path in template_dir.glob("*"):
        if file_path.is_file():
            templates.append({
                "name": file_path.name,
                "path": str(file_path),
                "type": file_path.suffix.lower()
            })
    
    return {"templates": templates}

@app.get("/uploads")
async def list_uploaded_files():
    """List uploaded documents"""
    upload_dir = Path("../uploads")
    files = []
    
    for file_path in upload_dir.glob("*"):
        if file_path.is_file():
            files.append({
                "name": file_path.name,
                "path": str(file_path),
                "size": file_path.stat().st_size
            })
    
    return {"files": files}

@app.delete("/cleanup")
async def cleanup_files():
    """Clean up uploaded and output files"""
    try:
        # Clean uploads
        upload_dir = Path("../uploads")
        for file_path in upload_dir.glob("*"):
            if file_path.is_file():
                file_path.unlink()
        
        # Clean outputs
        output_dir = Path("../outputs")
        for file_path in output_dir.glob("*"):
            if file_path.is_file():
                file_path.unlink()
        
        return {"message": "Cleanup completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
