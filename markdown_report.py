import pandas as pd


def build_and_save_markdown_report(df):
    report_builder = MarkdownReportBuilder(df)
    markdown_report = report_builder.make_report()
    print(markdown_report)
    report_builder.save_as_markdown()


class MarkdownReportBuilder:
    def __init__(self, df: pd.DataFrame):
        self.grouped_dfs = df.groupby(["label_category", "label_action"])
        self.categories = {
            "### 📝 학술/연구": [
                ("#### 📌 처리가 필요한 메일", "academic", "action needed"),
                ("#### 📎 읽어볼 메일", "academic", "read only"),
            ],
            "### 🏢 행정 처리": [
                ("#### 📌 처리가 필요한 메일", "administration", "action needed"),
                ("#### 📎 읽어볼 메일", "administration", "read only"),
            ],
            "### 📂 기타/그 외": [
                ("#### 📌 처리가 필요한 메일", "other", "action needed"),
                ("#### 📎 읽어볼 메일", "other", "read only"),
            ],
        }

    def df_to_text(self, df: pd.DataFrame) -> str:
        if df is None or df.empty:
            return None
        return "\n".join(f"- [ ] {title}" for title in df["summary"].tolist())

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

    build_and_save_markdown_report(df)
