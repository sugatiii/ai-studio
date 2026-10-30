from pathlib import Path


class PromptLoader:

    @staticmethod
    def load_file(file_path: str) -> str:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        return path.read_text(
            encoding="utf-8"
        )

    @staticmethod
    def build_prompt(
        prompt_file: str,
        input_files: list[str],
    ) -> str:

        prompt_content = PromptLoader.load_file(
            prompt_file
        )

        content = f"""
[PROMPT]

{prompt_content}

--------------------------------------------------
"""

        for file in input_files:

            file_content = PromptLoader.load_file(
                file
            )

            content += f"""

[INPUT FILE]

Path:
{file}

Content:

{file_content}

--------------------------------------------------
"""

        return content.strip()