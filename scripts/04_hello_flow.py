from crewai.flow.flow import Flow, start


class HelloWorldFlow(Flow):

    @start()
    def say_hello(self):
        message = "Hello, World!"
        print(message)
        return message


if __name__ == "__main__":
    flow = HelloWorldFlow()
    result = flow.kickoff()

    print(f"\nFinal result: {result}")