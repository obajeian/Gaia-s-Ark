import sys
import os
import numpy as np
from pathlib import Path

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from carbon_model import CarbonModel

def analyze_model_performance():
    model = CarbonModel()
    
    # Load data
    print("Loading data...")
    data = model.load_data()
    if not data:
        print("No data found in database. Please ensure data_preprocessor.py has run.")
        return

    # Prepare features and target
    X, y, _ = model.prepare_features(data)
    
    # Calculate statistics
    mean_carbon = np.mean(y)
    min_carbon = np.min(y)
    max_carbon = np.max(y)
    std_carbon = np.std(y)
    
    mse = 1014.06 # User's reported value
    rmse = np.sqrt(mse)
    
    print(f"\n--- Data Statistics ---")
    print(f"Count: {len(y)} records")
    print(f"Mean Carbon Stock: {mean_carbon:.2f} tonnes")
    print(f"Range: {min_carbon:.2f} - {max_carbon:.2f} tonnes")
    print(f"Standard Deviation: {std_carbon:.2f}")
    
    print(f"\n--- Error Context ---")
    print(f"Reported MSE: {mse}")
    print(f"RMSE (Average Error): {rmse:.2f} tonnes")
    print(f"Error as % of Mean: {(rmse/mean_carbon)*100:.2f}%")
    
    if rmse < std_carbon:
        print("\nResult: The model is performing well (Error < Standard Deviation).")
    else:
        print("\nResult: The model performance is poor (Error > Standard Deviation).")

if __name__ == "__main__":
    analyze_model_performance()
