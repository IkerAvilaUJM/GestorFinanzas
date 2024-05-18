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

    Methods:
        save_tracker(filepath): Saves the DataFrame to a JSON file.
        load_tracker(filepath): Loads the DataFrame from a JSON file.
        get_category_expenses(): Returns total amount for each category as a DataFrame.
        get_daily_expenses(exclude_categories=None): Returns total amount for each day as a DataFrame, with optional exclusion of categories.
        add_movement(concept, date, amount, category): Adds a movement to the DataFrame.
        get_starting_date(): Returns the oldest date in the DataFrame.
        get_end_date(): Returns the newest date in the DataFrame.
        parse_date(date_str): Parses a date string to a datetime.date object.
    """

    def __init__(self):
        """
        Initializes the FinanceTracker with an empty DataFrame.
        """
        self.data = pd.DataFrame(columns=["Concepto", "Categoria", "Importe", "Fecha"])
        self.data["Fecha"] = pd.to_datetime(self.data["Fecha"]).dt.date

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
        self.data["Fecha"] = pd.to_datetime(self.data["Fecha"]).dt.date

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
        # Append the data to the FinanceTracker's data
        self.data = pd.concat([self.data, df], ignore_index=True)

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
        self.data = self.data.append({"Concepto": concept, "Fecha": date, "Importe": amount, "Categoria": category}, ignore_index=True)

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

    def __add__(self, other):
        """
        Combines two FinanceTracker objects by adding the rows of one DataFrame to the other.
        
        Args:
            other (FinanceTracker): Another FinanceTracker object.
            
        Returns:
            FinanceTracker: A new FinanceTracker object containing combined data.
        """
        combined = FinanceTracker()
        combined.data = pd.concat([self.data, other.data]).reset_index(drop=True)
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
