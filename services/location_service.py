"""
Location Service for Blind Assist.
Formats browser geolocation coordinates, produces accessible voice feedback,
and generates OpenStreetMap navigational links.
"""

from typing import Dict, Any, Optional


class LocationService:
    """Service to process GPS/browser coordinates for visually impaired users."""

    @classmethod
    def generate_osm_url(cls, latitude: float, longitude: float, zoom: int = 16) -> str:
        """Constructs an OpenStreetMap navigation URL for the coordinates."""
        return f"https://www.openstreetmap.org/?mlat={latitude:.5f}&mlon={longitude:.5f}#map={zoom}/{latitude:.5f}/{longitude:.5f}"

    @classmethod
    def format_location_info(
        cls,
        latitude: float,
        longitude: float,
        accuracy: Optional[float] = None,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Creates structured location details with bilingual spoken descriptions.
        """
        acc_text = f"{int(accuracy)} meters" if accuracy is not None else "standard accuracy"
        acc_text_ta = f"{int(accuracy)} மீட்டர்கள்" if accuracy is not None else "இயல்பான துல்லியம்"

        speech_en = (
            f"Your current location has been detected. Latitude is {latitude:.4f}, "
            f"Longitude is {longitude:.4f}, with an accuracy of {acc_text}."
        )
        speech_ta = (
            f"உங்கள் தற்போதைய இருப்பிடம் கண்டறியப்பட்டது. அட்சரேகை {latitude:.4f}, "
            f"தீர்க்கரேகை {longitude:.4f}, துல்லியம் {acc_text_ta}."
        )

        map_url = cls.generate_osm_url(latitude, longitude)

        return {
            "latitude": round(latitude, 5),
            "longitude": round(longitude, 5),
            "accuracy": round(accuracy, 1) if accuracy is not None else None,
            "map_url": map_url,
            "speech": speech_ta if language == 'ta' else speech_en,
            "speech_en": speech_en,
            "speech_ta": speech_ta,
            "location_summary": f"Lat: {latitude:.4f}, Lon: {longitude:.4f} (±{acc_text})"
        }
