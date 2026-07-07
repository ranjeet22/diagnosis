from app.core.config import settings


def test_config_defaults():
    """
    Validates that settings are successfully instantiated and default or environment values are loaded.
    """
    assert settings.APP_NAME == "Diagnōsis"
    assert settings.STORAGE_MAX_FILE_SIZE_MB == 50
    assert isinstance(settings.CORS_ORIGINS, list)
    assert settings.JWT_ALGORITHM == "HS256"
