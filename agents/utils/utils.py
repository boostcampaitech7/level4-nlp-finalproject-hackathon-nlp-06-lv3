import yaml

from prompt.prompt import load_template, load_template_with_variables


# YAML 파일에서 카테고리 정보 로드
def load_categories_from_yaml(classification_type: str, is_prompt: bool = False) -> list[dict[str, str]]:
    """
    YAML 파일에서 카테고리 정보를 로드합니다.

    Args:
        file_path (str): YAML 파일 경로
        is_prompt (bool): True일 경우 name과 rubric만 로드하고,
                          False일 경우 name과 description만 로드합니다.
    Returns:
        list: 카테고리 정보 리스트

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 경우 예외를 발생시킵니다.
        ValueError: YAML 파일 파싱 중 오류가 발생할 경우 예외를 발생시킵니다.
    """
    yaml_file_path = f"prompt/template/classification/{classification_type}.yaml"
    try:
        with open(yaml_file_path, "r", encoding="utf-8") as file:
            categories: dict = yaml.safe_load(file)

            if is_prompt:
                return [{"name": category["name"], "rubric": category["rubric"]} for category in categories]
            else:
                return [{"name": category["name"], "description": category["description"]} for category in categories]
    except FileNotFoundError:
        raise FileNotFoundError(f"카테고리 파일 {yaml_file_path}이(가) 존재하지 않습니다.")
    except yaml.YAMLError as e:
        raise ValueError(f"YAML 파일 파싱 중 오류 발생: {e}")


# 시스템 및 사용자 프롬프트 생성 함수
def build_messages(template_type: str, target_range: str, action: str, **kwargs) -> list:
    """
    OpenAI.chat.completion.create 함수에 넘겨줄 messages 인자를 생성합니다.

    Args:
        template_type (str): 템플릿이 위치한 디렉토리 유형 (예: "self_refine")
        target_range (str): 템플릿 txt 파일의 접두사 (예: "final")
        action (str): 템플릿의 용도 (예: "feedback")

    Returns:
        list: 생성된 메시지 리스트

    Raises:
        FileNotFoundError: 템플릿 파일이 존재하지 않을 경우 예외 발생
    """
    try:
        system_prompt = load_template(template_type=template_type, file_name=f"{target_range}_{action}_system.txt")
        user_prompt = load_template_with_variables(
            template_type=template_type, file_name=f"{target_range}_{action}_user.txt", **kwargs
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    except FileNotFoundError as e:
        print(e)
        raise
