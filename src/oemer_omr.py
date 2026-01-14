"""
OEMER (End-to-end OMR) Integration
Uses the OEMER system by BreezeWhite from GitHub
https://github.com/BreezeWhite/oemer

This is optimized for Vercel serverless deployment
Enhanced with AI-based advanced notation detection
"""
import os
import tempfile
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)


class OemerOMR:
    """
    Integration with OEMER (End-to-end OMR) system
    Lightweight and serverless-friendly alternative to Audiveris
    Enhanced with advanced notation detection for dynamics, crescendos, and more
    """
    
    def __init__(self):
        """Initialize OEMER OMR system"""
        self.logger = logger
        self.oemer_available = self._check_oemer_available()
        self.temp_dir = tempfile.mkdtemp(prefix='mugic_oemer_')
        
        # Initialize advanced notation detector
        try:
            from src.advanced_notation_detector import AdvancedNotationDetector
            self.advanced_detector = AdvancedNotationDetector()
            self.has_advanced_detection = True
            self.logger.info("✓ Advanced notation detection enabled")
        except Exception as e:
            self.logger.warning(f"Advanced detection unavailable: {e}")
            self.advanced_detector = None
            self.has_advanced_detection = False
        
        if self.oemer_available:
            self.logger.info("✓ OEMER is available and ready")
        else:
            self.logger.warning("OEMER not available. Install with: pip install oemer")
    
    def _check_oemer_available(self) -> bool:
        """Check if OEMER is installed and available"""
        try:
            import oemer
            return True
        except ImportError:
            return False
    
    def is_available(self) -> bool:
        """Check if OEMER is available"""
        return self.oemer_available
    
    def analyze_sheet_music(self, pdf_path: str) -> Dict[str, Any]:
        """
        Analyze sheet music using OEMER
        
        Args:
            pdf_path: Path to PDF sheet music file
            
        Returns:
            Musical analysis dictionary
        """
        try:
            if not self.is_available():
                raise RuntimeError(
                    "OEMER not found. Please install OEMER with: pip install oemer"
                )
            
            self.logger.info(f"Processing {pdf_path} with OEMER")
            
            # Check if input is PDF or image
            file_ext = os.path.splitext(pdf_path)[1].lower()
            
            if file_ext == '.pdf':
                # Convert PDF to image first (OEMER works with images)
                image_path = self._pdf_to_image(pdf_path)
            elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                # Already an image, use directly
                image_path = pdf_path
                self.logger.info(f"Using image directly: {image_path}")
            else:
                raise ValueError(f"Unsupported file format: {file_ext}. Use PDF or image files.")
            
            # Run OEMER to transcribe to MusicXML
            musicxml_path = self._run_oemer(image_path)
            
            if not musicxml_path or not os.path.exists(musicxml_path):
                raise RuntimeError("OEMER failed to generate MusicXML output")
            
            # Parse MusicXML to extract musical information
            analysis = self._parse_musicxml(musicxml_path)
            
            # Enhance with advanced notation detection
            if self.has_advanced_detection and self.advanced_detector:
                self.logger.info("Running advanced notation detection...")
                analysis = self.advanced_detector.enhance_omr_analysis(image_path, analysis)
            
            self.logger.info(f"✓ OEMER analysis complete: {len(analysis['notes'])} notes detected")
            return analysis
            
        except Exception as e:
            self.logger.error(f"OEMER analysis failed: {str(e)}")
            raise
    
    def _pdf_to_image(self, pdf_path: str) -> str:
        """
        Convert PDF to image for OEMER processing
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Path to generated image
        """
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            
            self.logger.info(f"Converting PDF to image: {pdf_path}")
            
            # Open PDF
            doc = fitz.open(pdf_path)
            
            if len(doc) == 0:
                raise ValueError("PDF file has no pages")
            
            self.logger.info(f"PDF has {len(doc)} page(s). Processing first page.")
            
            # Convert first page to image
            page = doc[0]
            
            # Render at high resolution for better OMR accuracy
            # OEMER works best with high-resolution images (300 DPI equivalent)
            zoom = 3  # 3x resolution for optimal quality
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Save as PNG (lossless format, best for OMR)
            output_path = os.path.join(self.temp_dir, "sheet_music.png")
            pix.save(output_path)
            
            doc.close()
            
            # Log image details
            img_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            self.logger.info(f"✓ PDF converted to image: {output_path}")
            self.logger.info(f"  Image size: {pix.width}x{pix.height} ({img_size:.2f} MB)")
            
            return output_path
            
        except ImportError as e:
            self.logger.error("PyMuPDF (fitz) not installed. Install with: pip install PyMuPDF")
            raise RuntimeError("PyMuPDF required for PDF processing") from e
        except Exception as e:
            self.logger.error(f"Error converting PDF to image: {e}")
            raise RuntimeError(f"PDF conversion failed: {str(e)}") from e
    
    def _run_oemer(self, image_path: str) -> Optional[str]:
        """
        Run OEMER on the image
        
        Args:
            image_path: Path to input image
            
        Returns:
            Path to generated MusicXML file
        """
        try:
            # Import OEMER's main function
            from oemer.ete import extract
            from argparse import Namespace
            
            # Create output directory
            output_dir = self.temp_dir
            
            # Prepare arguments
            args = Namespace(
                img_path=image_path,
                output_path=output_dir,
                use_tf=False,  # Use ONNX runtime (faster and lighter)
                save_cache=False,  # Don't save cache in serverless
                without_deskew=False  # Enable deskewing by default
            )
            
            self.logger.info("Running OEMER transcription...")
            
            # Run OEMER
            musicxml_path = extract(args)
            
            if musicxml_path and os.path.exists(musicxml_path):
                self.logger.info(f"OEMER completed: {musicxml_path}")
                return musicxml_path
            else:
                self.logger.error("OEMER did not generate output")
                return None
                
        except Exception as e:
            self.logger.error(f"Error running OEMER: {e}")
            return None
    
    def _parse_musicxml(self, musicxml_path: str) -> Dict[str, Any]:
        """
        Parse MusicXML file generated by OEMER
        
        Args:
            musicxml_path: Path to MusicXML file
            
        Returns:
            Analysis dictionary with notes, rhythms, metadata
        """
        try:
            from music21 import converter
            
            # Parse MusicXML
            score = converter.parse(musicxml_path)
            
            # Extract notes
            notes_list = []
            rhythms_list = []
            
            # Get all notes from all parts
            for part in score.parts:
                for element in part.flatten().notesAndRests:
                    if hasattr(element, 'pitch') and element.pitch:
                        # It's a note
                        notes_list.append({
                            'pitch': element.pitch.nameWithOctave,
                            'midi_note': element.pitch.midi,
                            'start_time': float(element.offset),
                            'duration': float(element.duration.quarterLength),
                            'velocity': 80
                        })
                        
                        rhythms_list.append({
                            'type': element.duration.type,
                            'duration': float(element.duration.quarterLength),
                            'start_time': float(element.offset)
                        })
            
            # Extract metadata
            time_signature = '4/4'
            key_signature = 'C'
            tempo_marking = 120
            
            # Get time signature
            ts = score.flatten().getElementsByClass('TimeSignature')
            if ts:
                time_signature = ts[0].ratioString
            
            # Get key signature
            ks = score.flatten().getElementsByClass('KeySignature')
            if ks:
                key_signature = ks[0].asKey().tonic.name
            
            # Get tempo
            tempo_marks = score.flatten().getElementsByClass('MetronomeMark')
            if tempo_marks:
                tempo_marking = int(tempo_marks[0].number)
            
            # Count measures
            measures = len(score.parts[0].getElementsByClass('Measure')) if score.parts else 0
            
            analysis = {
                'notes': notes_list,
                'rhythms': rhythms_list,
                'time_signature': time_signature,
                'key_signature': key_signature,
                'tempo': tempo_marking,
                'clef': 'treble',  # Default
                'num_pages': 1,
                'num_staves': len(score.parts),
                'total_measures': measures,
                'analysis_method': 'OEMER (End-to-end OMR)',
                'has_real_detection': True,
                'confidence': 0.90,  # OEMER typically has high confidence
                'musicxml_path': musicxml_path
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error parsing MusicXML: {e}")
            raise
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.logger.info("Cleaned up temporary files")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup temp directory: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.cleanup()
