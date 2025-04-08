import pandas as pd
import numpy as np

# Set a random seed for reproducibility
np.random.seed(42)

# Generate 50 sample data points
num_samples = 50
data = {
    "headline_length": np.random.randint(5, 100, size=num_samples),
    "load_time_ms": np.random.randint(200, 2000, size=num_samples),
    "missing_elements": np.random.randint(0, 5, size=num_samples),
    "bug_occurred": []
}

# Simple logic to simulate when a bug might occur
for i in range(num_samples):
    if data["headline_length"][i] < 20 or data["load_time_ms"][i] > 1500 or data["missing_elements"][i] >= 2:
        data["bug_occurred"].append(1)
    else:
        data["bug_occurred"].append(0)

# Create DataFrame and save as CSV
df = pd.DataFrame(data)
df.to_csv("synthetic_bug_data.csv", index=False)

print("Synthetic dataset saved as 'synthetic_bug_data.csv'")
