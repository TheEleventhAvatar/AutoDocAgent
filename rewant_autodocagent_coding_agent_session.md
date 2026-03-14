# Coding Agent Session – AutoDocAgent

Repository: https://github.com/TheEleventhAvatar/AutoDocAgent  
Coding Agent: Windsurf (Cascade)

## Objective
Build an AI-powered document automation system using LangChain that extracts structured data from messy PDFs and images and automatically fills enterprise templates.

## Session Summary

User:
Design an architecture for a document automation pipeline that converts unstructured PDFs and images into structured data.

Agent:
Suggested pipeline:
- Document ingestion
- OCR / PDF parsing
- LLM-based extraction using LangChain
- Schema validation
- Enterprise template autofill

User:
Generate Python code for document ingestion and document parsing.

Agent:
Implemented ingestion logic for PDFs and images with OCR fallback for scanned documents.

User:
Add structured data extraction using LLMs.

Agent:
Provided LangChain-based extraction pipeline with prompt templates and JSON schema validation.

User:
Debug cases where extracted fields sometimes return null values.

Agent:
Suggested retry logic, schema enforcement, and prompt adjustments to improve extraction reliability.

Full implementation available in the GitHub repository.

## Outcome
The session produced the core architecture for AutoDocAgent, a document automation system that uses LangChain to extract structured data from messy documents and automatically populate enterprise templates and forms.
