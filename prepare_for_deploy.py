import argparse
import os
from airtable import Airtable

# Define command-line arguments
parser = argparse.ArgumentParser(
    description="Filter Airtable base by name and create .env file"
)
parser.add_argument("--name", type=str, required=True, help="Name to filter by")
args = parser.parse_args()

# Read Airtable API credentials and table information from environment variables
api_key = os.environ["AIRTABLE_API_KEY"]
base_key = os.environ["AIRTABLE_BASE_KEY"]
table_name = os.environ["AIRTABLE_TABLE_NAME"]

# Read OPENAI_API_KEY and SLACK_SCOPES from the environment
openai_api_key = os.environ["OPENAI_API_KEY"]
slack_scopes = os.environ["SLACK_SCOPES"]

# Initialize Airtable client
airtable = Airtable(base_key, table_name, api_key=api_key)

# Filter the table to the row where the value of the column ENV_SLACK_BOT_NAME matches the provided keyword
records = airtable.search("ENV_SLACK_BOT_NAME", args.name)

# Create a shell script file named .env.{name}
with open(f".env.{args.name}", "w") as env_file:
    # Write the OPENAI_API_KEY and SLACK_SCOPES to the file
    env_file.write(f'export OPENAI_API_KEY="{openai_api_key}"\n')
    env_file.write(f'export SLACK_SCOPES="{slack_scopes}"\n')

    # Iterate over the filtered records
    for record in records:
        # Extract all columns prefixed with "ENV_" and write the export statements to the file
        for field, value in record["fields"].items():
            if field.startswith("ENV_"):
                # Strip out the ENV_ prefix from the key name
                key_name = field.replace("ENV_", "")
                env_file.write(f'export {key_name}="{value}"\n')

# If no records were found, print a message
if not records:
    print(f"No records found with ENV_SLACK_BOT_NAME = {args.name}")
else:
    print(
        f"Created .env.{args.name} file. For deploy run:\nsource .env.{args.name} && ./deploy.sh {args.name}"
    )
