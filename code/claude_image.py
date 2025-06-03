import base64
import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import mimetypes
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

import requests
from dotenv import load_dotenv
from PIL import Image
import fitz  # PyMuPDF for PDF handling


class AnthropicDocumentAnalyzer:
    """Client for analyzing images and PDFs using Anthropic's Claude API."""
    
    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"
    DEFAULT_MODEL = "claude-sonnet-4-20250514"
    DEFAULT_MAX_TOKENS = 1024
    
    # Supported file types
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    SUPPORTED_DOCUMENT_FORMATS = {'.pdf'}
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the analyzer with API key from environment or parameter."""
        load_dotenv()
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set ANTHROPIC_API_KEY or pass api_key parameter.")
        
        # Initialize mimetypes
        mimetypes.init()
    
    def pdf_to_images(self, pdf_path: Path, dpi: int = 200) -> List[Tuple[bytes, str]]:
        """Convert PDF pages to images and return as bytes with media type."""
        images = []
        pdf_document = fitz.open(str(pdf_path))
        
        try:
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                # Render page to image
                mat = fitz.Matrix(dpi/72, dpi/72)  # 72 is default PDF DPI
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                images.append((img_data, "image/png"))
        finally:
            pdf_document.close()
        
        return images
    
    def encode_file(self, file_path: Path) -> List[Tuple[str, str]]:
        """
        Encode file to base64. Returns list of (encoded_data, media_type) tuples.
        PDFs are converted to images first.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        suffix = file_path.suffix.lower()
        
        if suffix in self.SUPPORTED_IMAGE_FORMATS:
            # Handle regular images
            media_type, _ = mimetypes.guess_type(str(file_path))
            if not media_type:
                media_type = f"image/{suffix.lstrip('.')}"
            
            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            
            return [(encoded, media_type)]
        
        elif suffix in self.SUPPORTED_DOCUMENT_FORMATS:
            # Handle PDFs by converting to images
            images = self.pdf_to_images(file_path)
            encoded_images = []
            
            for img_data, media_type in images:
                encoded = base64.b64encode(img_data).decode("utf-8")
                encoded_images.append((encoded, media_type))
            
            return encoded_images
        
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def analyze_document(
        self, 
        file_path: str | Path,
        prompt: str = "Extract all key information from this document, including text and images.",
        model: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, any]:
        """Analyze a document and return the response."""
        file_path = Path(file_path)
        encoded_items = self.encode_file(file_path)
        
        # Build content list with all images/pages
        content = []
        for encoded_data, media_type in encoded_items:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": encoded_data
                }
            })
        
        # Add the text prompt
        content.append({
            "type": "text",
            "text": prompt
        })
        
        payload = {
            "model": model or self.DEFAULT_MODEL,
            "max_tokens": max_tokens or self.DEFAULT_MAX_TOKENS,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.API_VERSION,
            "content-type": "application/json"
        }
        
        response = requests.post(self.API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        return {
            "file": str(file_path),
            "pages": len(encoded_items),
            "response": response.json()["content"][0]["text"]
        }
    
    def get_supported_files(self, folder_path: Path) -> List[Path]:
        """Get all supported files from a folder."""
        supported_extensions = self.SUPPORTED_IMAGE_FORMATS | self.SUPPORTED_DOCUMENT_FORMATS
        files = []
        
        for file_path in folder_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                files.append(file_path)
        
        return sorted(files)
    
    def analyze_folder(
        self,
        folder_path: str | Path,
        prompt: Optional[str] = None,
        max_workers: int = 3,
        delay_between_calls: float = 0.5
    ) -> List[Dict[str, any]]:
        """
        Analyze all supported files in a folder.
        
        Args:
            folder_path: Path to folder containing documents
            prompt: Custom prompt for analysis
            max_workers: Maximum concurrent API calls
            delay_between_calls: Delay in seconds between API calls to avoid rate limiting
        
        Returns:
            List of analysis results
        """
        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            raise ValueError(f"Invalid folder path: {folder_path}")
        
        files = self.get_supported_files(folder_path)
        if not files:
            print(f"No supported files found in {folder_path}")
            return []
        
        print(f"Found {len(files)} files to process:")
        for f in files:
            print(f"  - {f.name}")
        print()
        
        results = []
        failed = []
        
        # Process files with rate limiting
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks with delays
            future_to_file = {}
            for i, file_path in enumerate(files):
                if i > 0:
                    time.sleep(delay_between_calls)
                
                future = executor.submit(
                    self.analyze_document,
                    file_path,
                    prompt or f"Extract all key information from this {file_path.suffix} file."
                )
                future_to_file[future] = file_path
            
            # Collect results
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"✓ Processed: {file_path.name}")
                except Exception as e:
                    error_info = {
                        "file": str(file_path),
                        "error": str(e)
                    }
                    failed.append(error_info)
                    print(f"✗ Failed: {file_path.name} - {e}")
        
        print(f"\nCompleted: {len(results)} successful, {len(failed)} failed")
        
        return {
            "successful": results,
            "failed": failed
        }
    
    def save_results(self, results: Dict[str, List], output_file: str = "analysis_results.txt"):
        """Save analysis results to a text file."""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("Document Analysis Results\n")
            f.write("=" * 50 + "\n\n")
            
            # Write successful analyses
            for result in results["successful"]:
                f.write(f"File: {result['file']}\n")
                f.write(f"Pages/Images: {result['pages']}\n")
                f.write("-" * 30 + "\n")
                f.write(result['response'])
                f.write("\n\n" + "=" * 50 + "\n\n")
            
            # Write failed analyses
            if results["failed"]:
                f.write("\nFailed Files:\n")
                f.write("-" * 30 + "\n")
                for failed in results["failed"]:
                    f.write(f"File: {failed['file']}\n")
                    f.write(f"Error: {failed['error']}\n\n")
        
        print(f"\nResults saved to: {output_file}")


def main():
    """Example usage of the AnthropicDocumentAnalyzer."""
    try:
        # Initialize analyzer
        analyzer = AnthropicDocumentAnalyzer()
        
        # Analyze a folder
        folder_path = "../data"  # Change this to your folder path
        results = analyzer.analyze_folder(
            folder_path,
            prompt="Extract and summarize all text content, describe any images, and identify key information.",
            max_workers=3,  # Adjust based on your API rate limits
            delay_between_calls=0.5  # Add delay to avoid rate limiting
        )
        
        # Save results to file
        analyzer.save_results(results)
        
        # Print summary
        print("\nSummary:")
        for result in results["successful"]:
            print(f"\n{Path(result['file']).name}:")
            print(result['response'][:200] + "..." if len(result['response']) > 200 else result['response'])
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()