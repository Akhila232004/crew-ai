from crewai.flow.flow import Flow, start, listen
from pydantic import BaseModel


# -----------------------------------
# Mock JSON Database
# -----------------------------------

MOCK_USERS = {
    "101": {
        "name": "Akhila",
        "email": "akhila@example.com",
        "country": "India"
    },
    "102": {
        "name": "Rahul",
        "email": "rahul@example.com",
        "country": "India"
    },
    "103": {
        "name": "John",
        "email": "john@example.com",
        "country": "USA"
    }
}


MOCK_PURCHASES = {
    "101": [
        {
            "product": "Laptop",
            "price": 75000
        },
        {
            "product": "Headphones",
            "price": 3000
        }
    ],
    "102": [
        {
            "product": "Mobile Phone",
            "price": 25000
        }
    ],
    "103": [
        {
            "product": "Keyboard",
            "price": 5000
        },
        {
            "product": "Mouse",
            "price": 1500
        }
    ]
}


# -----------------------------------
# Pydantic Models
# -----------------------------------

class Purchase(BaseModel):
    product: str
    price: float


class UserProfile(BaseModel):
    user_id: str
    name: str
    email: str
    country: str


class UnifiedUserProfile(BaseModel):
    user_id: str
    name: str
    email: str
    country: str
    purchases: list[Purchase]


# -----------------------------------
# Flow State
# -----------------------------------

class HydratorState(BaseModel):
    user_id: str = ""
    profile: UserProfile | None = None
    purchases: list[Purchase] = []
    unified_profile: UnifiedUserProfile | None = None


# -----------------------------------
# CrewAI Flow
# -----------------------------------

class MockAPIDataHydrator(Flow[HydratorState]):

    @start()
    def get_user_id(self):
        """Get User ID from the user."""

        self.state.user_id = input(
            "Enter User ID: "
        ).strip()

        print(f"\nUser ID received: {self.state.user_id}")

        return self.state.user_id


    @listen(get_user_id)
    def fetch_user_profile(self, user_id):
        """Fetch user profile from mock database."""

        user_data = MOCK_USERS.get(user_id)

        if not user_data:
            print("\nUser not found!")
            return None

        self.state.profile = UserProfile(
            user_id=user_id,
            name=user_data["name"],
            email=user_data["email"],
            country=user_data["country"]
        )

        print("\nUser Profile Found:")
        print(self.state.profile)

        return self.state.profile


    @listen(fetch_user_profile)
    def fetch_purchase_history(self, profile):
        """Fetch purchase history using User ID."""

        if profile is None:
            return []

        purchase_data = MOCK_PURCHASES.get(
            profile.user_id,
            []
        )

        self.state.purchases = [
            Purchase(
                product=item["product"],
                price=item["price"]
            )
            for item in purchase_data
        ]

        print("\nPurchase History:")
        for purchase in self.state.purchases:
            print(purchase)

        return self.state.purchases


    @listen(fetch_purchase_history)
    def create_unified_profile(self, purchases):
        """Combine profile and purchases."""

        if self.state.profile is None:
            print("\nCannot create unified profile.")
            return None

        self.state.unified_profile = UnifiedUserProfile(
            user_id=self.state.profile.user_id,
            name=self.state.profile.name,
            email=self.state.profile.email,
            country=self.state.profile.country,
            purchases=purchases
        )

        print("\nUnified User Profile:")
        print(self.state.unified_profile)

        return self.state.unified_profile


# -----------------------------------
# Run Flow
# -----------------------------------

if __name__ == "__main__":
    flow = MockAPIDataHydrator()
    flow.kickoff()