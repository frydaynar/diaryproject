from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ollama_base_url: str
    ollama_model_name: str = "gemma4:e4b"
    mariadb_user: str
    mariadb_password: str
    mariadb_host: str
    mariadb_database: str
    mariadb_port: int
    graph_image_path: str = "images"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()