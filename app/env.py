import os

DEFAULT_SYSTEM_TEXT = """
You are a bot in a slack chat room. You can receive messages from multiple people.
Format bold text *like this*, italic text _like this_ and strikethrough text ~like this~.
Slack user IDs match the regex `<@U.*?>`.
Your Slack user ID is <@{bot_user_id}>.
"""

# OPENAI_SYSTEM_TEXT is for dev, DEFAULT_SYSTEM_TEXT is prod, SLACK_BASE_PROMPT is for bot specific in prod
SYSTEM_TEXT = os.environ.get("SLACK_BASE_PROMPT", "") + os.environ.get("OPENAI_SYSTEM_TEXT", DEFAULT_SYSTEM_TEXT)

DEFAULT_OPENAI_TIMEOUT_SECONDS = 60
OPENAI_TIMEOUT_SECONDS = int(
    os.environ.get("OPENAI_TIMEOUT_SECONDS", DEFAULT_OPENAI_TIMEOUT_SECONDS)
)

ALLOW_FREE_OPENAI_API_KEY = os.environ.get("ALLOW_FREE_OPENAI_API_KEY", "false") == "true"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "") if ALLOW_FREE_OPENAI_API_KEY else ""
DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
CONFIG_ENABLE_PROMPT_OVERRIDE = os.environ.get("CONFIG_ENABLE_PROMPT_OVERRIDE", "true") == "true"
CONFIG_ENABLE_OPENAI_MODEL = os.environ.get("CONFIG_ENABLE_OPENAI_MODEL", "true") == "true"
CONFIG_ENABLE_OPENAI_KEY = os.environ.get("CONFIG_ENABLE_OPENAI_MODEL", "true") == "true"

MODEL_NAME_MAPPING = {
    "gpt-3.5-turbo": "GPT-3.5 Turbo",
    "gpt-4": "GPT-4"
}

USE_SLACK_LANGUAGE = os.environ.get("USE_SLACK_LANGUAGE", "true") == "true"

SLACK_APP_LOG_LEVEL = os.environ.get("SLACK_APP_LOG_LEVEL", "DEBUG")

TRANSLATE_MARKDOWN = os.environ.get("TRANSLATE_MARKDOWN", "false") == "true"
