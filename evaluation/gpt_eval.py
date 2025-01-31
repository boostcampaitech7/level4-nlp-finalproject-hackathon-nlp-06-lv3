from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


def calculate_g_eval(source_texts, generated_texts, g_eval_config, eval_type, additional=False):
    """
    Summary / Report 평가 타입에 따라 G-EVAL 실행.

    Args:
        g_eval_config (dict): g-eval 관련 설정만 포함된 딕셔너리
    """
    prompt_files = g_eval_config.get("prompts", {})
    model_name = g_eval_config.get("openai_model", "gpt-4")

    # 평가할 기준 (기본 4개 + 추가 옵션 포함 시 7개)
    aspects = ["consistency", "coherence", "fluency", "relevance"]
    if additional:
        aspects += ["readability", "clearance", "practicality"]

    results_list = []
    for src, gen in zip(source_texts, generated_texts):
        aspect_scores = {}

        for aspect in aspects:
            prompt_path = prompt_files.get(aspect)
            if not prompt_path:
                aspect_scores[aspect] = 0.0  # 프롬프트 파일이 없으면 0점 처리
                continue

            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    base_prompt = f.read()

                # {Document}, {Summary} 치환
                cur_prompt = base_prompt.format(Document=src, Summary=gen)

                # OpenAI API 호출
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "system", "content": cur_prompt}],
                    temperature=0.7,
                    max_tokens=50,
                    n=1,
                )

                # GPT가 준 output을 float로 변환
                gpt_text = response.choices[0].message.content.strip()
                score_value = float(gpt_text)
                aspect_scores[aspect] = score_value

            except (FileNotFoundError, ValueError) as e:
                print(f"[Error] eval_type={eval_type}, aspect={aspect}, error={e}")
                aspect_scores[aspect] = 0.0

        results_list.append(aspect_scores)

    return results_list
