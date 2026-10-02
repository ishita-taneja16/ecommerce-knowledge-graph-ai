import os
import pandas as pd

def get_data_dir(custom_path=None):
    if custom_path:
        return custom_path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "data")

def load_ecommerce_data(data_dir=None):
    """
    Loads all e-commerce CSV dataset files into pandas DataFrames.
    Returns a dictionary of entity DataFrames.
    """
    target_dir = get_data_dir(data_dir)
    
    files = {
        "brands": "brands.csv",
        "categories": "categories.csv",
        "vendors": "vendors.csv",
        "customers": "customers.csv",
        "products": "products.csv",
        "orders": "orders.csv",
    }
    
    data = {}
    for key, filename in files.items():
        file_path = os.path.join(target_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Required CSV data file not found: {file_path}")
        data[key] = pd.read_csv(file_path, dtype=str)
        
    return data
