"""
Audiveris OMR Integration
Uses the Audiveris open-source OMR system from GitHub
https://github.com/Audiveris/audiveris
"""
import os
import subprocess
import logging
import shutil
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path
import xml.etree.ElementTree as ET
from music21 import converter, stream

logger = logging.getLogger(__name__)


class AudiverisOMR:
    """
    Integration with Audiveris OMR system
    Requires Audiveris to be installed and accessible
    """
    
    def __init__(self, audiveris_path: Optional[str] = None):
        """
        Initialize Audiveris OMR
        
        Args:
            audiveris_path: Path to Audiveris installation (e.g., /opt/audiveris)
                          If None, will search common locations
        """
        self.logger = logger
        self.audiveris_path = audiveris_path or self._find_audiveris()
        self.temp_dir = tempfile.mkdtemp(prefix='mugic_audiveris_')
        
        if self.audiveris_path:
            self.logger.info(f"Audiveris found at: {self.audiveris_path}")
        else:
            self.logger.warning("Audiveris not found. Using fallback OMR.")
    
    def _find_audiveris(self) -> Optional[str]:
        """Search for Audiveris installation"""
        # Common installation locations
        search_paths = [
            '/opt/audiveris',
            '/usr/local/audiveris',
            os.path.expanduser('~/audiveris'),
            './audiveris',
            '../audiveris'
        ]
        
        # Also check for audiveris executable in PATH
        audiveris_exe = shutil.which('audiveris')
        if audiveris_exe:
            return os.path.dirname(audiveris_exe)
        
        # Check common paths
        for path in search_paths:
            if os.path.exists(path):
                # Check for the main jar or executable
                if os.path.exists(os.path.join(path, 'audiveris.jar')) or \
                   os.path.exists(os.path.join(path, 'bin', 'audiveris')):
                    return path
        
        return None
    
    def is_available(self) -> bool:
        """Check if Audiveris is available"""
        return self.audiveris_path is not None
    
    def analyze_sheet_music(self, pdf_path: str) -> Dict[str, Any]:
        """
        Analyze sheet music using Audiveris
        
        Args:
            pdf_path: Path to PDF sheet music file
            
        Returns:
            Musical analysis dictionary
        """
        try:
            if not self.is_available():
                raise RuntimeError(
                    "Audiveris not found. Please install Audiveris from: "
                    "https://github.com/Audiveris/audiveris/releases"
                )
            
            self.logger.info(f"Processing {pdf_path} with Audiveris")
            
            # Run Audiveris to transcribe PDF to MusicXML
            musicxml_path = self._run_audiveris(pdf_path)
            
            if not musicxml_path or not os.path.exists(musicxml_path):
                raise RuntimeError("Audiveris failed to generate MusicXML output")
            
            # Parse MusicXML to extract musical information
            analysis = self._parse_musicxml(musicxml_path)
            
            self.logger.info(f"Audiveris analysis complete: {len(analysis['notes'])} notes")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Audiveris analysis failed: {str(e)}")
            raise
    
    def _run_audiveris(self, input_pdf: str) -> Optional[str]:
        """
        Run Audiveris command-line tool
        
        Args:
            input_pdf: Path to input PDF
            
        Returns:
            Path to generated MusicXML file
        """
        try:
            # Output file path
            output_dir = self.temp_dir
            basename = os.path.splitext(os.path.basename(input_pdf))[0]
            output_mxl = os.path.join(output_dir, f"{basename}.mxl")
            
            # Audiveris command (adjust based on installation)
            # The -batch flag runs in batch mode without GUI
            # -export saves to MusicXML format
            
            # Try different command formats
            commands = [
                # Standard Audiveris CLI
                [
                    'java', '-jar', 
                    os.path.join(self.audiveris_path, 'audiveris.jar'),
                    '-batch',
                    '-export',
                    '-output', output_dir,
                    input_pdf
                ],
                # Alternative: using audiveris script
                [
                    os.path.join(self.audiveris_path, 'bin', 'audiveris'),
                    '-batch',
                    '-export',
                    '-output', output_dir,
                    input_pdf
                ],
                # Alternative: direct executable
                [
                    'audiveris',
                    '-batch',
                    '-export',
                    '-output', output_dir,
                    input_pdf
                ]
            ]
            
            success = False
            for cmd in commands:
                try:
                    self.logger.info(f"Trying command: {' '.join(cmd)}")
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode == 0:
                        self.logger.info("Audiveris completed successfully")
                        success = True
                        break
                    else:
                        self.logger.warning(f"Command failed: {result.stderr}")
                        
                except FileNotFoundError:
                    continue
                except Exception as e:
                    self.logger.warning(f"Command error: {e}")
                    continue
            
            if not success:
                raise RuntimeError("All Audiveris command attempts failed")
            
            # Find the generated MusicXML file
            # Audiveris may generate .mxl or .xml files
            for ext in ['.mxl', '.xml', '.musicxml']:
                potential_path = os.path.join(output_dir, basename + ext)
                if os.path.exists(potential_path):
                    return potential_path
            
            # Search output directory
            for file in os.listdir(output_dir):
                if file.endswith(('.mxl', '.xml', '.musicxml')):
                    return os.path.join(output_dir, file)
            
            return None
            
        except subprocess.TimeoutExpired:
            self.logger.error("Audiveris timeout")
            return None
        except Exception as e:
            self.logger.error(f"Error running Audiveris: {e}")
            return None
    
    def _parse_musicxml(self, musicxml_path: str) -> Dict[str, Any]:
        """
        Parse MusicXML file generated by Audiveris
        
        Args:
            musicxml_path: Path to MusicXML file
            
        Returns:
            Analysis dictionary with notes, rhythms, metadata
        """
        try:
            # Use music21 to parse MusicXML
            score = converter.parse(musicxml_path)
            
            # Extract notes
            notes_list = []
            rhythms_list = []
            
            # Get all notes from all parts
            for part in score.parts:
                current_time = 0.0
                
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
                'analysis_method': 'Audiveris OMR',
                'has_real_detection': True,
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


def download_audiveris(install_path: str = './audiveris') -> bool:
    """
    Helper function to download and setup Audiveris
    
    Args:
        install_path: Where to install Audiveris
        
    Returns:
        True if successful
    """
    logger.info(f"Downloading Audiveris to {install_path}")
    
    try:
        # Audiveris GitHub release URL
        # This would need to be updated with the actual latest release
        audiveris_version = "5.3.1"
        
        system = os.uname().sysname.lower()
        
        if system == 'linux':
            download_url = f"https://github.com/Audiveris/audiveris/releases/download/{audiveris_version}/Audiveris-{audiveris_version}.tar.gz"
        elif system == 'darwin':  # macOS
            download_url = f"https://github.com/Audiveris/audiveris/releases/download/{audiveris_version}/Audiveris-{audiveris_version}.dmg"
        elif system == 'windows':
            download_url = f"https://github.com/Audiveris/audiveris/releases/download/{audiveris_version}/Audiveris-{audiveris_version}.exe"
        else:
            logger.error(f"Unsupported platform: {system}")
            return False
        
        logger.info(f"Please download Audiveris from: {download_url}")
        logger.info("Or visit: https://github.com/Audiveris/audiveris/releases")
        
        return False  # Manual download required
        
    except Exception as e:
        logger.error(f"Error setting up Audiveris: {e}")
        return False
