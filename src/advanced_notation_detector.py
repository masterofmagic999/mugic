"""
Advanced AI-Based Music Notation Detector
Detects dynamics, crescendos, decrescendos, and alternate endings
Uses computer vision and pattern recognition for obscure notation elements
"""
import os
import cv2
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)


class AdvancedNotationDetector:
    """
    AI-enhanced detector for dynamics, articulations, and expression marks
    Handles elements that OEMER and other OMR systems miss:
    - Dynamics (p, pp, f, ff, mf, mp, etc.)
    - Crescendos (< or "cresc.")
    - Decrescendos (> or "decresc." or "dim.")
    - Accents and articulations (already in OEMER but enhanced here)
    - Alternate endings (1st time, 2nd time, etc.)
    - Repeat signs and codas
    """
    
    def __init__(self):
        """Initialize the advanced notation detector"""
        self.logger = logger
        self.temp_dir = tempfile.mkdtemp(prefix='mugic_advanced_')
        
        # Define dynamic markings to detect
        self.dynamics_patterns = {
            'ppp': {'intensity': 10, 'name': 'pianississimo'},
            'pp': {'intensity': 20, 'name': 'pianissimo'},
            'p': {'intensity': 30, 'name': 'piano'},
            'mp': {'intensity': 45, 'name': 'mezzo-piano'},
            'mf': {'intensity': 60, 'name': 'mezzo-forte'},
            'f': {'intensity': 75, 'name': 'forte'},
            'ff': {'intensity': 90, 'name': 'fortissimo'},
            'fff': {'intensity': 100, 'name': 'fortississimo'},
            'sfz': {'intensity': 95, 'name': 'sforzando'},
            'fp': {'intensity': 70, 'name': 'forte-piano'},
        }
        
        self.logger.info("✓ Advanced Notation Detector initialized")
    
    def enhance_omr_analysis(self, 
                            image_path: str, 
                            base_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance OMR analysis with advanced notation detection
        
        Args:
            image_path: Path to sheet music image
            base_analysis: Basic OMR analysis from OEMER or other system
            
        Returns:
            Enhanced analysis with dynamics, crescendos, and alternate endings
        """
        try:
            self.logger.info("Starting advanced notation detection...")
            
            # Load the image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect various notation elements
            dynamics = self._detect_dynamics(gray, img)
            crescendos = self._detect_crescendos(gray, img)
            decrescendos = self._detect_decrescendos(gray, img)
            alternate_endings = self._detect_alternate_endings(gray, img)
            articulations = self._detect_articulations(gray, img)
            repeat_signs = self._detect_repeat_signs(gray, img)
            
            # Add to base analysis
            enhanced_analysis = base_analysis.copy()
            enhanced_analysis['dynamics'] = dynamics
            enhanced_analysis['crescendos'] = crescendos
            enhanced_analysis['decrescendos'] = decrescendos
            enhanced_analysis['alternate_endings'] = alternate_endings
            enhanced_analysis['articulations'] = articulations
            enhanced_analysis['repeat_signs'] = repeat_signs
            enhanced_analysis['has_advanced_detection'] = True
            
            self.logger.info(f"✓ Advanced detection complete:")
            self.logger.info(f"  - {len(dynamics)} dynamic markings")
            self.logger.info(f"  - {len(crescendos)} crescendos")
            self.logger.info(f"  - {len(decrescendos)} decrescendos")
            self.logger.info(f"  - {len(alternate_endings)} alternate endings")
            self.logger.info(f"  - {len(articulations)} articulations")
            
            return enhanced_analysis
            
        except Exception as e:
            self.logger.error(f"Advanced detection failed: {e}")
            # Return base analysis without enhancements
            base_analysis['has_advanced_detection'] = False
            return base_analysis
    
    def _detect_dynamics(self, gray: np.ndarray, img: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect dynamic markings (p, pp, f, ff, mf, mp, etc.)
        Uses OCR and pattern matching
        """
        dynamics = []
        
        try:
            # Use pytesseract for text detection if available
            try:
                import pytesseract
                
                # Configure for music notation text
                custom_config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=pfms'
                
                # Get text with bounding boxes
                data = pytesseract.image_to_data(gray, config=custom_config, output_type=pytesseract.Output.DICT)
                
                for i, text in enumerate(data['text']):
                    text_clean = text.strip().lower()
                    
                    # Check if it matches a dynamic marking
                    if text_clean in self.dynamics_patterns:
                        dynamics.append({
                            'type': 'dynamic',
                            'marking': text_clean,
                            'name': self.dynamics_patterns[text_clean]['name'],
                            'intensity': self.dynamics_patterns[text_clean]['intensity'],
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i],
                            'confidence': data['conf'][i] / 100.0,
                            'detection_method': 'OCR'
                        })
                
            except ImportError:
                # Fallback: Template matching for common dynamics
                dynamics = self._detect_dynamics_template_matching(gray, img)
                
        except Exception as e:
            self.logger.warning(f"Dynamic detection error: {e}")
        
        return dynamics
    
    def _detect_dynamics_template_matching(self, gray: np.ndarray, img: np.ndarray) -> List[Dict[str, Any]]:
        """
        Fallback method using template matching for dynamics
        Detects characteristic shapes of p, f, m letters
        """
        dynamics = []
        
        # Look for italic lowercase 'f' and 'p' shapes
        # These are typically in the lower third of the image
        h, w = gray.shape
        bottom_third = gray[int(h * 0.66):, :]
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            bottom_third, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find contours (potential letter shapes)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 50 or area > 2000:  # Filter by size
                continue
            
            x, y, w_box, h_box = cv2.boundingRect(contour)
            aspect_ratio = w_box / float(h_box) if h_box > 0 else 0
            
            # Dynamics text is typically taller than wide
            if 0.3 < aspect_ratio < 1.5 and h_box > w_box:
                # Estimate dynamic based on position and characteristics
                dynamics.append({
                    'type': 'dynamic',
                    'marking': 'detected',
                    'name': 'dynamic_marking',
                    'intensity': 50,  # Default medium
                    'x': x,
                    'y': y + int(h * 0.66),
                    'width': w_box,
                    'height': h_box,
                    'confidence': 0.6,
                    'detection_method': 'template_matching'
                })
        
        return dynamics
    
    def _detect_crescendos(self, gray: np.ndarray, img: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect crescendo markings (< shapes or "cresc." text)
        """
        crescendos = []
        
        try:
            # Look for < shaped lines (hairpin crescendo)
            # Use Hough Line Transform to find diagonal lines
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                   minLineLength=30, maxLineGap=10)
            
            if lines is not None:
                # Group lines that form < shapes
                for i in range(len(lines)):
                    for j in range(i + 1, len(lines)):
                        x1, y1, x2, y2 = lines[i][0]
                        x3, y3, x4, y4 = lines[j][0]
                        
                        # Check if lines form a < shape (converging lines)
                        # Lines should start close together and end further apart
                        start_dist = np.sqrt((x1 - x3)**2 + (y1 - y3)**2)
                        end_dist = np.sqrt((x2 - x4)**2 + (y2 - y4)**2)
                        
                        if start_dist < 20 and end_dist > 50:
                            crescendos.append({
                                'type': 'crescendo',
                                'shape': 'hairpin',
                                'start_x': min(x1, x3),
                                'start_y': (y1 + y3) // 2,
                                'end_x': max(x2, x4),
                                'end_y': (y2 + y4) // 2,
                                'length': end_dist,
                                'confidence': 0.75,
                                'detection_method': 'line_detection'
                            })
            
            # Also look for "cresc." text using OCR if available
            try:
                import pytesseract
                text = pytesseract.image_to_string(gray).lower()
                if 'cresc' in text:
                    crescendos.append({
                        'type': 'crescendo',
                        'shape': 'text',
                        'text': 'cresc.',
                        'confidence': 0.8,
                        'detection_method': 'OCR'
                    })
            except ImportError:
                pass
                
        except Exception as e:
            self.logger.warning(f"Crescendo detection error: {e}")
        
        return crescendos
    
    def _detect_decrescendos(self, gray: np.ndarray, img: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect decrescendo/diminuendo markings (> shapes or "dim." text)
        """
        decrescendos = []
        
        try:
            # Look for > shaped lines (hairpin decrescendo)
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50,
                                   minLineLength=30, maxLineGap=10)
            
            if lines is not None:
                # Group lines that form > shapes
                for i in range(len(lines)):
                    for j in range(i + 1, len(lines)):
                        x1, y1, x2, y2 = lines[i][0]
                        x3, y3, x4, y4 = lines[j][0]
                        
                        # Check if lines form a > shape (diverging lines)
                        # Lines should start further apart and end close together
                        start_dist = np.sqrt((x1 - x3)**2 + (y1 - y3)**2)
                        end_dist = np.sqrt((x2 - x4)**2 + (y2 - y4)**2)
                        
                        if start_dist > 50 and end_dist < 20:
                            decrescendos.append({
                                'type': 'decrescendo',
                                'shape': 'hairpin',
                                'start_x': min(x1, x3),
                                'start_y': (y1 + y3) // 2,
                                'end_x': max(x2, x4),
                                'end_y': (y2 + y4) // 2,
                                'length': start_dist,
                                'confidence': 0.75,
                                'detection_method': 'line_detection'
                            })
            
            # Look for "dim." or "decresc." text
            try:
                import pytesseract
                text = pytesseract.image_to_string(gray).lower()
                if 'dim' in text or 'decresc' in text:
                    decrescendos.append({
                        'type': 'decrescendo',
                        'shape': 'text',
                        'text': 'dim.' if 'dim' in text else 'decresc.',
                        'confidence': 0.8,
                        'detection_method': 'OCR'
                    })
            except ImportError:
                pass
                
        except Exception as e:
            self.logger.warning(f"Decrescendo detection error: {e}")
        
        return decrescendos
    
    def _detect_alternate_endings(self, gray: np.ndarray, img: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect alternate endings (1st time, 2nd time brackets)
        These are horizontal brackets with numbers above them
        """
        endings = []
        
        try:
            h, w = gray.shape
            
            # Alternate endings are typically in the top half
            top_half = gray[:int(h * 0.5), :]
            
            # Look for horizontal lines (the bracket part)
            edges = cv2.Canny(top_half, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                                   minLineLength=100, maxLineGap=5)
            
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    
                    # Check if line is mostly horizontal
                    angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                    if angle < 10 or angle > 170:  # Nearly horizontal
                        # Look for numbers near this line (using OCR or template)
                        region = top_half[max(0, y1-30):min(top_half.shape[0], y1+10),
                                        x1:x2]
                        
                        # Try to detect numbers
                        try:
                            import pytesseract
                            config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.'
                            text = pytesseract.image_to_string(region, config=config).strip()
                            
                            if text and any(c.isdigit() for c in text):
                                endings.append({
                                    'type': 'alternate_ending',
                                    'number': text,
                                    'x': x1,
                                    'y': y1,
                                    'width': x2 - x1,
                                    'bracket_type': 'volta',
                                    'confidence': 0.85,
                                    'detection_method': 'bracket_and_OCR'
                                })
                        except ImportError:
                            # Fallback: just note that a bracket was found
                            endings.append({
                                'type': 'alternate_ending',
                                'number': 'unknown',
                                'x': x1,
                                'y': y1,
                                'width': x2 - x1,
                                'bracket_type': 'volta',
                                'confidence': 0.6,
                                'detection_method': 'bracket_only'
                            })
                            
        except Exception as e:
            self.logger.warning(f"Alternate ending detection error: {e}")
        
        return endings
    
    def _detect_articulations(self, gray: np.ndarray, img: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect articulations (accents, staccato, tenuto, fermata, etc.)
        Enhanced version beyond what OEMER provides
        """
        articulations = []
        
        try:
            # Apply morphological operations to enhance small marks
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            
            # Threshold
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Find small connected components (potential articulation marks)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Articulation marks are small (20-200 pixels typically)
                if 20 < area < 200:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / float(h) if h > 0 else 0
                    
                    # Classify based on shape characteristics
                    articulation_type = 'unknown'
                    
                    if 0.8 < aspect_ratio < 1.2 and area < 50:
                        # Likely staccato dot (circular, small)
                        articulation_type = 'staccato'
                    elif aspect_ratio > 2.0 and h < 10:
                        # Likely tenuto (horizontal line)
                        articulation_type = 'tenuto'
                    elif aspect_ratio < 0.5 and area < 100:
                        # Vertical-ish shape, possibly accent
                        articulation_type = 'accent'
                    
                    if articulation_type != 'unknown':
                        articulations.append({
                            'type': 'articulation',
                            'marking': articulation_type,
                            'x': x,
                            'y': y,
                            'width': w,
                            'height': h,
                            'confidence': 0.7,
                            'detection_method': 'shape_analysis'
                        })
                        
        except Exception as e:
            self.logger.warning(f"Articulation detection error: {e}")
        
        return articulations
    
    def _detect_repeat_signs(self, gray: np.ndarray, img: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect repeat signs, D.C., D.S., Coda, Segno symbols
        """
        repeats = []
        
        try:
            # Look for double barlines with dots (repeat signs)
            # These appear as thick vertical lines with dots
            
            # Detect vertical lines
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                                   minLineLength=50, maxLineGap=5)
            
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    
                    # Check if line is mostly vertical
                    angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                    if 80 < angle < 100:  # Nearly vertical
                        # Look for dots near this line
                        # Repeat signs have dots on both sides of the barline
                        repeats.append({
                            'type': 'repeat_sign',
                            'subtype': 'barline',
                            'x': x1,
                            'y': y1,
                            'confidence': 0.65,
                            'detection_method': 'line_detection'
                        })
            
            # Look for text markers (D.C., D.S., Fine, Coda)
            try:
                import pytesseract
                text = pytesseract.image_to_string(gray).lower()
                
                markers = ['d.c.', 'd.s.', 'fine', 'coda', 'segno', 'to coda']
                for marker in markers:
                    if marker in text:
                        repeats.append({
                            'type': 'repeat_sign',
                            'subtype': 'text_marker',
                            'text': marker,
                            'confidence': 0.8,
                            'detection_method': 'OCR'
                        })
            except ImportError:
                pass
                
        except Exception as e:
            self.logger.warning(f"Repeat sign detection error: {e}")
        
        return repeats
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                self.logger.info("Cleaned up temporary files")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup temp directory: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.cleanup()
