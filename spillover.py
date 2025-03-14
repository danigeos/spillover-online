import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit UI elements
st.title("Spillover: Water Transfer and Erosion between Lakes")

col1, col2, col3, col4 = st.columns(4)
with col1:
    H1_init = float(st.text_input("Initial Level Lake 1 (m)", "500"))
    H2_init = float(st.text_input("Initial Level Lake 2 (m)", "200"))
    H3_init = float(st.text_input("Initial Level Lake 3 (m)", "100"))
    H4_init = float(st.text_input("Initial Level Lake 4 (m)", "50"))
    total_time = float(st.text_input("Final Time (h)", "10")) * 3600
with col2:
    A1 = float(st.text_input("Area Lake 1 (m²)", "10e6"))
    A2 = float(st.text_input("Area Lake 2 (m²)", "10e6"))
    A3 = float(st.text_input("Area Lake 3 (m²)", "10e6"))
    A4 = float(st.text_input("Area Lake 4 (m²)", "10e6"))
with col3:
    H_thresh1 = float(st.text_input("Initial Threshold Level 1 (m)", "499"))
    H_thresh2 = float(st.text_input("Initial Threshold Level 2 (m)", "199"))
    H_thresh3 = float(st.text_input("Initial Threshold Level 3 (m)", "99"))
    distance1 = float(st.text_input("Distance Lake 1 - Lake 2 (m)", "500"))
    distance2 = float(st.text_input("Distance Lake 2 - Lake 3 (m)", "500"))
    distance3 = float(st.text_input("Distance Lake 3 - Lake 4 (m)", "500"))
with col4:
    erosion_factor1 = float(st.text_input("Erodability 1 (m yr-1 Pa-1.5)", "1e-4")) / 86400
    erosion_factor2 = float(st.text_input("Erodability 2 (m yr-1 Pa-1.5)", "1e-4")) / 86400
    erosion_factor3 = float(st.text_input("Erodability 3 (m yr-1 Pa-1.5)", "1e-4")) / 86400
    width_factor = float(st.text_input("Width factor", "5"))
    mannings_n = float(st.text_input("Manning's n", "0.03"))

# Constants
g = 9.81  # Gravity acceleration (m/s²)
iterations = 100001  # Fixed number of iterations

time_steps = np.linspace(0, float(total_time), iterations)

# Time evolution storage
H1 = [float(H1_init)]
H2 = [float(H2_init)]
H3 = [float(H3_init)]
H4 = [float(H4_init)]
Q1_values = []
Q2_values = []
Q3_values = []
H_thresh_values1 = [float(H_thresh1)]
H_thresh_values2 = [float(H_thresh2)]
H_thresh_values3 = [float(H_thresh3)]
erosion_rates1 = []
erosion_rates2 = []
erosion_rates3 = []
velocity_values1 = []
velocity_values2 = []
velocity_values3 = []

dt = float(total_time) / (iterations - 1)

for t in time_steps:
    # Compute slopes
    slope1 = (H1[-1] - H2[-1]) / distance1
    slope2 = (H2[-1] - H3[-1]) / distance2
    slope3 = (H3[-1] - H4[-1]) / distance3
    
    # Flow between Lake 1 and Lake 2 (allow bidirectional flow)
    if H1[-1] > H_thresh1 and H1[-1] > H2[-1]:
        depth1 = H1[-1] - H_thresh1
        width1 = width_factor * depth1
        hydraulic_radius1 = (depth1 * width1) / (width1 + 2 * depth1)
        velocity1 = (1 / mannings_n) * (hydraulic_radius1 ** (2/3)) * (abs(slope1) ** 0.5)
        Q1 = velocity1 * depth1 * width1
        shear_stress1 = 1000 * g * abs(slope1) * depth1
        erosion_rate1 = erosion_factor1 * (shear_stress1 ** 1.5)
        dH_thresh1 = erosion_rate1 * dt
        H_thresh1 -= dH_thresh1
    elif H2[-1] > H_thresh1 and H2[-1] > H1[-1]:  # Reverse flow from Lake 2 to Lake 1
        depth1 = H2[-1] - H_thresh1
        width1 = width_factor * depth1
        hydraulic_radius1 = (depth1 * width1) / (width1 + 2 * depth1)
        velocity1 = - (1 / mannings_n) * (hydraulic_radius1 ** (2/3)) * (abs(slope1) ** 0.5)
        Q1 = velocity1 * depth1 * width1
        shear_stress1 = 1000 * g * abs(slope1) * depth1
        erosion_rate1 = erosion_factor1 * (shear_stress1 ** 1.5)
        dH_thresh1 = erosion_rate1 * dt
        H_thresh1 -= dH_thresh1
    else:
        Q1, velocity1, erosion_rate1 = 0, 0, 0
    
    # Flow between Lake 2 and Lake 3 (allow bidirectional flow)
    if H2[-1] > H_thresh2 and H2[-1] > H3[-1]:
        depth2 = H2[-1] - H_thresh2
        width2 = width_factor * depth2
        hydraulic_radius2 = (depth2 * width2) / (width2 + 2 * depth2)
        velocity2 = (1 / mannings_n) * (hydraulic_radius2 ** (2/3)) * (abs(slope2) ** 0.5)
        Q2 = velocity2 * depth2 * width2
        shear_stress2 = 1000 * g * abs(slope2) * depth2
        erosion_rate2 = erosion_factor2 * (shear_stress2 ** 1.5)
        dH_thresh2 = erosion_rate2 * dt
        H_thresh2 -= dH_thresh2
    elif H3[-1] > H_thresh2 and H3[-1] > H2[-1]:  # Reverse flow from Lake 3 to Lake 2
        depth2 = H3[-1] - H_thresh2
        width2 = width_factor * depth2
        hydraulic_radius2 = (depth2 * width2) / (width2 + 2 * depth2)
        velocity2 = - (1 / mannings_n) * (hydraulic_radius2 ** (2/3)) * (abs(slope2) ** 0.5)
        Q2 = velocity2 * depth2 * width2
        shear_stress2 = 1000 * g * abs(slope2) * depth2
        erosion_rate2 = erosion_factor2 * (shear_stress2 ** 1.5)
        dH_thresh2 = erosion_rate2 * dt
        H_thresh2 -= dH_thresh2
    else:
        Q2, velocity2, erosion_rate2 = 0, 0, 0
    
    # Flow between Lake 3 and Lake 4 (allow bidirectional flow)
    if H3[-1] > H_thresh3 and H3[-1] > H4[-1]:
        depth3 = H3[-1] - H_thresh3
        width3 = width_factor * depth3
        hydraulic_radius3 = (depth3 * width3) / (width3 + 2 * depth3)
        velocity3 = (1 / mannings_n) * (hydraulic_radius3 ** (2/3)) * (abs(slope3) ** 0.5)
        Q3 = velocity3 * depth3 * width3
        shear_stress3 = 1000 * g * abs(slope3) * depth3
        erosion_rate3 = erosion_factor3 * (shear_stress3 ** 1.5)
        dH_thresh3 = erosion_rate3 * dt
        H_thresh3 -= dH_thresh3
    elif H4[-1] > H_thresh3 and H4[-1] > H3[-1]:  # Reverse flow from Lake 4 to Lake 3
        depth3 = H4[-1] - H_thresh3
        width3 = width_factor * depth3
        hydraulic_radius3 = (depth3 * width3) / (width3 + 2 * depth3)
        velocity3 = - (1 / mannings_n) * (hydraulic_radius3 ** (2/3)) * (abs(slope3) ** 0.5)
        Q3 = velocity3 * depth3 * width3
        shear_stress3 = 1000 * g * abs(slope3) * depth3
        erosion_rate3 = erosion_factor3 * (shear_stress3 ** 1.5)
        dH_thresh3 = erosion_rate3 * dt
        H_thresh3 -= dH_thresh3
    else:
        Q3, velocity3, erosion_rate3 = 0, 0, 0
    
    H1.append(H1[-1] - Q1 * dt / A1)
    H2.append(H2[-1] + (Q1 - Q2) * dt / A2)
    H3.append(H3[-1] + (Q2 - Q3) * dt / A3)
    H4.append(H4[-1] + Q3 * dt / A4)
    Q1_values.append(Q1)
    Q2_values.append(Q2)
    Q3_values.append(Q3)
    H_thresh_values1.append(H_thresh1)
    H_thresh_values2.append(H_thresh2)
    H_thresh_values3.append(H_thresh3)
    erosion_rates1.append(erosion_rate1)
    erosion_rates2.append(erosion_rate2)
    erosion_rates3.append(erosion_rate3)
    velocity_values1.append(velocity1)
    velocity_values2.append(velocity2)
    velocity_values3.append(velocity3)

# Plot results
fig, axs = plt.subplots(2, 1, figsize=(10, 10))

# First panel - Lake levels and thresholds
axs[0].plot(time_steps / 3600, H1[:-1], 'b-', label='Lake1')
axs[0].plot(time_steps / 3600, H2[:-1], 'r-', label='Lake2')
axs[0].plot(time_steps / 3600, H3[:-1], 'g-', label='Lake3')
axs[0].plot(time_steps / 3600, H4[:-1], 'y-', label='Lake4')
axs[0].plot(time_steps / 3600, H_thresh_values1[:-1], 'b--', label='Thres1')
axs[0].plot(time_steps / 3600, H_thresh_values2[:-1], 'r--', label='Thres2')
axs[0].plot(time_steps / 3600, H_thresh_values3[:-1], 'g--', label='Thres3')
axs[0].set_xlabel('Time (hours)')
axs[0].set_ylabel('Level (m)')
axs[0].legend()
axs[0].grid()

# Second panel - Discharge, Velocity, and Erosion rates with separate y-axes
ax1 = axs[1]
ax1.set_xlabel('Time (hours)')
ax1.set_ylabel('Discharge (m³/s)', color='b')
ax1.plot(time_steps / 3600, Q1_values, 'b-', label='Disch1')
ax1.plot(time_steps / 3600, Q2_values, 'b--', label='Disch2')
ax1.plot(time_steps / 3600, Q3_values, 'b:', label='Disch3')
ax1.tick_params(axis='y', labelcolor='b')
ax1.legend(loc='upper left')
ax1.grid()

ax2 = ax1.twinx()
ax2.set_ylabel('Velocity (m/s)', color='r')
ax2.plot(time_steps / 3600, velocity_values1, 'r-', label='Vel1')
ax2.plot(time_steps / 3600, velocity_values2, 'r--', label='Vel2')
ax2.plot(time_steps / 3600, velocity_values3, 'r:', label='Vel3')
ax2.tick_params(axis='y', labelcolor='r')
ax2.legend(loc='upper right')

ax3 = ax1.twinx()
ax3.spines['right'].set_position(('outward', 60))  # Offset third axis
ax3.set_ylabel('Erosion Rate (m/s)', color='g')
ax3.plot(time_steps / 3600, erosion_rates1, 'g-', label='Eros1')
ax3.plot(time_steps / 3600, erosion_rates2, 'g--', label='Eros2')
ax3.plot(time_steps / 3600, erosion_rates3, 'g:', label='Eros3')
ax3.tick_params(axis='y', labelcolor='g')
ax3.legend(loc='lower right')

st.pyplot(fig)
