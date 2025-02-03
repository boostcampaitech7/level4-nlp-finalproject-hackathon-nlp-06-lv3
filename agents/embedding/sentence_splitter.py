import re


def _mask_text(text: str) -> tuple[str, dict]:
    """
    1) 이메일, 소수/금액, 약어(J.K.), 연속된 점(..., …… 등), 전화번호 등을
       <MASK_...>로 치환한다.
    2) 마스킹 딕셔너리(mask_dict)에 {<MASK_...>: 원본 문자열} 형태로 저장한다.
    """
    mask_dict = {}

    patterns = {
        "EMAIL": r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
        "ELLIPSIS": r"(\.{2,})|([…]{2,})",
        "DECIMAL": r"\b\d{1,3}(,\d{3})*(\.\d+)?\b",
        "ABBREVIATION": r"\b([A-Z]\.)+[A-Z]?\b",
        "PHONE": r"\b\d{2,3}-\d{3,4}-\d{4}\b",
    }

    masked_text = text
    placeholder_index = 0

    for pattern_name, pattern_regex in patterns.items():
        while True:
            match = re.search(pattern_regex, masked_text)
            if not match:
                break
            original_str = match.group()
            placeholder = f"<MASK_{pattern_name}_{placeholder_index}>"
            placeholder_index += 1

            mask_dict[placeholder] = original_str

            masked_text = re.sub(pattern_regex, placeholder, masked_text, count=1)

    return masked_text, mask_dict


def _split_sentences(masked_text: str) -> list:
    """
    . ? ! 을 기준으로 문장을 분리하되, 파이썬 re 모듈의 look-behind 제약을 피하기 위해
    re.split(r'([.?!]+)', masked_text)을 사용한 2단계 방식으로 나눈다.

    1) 분리 시, 문장 본문과 문장부호를 번갈아 추출
    2) "본문 + 문장부호" 결합
    """
    parts = re.split(r"([.?!]+)", masked_text)

    sentences = []
    buffer_str = ""

    for i, chunk in enumerate(parts):
        if i % 2 == 0:
            buffer_str = chunk.strip()
        else:
            buffer_str += chunk  # 문장 본문 + 문장부호
            sentences.append(buffer_str.strip())
            buffer_str = ""

    if buffer_str.strip():
        sentences.append(buffer_str.strip())

    return [s for s in sentences if s]


def _restore_masks(sentences: list, mask_dict: dict) -> list:
    """
    split_sentences_v2 결과 리스트에 들어있는 <MASK_...>를 원본 문자열로 복원.
    """
    restored_sentences = []
    for sent in sentences:
        for placeholder, original_str in mask_dict.items():
            if placeholder in sent:
                sent = sent.replace(placeholder, original_str)
        restored_sentences.append(sent)
    return restored_sentences


def _merge_broken_abbrevs_and_decimals(sentences: list) -> list:
    """
    후처리 단계.
    1) 약어(J.K.)로 끝나는 문장과 그 다음 문장을 연결해
       "J.K. Rowling"이 끊기지 않도록 시도.
    2) 소수/금액형 숫자(예: "3,145.")로 끝나고, 다음 문장이 숫자로 시작하면
       연결해 "3,145.12" 형태로 만든다(만약 실제로 "3,145. 12"가 붙어 있어야 한다면 수정 필요).

    - 아래 규칙은 예시이므로, 실제 현장 상황에 따라 조건을 커스터마이징해야 한다.
    """
    merged = []
    skip_next = False

    for i in range(len(sentences)):
        if skip_next:
            skip_next = False
            continue

        current_sent = sentences[i]
        if i < len(sentences) - 1:
            next_sent = sentences[i + 1]

            if re.search(r"[A-Za-z]\.$", current_sent):
                if re.match(r"^[A-Za-z가-힣]", next_sent.strip()):
                    merged.append(current_sent + " " + next_sent)
                    skip_next = True
                    continue

            if re.search(r"\d\.$", current_sent):
                if re.match(r"^\d", next_sent.strip()):
                    merged.append(current_sent + next_sent)
                    skip_next = True
                    continue

        merged.append(current_sent)

    return merged


def split_sentences(text: str) -> list:
    """
    1) 마스킹
    2) 문장 분할
    3) 마스킹 복원
    4) (추가) 병합 후처리
    """
    # 1) 마스킹
    masked_text, mask_dict = _mask_text(text)

    # 2) 문장 분할
    splitted_sentences = _split_sentences(masked_text)

    # 3) 복원
    restored_sentences = _restore_masks(splitted_sentences, mask_dict)

    # 4) 후처리로 약어/소수 등이 끊긴 문장 병합
    final_sentences = _merge_broken_abbrevs_and_decimals(restored_sentences)

    return final_sentences


if __name__ == "__main__":
    print(split_sentences("안녕하세요?"))
