import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit UI elements
st.title("Spillover: Water Transfer and Erosion between Lakes")

col1, col2, col3 = st.columns(3)
with col1:
    H1_init = float(st.text_input("Initial Level Lake 1 (m)", "500"))
    H2_init = float(st.text_input("Initial Level Lake 2 (m)", "200"))
    H_thresh = float(st.text_input("Initial Threshold Level (m)", "499"))
    distance_between_lakes = float(st.text_input("Distance (m)", "500"))
with col2:
    A1 = float(st.text_input("Area Lake 1 (m²)", "5e6"))
    A2 = float(st.text_input("Area Lake 2 (m²)", "10e6"))
    width_factor = float(st.text_input("Width factor", "5"))
with col3:
    total_time = float(st.text_input("Final Time (h)", "10")) * 3600
    erosion_factor = float(st.text_input("Erodaility (m yr-1 Pa-1.5)", "1e-4")) / 86400
    mannings_n = float(st.text_input("Manning's n", "0.03"))
 
# Constants
g = 9.81  # Gravity acceleration (m/s²)
iterations = 1001  # Fixed number of iterations

time_steps = np.linspace(0, float(total_time), iterations)

# Time evolution storage
H1 = [float(H1_init)]
H2 = [float(H2_init)]
Q_values = []
H_thresh_values = [float(H_thresh)]
erosion_rates = []
velocity_values = []

dt = float(total_time) / (iterations - 1)  # Compute dt based on total_time and iterations

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
        shear_stress = 1000 * g * slope * depth  # Approximate shear stress (Pa)
        erosion_rate = erosion_factor * (shear_stress ** 1.5)
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
fig, axs = plt.subplots(2, 1, figsize=(10, 10))

# Water levels plot
axs[0].plot(time_steps / 3600, H1[:-1], label='Lake 1 Level')
axs[0].plot(time_steps / 3600, H2[:-1], label='Lake 2 Level')
axs[0].plot(time_steps / 3600, H_thresh_values[:-1], label='Threshold')
axs[0].set_xlabel('Time (hours)')
axs[0].set_ylabel('Level (m)')
axs[0].legend()
axs[0].grid()

# Combined plot with different scales
twin_ax1 = axs[1].twinx()
twin_ax2 = axs[1].twinx()
twin_ax2.spines.right.set_position(("outward", 60))

axs[1].plot(time_steps / 3600, Q_values, color='blue')
twin_ax1.plot(time_steps / 3600, np.array(erosion_rates) / 1e3, color='green')
twin_ax2.plot(time_steps / 3600, velocity_values, color='purple')

axs[1].set_xlabel('Time (hours)')
axs[1].set_ylabel('Water Discharge (m³/s)', color='blue')
twin_ax1.set_ylabel('Erosion Rate (mm/s)', color='green')
twin_ax2.set_ylabel('Flow Velocity (m/s)', color='purple')

axs[1].legend(loc='upper left')
twin_ax1.legend(loc='upper center')
twin_ax2.legend(loc='upper right')
axs[1].grid()

st.pyplot(fig)

