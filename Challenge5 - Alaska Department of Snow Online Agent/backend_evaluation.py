import pandas as pd
from vertexai.preview.evaluation import EvalTask, MetricPromptTemplateExamples
import datetime

# Timestamp
run_ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

# Test dataset for evaluation
test_dataset = [
    {
        "query": "Does ADS have a smartphone app?",
        "response": "Yes. The ADS “SnowLine” app offers real-time plow tracking, road conditions, and the ability to submit service requests directly from your phone."
    },
    {
        "query": "What concerns does the CFO have about ADS operations?",
        "response": "The CFO is primarily concerned about controlling operational costs, especially regarding cloud-based technology solutions for data management."
    },
    {
        "query": "How many people does ADS serve?",
        "response": "ADS serves approximately 750,000 people across Alaska’s widely distributed communities and remote areas."
    },
    {
        "query": "Does ADS use cloud services for its data?",
        "response": "ADS is exploring cloud options for real-time data sharing, but some administrators have reservations about security, compliance, and ongoing costs."
    },
    {
        "query": "What kind of vehicles does ADS operate?",
        "response": "ADS operates a fleet of snowplows, graders, and specialized “snow blowers” designed for extreme weather. Some remote regions also use tracked vehicles."
    },
    {
        "query": "How do I volunteer to help with community snow events?",
        "response": "Check your local ADS district’s website or bulletin board. Some regions host volunteer programs for sidewalk clearing and elderly assistance."
    },
    {
        "query": "What is ADS’s stance on snow tires and chains?",
        "response": "ADS recommends snow tires or chains in harsh conditions. However, regulations vary by municipality. Check local ordinances for mandatory use periods."
    },
    {
        "query": "How do I request a refund if a private contractor damaged my property?",
        "response": "ADS is not responsible for private contractor damages. Contact the contractor directly or your local municipality for guidance on claims."
    },
    {
        "query": "Does ADS offer financial assistance for snow removal equipment?",
        "response": "ADS does not provide direct financial assistance. However, some state grants may be available to local governments for purchasing snow removal equipment."
    },
    {
        "query": "Are ADS plows available for hire for private property?",
        "response": "No. ADS resources are dedicated to public roads and infrastructure. Private snow removal must be arranged through local contractors."
    }
]


# Create evaluation DataFrame
eval_dataset = pd.DataFrame([
    {
        "instruction": (
            "You are a helpful assistant for the Alaska Department of Snow.\n"
            "Answer the user's query clearly and accurately based on official ADS knowledge."
        ),
        "context": item["query"],
        "response": item["response"]
    }
    for item in test_dataset
])

#Prompt Template
prompt_template = (
    "Instruction: {instruction}\n"
    "User: {context}\n"
    "Bot: {response}"
)

# Define the evaluation task
eval_task = EvalTask(
    dataset=eval_dataset,
    metrics=[
        MetricPromptTemplateExamples.Pointwise.INSTRUCTION_FOLLOWING,
        MetricPromptTemplateExamples.Pointwise.GROUNDEDNESS,
        MetricPromptTemplateExamples.Pointwise.VERBOSITY,
        MetricPromptTemplateExamples.Pointwise.SUMMARIZATION_QUALITY
    ],
    experiment=f"alaska-snow-chatbot-eval-{run_ts}"
)

# Run evaluation task
result = eval_task.evaluate(
    prompt_template=prompt_template,
    experiment_run_name=f"alaska-snow-chatbot-eval-{run_ts}"
)
