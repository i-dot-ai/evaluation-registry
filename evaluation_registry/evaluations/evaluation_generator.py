import json

from django.conf import settings
from openai import OpenAI

evaluation_initial_data_schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "title of the evaluation"},
        "brief_description": {"type": "string", "description": "300 word description of the evaluation"},
        "lead_department": {
            "type": "string",
            "description": "government department associated with this evaluation",
        },
        "status": {"enum": ["planned", "ongoing", "complete"], "description": "current status of the evaluation"},
        "evaluation_design_types": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "design type of this evaluation",
            },
        },
    },
    "required": ["title", "brief_description", "lead_department", "status", "evaluation_design_types"],
}


def extract_structured_text(plain_text: str) -> dict:
    client = OpenAI(api_key=settings.OPENAI_KEY)

    prompt = {
        "name": "extract_evaluation_info",
        "description": "Extract evaluation information from the body of the input text",
        "type": "object",
        "parameters": evaluation_initial_data_schema,
    }

    response = client.chat.completions.create(  # type: ignore
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": " ".join(plain_text.split(" ")[:2500])}],
        tools=[{"type": "function", "function": prompt}],
        tool_choice="auto",
    )

    return json.loads(response.choices[0].message.tool_calls[0].function.arguments)
