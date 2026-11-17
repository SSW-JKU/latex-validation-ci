class LintNotification:
    file: str
    type: str
    line: int
    message: str
    code_snippet: str

    def __init__(self, file: str, type: str, line: int, message: str, code_snippet: str) -> None:
        self.file = file
        self.type = type
        self.line = line
        self.message = message
        self.code_snippet = code_snippet

    def __repr__(self) -> str:
        return (
            f"LintNotification(file={self.file},"
            f"type={self.type}, line={self.line}, message={self.message}, code_snippet={self.code_snippet})"
        )
