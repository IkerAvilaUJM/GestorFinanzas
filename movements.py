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

#############################################################
### ------------- CLASS FinanceTracker ------------------ ###
### Class to contain movements as formatted data
### The class main object is a dataframe wit the following columns:
###     - Concepto: str
###     - Categoria: str
###     - Importe: float
###     - Fecha: Date without time
### The class should contain the following methods:
###     - save_tracker: saves dataframe as json
###     - load_tracker: loads dataframe from json
###     - get_category_expenses: Return total amount for each category as a dataframe (index:category, column:total)
###     - get_daily_expenses: Return total amount for each day as dataframe (index:Fecha (Date), colum:total)
###             ·allow exclussion of certain categories (alquiler, salario, etc.)
###     - add_movement: Adds a movement to the dataframe given: (concept, date, amount, category)
###     - get_starting_date: returns the first (oldest) date in the dataframe: Date without time
###     - get_end_date: returns the last (newest) date in the dataframe: Date without time
### The class should overload the following methods:
###     - __init__: initializes the dataframe
###     - __add__: combines two dataframes, by adding the rows of one after the rows of the other
###     - __str__: returns a string stating it is a FinanceTracker object ranging from {starting_date} to {end_date}.

class FinanceTracker:
    def __init__(self, name=None):
        self.category_map = {}  # Dictionary to store concept-category mappings
        self.categories = ["alquiler", "suscripciones", "ropa", "deporte", "sueldo", "beca", "comer fuera",
                           "supermercado", "transporte", "ocio", "salud", "ropa", "mascotas", "paga",
                           "regalos", "viajes", "bares", "fiesta", "internet", "tecnologia", "otros"]
        # name of the Tracker if any
        self.name = name
        # Convert categories to list and sort
        self.categories = sorted(self.categories)
        # Initialize DataFrame with categories to store the total expense per category
        self.total_expenses = pd.DataFrame(0.0, index=self.categories, columns=["total"])
        # variable to store the final total expense
        self.total = 0.0
    
    def __str__(self):
        return f"{self.name}"
    
    def set_name(self, name):
        self.name = name

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
    
    def save_total_expenses(self):
        with open("total_expenses"+self.name+".json" ,"w") as file:
            json.dump(self.total_expenses, file)
    
    def load_total_expenses(self):
        try:
            with open("total_expenses"+self.name+".json" ,"r") as file:
                self.total_expenses = json.load(file)
        except FileNotFoundError:
            pass