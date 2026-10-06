from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, Generic, TypedDict, runtime_checkable, Any
from enum import Enum


# --- Value Objects ---
@dataclass(frozen=True, slots=True)
class Price:
    amount: float
    currency: str = "UAH"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Price cannot be negative")

    def __add__(self, other: "Price") -> "Price":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Price(self.amount + other.amount, self.currency)

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"


# --- Models ---
@dataclass
class Category:
    name: str


@dataclass
class Product:
    id: int
    name: str
    _price: Price
    category: Category

    @property
    def price(self) -> Price:
        return self._price

    def __str__(self) -> str:
        return f"{self.name} ({self.price}) - {self.category.name}"


@dataclass
class InventoryItem:
    product: Product
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")

    @property
    def total_value(self) -> Price:
        return Price(self.product.price.amount * self.quantity, self.product.price.currency)


# --- Protocols & Abstractions ---
@runtime_checkable
class PricingStrategy(Protocol):
    def calculate(self, price: Price) -> Price:
        ...


class Discount(ABC):
    @abstractmethod
    def apply(self, price: Price) -> Price:
        ...


class PercentageDiscount(Discount):
    def __init__(self, percent: float) -> None:
        self.percent = percent

    def apply(self, price: Price) -> Price:
        return Price(price.amount * (1 - self.percent / 100), price.currency)


# --- Generic Repository ---
T = TypeVar("T", bound=Any)

class Repository(Generic[T]):
    def __init__(self) -> None:
        self._storage: dict[int, T] = {}

    def add(self, id: int, item: T) -> None:
        self._storage[id] = item

    def get(self, id: int) -> T | None:
        return self._storage.get(id)

    def all(self) -> list[T]:
        return list(self._storage.values())


# --- TypedDict ---
class ProductData(TypedDict):
    id: int
    name: str
    price: float
    category: str


# --- Store Catalog ---
class StoreCatalog:
    def __init__(self, repository: Repository[Product]) -> None:
        self.repository = repository

    def add_product(self, product: Product) -> None:
        self.repository.add(product.id, product)

    def find_most_expensive(self) -> Product | None:
        items = self.repository.all()
        if not items:
            return None
        return max(items, key=lambda p: p.price.amount)


# --- Main Demo ---
def main() -> None:
    repo = Repository[Product]()
    catalog = StoreCatalog(repo)
    
    cat_tech = Category("Electronics")
    laptop = Product(1, "Laptop", Price(30000), cat_tech)
    mouse = Product(2, "Mouse", Price(500), cat_tech)
    
    catalog.add_product(laptop)
    catalog.add_product(mouse)
    
    print(f"Most expensive: {catalog.find_most_expensive()}")
    
    discount = PercentageDiscount(10)
    final_price = discount.apply(laptop.price)
    print(f"Discounted laptop price: {final_price}")

if __name__ == "__main__":
    main()