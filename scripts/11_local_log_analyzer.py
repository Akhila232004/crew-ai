from crewai.flow.flow import Flow, start, listen
from pydantic import BaseModel


class LogState(BaseModel):
    file_path: str = ""
    log_lines: list[str] = []
    error_lines: list[str] = []
    summary: dict = {}


class LocalLogAnalyzer(Flow[LogState]):

    @start()
    def read_log_file(self):
        """Read the local .log file."""

        self.state.file_path = input(
            "Enter the path of the .log file: "
        ).strip()

        try:
            with open(self.state.file_path, "r") as file:
                self.state.log_lines = file.readlines()

            print(
                f"\nSuccessfully read "
                f"{len(self.state.log_lines)} lines."
            )

            return self.state.log_lines

        except FileNotFoundError:
            print("\nError: File not found.")
            self.state.log_lines = []
            return []


    @listen(read_log_file)
    def filter_errors(self, log_lines):
        """Keep only lines containing ERROR."""

        self.state.error_lines = [
            line.strip()
            for line in log_lines
            if "ERROR" in line
        ]

        print(
            f"\nFound {len(self.state.error_lines)} "
            f"ERROR lines."
        )

        return self.state.error_lines


    @listen(filter_errors)
    def create_summary(self, error_lines):
        """Create a summary dictionary."""

        self.state.summary = {
            "total_log_lines": len(self.state.log_lines),
            "total_errors": len(error_lines),
            "errors": error_lines
        }

        print("\nSummary Dictionary:")
        print(self.state.summary)

        return self.state.summary


    @listen(create_summary)
    def write_report(self, summary):
        """Write the final report to report.txt."""

        with open("report.txt", "w") as file:

            file.write("LOG ANALYSIS REPORT\n")
            file.write("=" * 30 + "\n\n")

            file.write(
                f"Total Log Lines: "
                f"{summary['total_log_lines']}\n"
            )

            file.write(
                f"Total ERROR Lines: "
                f"{summary['total_errors']}\n\n"
            )

            file.write("ERROR DETAILS:\n")

            if summary["errors"]:
                for error in summary["errors"]:
                    file.write(f"- {error}\n")
            else:
                file.write("No errors found.\n")

        print(
            "\nReport successfully created: report.txt"
        )


if __name__ == "__main__":
    flow = LocalLogAnalyzer()
    flow.kickoff()