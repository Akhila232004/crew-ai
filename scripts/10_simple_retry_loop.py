from crewai.flow.flow import Flow, start, listen, router
from pydantic import BaseModel


class RetryState(BaseModel):
    retry_count: int = 0
    max_retries: int = 3
    status: str = "PENDING"


class SimpleRetryLoop(Flow[RetryState]):

    @start()
    def network_call(self):
        """Simulate a network call that fails."""

        print(f"\nAttempt {self.state.retry_count + 1}")

        # Simulating a failed network call
        print("Network call failed!")

        return "failed"


    @listen(network_call)
    def increment_retry(self):
        """Increase the retry counter."""

        self.state.retry_count += 1

        print(f"Retry count: {self.state.retry_count}")

        return self.state.retry_count


    @router(increment_retry)
    def decide_next_step(self):
        """Decide whether to retry or handle failure."""

        if self.state.retry_count < self.state.max_retries:
            return "retry"

        return "failure"


    @listen("retry")
    def retry_network_call(self):
        """Retry the network call."""

        print("Retrying network call...")

        return self.network_call()


    @listen("failure")
    def failure_handler(self):
        """Handle failure after maximum retries."""

        self.state.status = "FAILED"

        print("\nMaximum retry limit reached!")
        print("Routing to failure handler...")
        print(f"Final Status: {self.state.status}")


if __name__ == "__main__":
    flow = SimpleRetryLoop()
    flow.kickoff()