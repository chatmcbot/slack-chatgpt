DEFAULT_MESSAGE = (
    "This bot offers limited use of GPT-4 by default."
    "If you run out, you can purchase more tokens or use <https://platform.openai.com/account/api-keys|your own OpenAI key> and models."
)

DEFAULT_CONFIGURE_LABEL = "Overrides"


def build_home_tab(message: str, configure_label: str) -> dict:
    return {
        "type": "home",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message,
                },
                "accessory": {
                    "action_id": "configure",
                    "type": "button",
                    "text": {"type": "plain_text", "text": configure_label},
                    "style": "primary",
                    "value": "api_key",
                },
            }
        ],
    }
