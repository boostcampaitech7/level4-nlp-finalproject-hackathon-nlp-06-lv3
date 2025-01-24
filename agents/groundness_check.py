from langchain_upstage import UpstageGroundednessCheck


def check_groundness(context: str, answer: str) -> str:
    groundness_check = UpstageGroundednessCheck()
    response = groundness_check.invoke(
        {
            "context": context,
            "answer": answer,
        }
    )
    return response
