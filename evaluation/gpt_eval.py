from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


def calculate_g_eval(source_texts, generated_texts, config, eval_type, additional=False):
    """
    Summary / Report 평가 타입에 따라 G-EVAL 실행.

    - eval_type: "summary" 또는 "report"
    - additional: True이면 기본 4개 기준 + 추가 3개 기준까지 평가

    기본 평가 기준 (4개):
      - consistency (일관성)
      - coherence (논리적 연결성)
      - fluency (유창성)
      - relevance (관련성)

    추가 평가 기준 (additional=True 일 때 3개 추가):
      - readability (가독성)
      - clearance (명확성)
      - practicality (실용성)

    반환 형태:
      [
        {"consistency": float, "coherence": float, "fluency": float, "relevance": float,
         "readability": float, "clearance": float, "practicality": float},
        ...
      ]
    """
    if eval_type not in config:
        raise ValueError(f"Invalid eval_type '{eval_type}' in config.")

    # 평가용 설정 불러오기
    eval_config = config[eval_type].get("g_eval", {})
    prompt_files = eval_config.get("prompts", {})
    model_name = eval_config.get("openai_model", "gpt-4")

    # 기본 4개 기준 + 추가 3개 기준 (additional=True일 때만)
    aspects = ["consistency", "coherence", "fluency", "relevance"]
    if additional:
        aspects += ["readability", "clearance", "practicality"]

    results_list = []
    for src, gen in zip(source_texts, generated_texts):
        aspect_scores = {}
        for aspect in aspects:
            prompt_path = prompt_files.get(aspect, None)
            if not prompt_path:
                # 프롬프트 파일이 없다면 0점 처리
                aspect_scores[aspect] = 0.0
                continue

            # 프롬프트 읽어오기
            with open(prompt_path, "r", encoding="utf-8") as f:
                base_prompt = f.read()

            # {Document}, {Summary} 치환
            cur_prompt = base_prompt.format(Document=src, Summary=gen)

            # OpenAI API 호출
            try:
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
            except Exception as e:
                print(f"[Error in G-EVAL] eval_type={eval_type}, aspect={aspect}, error={e}")
                aspect_scores[aspect] = 0.0

        results_list.append(aspect_scores)

    return results_list
