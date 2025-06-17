# Importing required packages
import os
from dotenv import load_dotenv
from vertexai import init 
from vertexai.preview.generative_models import GenerativeModel, SafetySetting, HarmCategory
from google.cloud import bigquery
from system_prompts import system_instruction_input_handler, system_instruction_output_handler, system_instrution_alaska_chatbot

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
DATASET = os.getenv("DATASET")
TABLE_EMBEDDED = os.getenv("TABLE_EMBEDDED")

# Define model constants
MODEL_NAME = "gemini-2.0-flash"
EMBEDDING_MODEL_NAME = "text-embedding-005"

# Initialize Vertex AI and BigQuery clients
init(project=PROJECT_ID, location=LOCATION)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key_gcloud.json"
bq_client = bigquery.Client(project=PROJECT_ID)


# Define safety settings
safety_settings = [
    SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=1),
    SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=1),
    SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=1),
    SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=1),
]

def user_request_check(prompt: str) -> str:
    """
    To verify if the user's input is safe to process.
    Returns 'not safe' if the content is inappropriate.
    """
    model = GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_instruction_input_handler
    )
    chat = model.start_chat(response_validation=False)
    return chat.send_message(prompt).text.strip().lower()

def llm_response_check(prompt: str) -> str:
    """
    Validates the generated LLM response for safety before returning to the user.
    Returns 'not safe' if the response content is inappropriate.
    """
    model = GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_instruction_output_handler
    )
    chat = model.start_chat(response_validation=False)
    return chat.send_message(prompt).text.strip().lower()

def query_vector_search_data(user_input: str):
    """
    Performs vector similarity search on embedded data using BigQuery.
    Stores top 5 matching records in a alaska_dept_result table.
    """
    search_sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET}.alaska_dept_result` AS
    SELECT
        query.query,
        base.content
    FROM
        VECTOR_SEARCH(
            TABLE `{DATASET}.{TABLE_EMBEDDED}`,
            'ml_generate_embedding_result',
            (
                SELECT
                    ml_generate_embedding_result,
                    content AS query
                FROM
                    ML.GENERATE_EMBEDDING(
                        MODEL `{DATASET}.Embeddings`,
                        (SELECT '{user_input}' AS content)
                    )
            ),
            top_k => 5,
            options => '{{"fraction_lists_to_search": 1.0}}'
        );
    """
    bq_client.query(search_sql).result()

def get_response_from_gemini() -> str:
    """
    Retrieves relevant context from BigQuery, appends it to system prompt,
    and uses Gemini to generate a safe, informed response.
    """
    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET}.alaska_dept_result`"
    result_df = bq_client.query(query).to_dataframe()
    context = "\n\n".join(
        result_df.apply(lambda row: f"Q: {row['query']}\nA: {row['content']}", axis=1)
    )
    prompt = system_instrution_alaska_chatbot + context
    model = GenerativeModel(MODEL_NAME)
    response = model.generate_content(
                    prompt,
                    safety_settings=safety_settings
                )

    return response.text.strip()

def process_user_input(user_input: str) -> str:
    """
    Main handler function for user input:
    - Validates the input for safety
    - Runs vector similarity search for relevant FAQ content
    - Generates response via Gemini
    - Validates the generated response
    - Returns the safe final response or a warning
    """
    request_check =user_request_check(user_input).strip().lower()
    if request_check == "not safe":
        return "Sorry, the request contains unsafe content."

    query_vector_search_data(user_input)
    llm_response = get_response_from_gemini()
    response_check = llm_response_check(llm_response).strip().lower()
    if response_check == "not safe":
        return "Sorry, the response contains unsafe content."

    return llm_response
