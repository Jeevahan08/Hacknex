from fastapi import APIRouter

router = APIRouter()

SUPPORTED_LANGUAGES = [
    {
        "code": "en-IN",
        "name": "English",
        "native_name": "English (India)",
        "script": "Latin",
        "direction": "ltr",
        "enabled": True,
        "is_source": True,
        "is_target": True
    },
    {
        "code": "ta-IN",
        "name": "Tamil",
        "native_name": "தமிழ்",
        "script": "Tamil",
        "direction": "ltr",
        "enabled": True,
        "is_source": True,
        "is_target": True
    },
    {
        "code": "hi-IN",
        "name": "Hindi",
        "native_name": "हिन्दी",
        "script": "Devanagari",
        "direction": "ltr",
        "enabled": True,
        "is_source": True,
        "is_target": True
    },
    {
        "code": "ml-IN",
        "name": "Malayalam",
        "native_name": "മലയാളം",
        "script": "Malayalam",
        "direction": "ltr",
        "enabled": True,
        "is_source": True,
        "is_target": True
    },
    {
        "code": "te-IN",
        "name": "Telugu",
        "native_name": "తెలుగు",
        "script": "Telugu",
        "direction": "ltr",
        "enabled": True,
        "is_source": True,
        "is_target": True
    },
    {
        "code": "kn-IN",
        "name": "Kannada",
        "native_name": "ಕನ್ನಡ",
        "script": "Kannada",
        "direction": "ltr",
        "enabled": True,
        "is_source": True,
        "is_target": True
    },
    {
        "code": "mr-IN",
        "name": "Marathi",
        "native_name": "मराठी",
        "script": "Devanagari",
        "direction": "ltr",
        "enabled": True,
        "is_source": True,
        "is_target": True
    }
]

@router.get("/languages")
async def get_languages():
    return {
        "languages": SUPPORTED_LANGUAGES,
        "default_source": "en-IN",
        "default_targets": ["ta-IN", "hi-IN", "ml-IN", "mr-IN"]
    }
