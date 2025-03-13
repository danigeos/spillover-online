import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit UI elements
st.title("Spillover: Simulation of Water Transfer and Erosion between Lakes")

col1, col2, col3 = st.columns(3)
with col1:
    mannings_n = st.slider("Manning's n", 0.01, 0.1, 0.03, 0.005)
    width_factor = st.slider("Width Factor", 1, 10, 5, 1)
with col2:
    distance_between_lakes = st.slider("Lake Distance (m)", 500, 5000, 1000, 100)
    erosion_factor = st.slider("Erosion Rate", 0.001, 0.1, 0.01, 0.001)
with col3:
    total_time = st.slider("Simulation Time (s)", 10000, 100000, 36000, 5000)
    dt = st.slider("Time Step (s)", 1, 60, 10, 1)

# Constants
g = 9.81  # Gravity acceleration (m/s²)

# Lake properties
A1 = 1e6  # Surface area of Lake 1 (m²)
A2 = 0.8e6  # Surface area of Lake 2 (m²)
H1_init = 10  # Initial level of Lake 1 (m)
H2_init = 5  # Initial level of Lake 2 (m)
H_thresh = 9  # Initial threshold level between the lakes (m)

# Time evolution storage
time_steps = np.arange(0, total_time, dt)
H1 = [H1_init]
H2 = [H2_init]
Q_values = []
H_thresh_values = [H_thresh]
erosion_rates = []
velocity_values = []

for t in time_steps:
    # Compute slope dynamically
    slope = max((H1[-1] - H2[-1]) / distance_between_lakes, 0)  # Ensure non-negative slope
    
    # Compute flow only if lake 1 is above the threshold
    if H1[-1] > H_thresh:
        depth = H1[-1] - H_thresh  # Flow depth
        width = width_factor * depth  # Channel width
        hydraulic_radius = (depth * width) / (width + 2 * depth)  # Improved hydraulic radius calculation
        velocity = (1 / mannings_n) * (hydraulic_radius ** (2/3)) * (slope ** 0.5)
        Q = velocity * depth * width  # Discharge (m³/s)
        
        # Lower the threshold due to erosion
        erosion_rate = erosion_factor * slope * depth * velocity
        dH_thresh = erosion_rate * dt
        H_thresh -= dH_thresh
    else:
        Q = 0  # No flow if lake 1 is below the threshold
        erosion_rate = 0
        velocity = 0
    
    # Compute level changes
    dH1 = -Q * dt / A1  # Change in Lake 1 level
    dH2 = Q * dt / A2  # Change in Lake 2 level
    
    H1.append(H1[-1] + dH1)
    H2.append(H2[-1] + dH2)
    Q_values.append(Q)
    H_thresh_values.append(H_thresh)
    erosion_rates.append(erosion_rate)
    velocity_values.append(velocity)

# Plot results
st.subheader("Simulation Results")
fig, axs = plt.subplots(2, 1, figsize=(10, 10))

# Water levels plot
axs[0].plot(time_steps / 3600, H1[:-1], label='Lake 1 Level (m)')
axs[0].plot(time_steps / 3600, H2[:-1], label='Lake 2 Level (m)')
axs[0].set_xlabel('Time (hours)')
axs[0].set_ylabel('Water Level (m)')
axs[0].legend()
axs[0].grid()

# Combined plot (Water Discharge, Erosion Rate, Flow Velocity)
axs[1].plot(time_steps / 3600, Q_values, label='Water Discharge (m³/s)', color='blue')
axs[1].plot(time_steps / 3600, erosion_rates, label='Erosion Rate (m/s)', color='green')
axs[1].plot(time_steps / 3600, velocity_values, label='Flow Velocity (m/s)', color='purple')
axs[1].set_xlabel('Time (hours)')
axs[1].set_ylabel('Value')
axs[1].legend()
axs[1].grid()

st.pyplot(fig)
