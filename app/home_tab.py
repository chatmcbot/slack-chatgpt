DEFAULT_MESSAGE = (
    "Please use overrides to enter your OpenAI key, choose a model and override the prompt."
    " You can <https://platform.openai.com/account/api-keys|your create one here>."
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
