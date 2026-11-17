class SpellingNotification:
    def __init__(self, file: str, type: str, line: int, column: int, message: str, code_snippet: str, suggestions: str):
        self.file = file
        self.line = line
        self.column = column
        self.type = type
        self.message = message
        self.code_snippet = code_snippet
        self.suggestions = suggestions
        self.message_and_suggestions_mixed = f"{message}{suggestions}"

    def __repr__(self) -> str:
        return (
            f"SpellingNotification(file={self.file}, type={self.type}, line={self.line}, column={self.column}, "
            f" message={self.message}, code_snippet={self.code_snippet}, suggestions={self.suggestions})"
        )
