from datetime import datetime
import json

class Movement:
    def __init__(self, concept, date, amount):
        self.concept = concept
        self.date = date
        self.amount = amount

    def __str__(self):
        return f"{self.date} - {self.concept}: ${self.amount:.2f}"

    def to_expense(self, category):
        return Expense(self.concept, self.date, self.amount, category)


class Expense(Movement):
    def __init__(self, concept, date, amount, category):
        super().__init__(concept, date, amount)
        self.category = category

    def __str__(self):
        return f"{super().__str__()} (Category: {self.category})"


class Income(Movement):
    def __init__(self, concept, date, amount, source):
        super().__init__(concept, date, amount)
        self.source = source

    def __str__(self):
        return f"{super().__str__()} (Source: {self.source})"
    
class FinanceTracker:
    def __init__(self):
        self.category_map = {}  # Dictionary to store concept-category mappings
        self.categories = {"Rent", "Subscription", "Groceries", "Sport", "Unknown"}

    def classify_concept(self, concept, category):
        self.category_map[concept] = category

    def create_expense(self, concept, date, amount):
        # Check if the amount is negative to determine if it's an expense
        if amount < 0:
            if concept in self.category_map:
                category = self.category_map[concept]
            else:
                # Ask user for category
                while True:
                    print(f"'{concept}' is not classified. Please select a category:")
                    print("Categories:", ", ".join(sorted(self.categories)))
                    new_category = input("Category name (or type a new category): ").strip()
                    if new_category in self.categories:
                        break
                    else:
                        self.categories.add(new_category)
                        break

                self.classify_concept(concept, new_category)
                category = new_category
            return Expense(concept, date, amount, category)
        else:
            raise ValueError("Amount must be negative for expenses.")
        
    def save_category_map(self):
        with open("category_map.json", "w") as file:
            json.dump(self.category_map, file)

    def load_category_map(self):
        try:
            with open("category_map.json", "r") as file:
                self.category_map = json.load(file)
        except FileNotFoundError:
            pass