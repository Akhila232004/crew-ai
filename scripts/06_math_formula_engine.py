from crewai.flow.flow import Flow, start, listen
from pydantic import BaseModel


class MathState(BaseModel):
    number: float = 0


class MathFormulaEngine(Flow[MathState]):

    @start()
    def get_input(self):
        """Take a base number from the user."""
        user_input = float(input("Enter a base number: "))

        self.state.number = user_input

        print(f"\nInitial number: {self.state.number}")
        return self.state.number

    @listen(get_input)
    def multiply_number(self, number):
        """Step 1: Multiply the number."""
        self.state.number = number * 2

        print(f"Step 1 - After multiplying by 2: {self.state.number}")
        return self.state.number

    @listen(multiply_number)
    def add_constant(self, number):
        """Step 2: Add a constant."""
        self.state.number = number + 10

        print(f"Step 2 - After adding 10: {self.state.number}")
        return self.state.number

    @listen(add_constant)
    def square_number(self, number):
        """Step 3: Square the result."""
        self.state.number = number ** 2

        print(f"Step 3 - Final result after squaring: {self.state.number}")

        return self.state.number


if __name__ == "__main__":
    flow = MathFormulaEngine()
    result = flow.kickoff()

    print(f"\nFinal Output: {result}")