from crewai.flow.flow import Flow, start, router, listen
from pydantic import BaseModel


class OrderState(BaseModel):
    price: float = 0
    country: str = ""
    shipping_type: str = ""


class EcommerceOrderRouter(Flow[OrderState]):

    @start()
    def get_order(self):
        self.state.price = float(input("Enter order price: "))
        self.state.country = input("Enter country: ")

        return "order_received"


    @router(get_order)
    def route_order(self):
        if self.state.price >= 1000:
            return "premium"

        return "ground"


    @listen("premium")
    def premium_shipping(self):
        self.state.shipping_type = "Premium Shipping"

        print("\nHigh-value order detected!")
        print("Shipping Method: Premium Shipping")


    @listen("ground")
    def ground_shipping(self):
        self.state.shipping_type = "Ground Shipping"

        print("\nStandard order detected!")
        print("Shipping Method: Ground Shipping")


if __name__ == "__main__":
    flow = EcommerceOrderRouter()
    flow.kickoff()

    print(f"\nFinal Shipping Type: {flow.state.shipping_type}")