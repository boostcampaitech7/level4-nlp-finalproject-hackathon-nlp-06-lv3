import os
import pickle


def save_mail_dict(mail_dict, file_path):
    """메일 데이터를 파일로 저장하는 함수."""
    with open(file_path, "wb") as f:
        pickle.dump(mail_dict, f)


def load_mail_dict(file_path):
    """파일에서 메일 데이터를 불러오는 함수."""
    return pickle.load(open(file_path, "rb")) if os.path.exists(file_path) else None
