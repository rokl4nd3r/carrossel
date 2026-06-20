from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Carrossel MVP"
    output_dir: str = "output"
    public_base_url: str = ""

    sd_base_url: str = "http://127.0.0.1:7860"
    sd_steps: int = 24
    sd_cfg_scale: float = 7.0
    sd_width: int = 1080
    sd_height: int = 1350
    sd_sampler: str = "DPM++ 2M Karras"
    sd_negative_prompt: str = (
        "low quality, blurry, deformed, bad anatomy, watermark, logo, text, "
        "letters, words, typography, jpeg artifacts, cropped, frame, border"
    )

    llm_provider: str = "fallback"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3.5:9b"

    openai_compatible_base_url: str = "http://127.0.0.1:1234/v1"
    openai_compatible_api_key: str = "change-me"
    openai_compatible_model: str = "qwen/qwen3.5-9b"

    default_style: str = (
        "editorial premium, realistic background, cinematic light, clean composition, "
        "high detail, social media campaign background, no text"
    )
    default_brand_name: str = "Carrossel"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
