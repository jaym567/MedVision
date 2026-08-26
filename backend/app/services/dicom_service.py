# backend/app/services/dicom_service.py
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import pydicom
from pydicom.errors import InvalidDicomError
from pathlib import Path

logger = logging.getLogger(__name__)


class DicomMetadata:
    """
    Normalized DICOM metadata container.

    Extracts and normalizes key DICOM tags into a predictable structure.
    Handles missing optional tags gracefully.
    """

    def __init__(self, dataset: pydicom.Dataset):
        self.dataset = dataset

    def _safe_get(self, tag: str, default: Any = None) -> Any:
        """Safely get DICOM tag value with fallback and convert to JSON-serializable Python types."""
        try:
            value = getattr(self.dataset, tag, default)
            # Convert pydicom types to Python natives
            if value is not None:
                # pydicom PersonName objects should be converted via str(), not bytes.decode()
                if hasattr(value, 'family_name') or hasattr(value, 'given_name'):
                    return value
                elif hasattr(value, 'decode') and isinstance(value, (bytes, bytearray)):
                    return value.decode('utf-8', errors='ignore')
                elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes, dict)):
                    # Handle MultiValue, list, tuple, etc.
                    converted = []
                    for item in value:
                        try:
                            if isinstance(item, (int, float, str, bool)):
                                converted.append(item)
                            elif hasattr(item, 'is_integer') and item.is_integer():
                                converted.append(int(item))
                            else:
                                converted.append(float(item) if hasattr(item, '__float__') else str(item))
                        except (ValueError, TypeError):
                            converted.append(str(item))
                    return converted
                elif hasattr(value, 'is_integer') and callable(value.is_integer):
                    return int(value) if value.is_integer() else float(value)
                elif hasattr(value, '__float__') and not isinstance(value, (int, float, str, bool)):
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return str(value)
            return value
        except Exception as e:
            logger.warning(f"Error accessing DICOM tag {tag}: {e}")
            return default

    def _safe_get_date(self, tag: str) -> Optional[str]:
        """
        Safely get date tag and convert to ISO format.

        DICOM dates are YYYYMMDD format.
        """
        value = self._safe_get(tag)
        if value:
            try:
                # Parse DICOM date format YYYYMMDD
                if isinstance(value, str) and len(value) == 8:
                    year = value[0:4]
                    month = value[4:6]
                    day = value[6:8]
                    return f"{year}-{month}-{day}"
            except Exception as e:
                logger.warning(f"Error parsing date {tag}: {e}")
        return None

    def _safe_get_name(self, tag: str) -> Optional[str]:
        """
        Safely get person name tag.

        DICOM person names are in format: LastName^FirstName^MiddleName^Prefix^Suffix
        """
        value = self._safe_get(tag)
        if value:
            try:
                # DICOM PersonName or string format - convert to readable space-separated string
                return str(value).replace('^', ' ').strip()
            except Exception as e:
                logger.warning(f"Error parsing name {tag}: {e}")
        return None

    @property
    def patient_id(self) -> Optional[str]:
        """Patient ID (used as MRN)."""
        return self._safe_get('PatientID')

    @property
    def patient_name(self) -> Optional[str]:
        """Patient name in readable format."""
        return self._safe_get_name('PatientName')

    @property
    def patient_birth_date(self) -> Optional[str]:
        """Patient birth date in ISO format."""
        return self._safe_get_date('PatientBirthDate')

    @property
    def patient_sex(self) -> Optional[str]:
        """Patient sex (M/F/O)."""
        sex = self._safe_get('PatientSex')
        if sex:
            sex = str(sex).upper()
            return sex if sex in ['M', 'F', 'O'] else 'O'
        return None

    @property
    def study_instance_uid(self) -> Optional[str]:
        """Unique study identifier."""
        return self._safe_get('StudyInstanceUID')

    @property
    def series_instance_uid(self) -> Optional[str]:
        """Unique series identifier."""
        return self._safe_get('SeriesInstanceUID')

    @property
    def sop_instance_uid(self) -> Optional[str]:
        """Unique instance (image) identifier."""
        return self._safe_get('SOPInstanceUID')

    @property
    def accession_number(self) -> Optional[str]:
        """Accession number."""
        return self._safe_get('AccessionNumber')

    @property
    def modality(self) -> Optional[str]:
        """Imaging modality (CT, MR, etc)."""
        return self._safe_get('Modality')

    @property
    def study_date(self) -> Optional[str]:
        """Study date in ISO format."""
        return self._safe_get_date('StudyDate')

    @property
    def study_description(self) -> Optional[str]:
        """Study description."""
        return self._safe_get('StudyDescription')

    @property
    def body_part_examined(self) -> Optional[str]:
        """Body part examined."""
        return self._safe_get('BodyPartExamined')

    @property
    def manufacturer(self) -> Optional[str]:
        """Equipment manufacturer."""
        return self._safe_get('Manufacturer')

    @property
    def rows(self) -> Optional[int]:
        """Image rows (height)."""
        return self._safe_get('Rows')

    @property
    def columns(self) -> Optional[int]:
        """Image columns (width)."""
        return self._safe_get('Columns')

    @property
    def pixel_spacing(self) -> Optional[list]:
        """Pixel spacing [row, column] in mm."""
        return self._safe_get('PixelSpacing')

    @property
    def slice_thickness(self) -> Optional[float]:
        """Slice thickness in mm."""
        value = self._safe_get('SliceThickness')
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def window_center(self) -> Optional[float]:
        """Window center for display."""
        value = self._safe_get('WindowCenter')
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def window_width(self) -> Optional[float]:
        """Window width for display."""
        value = self._safe_get('WindowWidth')
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def photometric_interpretation(self) -> Optional[str]:
        """Photometric interpretation."""
        return self._safe_get('PhotometricInterpretation')

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metadata to dictionary for JSON storage.

        Returns only non-None values to keep database lean.
        """
        data = {
            'patient_id': self.patient_id,
            'patient_name': self.patient_name,
            'patient_birth_date': self.patient_birth_date,
            'patient_sex': self.patient_sex,
            'study_instance_uid': self.study_instance_uid,
            'series_instance_uid': self.series_instance_uid,
            'sop_instance_uid': self.sop_instance_uid,
            'accession_number': self.accession_number,
            'modality': self.modality,
            'study_date': self.study_date,
            'study_description': self.study_description,
            'body_part_examined': self.body_part_examined,
            'manufacturer': self.manufacturer,
            'rows': self.rows,
            'columns': self.columns,
            'pixel_spacing': self.pixel_spacing,
            'slice_thickness': self.slice_thickness,
            'window_center': self.window_center,
            'window_width': self.window_width,
            'photometric_interpretation': self.photometric_interpretation,
        }

        # Remove None values
        return {k: v for k, v in data.items() if v is not None}


class DicomService:
    """
    Service for DICOM file validation and metadata extraction.

    Uses pydicom to parse DICOM files and extract normalized metadata.
    Handles corrupt files and missing tags gracefully.
    """

    @staticmethod
    def validate_dicom_file(file_path: Path) -> bool:
        """
        Validate that file can be parsed as DICOM.

        Args:
            file_path: Path to DICOM file

        Returns:
            True if valid DICOM, False otherwise
        """
        try:
            pydicom.dcmread(file_path, stop_before_pixels=True)
            return True
        except InvalidDicomError:
            logger.warning(f"Invalid DICOM file: {file_path}")
            return False
        except Exception as e:
            logger.error(f"Error validating DICOM file {file_path}: {e}")
            return False

    @staticmethod
    def extract_metadata(file_path: Path) -> Optional[DicomMetadata]:
        """
        Extract metadata from DICOM file.

        Args:
            file_path: Path to DICOM file

        Returns:
            DicomMetadata object, or None if parsing fails

        Raises:
            InvalidDicomError: If file is not valid DICOM
            ValueError: If required metadata is missing
        """
        try:
            # Read DICOM file (stop before pixels for efficiency)
            dataset = pydicom.dcmread(file_path, stop_before_pixels=True)

            # Extract metadata
            metadata = DicomMetadata(dataset)

            # Validate required fields
            if not metadata.study_instance_uid:
                raise ValueError("Missing required field: StudyInstanceUID")

            if not metadata.sop_instance_uid:
                raise ValueError("Missing required field: SOPInstanceUID")

            logger.info(
                f"Extracted DICOM metadata: "
                f"StudyInstanceUID={metadata.study_instance_uid}, "
                f"Modality={metadata.modality}"
            )

            return metadata

        except InvalidDicomError as e:
            logger.error(f"Invalid DICOM file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error extracting DICOM metadata from {file_path}: {e}")
            raise

    @staticmethod
    def parse_patient_name(dicom_name: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        """
        Parse DICOM patient name into first and last names.

        Args:
            dicom_name: DICOM patient name (may be None or in various formats)

        Returns:
            Tuple of (first_name, last_name)
        """
        if not dicom_name:
            return None, None

        # DICOM format: LastName^FirstName^MiddleName^Prefix^Suffix
        # Or already parsed by DicomMetadata: "FirstName LastName"

        parts = dicom_name.split()
        if len(parts) >= 2:
            # "FirstName LastName" format
            first_name = parts[0]
            last_name = ' '.join(parts[1:])
            return first_name, last_name
        elif len(parts) == 1:
            # Single name - use as last name
            return None, parts[0]

        return None, None
