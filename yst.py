# Import necessary libraries
import streamlit as st
import math
import numpy
import plotly
import pandas as pd
import plotly.express as px
import calendar
import plotly.graph_objects as go

# GHI values of Nigeria States using a 22-year climatology average (annual) from NASA (in kWh/m² per day)
ghi = {
    'Abia': 4.71, 'Adamawa': 5.70, 'Akwa Ibom': 4.21, 'Anambra': 4.81, 'Bauchi': 5.77, 'Bayelsa': 4.88,
    'Benue': 5.19, 'Borno': 5.90, 'Cross River': 4.74, 'Delta': 4.53, 'Ebonyi': 5.05, 'Edo': 4.66,
    'Ekiti': 4.94, 'Enugu': 4.92, 'FCT': 5.45, 'Gombe': 5.77, 'Imo': 4.71, 'Jigawa': 6.16, 'Kaduna': 5.64,
    'Kano': 5.87, 'Katsina': 5.94, 'Kebbi': 5.62, 'Kogi': 5.40, 'Kwara': 5.16, 'Lagos': 4.74, 'Nassarawa': 5.36,
    'Niger': 5.51, 'Ogun': 4.74, 'Ondo': 4.66, 'Osun': 4.89, 'Oyo': 5.11, 'Plateau': 5.52, 'Rivers': 4.13,
    'Sokoto': 6.24, 'Taraba': 5.53, 'Yobe': 6.11, 'Zamfara': 6.01
}

# Monthly variation factors (percentage)
monthly_variation_factors = {
    'January': 1.2, 'February': 1.1, 'March': 1.0, 'April': 0.8,
    'May': 0.7, 'June': 0.6, 'July': 0.5, 'August': 0.5,
    'September': 0.6, 'October': 0.8, 'November': 1.0, 'December': 1.1
}

# Function to calculate monthly PV potential
def calculate_pv_potential_monthly(state, panel_length, panel_width, panel_efficiency, inverter_efficiency):
    ghi_value = ghi[state]
    panel_area = panel_length * panel_width

    # Calculate monthly variation factors for the state
    monthly_factors = [monthly_variation_factors[month] for month in monthly_variation_factors]

    # Calculate monthly PV potential
    monthly_pv_potential = [ghi_value * panel_area * panel_efficiency * inverter_efficiency * factor
                            for factor in monthly_factors]

    return monthly_pv_potential

# Function to plot energy generation across months
def plot_generation_across_months(min_panels_across_months, monthly_potential, autonomy_days):
    # Get the number of days for each month
    days_in_month = [calendar.monthrange(2023, month)[1] for month in range(1, 13)]

    # Calculate total potential for each month based on the actual number of days
    total_potential = [min_panels_across_months * potential * days for potential, days in zip(monthly_potential, days_in_month)]

    # Create Plotly bar chart
    fig = go.Figure(data=[go.Bar(x=list(monthly_variation_factors.keys()), y=total_potential, marker_color='orange')])
    fig.update_layout(title='Monthly Energy Generation for Designed PV System',
                      xaxis_title='Month', yaxis_title='Energy Generation (kWh)',
                      hovermode='x unified', hoverlabel=dict(bgcolor="black", font_size=16))
    st.plotly_chart(fig)

# Streamlit UI for PV System Designer Setup
st.title("Solar Panel Analysis")

panel_length = st.number_input("Enter solar panel length in meters:")
panel_width = st.number_input("Enter solar panel width in meters:")
panel_efficiency = st.number_input("Enter solar panel efficiency in %:", min_value=0.0, max_value=100.0, value=15.0) / 100
inverter_efficiency = st.number_input("Enter estimated inverter efficiency in %:", min_value=0.0, max_value=100.0, value=90.0) / 100

state_options = list(ghi.keys())
state = st.selectbox("Select project state:", state_options)

monthly_pv_potential = calculate_pv_potential_monthly(state, panel_length, panel_width, panel_efficiency, inverter_efficiency)

# Plotting the monthly PV potential for a single panel
def plot_pv_potential(state, monthly_pv_potential):
    months = list(monthly_variation_factors.keys())

    # Create Plotly line chart
    fig = go.Figure(data=go.Scatter(x=months, y=monthly_pv_potential, mode='lines+markers', marker_color='orange'))
    fig.update_layout(title=f'PV Potential for a Single Panel in {state}',
                      xaxis_title='Month', yaxis_title='PV Potential (kWh/day)',
                      hovermode='x unified', hoverlabel=dict(bgcolor="black", font_size=16))
    st.plotly_chart(fig)

# Streamlit UI for Plotting PV potential
st.title("Average PV Potential for a Single Panel")

# Call the function to plot PV potential
plot_pv_potential(state, monthly_pv_potential)

# Streamlit UI for PV System Sizing
st.title("PV System Sizing")

# Input target energy for all months
daily_target_energy = st.number_input("Enter daily target energy (in kWh):", value=5.0)

# Determine the smallest PV potential and use it to calculate the number of panels needed
min_pv_potential = min(monthly_pv_potential)
min_panels_across_months = math.ceil(daily_target_energy / min_pv_potential)

st.write(f"Number of Panels Needed to Meet the Daily Target Across All Months: {min_panels_across_months} panels ({panel_length}m x {panel_width}m)")

# Solar bank details
autonomy_days = st.number_input("Enter number of autonomy days:", value=1)
battery_voltage = st.number_input("Enter solar bank voltage (for battery modules connected in parallel):", value=12.0)
depth_of_discharge = st.number_input("Enter depth of discharge of Solar Bank (in %):", value=50.0) / 100
battery_efficiency = st.number_input("Enter estimated bank efficiency when charging & discharging (in %):", value=85.0) / 100

# Calculate battery capacity needed
total_battery_capacity = math.ceil((((daily_target_energy * autonomy_days * 1000) / (battery_voltage)) * (1 / battery_efficiency) * (1 / depth_of_discharge)))

st.write(f"Target Autonomy Days: {autonomy_days} days")
st.write(f"Solar Bank Capacity Needed for Autonomy Days: {total_battery_capacity:.2f} Ah")

# User inputs for battery module
battery_capacity = st.number_input("Enter the capacity of a single battery module in the solar bank (in Ah):", value=100)

number_of_batteries = math.ceil(total_battery_capacity / battery_capacity)

st.write(f"Number of Batteries Needed for Solar Bank: {number_of_batteries} batteries (Rating: {battery_capacity}Ah, {battery_voltage}V)")

# Streamlit UI for Plotting Energy Generation Across Months
st.title("Energy Generation Across Months")

# Plotting the energy generation across all 12 months
plot_generation_across_months(min_panels_across_months, monthly_pv_potential, autonomy_days)

# Streamlit UI for PV System Cost Variables
st.title("PV System Cost Variables")

# PV System cost variables
solar_panel_costs = {'procurement': 0, 'installation': 0, 'maintenance': 0}
controller_costs = {'procurement': 0, 'installation': 0, 'maintenance': 0}
inverter_costs = {'procurement': 0, 'installation': 0, 'maintenance': 0}
battery_costs = {'procurement': 0, 'installation': 0, 'maintenance': 0}
misc_costs = {'procurement': 0, 'installation': 0, 'maintenance': 0}

# Input procurement costs
st.subheader("Procurement Costs")
solar_panel_costs['procurement'] = st.number_input("Unit cost of a solar panel (in naira): ")
controller_costs['procurement'] = st.number_input("Charge controller cost (in naira): ")
inverter_costs['procurement'] = st.number_input("Inverter cost (in naira): ")
battery_costs['procurement'] = st.number_input("Unit cost of a battery (in naira): ")
misc_costs['procurement'] = st.number_input("Miscellaneous procurement costs (in naira): ")

# Input installation costs
st.subheader("Installation Costs")
solar_panel_costs['installation'] = st.number_input("Installation cost per solar panel (in naira): ")
controller_costs['installation'] = st.number_input("Installation cost of charge controller (in naira): ")
inverter_costs['installation'] = st.number_input("Installation cost of inverter (in naira): ")
battery_costs['installation'] = st.number_input("Installation cost per battery (in naira): ")
misc_costs['installation'] = st.number_input("Miscellaneous installation costs (in naira): ")

# Calculate costs
solar_panel_procurement_cost = solar_panel_costs["procurement"] * min_panels_across_months
solar_panel_installation_cost = solar_panel_costs["installation"] * min_panels_across_months
controller_procurement_cost = controller_costs["procurement"]
controller_installation_cost = controller_costs["installation"]
inverter_procurement_cost = inverter_costs["procurement"]
inverter_installation_cost = inverter_costs["installation"]
battery_procurement_cost = battery_costs["procurement"] * number_of_batteries
battery_installation_cost = battery_costs["installation"] * number_of_batteries
misc_procurement_cost = misc_costs["procurement"]
misc_installation_cost = misc_costs["installation"]

# Calculate total costs
total_procurement_cost = solar_panel_procurement_cost + controller_procurement_cost + inverter_procurement_cost + battery_procurement_cost + misc_procurement_cost
total_installation_cost = solar_panel_installation_cost + controller_installation_cost + inverter_installation_cost + battery_installation_cost + misc_installation_cost
commission_cost = total_procurement_cost + total_installation_cost

st.write(f"Total Procurement Cost: ₦{total_procurement_cost:.2f}")
st.write(f"Total Installation Cost: ₦{total_installation_cost:.2f}")
st.write(f"Total Cost of setting up the PV system: ₦{commission_cost:.2f}")

# Input maintenance costs
st.subheader("Maintenance Costs")
solar_panel_costs['maintenance'] = st.number_input("Current maintenance cost per solar panel (in naira): ")
controller_costs['maintenance'] = st.number_input("Current maintenance cost of charge controller (in naira): ")
inverter_costs['maintenance'] = st.number_input("Current maintenance cost of inverter (in naira): ")
battery_costs['maintenance'] = st.number_input("Current maintenance cost per battery (in naira): ")
misc_costs['maintenance'] = st.number_input("Current miscellaneous maintenance costs (in naira): ")

# Calculate maintenance cost
solar_panel_maintenance_cost = solar_panel_costs["maintenance"] * min_panels_across_months
controller_maintenance_cost = controller_costs["maintenance"]
inverter_maintenance_cost = inverter_costs["maintenance"]
battery_maintenance_cost = battery_costs["maintenance"] * number_of_batteries
misc_maintenance_cost = misc_costs["maintenance"]

maintenance_cost = solar_panel_maintenance_cost + controller_maintenance_cost + inverter_maintenance_cost + battery_maintenance_cost + misc_maintenance_cost

st.write(f"Current rate of maintenance: ₦{maintenance_cost:.2f} per visit")

maintenance_rounds = st.number_input("Enter proposed number of maintenance visits per year: ")
warranty_years = st.number_input("Enter the number of warranty years (for maintenance only): ")
grid_rate = st.number_input("Enter the average price of grid electricity in project region (per kWh in naira): ")
inflation_rate = st.number_input("Enter the expected yearly inflation rate in %: ") / 100
num_years = st.number_input("Enter the number of years for price simulation: ", min_value=1, value=5, step=1)

usage_cost = maintenance_cost * maintenance_rounds

# Initialize empty cost table
pv_cost_table = []
grid_cost_table = []

# Calculate cost table
for i in range(num_years):
    # Calculate grid electricity cost
    if i == 0:
        grid_cost_table.append(daily_target_energy * grid_rate * 365)
    else:
        grid_cost_table.append(grid_cost_table[i-1] * (1 + inflation_rate))

    # Calculate PV electricity cost
    if warranty_years > 0 and i < warranty_years:
        pv_cost_table.append(0)  # First warranty_years are free
    else:
        if i >= warranty_years:
            # Continue with usage cost and inflation after warranty period ends
            pv_cost_table.append(usage_cost * (1 + inflation_rate)**i)
        else:
            # Continue with 0 cost during warranty period
            pv_cost_table.append(0)

# Create a list of dictionaries containing cost data for each year
cost_data = []
for i in range(num_years):
    year = i+1
    pv_cost = pv_cost_table[i]
    grid_cost = grid_cost_table[i]
    cost_data.append({'Year': year, 'PV Cost': pv_cost, 'Grid Cost': grid_cost})

# Create a pandas DataFrame from the cost data
cost_table = pd.DataFrame(cost_data)
cost_table = cost_table.round(2)

# Show the cost table
st.write(cost_table)

# Create the plotly figure
fig = px.line(cost_table, x='Year', y=['PV Cost', 'Grid Cost'],
              labels={'value': 'Cost (₦)', 'variable': 'Energy Source'},
              title=f'Annual Cost of Electricity: PV System vs Grid Supply over {num_years} Years')

# Customize the plotly figure
fig.update_traces(mode='markers+lines', hovertemplate='Year: %{x}<br>Cost: ₦%{y:.2f}<extra></extra>')
fig.update_layout(hovermode='x unified', hoverlabel=dict(bgcolor="black", font_size=16))
fig.update_xaxes(title_text='Year')
fig.update_yaxes(title_text='Cost (₦)', tickprefix='₦')

# Show the plotly figure
st.plotly_chart(fig)

# Calculate cumulative PV cost
pv_cost_table = []
for i in range(num_years):
    # Calculate PV electricity cost
    if warranty_years > 0 and i < warranty_years:
        pv_cost_table.append(0)  # First warranty_years are free
    else:
        if i >= warranty_years:
            # Continue with usage cost and inflation after warranty period ends
            pv_cost_table.append(usage_cost * (1 + inflation_rate)**i)
        else:
            # Continue with 0 cost during warranty period
            pv_cost_table.append(0)

if commission_cost is not None:
    pv_cost_table[0] += commission_cost

# Create a list of dictionaries containing cost data for each year
cost_data = []
for i in range(num_years):
    year = i+1
    pv_cost = pv_cost_table[i]
    grid_cost = grid_cost_table[i]
    cost_data.append({'Year': year, 'PV Cost': pv_cost, 'Grid Cost': grid_cost})

# Create a pandas DataFrame from the cost data
cost_table = pd.DataFrame(cost_data)
cost_table['Cumulative PV Cost'] = cost_table['PV Cost'].cumsum() # Add cumulative PV cost column
cost_table['Cumulative Grid Cost'] = cost_table['Grid Cost'].cumsum() # Add cumulative grid cost column

# Create the plotly figure
fig2 = px.line(cost_table, x='Year', y=['Cumulative PV Cost', 'Cumulative Grid Cost'],
              labels={'value': 'Cost (₦)', 'variable': 'Energy Source'},
              title=f'{num_years}-Year Cumulative Life Cycle Cost Comparison: PV System vs Grid Electricity')

# Customize the plotly figure
fig2.update_traces(mode='markers+lines', hovertemplate='Year: %{x}<br>Cost: ₦%{y:.2f}<extra></extra>')
fig2.update_layout(hovermode='x unified', hoverlabel=dict(bgcolor="black", font_size=16))
fig2.update_xaxes(title_text='Year')
fig2.update_yaxes(title_text='Cumulative Cost (₦)', tickprefix='₦')

# Show the plotly figure
st.plotly_chart(fig2)

# Streamlit UI for Carbon Emissions Assessment
st.title("Carbon Emissions Assessment")

# Carbon factors
grid_cf = 402  # gCO2/kWh
solar_cf = 41  # gCO2/kWh

# User input for number of years to assess carbon emissions
num_years = st.number_input("Enter the number of years for carbon emissions assessment: ", min_value=1, value=1, step=1)

# Calculate carbon emissions per day for each energy source
grid_emission = daily_target_energy * grid_cf / 1000  # kgCO2/day
solar_emission = daily_target_energy * solar_cf / 1000  # kgCO2/day

# Calculate total carbon emissions for each energy source over the given number of years
total_grid_emission = grid_emission * 365 * num_years  # kgCO2
total_solar_emission = solar_emission * 365 * num_years  # kgCO2

# Display total carbon emissions for each energy source
st.write(f"Total carbon emissions from Grid usage over {num_years} years: {total_grid_emission:.2f} kgCO2")
st.write(f"Total carbon emissions from PV System usage over {num_years} years: {total_solar_emission:.2f} kgCO2")

# Plot pie chart
data = {'Energy Source': ['Grid Electricity', 'PV System Solar Energy'],
        'Carbon Emission (kgCO2)': [total_grid_emission, total_solar_emission],
        'Color': ['#0077c2', '#FDB813']}
fig = px.pie(data, values='Carbon Emission (kgCO2)', names='Energy Source', color='Color')
fig.update_traces(textposition='inside', textinfo='percent+label', pull=[0.1, 0])

# Show the pie chart
st.plotly_chart(fig)
