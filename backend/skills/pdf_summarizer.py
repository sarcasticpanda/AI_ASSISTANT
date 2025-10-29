"""
PDF Summarizer Skill - Summarize PDF documents
Extracts text from PDF and generates summary using Qwen LLM.
"""

import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Import core modules
try:
    from core import pdf_utils, qwen_api, mongo_manager
except ImportError as e:
    logger.warning(f"Core modules not available: {e}")


def summarize_pdf(pdf_path: str) -> Dict:
    """
    Summarize a PDF file.
    
    Process:
    1. Extract text from PDF
    2. Split into chunks (max 2500 chars each)
    3. Summarize each chunk using Qwen
    4. Merge chunk summaries into final summary
    5. Save to database
    
    Args:
        pdf_path: Absolute path to PDF file
    
    Returns:
        dict: Summary result
        {
            "filename": "report.pdf",
            "summary": "This document discusses...",
            "chunks_processed": 5,
            "success": True
        }
    
    Example:
        result = summarize_pdf("C:/Users/Me/Documents/report.pdf")
        print(result["summary"])
    """
    logger.info(f"Summarizing PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        return {
            "success": False,
            "error": f"PDF file not found: {pdf_path}"
        }
    
    filename = os.path.basename(pdf_path)
    
    try:
        # Step 1: Extract text
        logger.info("Extracting text from PDF...")
        text = pdf_utils.extract_text_from_pdf(pdf_path)
        
        if not text.strip():
            return {
                "success": False,
                "error": "No text found in PDF (may be image-based)"
            }
        
        logger.info(f"Extracted {len(text)} characters")
        
        # Step 2: Chunk text
        logger.info("Chunking text...")
        chunks = pdf_utils.chunk_text(text, max_chars=2500)
        
        logger.info(f"Created {len(chunks)} chunks")
        
        # Step 3: Summarize each chunk
        logger.info("Summarizing chunks...")
        chunk_summaries = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Summarizing chunk {i+1}/{len(chunks)}...")
            
            try:
                summary = qwen_api.summarize_text(chunk, max_length=500)
                chunk_summaries.append(summary)
            except Exception as e:
                logger.error(f"Failed to summarize chunk {i+1}: {e}")
                chunk_summaries.append(f"[Error summarizing chunk {i+1}]")
        
        # Step 4: Merge summaries
        logger.info("Merging summaries...")
        
        if len(chunk_summaries) == 1:
            # Only one chunk, use it as final summary
            final_summary = chunk_summaries[0]
        else:
            # Multiple chunks, merge them
            try:
                final_summary = qwen_api.merge_summaries(chunk_summaries)
            except Exception as e:
                logger.error(f"Failed to merge summaries: {e}")
                # Fallback: concatenate
                final_summary = "\n\n".join(chunk_summaries)
        
        logger.info(f"Final summary: {len(final_summary)} characters")
        
        # Step 5: Save to database
        try:
            mongo_manager.save_pdf_summary(
                filename=filename,
                summary=final_summary,
                chunks=chunks,
                chunk_summaries=chunk_summaries
            )
            logger.info("✓ Saved summary to database")
        except Exception as e:
            logger.warning(f"Failed to save to database: {e}")
        
        # Return result
        return {
            "success": True,
            "filename": filename,
            "summary": final_summary,
            "chunks_processed": len(chunks),
            "chunk_summaries": chunk_summaries,
            "original_length": len(text),
            "summary_length": len(final_summary)
        }
    
    except Exception as e:
        logger.error(f"PDF summarization failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_saved_summary(filename: str) -> Dict:
    """
    Get previously saved summary from database.
    
    Args:
        filename: PDF filename
    
    Returns:
        dict: Summary data or None
    """
    try:
        summary = mongo_manager.get_pdf_summary(filename)
        
        if summary:
            return {
                "success": True,
                "filename": filename,
                "summary": summary.get("summary", ""),
                "chunks_count": summary.get("chunks_count", 0),
                "timestamp": summary.get("timestamp", "")
            }
        else:
            return {
                "success": False,
                "error": f"No summary found for {filename}"
            }
    
    except Exception as e:
        logger.error(f"Failed to get saved summary: {e}")
        return {
            "success": False,
            "error": str(e)
        }
