import openai

from scrt import OPENAI_KEY

def ask_gpt(prompt: str, role :str="You are a helpful assistant.", temperature=0.2):
    openai.api_key = OPENAI_KEY
    response_text = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": role},
            {
                "role": "user",
                "content": prompt,
                "temperature": temperature
            }
        ]
    )
    print(response_text.choices[0].message.content)
    return response_text.choices[0].message.content

def ask_mini_gpt(prompt: str, role :str="You are a helpful assistant.", temperature=0.2):
    openai.api_key = OPENAI_KEY
    response_text = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": role},
            {
                "role": "user",
                "content": prompt,
                "temperature": temperature
            }
        ]
    )
    print(response_text.choices[0].message.content)
    return response_text.choices[0].message.content