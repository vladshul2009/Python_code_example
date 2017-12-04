import json

# rewritable properties for response:
# headers, reason, text, body, content_type

async def handle_500(request, response):
    response.content_type = 'application/json'
    data = {
        "data": {},
        "message": "",
        "actions": ["server_side_unhandled_error."]
    }
    response.text = json.dumps(data, ensure_ascii=False)
    return response

async def handle_404(request, response):
    response.content_type = 'application/json'
    data = {
        "data": {},
        "message": "",
        "actions": ["method_not_found"]
    }
    response.text = json.dumps(data, ensure_ascii=False)
    return response
