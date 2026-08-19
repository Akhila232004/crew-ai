from crewai.flow.flow import Flow, start, router, listen
from pydantic import BaseModel


class FileState(BaseModel):
    filename: str = ""
    extension: str = ""
    result: str = ""


class FileExtensionClassifier(Flow[FileState]):

    @start()
    def get_filename(self):
        """Get the file name from the user."""

        self.state.filename = input("Enter a file name: ").strip()

        print(f"\nFile received: {self.state.filename}")

        return self.state.filename


    @router(get_filename)
    def classify_file(self):
        """Check the file extension and choose a route."""

        filename = self.state.filename.lower()

        if filename.endswith(".csv"):
            self.state.extension = ".csv"
            return "csv"

        elif filename.endswith(".txt"):
            self.state.extension = ".txt"
            return "txt"

        else:
            return "unsupported"


    @listen("csv")
    def csv_handler(self):
        """Handle CSV files."""

        self.state.result = "CSV file detected"

        print("\nCSV Handler")
        print("Processing CSV file...")


    @listen("txt")
    def txt_handler(self):
        """Handle TXT files."""

        self.state.result = "TXT file detected"

        print("\nTXT Handler")
        print("Processing TXT file...")


    @listen("unsupported")
    def unsupported_error(self):
        """Handle unsupported files."""

        self.state.result = "Unsupported file type"

        print("\nError!")
        print("Unsupported file extension.")


if __name__ == "__main__":
    flow = FileExtensionClassifier()
    flow.kickoff()

    print("\nFinal Result:")
    print(flow.state.result)