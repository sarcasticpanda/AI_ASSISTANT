"""
PDF Utils - PDF text extraction and chunking
Uses PyMuPDF (fitz) to extract text from PDFs and chunk it for LLM processing.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)

# Try importing PyMuPDF
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    logger.warning("PyMuPDF not installed. Install with: pip install PyMuPDF")
    PYMUPDF_AVAILABLE = False


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        str: Extracted text
    
    Example:
        text = extract_text_from_pdf("report.pdf")
        # Returns: "This is the content of the PDF..."
    """
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF not available. Install with: pip install PyMuPDF")
    
    logger.info(f"Extracting text from: {pdf_path}")
    
    try:
        # Open PDF
        doc = fitz.open(pdf_path)
        
        text_parts = []
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            if text.strip():  # Only add non-empty pages
                text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
        
        doc.close()
        
        full_text = "\n\n".join(text_parts)
        
        logger.info(f"✓ Extracted {len(full_text)} characters from {len(doc)} pages")
        
        return full_text
    
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise


def chunk_text(text: str, max_chars: int = 2500, overlap: int = 200) -> List[str]:
    """
    Split text into chunks for LLM processing.
    
    Args:
        text: Text to chunk
        max_chars: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks (for context)
    
    Returns:
        List[str]: List of text chunks
    
    Example:
        chunks = chunk_text(long_text, max_chars=2000)
        # Returns: ["chunk1...", "chunk2...", "chunk3..."]
    
    Strategy:
        - Try to split on paragraph boundaries (double newlines)
        - If paragraphs too long, split on sentence boundaries (periods)
        - If sentences too long, split at word boundaries
        - Maintain overlap between chunks for context continuity
    """
    if len(text) <= max_chars:
        # Text is short enough, return as single chunk
        return [text]
    
    logger.info(f"Chunking {len(text)} chars into ~{max_chars} char chunks")
    
    chunks = []
    
    # Split into paragraphs first
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        
        if not paragraph:
            continue
        
        # If adding this paragraph would exceed max_chars
        if len(current_chunk) + len(paragraph) + 2 > max_chars:
            if current_chunk:
                # Save current chunk
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap from previous
                if overlap > 0 and len(current_chunk) > overlap:
                    current_chunk = current_chunk[-overlap:] + "\n\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                # Paragraph itself is too long, need to split it
                if len(paragraph) > max_chars:
                    # Split long paragraph into sentences
                    sentences = paragraph.replace('. ', '.|').split('|')
                    
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 2 > max_chars:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                                
                                # Add overlap
                                if overlap > 0 and len(current_chunk) > overlap:
                                    current_chunk = current_chunk[-overlap:] + " " + sentence
                                else:
                                    current_chunk = sentence
                            else:
                                # Even single sentence is too long, force split
                                current_chunk = sentence
                        else:
                            current_chunk += (" " if current_chunk else "") + sentence
                else:
                    current_chunk = paragraph
        else:
            # Add paragraph to current chunk
            current_chunk += ("\n\n" if current_chunk else "") + paragraph
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    logger.info(f"✓ Created {len(chunks)} chunks")
    
    return chunks


def get_pdf_metadata(pdf_path: str) -> dict:
    """
    Extract metadata from PDF.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        dict: Metadata (title, author, pages, etc.)
    
    Example:
        metadata = get_pdf_metadata("report.pdf")
        # Returns: {"title": "Annual Report", "author": "...", "pages": 50}
    """
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF not available")
    
    try:
        doc = fitz.open(pdf_path)
        
        metadata = {
            "title": doc.metadata.get("title", "Unknown"),
            "author": doc.metadata.get("author", "Unknown"),
            "subject": doc.metadata.get("subject", ""),
            "keywords": doc.metadata.get("keywords", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "pages": len(doc),
            "file_size_bytes": doc.xref_length
        }
        
        doc.close()
        
        return metadata
    
    except Exception as e:
        logger.error(f"Failed to get PDF metadata: {e}")
        return {}


# ============================================================================
# UTILITIES
# ============================================================================

def is_available() -> bool:
    """Check if PyMuPDF is available"""
    return PYMUPDF_AVAILABLE
