# 매일메일(MaeilMail)

LLM Agent 기반 일별 메일 요약 비서 Chrome Extension입니다.

## 📌 프로젝트 개요

온 종일 쌓이는 메일을 핵심만 빠르게 파악하고, 놓치는 정보 없이 우선순위를 정해 효율적으로 업무를 처리할 수 있도록 돕자!

> 프로젝트 진행 경황 및 자세한 실험 내역은 [노션 링크](https://www.notion.so/gamchan/Upstage-234368a08ffd4965aad55b1a93b3cc3d?pvs=4)에서 확인하실 수 있습니다.

## 🏅 최종 결과

시연 영상 링크

## 🏛️ System Structures

![service_pipeline](./assets/service_pipeline.png)

## 💯 평가 지표 및 결과

- [프롬프트 버저닝](https://www.notion.so/gamchan/195815b39d3980078aa1c8e645bf435c?pvs=4)
- [실험](https://www.notion.so/gamchan/18c815b39d39805e916ad56f39fa2c6b?pvs=4)

### 분류

`정확도/토큰 사용량` 지표를 바탕으로 현재 프롬프트를 채택했습니다.

- [목적 별 분류](prompt/template/classification/category.yaml)
- [추가 행동 필요 여부 분류](prompt/template/classification/action.yaml)

### 메일 개별 요약

ROUGE-1에서 300~400%, BERTScore에서 60~80%, G-Eval conciseness 항목에서(5점 만점) 11% 상승폭이 있었습니다.

### 메일 전체 요약

5점 만점인 G-Eval 평가에서 평균 150% 상승폭이 있었습니다.

- [G-Eval 평가 항목 별 프롬프트](prompt/template/reflexion/g_eval/)
- [전체 요약 시스템 프롬프트](prompt/template/summary/final_summary_system.txt)
- [전체 요약 사용자 프롬프트](prompt/template/summary/final_summary_user.txt)

## ⚙️ Project Quick Setup

### 1. Git Clone

```shell
$ git clone git@github.com:boostcampaitech7/level4-nlp-finalproject-hackathon-nlp-06-lv3.git
$ cd level4-nlp-finalproject-hackathon-nlp-06-lv3
```

### 2. Create Virtual Environment

```shell
$ python -m venv .venv
$ source .venv/bin/activate
(.venv) $
```

### 3. Install Packages

```shell
(.venv) $ pip install -r requirements.txt
(.venv) $ sudo apt-get install build-essential
```

### 4. Setup Environment Variables

4.1. `.env`를 생성 후 환경 변수를 수정합니다.

```shell
(.venv) $ cp .env.example .env
```

- Upstage API Key는 [여기](https://console.upstage.ai/api-keys?api=chat)에서, Openai API Key는 [여기](https://platform.openai.com/welcome?step=create)에서 발급해주세요.
- Google Client ID 및 Google Client Secret은 [다음 게시물](https://www.notion.so/gamchan/OAuth-179815b39d398017aeb8f6a8172e6e76?pvs=4)을 참고해주세요.

```shell
# AI Service
UPSTAGE_API_KEY=your_upstage_api_key
OPENAI_API_KEY=your_openai_api_key

# Google OAuth 2.0(with GMail)
GOOGLE_CLIENT_ID=1234567890.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=1234567890
```

4.2. `main.py`를 실행하기 위해서 `client_secret_...usercontent.com.json` 파일 이름을 `credentials.json`으로 변경해주세요.

### 5. Execute pipeline

```shell
(.venv) $ python main.py
```

### (Optional) Execute with DB connection

```shell
(.venv) $ docker-compose -f server/docker-compose.yml up -d
(.venv) $ python batch_main.py
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
