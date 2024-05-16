from datetime import datetime
from time import sleep
import json

class Movement:
    def __init__(self, concept, date, amount, category=None):
        self.concept = concept
        date_with_time = datetime.strptime(date, "%d/%m/%Y")
        self.date = date_with_time.date()
        self.amount = amount
        self.category = category

    def __str__(self):
        return f"{self.date} - {self.concept}: ${self.amount:.2f}"
    
class FinanceTracker:
    def __init__(self):
        self.category_map = {}  # Dictionary to store concept-category mappings
        self.categories = {"alquiler", "suscripciones", "compras", "deporte", "sueldo", "beca"}
        self.total_expenses = {}  # Dictionary to store total expenses per category
        for i in self.categories:
            self.total_expenses[i] = 0

    def classify_concept(self, concept, category):
        self.category_map[concept] = category

    def create_movement(self, concept, date, amount):
        # Check if concept is already classified
        if concept in self.category_map:
            category = self.category_map[concept]
        else:
            # Ask user for category if concept not previously classified
            while True:
                new_category = input(f"'{concept}' is not classified. Please select a category:\n"
                     f"Categories: {', '.join(sorted(self.categories))}\n"
                     "Category name (or type a new category): ").strip()
                if new_category in self.categories:
                    break
                else:
                    self.categories.add(new_category)
                    self.total_expenses[new_category] = 0
                    break
            # store the category for the new concept
            self.classify_concept(concept, new_category)
            category = new_category
        self.total_expenses[category] += amount
        return Movement(concept, date, amount, category)
            
            
    def save_category_map(self):
        with open("category_map.json", "w") as file:
            json.dump(self.category_map, file)


    def load_category_map(self):
        try:
            with open("category_map.json", "r") as file:
                self.category_map = json.load(file)
        except FileNotFoundError:
            pass