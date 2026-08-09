from openai import OpenAI

client = OpenAI(
    base_url="https://api.gapgpt.app/v1",
    api_key="sk-NO0b6pIYBW1NryfJyyEvkTfdvcz7dmI1yOsdsaYpk2PXZ9Yy"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": "سلام! یک جمله کوتاه درباره مدیریت جلسات بگو."
        }
    ]
)

print(response.choices[0].message.content)