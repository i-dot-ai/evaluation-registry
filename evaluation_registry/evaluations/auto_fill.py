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
            "visibility": {"enum": ["draft", "civil_service", "public"], "description": "intended audience"},
        },
    },
    "required": ["title", "brief_description", "lead_department", "status", "evaluation_design_types"],
}
