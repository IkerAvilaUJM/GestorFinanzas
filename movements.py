from datetime import datetime
from time import sleep
import json
import pandas as pd

class Movement:
    def __init__(self, concept, date, amount, category=None):
        self.concept = concept
        date_with_time = datetime.strptime(date, "%d/%m/%Y")
        self.date = date_with_time.date()
        self.amount = amount
        self.category = category

    def __str__(self):
        return f"{self.date} - {self.concept}: ${self.amount:.2f}"
    
import pandas as pd

class FinanceTracker:
    def __init__(self):
        self.category_map = {}  # Dictionary to store concept-category mappings
        self.categories = ["alquiler", "suscripciones", "ropa", "deporte", "sueldo", "beca", "comer fuera",
                           "supermercado", "transporte", "ocio", "salud", "ropa", "mascotas", "paga",
                           "regalos", "viajes", "bares", "fiesta", "internet", "tecnologia", "otros"]
        # Convert categories to list and sort
        self.categories = sorted(self.categories)
        # Initialize DataFrame with categories and set index to "category"
        self.total_expenses = pd.DataFrame(0.0, index=self.categories, columns=["total"])
        self.total = 0.0

    def classify_concept(self, concept, category):
        self.category_map[concept] = category

    def add_movement(self, concept, date, amount, category):
        movement = Movement(concept, date, amount, category)
        self.total_expenses.at[category, 'total'] += float(amount)
        self.total += float(amount)
        self.category_map[concept] = category
        return movement
            
    def get_category(self, movement):
        if movement.concept in self.category_map:
            return self.category_map[movement.concept]
        else:
            return None
            
    def save_category_map(self):
        with open("category_map.json", "w") as file:
            json.dump(self.category_map, file)


    def load_category_map(self):
        try:
            with open("category_map.json", "r") as file:
                self.category_map = json.load(file)
            for concept, category in self.category_map.items():
                if category not in self.categories:
                    self.categories.add(category)
                    self.total_expenses[category] = 0
        except FileNotFoundError:
            pass