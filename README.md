<!-- PROJECT LOGO -->
<p align="center">
  

  <h3 align="center">Chat McBot</h3>

  <p align="center">
    An open-source ChatGPT Bot for Slack
    <br />
    <br />
    <a href="https://get.mcbot.chat"><img alt="Add to Slack" height="30" width="105" src="https://platform.slack-edge.com/img/add_to_slack.png"  /></a>
    <br />
    <br />
    <a href="https://mcbot.chat">Website</a>
  </p>
</p>

<img src="https://www.mcbot.chat/assets/example-slack.png" alt="Logo">


A fully customizable ChatGPT in Slack bot. Bring your own OpenAI key, configure the system prompt and choose between GPT-4 and 3.5-turbo.



## Development


To run this app on your local machine, you only need to follow these simple steps:

* Create a new Slack app using the manifest-dev.yml file
* Install the app into your Slack workspace
* Retrieve your OpenAI API key at https://platform.openai.com/account/api-keys
* Start the app

```bash
# Create an app-level token with connections:write scope
export SLACK_APP_TOKEN=xapp-1-...
# Install the app into your workspace to grab this token
export SLACK_BOT_TOKEN=xoxb-...
# Visit https://platform.openai.com/account/api-keys for this token
export OPENAI_API_KEY=sk-...

# Optional: gpt-3.5-turbo and gpt-4 are currently supported (default: gpt-3.5-turbo)
export OPENAI_MODEL=gpt-4
# Optional: You can adjust the timeout seconds for OpenAI calls (default: 30)
export OPENAI_TIMEOUT_SECONDS=60
# Optional: You can include priming instructions for ChatGPT to fine tune the bot purpose
export OPENAI_SYSTEM_TEXT="You proofread text. When you receive a message, you will check
for mistakes and make suggestion to improve the language of the given text"
# Optional: When the string is "true", this app translates ChatGPT prompts into a user's preferred language (default: true)
export USE_SLACK_LANGUAGE=true
# Optional: Adjust the app's logging level (default: DEBUG)
export SLACK_APP_LOG_LEVEL=INFO
# Optional: When the string is "true", translate between OpenAI markdown and Slack mrkdwn format (default: false)
export TRANSLATE_MARKDOWN=true

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Credits

Based on [seratch/ChatGPT-in-Slack](/https://github.com/seratch/ChatGPT-in-Slack)

