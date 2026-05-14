messages = [
    {"user_id": "u1", "channel": "email",    "message": "Hello, I want info about grants for education."},
    {"user_id": "u2", "channel": "whatsapp", "message": " "},
    {"user_id": "",   "channel": "email",    "message": "What is the deadline?"},
    {"user_id": "u3", "channel": "email",    "message": "Please send the report again."},
    {"user_id": "u1", "channel": "whatsapp", "message": " Can you help me find funding? "},
    {"user_id": "u4", "channel": "telegram", "message": "Good morning!"},
    {"user_id": "u5", "channel": "email",    "message": "Can you send me the scholarship document?"},
    {"user_id": "u6", "channel": "whatsapp", "message": ""},
]

def clean_and_classify(messages):
    result = []

    for msg in messages:
        user_id = msg["user_id"].strip()
        cleaned_message = msg["message"].strip()

        if not user_id or not cleaned_message:
            continue

        text = cleaned_message.lower()

        if any(kw in text for kw in ["grant", "funding", "deadline", "scholarship"]):
            category = "grant_search"
        elif any(kw in text for kw in ["report", "file", "send again", "document"]):
            category = "report_request"
        elif any(kw in text for kw in ["how", "what", "can you", "where", "why"]):
            category = "general_question"
        else:
            category = "unknown"

        result.append({
            "user_id": user_id,
            "channel": msg["channel"],
            "message": cleaned_message,
            "category": category,
        })

    return result

output = clean_and_classify(messages)
for item in output:
    print(item)

# Conflict rule:
# If a message matches multiple categories, I prioritize grant_search first
# because grant-related intent is the most specific and important for this task.
    
    # Output:
# {'user_id': 'u1', 'channel': 'email', 'message': 'Hello, I want info about grants for education.', 'category': 'grant_search'}
# {'user_id': 'u3', 'channel': 'email', 'message': 'Please send the report again.', 'category': 'report_request'}
# {'user_id': 'u1', 'channel': 'whatsapp', 'message': 'Can you help me find funding?', 'category': 'grant_search'}
# {'user_id': 'u4', 'channel': 'telegram', 'message': 'Good morning!', 'category': 'unknown'}
# {'user_id': 'u5', 'channel': 'email', 'message': 'Can you send me the scholarship document?', 'category': 'grant_search'}
