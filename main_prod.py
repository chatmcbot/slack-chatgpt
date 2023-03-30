# Unzip the dependencies managed by serverless-python-requirements
try:
    import unzip_requirements  # type:ignore
except ImportError:
    pass

#
# Imports
#

import json
import logging
import os
import openai

from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler
from slack_bolt import App, Ack, BoltContext

from app.bolt_listeners import register_listeners, before_authorize
from app.env import SYSTEM_TEXT, MODEL_NAME_MAPPING, USE_SLACK_LANGUAGE, SLACK_APP_LOG_LEVEL, DEFAULT_OPENAI_MODEL, CONFIG_ENABLE_PROMPT_OVERRIDE
from app.home_tab import build_home_tab, DEFAULT_MESSAGE, DEFAULT_CONFIGURE_LABEL
from app.i18n import translate

#
# Product deployment (AWS Lambda)
#


import boto3
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from slack_bolt.adapter.aws_lambda.lambda_s3_oauth_flow import LambdaS3OAuthFlow

SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=SLACK_APP_LOG_LEVEL)

s3_client = boto3.client("s3")
openai_bucket_name = os.environ["OPENAI_S3_BUCKET_NAME"]

client_template = WebClient()
client_template.retry_handlers.append(RateLimitErrorRetryHandler(max_retry_count=2))


def register_revocation_handlers(app: App):
    # Handle uninstall events and token revocations
    @app.event("tokens_revoked")
    def handle_tokens_revoked_events(
        event: dict,
        context: BoltContext,
        logger: logging.Logger,
    ):
        user_ids = event.get("tokens", {}).get("oauth", [])
        if len(user_ids) > 0:
            for user_id in user_ids:
                app.installation_store.delete_installation(
                    enterprise_id=context.enterprise_id,
                    team_id=context.team_id,
                    user_id=user_id,
                )
        bots = event.get("tokens", {}).get("bot", [])
        if len(bots) > 0:
            app.installation_store.delete_bot(
                enterprise_id=context.enterprise_id,
                team_id=context.team_id,
            )
            try:
                s3_client.delete_object(Bucket=openai_bucket_name, Key=context.team_id)
            except Exception as e:
                logger.error(
                    f"Failed to delete an OpenAI auth key: (team_id: {context.team_id}, error: {e})"
                )

    @app.event("app_uninstalled")
    def handle_app_uninstalled_events(
        context: BoltContext,
        logger: logging.Logger,
    ):
        app.installation_store.delete_all(
            enterprise_id=context.enterprise_id,
            team_id=context.team_id,
        )
        try:
            s3_client.delete_object(Bucket=openai_bucket_name, Key=context.team_id)
        except Exception as e:
            logger.error(
                f"Failed to delete an OpenAI auth key: (team_id: {context.team_id}, error: {e})"
            )


def handler(event, context_):
    app = App(
        process_before_response=True,
        before_authorize=before_authorize,
        oauth_flow=LambdaS3OAuthFlow(),
        client=client_template,
    )
    app.oauth_flow.settings.install_page_rendering_enabled = False
    register_listeners(app)
    register_revocation_handlers(app)

    if USE_SLACK_LANGUAGE is True:

        @app.middleware
        def set_locale(
            context: BoltContext,
            client: WebClient,
            logger: logging.Logger,
            next_,
        ):
            bot_scopes = context.authorize_result.bot_scopes
            if bot_scopes is not None and "users:read" in bot_scopes:
                user_id = context.actor_user_id or context.user_id
                try:
                    user_info = client.users_info(user=user_id, include_locale=True)
                    context["locale"] = user_info.get("user", {}).get("locale")
                except SlackApiError as e:
                    logger.debug(f"Failed to fetch user info due to {e}")
                    pass
            next_()

    @app.middleware
    def set_s3_openai_api_key(context: BoltContext, next_):
        try:
            s3_response = s3_client.get_object(
                Bucket=openai_bucket_name, Key=context.team_id
            )
            config_str: str = s3_response["Body"].read().decode("utf-8")
            config = json.loads(config_str)
            context["OPENAI_API_KEY"] = config.get("api_key")
            context["OPENAI_MODEL"] = config.get("model")
            context["SYSTEM_PROMPT"] = config.get("system_prompt")  # Added this line
        except:  # noqa: E722
            context["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
            context["OPENAI_MODEL"] = DEFAULT_OPENAI_MODEL
            context["SYSTEM_PROMPT"] = SYSTEM_TEXT
        next_()


    @app.event("app_home_opened")
    def render_home_tab(client: WebClient, context: BoltContext):
        message = DEFAULT_MESSAGE
        configure_label = DEFAULT_CONFIGURE_LABEL
        try:
            s3_client.get_object(Bucket=openai_bucket_name, Key=context.team_id)
            message = "This app is ready to use in this workspace :raised_hands:"
        except:  # noqa: E722
            pass

        openai_api_key = context.get("OPENAI_API_KEY")
        if openai_api_key is not None:
            message = translate(
                openai_api_key=openai_api_key, context=context, text=message
            )
            configure_label = translate(
                openai_api_key=openai_api_key,
                context=context,
                text=DEFAULT_CONFIGURE_LABEL,
            )

        client.views_publish(
            user_id=context.user_id,
            view=build_home_tab(message, configure_label),
        )

    @app.action("configure")
    def handle_some_action(ack, body: dict, client: WebClient, context: BoltContext):
        ack()
        already_set_api_key = context.get("OPENAI_API_KEY")
        already_set_model = context.get("OPENAI_MODEL")
        already_set_system_prompt = context.get("SYSTEM_PROMPT")
        api_key_text = "Save your OpenAI API key:"
        submit = "Submit"
        cancel = "Cancel"
        if already_set_api_key is not None:
            api_key_text = translate(
                openai_api_key=already_set_api_key, context=context, text=api_key_text
            )
            submit = translate(
                openai_api_key=already_set_api_key, context=context, text=submit
            )
            cancel = translate(
                openai_api_key=already_set_api_key, context=context, text=cancel
            )

        # Initialize an empty list for the blocks
        blocks = []

        # Append the "api_key" input block
        blocks.append({
            "type": "input",
            "block_id": "api_key",
            "label": {"type": "plain_text", "text": api_key_text},
            "element": {
                "type": "plain_text_input",
                "action_id": "input",
                "initial_value": already_set_api_key or "",  # Added this line
            },
        })

        # Append the "model" input block
        blocks.append({
            "type": "input",
            "block_id": "model",
            "label": {"type": "plain_text", "text": "OpenAI Model"},
            "element": {
                "type": "static_select",
                "action_id": "input",
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": MODEL_NAME_MAPPING["gpt-3.5-turbo"],
                        },
                        "value": "gpt-3.5-turbo",
                    },
                    {
                        "text": {"type": "plain_text", "text": MODEL_NAME_MAPPING["gpt-4"]},
                        "value": "gpt-4",
                    },
                ],
                "initial_option": {
                    "text": {
                        "type": "plain_text",
                        "text": MODEL_NAME_MAPPING[already_set_model] if already_set_model else MODEL_NAME_MAPPING["gpt-3.5-turbo"],
                    },
                    "value": already_set_model or "gpt-3.5-turbo",
                },
            },
        })

        if CONFIG_ENABLE_PROMPT_OVERRIDE:
            blocks.append({
                "type": "input",
                "block_id": "system_prompt",
                "label": {"type": "plain_text", "text": "Override System Prompt"},
                "element": {"type": "plain_text_input", "action_id": "input", "initial_value": already_set_system_prompt or SYSTEM_TEXT},
            })

        # Use the dynamically created list of blocks in the client.views_open() call
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "configure",
                "title": {"type": "plain_text", "text": "Configure"},
                "submit": {"type": "plain_text", "text": submit},
                "close": {"type": "plain_text", "text": cancel},
                "blocks": blocks,
            },
        )



    def validate_api_key_registration(ack: Ack, view: dict, context: BoltContext):
        already_set_api_key = context.get("OPENAI_API_KEY")

        inputs = view["state"]["values"]
        api_key = inputs["api_key"]["input"]["value"]
        model = inputs["model"]["input"]["selected_option"]["value"]
        try:
            # Verify if the API key is valid
            openai.Model.retrieve(api_key=api_key, id="gpt-3.5-turbo")
            try:
                # Verify if the given model works with the API key
                openai.Model.retrieve(api_key=api_key, id=model)
            except Exception:
                text = "This model is not yet available for this API key"
                if already_set_api_key is not None:
                    text = translate(
                        openai_api_key=already_set_api_key, context=context, text=text
                    )
                ack(
                    response_action="errors",
                    errors={"model": text},
                )
                return
            ack()
        except Exception:
            text = "This API key seems to be invalid"
            if already_set_api_key is not None:
                text = translate(
                    openai_api_key=already_set_api_key, context=context, text=text
                )
            ack(
                response_action="errors",
                errors={"api_key": text},
            )

    def save_api_key_registration(
        view: dict,
        logger: logging.Logger,
        context: BoltContext,
    ):
        inputs = view["state"]["values"]
        api_key = inputs["api_key"]["input"]["value"]
        model = inputs["model"]["input"]["selected_option"]["value"]
        system_prompt = inputs["system_prompt"]["input"]["value"]  # Added this line

        try:
            openai.Model.retrieve(api_key=api_key, id=model)
            s3_client.put_object(
                Bucket=openai_bucket_name,
                Key=context.team_id,
                Body=json.dumps({"api_key": api_key, "model": model, "system_prompt": system_prompt}),  # Updated this line
            )
        except Exception as e:
            logger.exception(e)


    app.view("configure")(
        ack=validate_api_key_registration,
        lazy=[save_api_key_registration],
    )

    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context_)
