from crewai.flow.flow import Flow, start
from pydantic import BaseModel, ValidationError, StrictInt, StrictStr


# Strict Pydantic schema
class UserData(BaseModel):
    name: StrictStr
    age: StrictInt
    email: StrictStr


# Flow state
class ValidationState(BaseModel):
    raw_data: dict = {}
    validated_data: UserData | None = None
    status: str = "PENDING"


class StructuredSchemaValidator(Flow[ValidationState]):

    @start()
    def get_and_validate_data(self):

        print("Enter user details:")

        name = input("Enter name: ")

        # Convert input to integer only if possible
        age_input = input("Enter age: ")

        try:
            age = int(age_input)
        except ValueError:
            age = age_input

        email = input("Enter email: ")

        # Store user input as a raw dictionary
        self.state.raw_data = {
            "name": name,
            "age": age,
            "email": email
        }

        print("\nRaw Data:")
        print(self.state.raw_data)

        try:
            # Validate data using Pydantic
            validated = UserData(**self.state.raw_data)

            self.state.validated_data = validated
            self.state.status = "PASS"

            print("\nValidation: PASS")
            print("Validated Data:")
            print(validated)

        except ValidationError as e:
            self.state.status = "FAIL"

            print("\nValidation: FAIL")
            print("Errors:")
            print(e)


if __name__ == "__main__":
    flow = StructuredSchemaValidator()
    flow.kickoff()

    print("\nFinal Status:", flow.state.status)