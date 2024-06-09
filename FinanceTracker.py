import pandas as pd
import json
from datetime import datetime

class FinanceTracker:
    """
    A class to track financial movements with various functionalities such as saving, loading,
    and analyzing the movements data.

    Attributes:
        data (pd.DataFrame): A DataFrame containing financial movements with columns:
                             "Concepto", "Categoria", "Importe", "Fecha".
        concept_to_category (dict): A dictionary mapping concepts to categories.

    Methods:
        save_tracker(filepath): Saves the DataFrame to a JSON file.
        load_tracker(filepath): Loads the DataFrame from a JSON file.
        _update_concept_to_category(): Updates the concept to category mapping based on the current data.
        fill_from_excel_kutxabank(filepath): Fills the FinanceTracker data from an Excel file from Kutxabank.
        get_category_expenses(): Returns total amount for each category as a DataFrame.
        get_daily_expenses(exclude_categories=None): Returns total amount for each day as a DataFrame, with optional exclusion of categories.
        add_movement(concept, date, amount, category): Adds a movement to the DataFrame.
        get_starting_date(): Returns the oldest date in the DataFrame.
        get_end_date(): Returns the newest date in the DataFrame.
        __add__(other): Combines two FinanceTracker objects by adding the rows of one DataFrame to the other.
        __str__(): Returns a string representation of the FinanceTracker object.
        parse_date(date_str): Parses a date string to a datetime.date object.
    """

    def __init__(self):
        """
        Initializes the FinanceTracker with an empty DataFrame.
        """
        self.data = pd.DataFrame(columns=["Concepto", "Categoria", "Importe", "Fecha"])
        # Ensure 'Categoria' column has dtype 'object' to accommodate string values
        self.data["Categoria"] = self.data["Categoria"].astype(object)
        self.data["Fecha"] = pd.to_datetime(self.data["Fecha"]).dt.date
        self.add_movement("Tracker init", str(datetime.today()).split()[0], 0.0, "Otros")
        self.concept_to_category = {}


    def save_tracker(self, filepath):
        """
        Saves the DataFrame to a JSON file.
        
        Args:
            filepath (str): The path to the file where the DataFrame should be saved.
        """
        self.data.to_json(filepath, orient="records", date_format="iso")

    def load_tracker(self, filepath):
        """
        Loads the DataFrame from a JSON file.
        
        Args:
            filepath (str): The path to the file from where the DataFrame should be loaded.
        """
        self.data = pd.read_json(filepath, orient="records")
        try:
            self.data["Fecha"] = pd.to_datetime(self.data["Fecha"]).dt.date
            self._update_concept_to_category()
        except KeyError:
            pass

    def save_concept_to_category(self, filepath):
        """
        Saves the concept to category mapping to a JSON file.
        
        Args:
            filepath (str): The path to the file where the mapping should be saved.
        """
        with open(filepath, "r") as f:
            old = json.load(f)
        with open(filepath, "w") as f:
            self.concept_to_category = {**old, **self.concept_to_category}
            json.dump(self.concept_to_category, f)
    
    def load_concept_to_category(self, filepath):
        """
        Loads the concept to category mapping from a JSON file.
        
        Args:
            filepath (str): The path to the file from where the mapping should be loaded.
        """
        with open(filepath, "r") as f:
            self.concept_to_category = json.load(f)

    def _update_concept_to_category(self):
        """
        Updates the concept to category mapping based on the current data.
        """
        self.concept_to_category = self.data[self.data["Categoria"].notna()].set_index("Concepto")["Categoria"].to_dict()

    def fill_from_excel_kutxabank(self, filepath):
        """
        Fills the FinanceTracker data from an Excel file from Kutxabank.
        
        Args:
            filepath (str): The path to the Excel file.
        """
        # Load the Excel file
        df = pd.read_excel(filepath, skiprows=6)
        # Drop rows with any NaN values
        df = df.dropna()
        # Keep only the required columns
        df = df[["concepto", "fecha valor", "importe"]]
        # Rename the columns to match FinanceTracker data format
        df.columns = ["Concepto", "Fecha", "Importe"]
        # Convert the date column to datetime.date
        df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True).dt.date
        # Add a None category column
        df["Categoria"] = None
        # Assign the existing categories to new movements where applicable
        df["Categoria"] = df["Concepto"].map(self.concept_to_category)

        # check if the data has only the default entry with todays date and "Otros" category
        if self.data.shape[0] == 1 and self.data["Concepto"].iloc[0] == "Tracker init":
            self.data = df.copy()  # Replace the existing data with the new DataFrame
        # Check if both DataFrames contain non-empty data
        elif not df.empty:
            # Append the data to the FinanceTracker's data
            self.data = pd.concat([self.data, df], ignore_index=True)

        # Update the concept to category mapping
        self._update_concept_to_category()


    def get_category_expenses(self):
        """
        Returns the total amount for each category.
        
        Returns:
            pd.DataFrame: A DataFrame with categories as index and total amount as the column.
        """
        return self.data.groupby("Categoria")["Importe"].sum().reset_index().set_index("Categoria").rename(columns={"Importe": "Total"})

    def get_daily_expenses(self, exclude_categories=None):
        """
        Returns the total amount for each day, optionally excluding certain categories.
        
        Args:
            exclude_categories (list of str, optional): List of categories to exclude. Defaults to None.
            
        Returns:
            pd.DataFrame: A DataFrame with dates as index and total amount as the column.
        """
        df = self.data.copy()
        if exclude_categories:
            df = df[~df["Categoria"].isin(exclude_categories)]
        return df.groupby("Fecha")["Importe"].sum().reset_index().set_index("Fecha").rename(columns={"Importe": "Total"})

    def add_movement(self, concept, date, amount, category):
        """
        Adds a movement to the DataFrame.
        
        Args:
            concept (str): The concept of the movement.
            date (str or datetime.date): The date of the movement.
            amount (float): The amount of the movement.
            category (str): The category of the movement.
        """
        date = self.parse_date(date)
        if category is None and concept in self.concept_to_category:
            category = self.concept_to_category[concept]
        new_movement = pd.DataFrame([{"Concepto": concept, "Fecha": date, "Importe": amount, "Categoria": category}])
        if self.data.empty:
            self.data = new_movement
        else:
            self.data = pd.concat([self.data, new_movement], ignore_index=True)
        
        # Update the concept to category mapping
        self._update_concept_to_category()

    def update_category(self, concept, category):
        """
        Updates the category of a concept in the DataFrame.
        
        Args:
            concept (str): The concept to update.
            category (str): The new category for the concept.
        """
        # Ensure that the category is a string
        category = str(category)
        self.concept_to_category[concept] = category
        # Update the category in the DataFrame
        self.data['Categoria'] = self.data['Categoria'].astype(object)
        self.data.loc[self.data["Concepto"] == concept, "Categoria"] = str(category)
        # print(category)


    def get_starting_date(self):
        """
        Returns the first (oldest) date in the DataFrame.
        
        Returns:
            datetime.date: The oldest date in the DataFrame.
        """
        return self.data["Fecha"].min()

    def get_end_date(self):
        """
        Returns the last (newest) date in the DataFrame.
        
        Returns:
            datetime.date: The newest date in the DataFrame.
        """
        return self.data["Fecha"].max()
    
    def get_total_expenses_earnings(self):
        """
        Returns the total expenses and earnings in the DataFrame.
        
        Returns:
            tuple: A tuple containing the total expenses and earnings.
        """
        expenses = self.data[self.data["Importe"] < 0]["Importe"].sum()
        earnings = self.data[self.data["Importe"] > 0]["Importe"].sum()
        return expenses, earnings
    

    def __add__(self, other):
            """
            Combines two FinanceTracker objects by adding the rows of one DataFrame to the other.
            
            Args:
                other (FinanceTracker): Another FinanceTracker object.
                
            Returns:
                FinanceTracker: A new FinanceTracker object containing combined data.
            """
            combined = FinanceTracker()

            if self.data.empty:
                return other

            # Exclude empty or all-NA entries before concatenation
            self_non_empty = self.data.dropna(how='all', axis=0).reset_index(drop=True)
            other_non_empty = other.data.dropna(how='all', axis=0).reset_index(drop=True)

            combined.data = pd.concat([self_non_empty, other_non_empty]).reset_index(drop=True)
            combined._update_concept_to_category()
            return combined

    def __str__(self):
        """
        Returns a string representation of the FinanceTracker object.
        
        Returns:
            str: A string stating it is a FinanceTracker object ranging from the starting date to the end date.
        """
        start_date = self.get_starting_date()
        end_date = self.get_end_date()
        return f"FinanceTracker object ranging from {start_date} to {end_date}"

    @staticmethod
    def parse_date(date_str):
        """
        Parses a date string in various formats to a datetime.date object.
        
        Args:
            date_str (str): The date string to parse.
        
        Returns:
            datetime.date: The parsed date object.
        
        Raises:
            ValueError: If the date format is not supported.
        """
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Date format for '{date_str}' is not supported")

# Example usage:
# tracker = FinanceTracker()
# tracker.add_movement("Rent", "2024-05-07", 500.0, "Alquiler")
# tracker.add_movement("Salary", "07/05/2024", 2000.0, "Salario")
# print(tracker)
# tracker.save_tracker("tracker.json")
# tracker.load_tracker("tracker.json")
# print(tracker.get_category_expenses())
# print(tracker.get_daily_expenses(exclude_categories=["Salario"]))
# tracker.fill_from_excel_kutxabank("Movimientos Kutxabank/2023-04.xls")
# print(tracker)
