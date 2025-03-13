import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Constants
g = 9.81  # Gravity acceleration (m/s²)
mannings_n = 0.03  # Manning's roughness coefficient
  # Channel width is 5 times the flow depth
col1, col2, col3 = st.columns(3)
with col1:
    H1_init = st.text_input('Lake 1 Initial Level (m)', value='10')
    H1_init = float(H1_init)
    H2_init = st.text_input('Lake 2 Initial Level (m)', value='0')
    H2_init = float(H2_init)
    H_thresh = st.text_input('Threshold Initial Level (m)', value='9.5')
    H_thresh = float(H_thresh)
    distance_between_lakes = st.text_input('Distance between lakes (m)', value=100)
    distance_between_lakes = float(distance_between_lakes)
with col2:
    A1 = st.text_input('Lake 1 Area (km²)', value='1.0')
    A1 = float(A1) * 1e6
    A2 = st.text_input('Lake 2 Area (km²)', value='10.0')
    A2 = float(A2) * 1e6
    total_time = st.text_input('Total Simulation Time (hours)', value='2')
    total_time = float(total_time) * 3600
with col3:
    width_factor = st.text_input('Channel Width Factor', value='5')
    width_factor = int(width_factor)
    grainsize = st.text_input('Grain Size (m)', value='0.001')  #Mean sediment grain size (m)
    grainsize = float(grainsize)
    C_erosion = st.text_input('Erosion Coefficient', value='1e-9') #Erosion coefficient (m^(2m) * kg^(-m) * s^(1+2m)) (empirical)
    C_erosion = float(C_erosion)

# Total simulation time (seconds)
dt = total_time/1e4  # Time step (seconds)

# Sediment properties
rho_water = 1000  # Density of water (kg/m³)
rho_sediment = 2650  # Density of sediment (kg/m³)
theta_crit = 0.045  # Shields critical parameter
m_exponent = 1.5  # Erosion exponent


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
        hydraulic_radius = depth / (1 + 2/width)  # Approximate hydraulic radius
        velocity = (1 / mannings_n) * (hydraulic_radius ** (2/3)) * (slope ** 0.5)
        Q = velocity * depth * width  # Discharge (m³/s)
        
        # Compute shear stress
        shear_stress = rho_water * g * hydraulic_radius * slope  # (Pa)
        
        # Compute critical shear stress for sediment movement
        tau_crit = theta_crit * (rho_sediment - rho_water) * g * grainsize  # (Pa)
        
        # Compute erosion rate using direct shear stress model
        if shear_stress > tau_crit:
            erosion_rate = C_erosion * (grainsize ** (1 - m_exponent)) * ((shear_stress - tau_crit) ** m_exponent)  # (m/s)
        else:
            erosion_rate = 0
        
        # Lower the threshold due to erosion
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

# First plot: Water levels
axs[0].plot(time_steps / 3600, H1[:-1], label='Lake 1 Level (m)')
axs[0].plot(time_steps / 3600, H2[:-1], label='Lake 2 Level (m)')
axs[0].plot(time_steps / 3600, H_thresh_values[:-1], label='Threshold Level (m)', linestyle='--', color='gray')
axs[0].set_xlabel('Time (hours)')
axs[0].set_ylabel('Water Level (m)')
axs[0].legend()
axs[0].grid()

# Second plot: Water discharge, erosion rate, and velocity with multiple y-axes
ax1 = axs[1]
ax2 = ax1.twinx()
ax3 = ax1.twinx()

ax3.spines["right"].set_position(("outward", 60))  # Offset third axis for clarity

ax1.plot(time_steps / 3600, Q_values, color='blue')
ax2.plot(time_steps / 3600, erosion_rates / 1000, color='green')
ax3.plot(time_steps / 3600, velocity_values, color='purple')

ax1.set_xlabel('Time (hours)')
ax1.set_ylabel('Discharge (m³/s)', color='blue')
ax2.set_ylabel('Erosion Rate (mm/s)', color='green')
ax3.set_ylabel('Flow Velocity (m/s)', color='purple')

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
ax3.legend(loc="lower right")

ax1.grid()

plt.tight_layout()
st.pyplot(fig)
