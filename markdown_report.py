import ast

import pandas as pd

GMAIL_URL = "https://mail.google.com/mail/u/0/?tab=rm&ogbl#inbox/"


def build_and_save_markdown_report(df):
    report_builder = MarkdownReportBuilder(df)
    markdown_report = report_builder.make_report()
    print(markdown_report)
    report_builder.save_as_markdown()

    return markdown_report


class MarkdownReportBuilder:
    def __init__(self, df: pd.DataFrame):
        self.grouped_dfs = df.groupby(["label_category", "label_action"])
        self.categories = {
            "## 📝 학술/연구": [
                ("### 📌 처리가 필요한 메일", "academic", "action needed"),
                ("### 📎 읽어볼 메일", "academic", "read only"),
            ],
            "## 🏢 행정 처리": [
                ("### 📌 처리가 필요한 메일", "administration", "action needed"),
                ("### 📎 읽어볼 메일", "administration", "read only"),
            ],
            "## 📂 기타/그 외": [
                ("### 📌 처리가 필요한 메일", "other", "action needed"),
                ("### 📎 읽어볼 메일", "other", "read only"),
            ],
        }
        self.is_seen = set()

    def df_to_text(self, df: pd.DataFrame) -> str:
        if df is None or df.empty:
            return None
        result_lines = []
        for _, row in df.iterrows():
            if row["message_id"] in self.is_seen:  # 이미 표출한 메일이면 continue
                continue

            links = f"[🔗]({GMAIL_URL}{row['message_id']})"
            if len(row["similar_mails"]) != 0:
                for similar_ids in row["similar_mails"]:
                    links += " " + f"[🔗]({GMAIL_URL}{similar_ids})"
                    self.is_seen.add(similar_ids)

            summary = row["summary"].replace("\n\n", "\n")

            result_lines.append(f"- [ ] {summary} {links}")

        return "\n".join(result_lines)

    def get_grouped_df_with(self, label_category: str, label_action: str) -> pd.DataFrame:
        return (
            self.grouped_dfs.get_group((label_category, label_action))
            if (label_category, label_action) in self.grouped_dfs.groups
            else None
        )

    def make_report(self) -> str:

        report_sections = []
        for category, sections in self.categories.items():
            section_content = [
                f"{subheader}\n\n{self.df_to_text(self.get_grouped_df_with(label_category, label_action))}"
                for subheader, label_category, label_action in sections
                if self.df_to_text(self.get_grouped_df_with(label_category, label_action))
            ]
            if section_content:
                report_sections.append(f"{category}\n\n" + "\n\n".join(section_content))

        return "\n\n".join(report_sections)

    def save_as_markdown(self, output_file: str = "report.md"):
        markdown_text = self.make_report()
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(markdown_text)
        print(f"✅ Markdown 보고서가 {output_file}로 저장되었습니다!")


if __name__ == "__main__":
    df = pd.read_csv("test_mail_10.csv", index_col=0)
    df["similar_mails"] = df["similar_mails"].apply(ast.literal_eval)
    print(df)
    build_and_save_markdown_report(df)
