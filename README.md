# Final Project

하루 동안 온 메일을 한 눈에 보기 좋게 정리해주는 메일 업무 비서
프로젝트 개요, 설치 방법 및 지침에 대한 안내 필수

## 📌 프로젝트 개요

주제선정 배경, 기대효과 등
온 종일 쌓이는 메일을 핵심만 빠르게 파악하고, 놓치는 정보 없이 우선순위를 정해 효율적으로 업무를 처리할 수 있도록 돕자!

## 🏅 최종 결과

시연 영상 링크

## System Structures

시스템 구조 사진

## 평가 지표 및 결과

### 분류

### 메일 개별 요약

### 메일 전체 요약

## ⚙️ Project Quick Setup

### Git Clone

```shell
$ git clone git@github.com:boostcampaitech7/level4-nlp-finalproject-hackathon-nlp-06-lv3.git
$ cd level4-nlp-finalproject-hackathon-nlp-06-lv3
```

### Create Virtual Environment

```shell
$ python -m venv .venv
$ source .venv/bin/activate
(.venv) $
```

### Install Packages

```shell
(.venv) $ pip install -r requirements.txt
(.venv) $ sudo apt-get install build-essential
```

### Setup Environment Variables

`.env`를 생성 후 환경 변수를 수정합니다.

```shell
(.venv) $ cp .env.example .env
```

- UPSTAGE_API_KEY=your_upstage_api_key
- OPENAI_API_KEY=your_openai_api_key
- GOOGLE_CLIENT_ID=1234567890.apps.googleusercontent.com
- GOOGLE_CLIENT_SECRET=1234567890
- SESSION_KEY=your_session_key
- MYSQL_DATABASE=maeilmail_db
- MYSQL_USER=maeilmail
- MYSQL_PASSWORD=0000
- MYSQL_HOST=localhost
- MYSQL_PORT=3307

```shell
# AI Service
UPSTAGE_API_KEY=your_upstage_api_key
OPENAI_API_KEY=your_openai_api_key

# Google OAuth 2.0(with GMail)
GOOGLE_CLIENT_ID=1234567890.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=1234567890

# FastAPI Backend
SESSION_KEY=your_session_key

# MySQL Database
MYSQL_DATABASE=maeilmail_db
MYSQL_USER=maeilmail
MYSQL_PASSWORD=0000
MYSQL_HOST=localhost
MYSQL_PORT=3307
```

## 📜 Config.yml

`config.yml` 파일을 사용하여 원하는 환경에서 실행을 설정할 수 있습니다. 아래는 기본 설정 예시입니다:

```yaml
gmail:
  start_date: # gmail에서 불러올 시작 날짜 (값이 없는 경우 2025/01/10)
  end_date: # gmail에서 불러올 끝 날짜 (값이 없는 경우 오늘 날짜)
  max_mails: 15 # gmail에서 불러올 메일 최대 개수

evaluation: # 평가 설정
  summary_eval: false # Summary 평가 수행 여부
  classification_eval: false # Classification 평가 수행 여부
  report_eval: false # Final Report 평가 수행 여부

seed: 42
temperature:
  summary: 0
  classification: 0

self_reflection:
  type: self-refine # self-refine | reflexion 변경 가능
  max_iteration: 3 # TODO: 3으로 원상복구
  reflexion:
    threshold_type: "average"
    threshold: 4.5

common_prompts: &common_prompts
  consistency: "prompt/template/g_eval/con_{eval_type}.txt"
  coherence: "prompt/template/g_eval/coh_{eval_type}.txt"
  fluency: "prompt/template/g_eval/flu_{eval_type}.txt"
  relevance: "prompt/template/g_eval/rel_{eval_type}.txt"
  readability: "prompt/template/g_eval/rdb_{eval_type}.txt"
  clearance: "prompt/template/g_eval/clr_{eval_type}.txt"
  practicality: "prompt/template/g_eval/prc_{eval_type}.txt"

summary: # Summary 평가 관련 설정
  metrics:
    - rouge
    - bert
    - g-eval

  bert_model: "distilbert-base-uncased"

  g_eval:
    openai_model: "gpt-4" # summary는 gpt-4가 아니면 정확한 답변 생성이 어려움
    additional: False # "readability", "clearance", "practicality"를 G-Eval에 적용할 여부
    prompts:
      <<: *common_prompts

# Report 평가 관련 설정
report:
  metrics:
    - g-eval

  g_eval:
    openai_model: "gpt-4o" # report는 gpt-4o로도 가능
    additional: False # "readability", "clearance", "practicality"를 G-Eval에 적용할 여부
    prompts:
      <<: *common_prompts

classification:
  do_manual_filter: False
  inference: 1 # TODO: 5로 원상 복구, Consistency 평가 용 반복 추론 횟수 설정

embedding:
  model_name: "bge-m3" # 혹은 "upstage"
  similarity_metric: "cosine-similarity" # 혹은 "dot-product"
  similarity_threshold: 0.8
  save_results: true

token_tracking: true
```

## 🔬 References

- Aman Madaan, Niket Tandon, Prakhar Gupta, Skyler Hallinan, Luyu Gao, Sarah Wiegreffe, Uri Alon, Nouha Dziri, Shrimai Prabhumoye, Yiming Yang, Shashank Gupta, Bodhisattwa Prasad Majumder, Katherine Hermann, Sean Welleck, Amir Yazdanbakhsh, Peter Clark, "Self-Refine: Iterative Refinement with Self-Feedback", 25 May, 2023. https://arxiv.org/abs/2303.17651.
- Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao, "Reflexion: Language Agents with Verbal Reinforcement Learning", 10 Oct, 2023. https://arxiv.org/abs/2303.11366.
- Lianmin Zheng, Wei-Lin Chiang, Ying Sheng, Siyuan Zhuang, Zhanghao Wu, Yonghao Zhuang, Zi Lin, Zhuohan Li, Dacheng Li, Eric P. Xing, Hao Zhang, Joseph E. Gonzalez, Ion Stoica, "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", 24 Dec, 2023. https://arxiv.org/abs/2306.05685.
- Yang Liu, Dan Iter, Yichong Xu, Shuohang Wang, Ruochen Xu, Chenguang Zhu, "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment", 23 May, 2023. https://arxiv.org/abs/2303.16634.
- Yukyung Lee, Joonghoon Kim, Jaehee Kim, Hyowon Cho, Pilsung Kang, "CheckEval: Robust Evaluation Framework using Large Language Model via Checklist", 27 Mar, 2024. https://arxiv.org/abs/2403.18771.

- 기타 등
- 등등

## 👥 Collaborators

<div align="center">

|                                                   팀원                                                    |                                  역할                                  |
| :-------------------------------------------------------------------------------------------------------: | :--------------------------------------------------------------------: |
|     <a href="https://github.com/gsgh3016"><img src="https://github.com/gsgh3016.png" width="100"></a>     |  Streamlit app 개발 참여, 데이터 관찰 및 분석, 데이터 재구성 및 증강   |
|       <a href="https://github.com/eyeol"> <img src="https://github.com/eyeol.png" width="100"></a>        |             Streamlit app 개발 참여, RAG 구현 및 성능 평가             |
|    <a href="https://github.com/jagaldol"> <img src="https://github.com/jagaldol.png" width="100"> </a>    |  협업 초기 환경 세팅 및 코드 모듈화, CoT 방식 실험 설계 및 성능 평가   |
|     <a href="https://github.com/Usunwoo"> <img src="https://github.com/Usunwoo.png" width="100"> </a>     |        베이스라인 모듈화, 메모리 사용 최적화, 모델 서치 및 실험        |
| <a href="https://github.com/canolayoo78"> <img src="https://github.com/canolayoo78.png" width="100"> </a> |  Streamlit app 개발 참여, 데이터 분석 및 정제, RAG 구현 및 성능 평가   |
|   <a href="https://github.com/chell9999"> <img src="https://github.com/chell9999.png" width="100"> </a>   | 문서 작업, RAG 전용 Vector DB 구성, 벤치마크 데이터셋 기반 데이터 증강 |

</div>

## 🛠️ Tools and Technologies

<div align="center">

![Python](https://img.shields.io/badge/-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![jupyter](https://img.shields.io/badge/-jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![PyTorch](https://img.shields.io/badge/-PyTorch-EE4C2C?style=for-the-badge&logo=PyTorch&logoColor=white)
![huggingface](https://img.shields.io/badge/-huggingface-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)

![unsloth](https://img.shields.io/badge/-unsloth-14B789?style=for-the-badge&logo=unsloth&logoColor=white)
![BitsandBytes](https://img.shields.io/badge/BitsandBytes-36474F?style=for-the-badge&logo=BitsandBytes&logoColor=white)
![LoRA](https://img.shields.io/badge/LoRA-40B5A4?style=for-the-badge&logo=LoRA&logoColor=white)
![langchain](https://img.shields.io/badge/-langchain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)

![RAG](https://img.shields.io/badge/RAG-1868F2?style=for-the-badge&logo=RAG&logoColor=white)
![pinecone](https://img.shields.io/badge/pinecone-000000?style=for-the-badge&logo=pinecone&logoColor=white)
![Cot](https://img.shields.io/badge/cot-535051?style=for-the-badge&logo=cot&logoColor=white)
![github action](https://img.shields.io/badge/GITHUB%20ACTIONS-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

</div>
