from pathlib import Path


class FileManager:

    @staticmethod
    def read(path: str) -> str:
        return Path(path).read_text(
            encoding="utf-8"
        )

    @staticmethod
    def write(
        path: str,
        content: str
    ):

        file = Path(path)

        file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file.write_text(
            content,
            encoding="utf-8"
        )