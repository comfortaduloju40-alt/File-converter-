"""
Central place for environment-driven configuration. Import `settings`
from here everywhere else instead of calling os.environ directly.
"""

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    BOT_TOKEN: str = field(default_factory=lambda: os.environ["BOT_TOKEN"])
    WEBHOOK_URL: str = field(default_factory=lambda: os.environ.get("WEBHOOK_URL", ""))
    PORT: int = field(default_factory=lambda: int(os.environ.get("PORT", "8080")))
    MAX_FILE_SIZE_MB: int = field(default_factory=lambda: int(os.environ.get("MAX_FILE_SIZE_MB", "20")))
    LOG_LEVEL: str = field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))
    TMP_DIR: str = field(default_factory=lambda: os.environ.get("TMP_DIR", "/tmp/converter"))


settings = Settings()
