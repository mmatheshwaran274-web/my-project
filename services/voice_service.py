"""
Voice Service for Blind Assist.
Parses natural language commands spoken by the user and maps them to system actions,
navigation routes, and accessible bilingual feedback (English & Tamil).
"""

import re


class VoiceService:
    """Service to parse voice commands and return structured actions and spoken responses."""

    # Command map with regex patterns, action type, target url, and localized responses
    COMMAND_DEFINITIONS = [
        {
            "patterns": [r"\b(open\s+)?dashboard\b", r"\bhome\b", r"\bmain\s+menu\b", r"\bடாஷ்போர்டு\b", r"\bமுகப்பு\b"],
            "action": "navigate",
            "url": "/dashboard",
            "speech_en": "Opening dashboard.",
            "speech_ta": "டாஷ்போர்டைத் திறக்கிறது.",
            "label": "Dashboard"
        },
        {
            "patterns": [r"\bread\s+text\b", r"\bopen\s+text\s+reader\b", r"\btext\s+reader\b", r"\bocr\b", r"\bscan\s+text\b", r"\bஉரையை\s+படிக்க\b"],
            "action": "navigate",
            "url": "/ocr",
            "speech_en": "Opening text reader.",
            "speech_ta": "உரையை படிக்க திறக்கிறது.",
            "label": "Text Reader"
        },
        {
            "patterns": [r"\bdetect\s+object(s)?\b", r"\bobject\s+detection\b", r"\bvision\b", r"\bwhat\s+do\s+you\s+see\b", r"\bidentify\s+object(s)?\b", r"\bபொருள்\s+கண்டறி\b"],
            "action": "navigate",
            "url": "/vision",
            "speech_en": "Opening object detection.",
            "speech_ta": "பொருள் கண்டறிதலைத் திறக்கிறது.",
            "label": "Object Detection"
        },
        {
            "patterns": [r"\bmy\s+location\b", r"\bwhere\s+am\s+i\b", r"\bget\s+location\b", r"\bcurrent\s+location\b", r"\bஇருப்பிடம்\b"],
            "action": "navigate",
            "url": "/location",
            "speech_en": "Getting your location.",
            "speech_ta": "உங்கள் இருப்பிடத்தை பெறுகிறது.",
            "label": "Location Assistance"
        },
        {
            "patterns": [r"\bemergency\b", r"\bhelp\s+me\b", r"\balert\b", r"\bpanic\b", r"\bcall\s+help\b", r"\bஅவசர\s+உதவி\b"],
            "action": "navigate",
            "url": "/emergency",
            "speech_en": "Opening emergency assistance.",
            "speech_ta": "அவசர உதவி பக்கத்தைத் திறக்கிறது.",
            "label": "Emergency Assistance"
        },
        {
            "patterns": [r"\b(open\s+)?profile\b", r"\bmy\s+profile\b", r"\buser\s+profile\b", r"\bசுயவிவரம்\b"],
            "action": "navigate",
            "url": "/profile",
            "speech_en": "Opening user profile.",
            "speech_ta": "பயனர் சுயவிவரத்தைத் திறக்கிறது.",
            "label": "Profile"
        },
        {
            "patterns": [r"\b(open\s+)?settings\b", r"\baccessibility\s+settings\b", r"\bpreferences\b", r"\bஅமைப்புகள்\b"],
            "action": "navigate",
            "url": "/settings",
            "speech_en": "Opening accessibility settings.",
            "speech_ta": "அணுகல்தன்மை அமைப்புகளைத் திறக்கிறது.",
            "label": "Settings"
        },
        {
            "patterns": [r"\b(show\s+)?history\b", r"\bactivity\s+history\b", r"\brecent\s+activit(y|ies)\b", r"\bவரலாறு\b"],
            "action": "navigate",
            "url": "/history",
            "speech_en": "Opening activity history.",
            "speech_ta": "செயல்பாட்டு வரலாற்றைத் திறக்கிறது.",
            "label": "Activity History"
        },
        {
            "patterns": [r"\bhelp\b", r"\bcommands\b", r"\bwhat\s+can\s+i\s+say\b", r"\bஉதவி\b"],
            "action": "info",
            "url": None,
            "speech_en": "Available commands: Read text, Detect objects, My location, Emergency, Open settings, Open profile, and Show history.",
            "speech_ta": "கட்டளைகள்: உரையை படிக்க, பொருள் கண்டறி, இருப்பிடம், அவசர உதவி, அமைப்புகள், சுயவிவரம், மற்றும் வரலாறு.",
            "label": "Help Commands"
        }
    ]

    @classmethod
    def process_command(cls, command_text: str, language: str = 'en') -> dict:
        """
        Interprets spoken command string and returns action payload.
        """
        if not command_text or not isinstance(command_text, str):
            return {
                "success": False,
                "command": "",
                "action": "unknown",
                "speech": "I did not hear any command. Please try again." if language != 'ta' else "எந்த கட்டளையும் கேட்கவில்லை. மீண்டும் முயற்சிக்கவும்.",
                "url": None
            }

        cleaned = command_text.strip().lower()

        for cmd in cls.COMMAND_DEFINITIONS:
            for pattern in cmd["patterns"]:
                if re.search(pattern, cleaned, re.IGNORECASE):
                    speech = cmd["speech_ta"] if language == 'ta' else cmd["speech_en"]
                    return {
                        "success": True,
                        "command": command_text,
                        "action": cmd["action"],
                        "url": cmd["url"],
                        "label": cmd["label"],
                        "speech": speech
                    }

        # Fallback for unrecognized command
        fallback_speech = (
            f"I did not recognize the command '{command_text}'. Say 'Help' to hear available commands."
            if language != 'ta'
            else f"'{command_text}' என்ற கட்டளை புரியவில்லை. 'உதவி' என்று கூறி கட்டளைகளைக் கேட்கவும்."
        )

        return {
            "success": False,
            "command": command_text,
            "action": "unrecognized",
            "url": None,
            "speech": fallback_speech
        }
