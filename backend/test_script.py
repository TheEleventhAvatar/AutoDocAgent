#!/usr/bin/env python3
"""
Test script for AutoDoc Agent backend
Tests all major components and API endpoints
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extractor import DocumentExtractor
from ai_agent import AIDataExtractor
from field_mapper import SemanticFieldMapper
from form_filler import FormFiller
from document_classifier import DocumentClassifier
from agent_loop import AutonomousAgent

class AutoDocTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_document_extractor(self):
        """Test document extraction functionality"""
        print("\n🔍 Testing Document Extractor...")
        
        try:
            extractor = DocumentExtractor()
            
            # Test text file extraction
            sample_file = "../sample_documents/sample_resume.txt"
            if os.path.exists(sample_file):
                text = extractor.extract_text(sample_file)
                assert len(text) > 0, "Text extraction failed"
                self.log_test("Text file extraction", True, f"Extracted {len(text)} characters")
            else:
                self.log_test("Text file extraction", False, "Sample file not found")
            
            # Test document info
            info = extractor.get_document_info(sample_file)
            assert info["is_supported"], "Document type not supported"
            self.log_test("Document info extraction", True)
            
        except Exception as e:
            self.log_test("Document extractor", False, str(e))
    
    def test_document_classifier(self):
        """Test document classification"""
        print("\n🏷️ Testing Document Classifier...")
        
        try:
            classifier = DocumentClassifier()
            
            # Test with sample resume
            sample_text = """
            JOHN DOE
            Software Engineer with 5+ years experience
            Skills: Python, JavaScript, React
            Education: Bachelor of Science in Computer Science
            """
            
            doc_type = classifier.classify(sample_text)
            assert doc_type in ["resume", "general"], f"Unexpected classification: {doc_type}"
            self.log_test("Document classification", True, f"Classified as: {doc_type}")
            
            # Test confidence scoring
            confidence = classifier.get_classification_confidence(sample_text, "resume")
            assert 0 <= confidence <= 1, "Confidence score out of range"
            self.log_test("Confidence scoring", True)
            
        except Exception as e:
            self.log_test("Document classifier", False, str(e))
    
    def test_ai_data_extractor(self):
        """Test AI data extraction"""
        print("\n🤖 Testing AI Data Extractor...")
        
        try:
            # Skip if no OpenAI API key
            if not os.getenv("OPENAI_API_KEY"):
                self.log_test("AI data extraction", False, "No OpenAI API key")
                return
            
            extractor = AIDataExtractor()
            
            sample_text = """
            Name: John Doe
            Date of Birth: March 15, 1995
            Address: 123 Main Street, New York, NY 10001
            Phone: (555) 123-4567
            Email: john.doe@email.com
            PAN: ABCDE1234F
            """
            
            data = extractor.extract_structured_data(sample_text, "kyc")
            assert isinstance(data, dict), "Extraction should return dictionary"
            self.log_test("AI data extraction", True, f"Extracted {len(data)} fields")
            
        except Exception as e:
            self.log_test("AI data extractor", False, str(e))
    
    def test_field_mapper(self):
        """Test semantic field mapping"""
        print("\n🔗 Testing Field Mapper...")
        
        try:
            mapper = SemanticFieldMapper()
            
            # Test synonym detection
            synonyms = mapper._are_synonyms("name", "full name")
            assert synonyms, "Synonym detection failed"
            self.log_test("Synonym detection", True)
            
            # Test field suggestions
            suggestions = mapper.suggest_field_corrections("Applicant Name", ["name", "email", "phone"])
            assert len(suggestions) > 0, "No suggestions generated"
            self.log_test("Field suggestions", True, f"Generated {len(suggestions)} suggestions")
            
        except Exception as e:
            self.log_test("Field mapper", False, str(e))
    
    def test_form_filler(self):
        """Test form filling functionality"""
        print("\n📝 Testing Form Filler...")
        
        try:
            filler = FormFiller()
            
            # Test template info
            template_dir = "../sample_templates"
            if os.path.exists(template_dir):
                templates = os.listdir(template_dir)
                if templates:
                    template_path = os.path.join(template_dir, templates[0])
                    info = filler.get_template_info(template_path)
                    assert "name" in info, "Template info missing name"
                    self.log_test("Template info extraction", True)
                else:
                    self.log_test("Template info extraction", False, "No templates found")
            else:
                self.log_test("Form filler", False, "Template directory not found")
                
        except Exception as e:
            self.log_test("Form filler", False, str(e))
    
    def test_autonomous_agent(self):
        """Test autonomous agent workflow"""
        print("\n🔄 Testing Autonomous Agent...")
        
        try:
            agent = AutonomousAgent()
            
            # Test template classification
            template_type = agent._classify_template_type("kyc_form.xlsx")
            assert template_type == "kyc_form", f"Wrong template type: {template_type}"
            self.log_test("Template classification", True)
            
            # Test missing fields report generation
            mock_data = {
                "merged_fields": {"name": "John Doe", "email": "john@example.com"},
                "document_count": 2,
                "document_info": []
            }
            
            mock_templates = [
                {
                    "template": {"name": "test.pdf", "file_path": "test.pdf"},
                    "type": "kyc_form",
                    "missing_required": ["pan", "address"],
                    "missing_optional": ["phone"],
                    "can_fill": False
                }
            ]
            
            report = agent._generate_missing_fields_report(mock_templates, mock_data)
            assert "summary" in report, "Missing fields report incomplete"
            self.log_test("Missing fields report", True)
            
        except Exception as e:
            self.log_test("Autonomous agent", False, str(e))
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n🌐 Testing API Endpoints...")
        
        try:
            # Test if server is running
            response = requests.get(f"{self.base_url}/", timeout=5)
            self.log_test("API server", response.status_code == 200)
            
            # Test templates endpoint
            response = requests.get(f"{self.base_url}/templates", timeout=5)
            self.log_test("Templates endpoint", response.status_code == 200)
            
            # Test uploads endpoint
            response = requests.get(f"{self.base_url}/uploads", timeout=5)
            self.log_test("Uploads endpoint", response.status_code == 200)
            
        except requests.exceptions.RequestException as e:
            self.log_test("API endpoints", False, f"Connection error: {e}")
    
    def test_sample_files(self):
        """Test sample files exist and are readable"""
        print("\n📁 Testing Sample Files...")
        
        sample_files = [
            "../sample_documents/sample_resume.txt",
            "../sample_documents/sample_invoice.txt",
            "../sample_documents/sample_kyc.txt",
            "../sample_documents/sample_bank_statement.txt"
        ]
        
        for file_path in sample_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        assert len(content) > 0, "Empty file"
                        self.log_test(f"Sample file: {os.path.basename(file_path)}", True)
                except Exception as e:
                    self.log_test(f"Sample file: {os.path.basename(file_path)}", False, str(e))
            else:
                self.log_test(f"Sample file: {os.path.basename(file_path)}", False, "File not found")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting AutoDoc Agent Tests...")
        print("=" * 50)
        
        # Run component tests
        self.test_document_extractor()
        self.test_document_classifier()
        self.test_ai_data_extractor()
        self.test_field_mapper()
        self.test_form_filler()
        self.test_autonomous_agent()
        
        # Run integration tests
        self.test_sample_files()
        self.test_api_endpoints()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed := [r for r in self.test_results if not r["success"]]:
            print("\n❌ Failed Tests:")
            for test in failed:
                print(f"  - {test['test']}: {test['message']}")
        
        print(f"\n{'🎉 All tests passed!' if passed == total else '⚠️ Some tests failed'}")
        return passed == total

def main():
    """Main test runner"""
    tester = AutoDocTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
