from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.local", extra="ignore")

    twitch_client_id: str = ""
    twitch_client_secret: str = ""
    twitch_oauth_token: str = ""
    twitch_channel: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_tts_voice: str = "nova"
    anthropic_api_key: str = ""
    neo4j_uri: str = ""
    neo4j_username: str = "neo4j"
    neo4j_password: str = ""
    redis_url: str = "redis://localhost:6379"
    twitch_rtmp_url: str = "rtmp://live.twitch.tv/app/"
    twitch_stream_key: str = ""
    vtuber_frontend_url: str = "http://localhost:12393"


settings = Settings()
