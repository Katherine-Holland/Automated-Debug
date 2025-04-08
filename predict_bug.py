import tensorflow as tf
import joblib
import numpy as np

# Load the trained model and scaler
model = tf.keras.models.load_model('bug_predictor_model.keras')
scaler = joblib.load('bug_scaler.save')

# Example new input: headline_length, load_time_ms, missing_elements
new_data = np.array([[18, 1600, 2]])  # You can change this to test other values

# Scale the input using the same scaler from training
scaled_data = scaler.transform(new_data)

# Make prediction
prediction = model.predict(scaled_data)

# Output result
bug_likelihood = prediction[0][0]
if bug_likelihood > 0.5:
    print(f"⚠️ Likely bug detected! (Confidence: {bug_likelihood:.2f})")
else:
    print(f"✅ No bug likely. (Confidence: {bug_likelihood:.2f})")