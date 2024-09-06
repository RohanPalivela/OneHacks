
def gemini_vision(contents_image, model):

    responses = model.generate_content(
        contents_image,
        stream=True)

    response_text = ""
    for response in responses:
        response_text += response.text
    return response_text

def extract_curly_braces(text):
    first_index = text.find('{')  # Find the first occurrence of '{'
    last_index = text.rfind('}')  # Find the last occurrence of '}'
    
    if first_index != -1 and last_index != -1 and first_index < last_index:
        return text[first_index:last_index+1]  # Include both braces
    else:
        return None
