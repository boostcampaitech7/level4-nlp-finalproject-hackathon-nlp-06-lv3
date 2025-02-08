from openai import OpenAI

from utils.token_usage_counter import TokenUsageCounter


def check_groundness(context: str, answer: str, api_key, agent_name: str = "") -> str:
    client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1/solar")
    response = client.chat.completions.create(
        model="groundedness-check",
        messages=[
            {
                "role": "user",
                "content": context,
            },
            {"role": "assistant", "content": answer},
        ],
    )

    groundness = response.choices[0].message.content
    TokenUsageCounter.add_usage(agent_name, "groundness_check", response.usage.total_tokens)
    return groundness
