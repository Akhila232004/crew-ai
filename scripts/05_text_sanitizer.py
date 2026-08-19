import re

from crewai.flow.flow import Flow, start, listen
from pydantic import BaseModel


class TextState(BaseModel):
    raw_text: str = ""
    normalized_text: str = ""
    clean_text: str = ""


class TextSanitizerFlow(Flow[TextState]):

    @start()
    def get_user_input(self):
        self.state.raw_text = input("Enter messy text: ")

        return self.state.raw_text

    @listen(get_user_input)
    def normalize_text(self, text):
        # Remove leading/trailing whitespace
        # Convert text to lowercase
        self.state.normalized_text = text.strip().lower()

        print("\nAfter normalization:")
        print(self.state.normalized_text)

        return self.state.normalized_text

    @listen(normalize_text)
    def remove_special_characters(self, text):
        # Keep only letters, numbers, and spaces
        self.state.clean_text = re.sub(
            r"[^a-z0-9\s]",
            "",
            text
        )

        # Convert multiple spaces into a single space
        self.state.clean_text = re.sub(
            r"\s+",
            " ",
            self.state.clean_text
        ).strip()

        return self.state.clean_text


if __name__ == "__main__":
    flow = TextSanitizerFlow()

    result = flow.kickoff()

    print("\nFinal clean text:")
    print(result)