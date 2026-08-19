from crewai.flow.flow import Flow, start, listen, and_
from pydantic import BaseModel


class AggregatorState(BaseModel):
    user_data: dict = {}
    order_data: list = []
    final_result: dict = {}


class ParallelTaskAggregator(Flow[AggregatorState]):

    @start()
    def collect_user_data(self):
        """Collect user profile data."""

        print("Collecting user data...")

        self.state.user_data = {
            "name": "Akhila",
            "country": "India"
        }

        print("User data collected.")

        return self.state.user_data


    @start()
    def collect_order_data(self):
        """Collect order data."""

        print("Collecting order data...")

        self.state.order_data = [
            {
                "product": "Laptop",
                "price": 75000
            },
            {
                "product": "Headphones",
                "price": 3000
            }
        ]

        print("Order data collected.")

        return self.state.order_data


    @listen(and_(collect_user_data, collect_order_data))
    def aggregate_data(self):
        """Run after both tasks finish and combine State data."""

        print("\nBoth data sources are ready.")

        self.state.final_result = {
            "user": self.state.user_data,
            "orders": self.state.order_data,
            "total_orders": len(self.state.order_data)
        }

        print("\nFinal Aggregated Result:")
        print(self.state.final_result)

        return self.state.final_result


if __name__ == "__main__":
    flow = ParallelTaskAggregator()
    flow.kickoff()