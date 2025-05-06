import streamlit as st
import matplotlib.pyplot as plt

def calculate_bess_efficiency(battery_energy_kwh, sfoc_tonnes_per_kwh, fuel_energy_density_mj_per_tonne, co2_emission_factor_tonnes_per_tonnefuel):
    fuel_saved_tonnes = battery_energy_kwh * sfoc_tonnes_per_kwh
    energy_saved_mj = fuel_saved_tonnes * fuel_energy_density_mj_per_tonne
    co2_saved_tonnes = fuel_saved_tonnes * co2_emission_factor_tonnes_per_tonnefuel
    battery_energy_mj = battery_energy_kwh * 3.6
    efficiency_ratio = energy_saved_mj / battery_energy_mj if battery_energy_mj > 0 else 0
    return fuel_saved_tonnes, energy_saved_mj, co2_saved_tonnes, efficiency_ratio

def calculate_cii(fc_j_tonnes, cf_j, dwt, distance_nm):
    m = fc_j_tonnes * 1000 * cf_j
    w = dwt * distance_nm
    return m / w if w > 0 else 0

def get_cii_rating(cii):
    if cii < 4:
        return "A"
    elif cii < 6:
        return "B"
    elif cii < 9:
        return "C"
    elif cii < 12:
        return "D"
    else:
        return "E"

def calculate_roi(fuel_saved_tpd, fuel_price_per_tonne, capex, opex_per_year):
    daily_net_savings = (fuel_saved_tpd * fuel_price_per_tonne) - (opex_per_year / 300)
    if daily_net_savings <= 0:
        return 0, float('inf')
    annual_savings = daily_net_savings * 300
    payback = capex / annual_savings
    return annual_savings, payback

def calculate_eexi(p_me, sfoc_me, cf, v_ref, dwt, eexi_ref):
    numerator = p_me * sfoc_me * cf
    denominator = v_ref * dwt
    attained = numerator / denominator if denominator > 0 else 0
    return attained, attained <= eexi_ref

def estimate_savings_percent_model(original_consumption_tpd, saving_percent, fuel_price_per_tonne):
    daily_savings = original_consumption_tpd * (saving_percent / 100)
    annual_savings_tonnes = daily_savings * 300
    cost_savings = annual_savings_tonnes * fuel_price_per_tonne
    return daily_savings, annual_savings_tonnes, cost_savings

# === Inputs ===
st.title("Battery Efficiency & IMO Performance Calculator")

battery_energy_kwh = st.number_input("Battery Energy (kWh/day)", value=1200)
sfoc_tonnes_per_kwh = st.number_input("SFOC (tonnes/kWh)", value=0.00022, format="%f")
fuel_energy_density = st.number_input("Fuel Energy Density (MJ/tonne)", value=42700)
co2_factor = st.number_input("CO₂ Factor (tCO₂/t fuel)", value=3.17)

fuel_consumed_annual = st.number_input("Annual Fuel Consumption (tonnes)", value=31200)
dwt = st.number_input("Deadweight (DWT)", value=61614)
distance_nm = st.number_input("Annual Distance Sailed (NM)", value=100000.0)

fuel_price = st.number_input("Fuel Price (USD/tonne)", value=601.0)
capex = st.number_input("CAPEX (USD)", value=800000)
opex = st.number_input("OPEX/year (USD)", value=12000)

p_me = st.number_input("Main Engine Power (kW)", value=23000)
sfoc_me = st.number_input("Main Engine SFOC (g/kWh)", value=170)
cf_eexi = st.number_input("Fuel CO₂ Factor (g/g)", value=3.114)
v_ref = st.number_input("Reference Speed (knots)", value=18.5)
eexi_ref = st.number_input("IMO Reference EEXI", value=16.5)

saving_percent = st.slider("Fuel Saving Percentage (Estimate)", min_value=0, max_value=20, value=10)
original_consumption_tpd = st.number_input("Original Fuel Consumption (tonnes/day)", value=104.0)

fuel_saved_tpd = 1.28  # Fixed based on auxiliary savings (10%)

# === Calculations ===
if st.button("Calculate Results"):
    fuel_saved_tonnes, energy_saved_mj, co2_saved_tonnes, eff_ratio = calculate_bess_efficiency(
        battery_energy_kwh, sfoc_tonnes_per_kwh, fuel_energy_density, co2_factor)
    adjusted_fuel_consumption = fuel_consumed_annual - (fuel_saved_tpd * 300)
    cii = calculate_cii(adjusted_fuel_consumption, co2_factor, dwt, distance_nm)
    cii_rating = get_cii_rating(cii)
    annual_savings, payback = calculate_roi(fuel_saved_tpd, fuel_price, capex, opex)
    eexi, compliance = calculate_eexi(p_me, sfoc_me, cf_eexi, v_ref, dwt, eexi_ref)
    daily_savings, annual_savings_tonnes, cost_savings = estimate_savings_percent_model(
        original_consumption_tpd, saving_percent, fuel_price)

    st.subheader("Battery Efficiency")
    st.write(f"Fuel Saved: {fuel_saved_tonnes:.2f} tonnes/day")
    st.write(f"Energy Saved: {energy_saved_mj:.2f} MJ/day")
    st.write(f"CO₂ Saved: {co2_saved_tonnes:.2f} tonnes/day")
    st.write(f"Efficiency Ratio: {eff_ratio:.2f} MJ/MJ")

    st.subheader("Carbon Intensity Indicator (CII)")
    st.write(f"Attained CII: {cii:.6f} gCO₂/DWT·nm")
    st.write(f"Estimated Rating: {cii_rating}")

    st.subheader("Return on Investment (ROI)")
    st.write(f"Annual Net Savings (after OPEX): ${annual_savings:,.2f}")
    if payback != float('inf'):
        st.write(f"Payback Period: {payback:.2f} years")
        months = [m / 12 for m in range(1, int(payback * 12) + 2)]
        cumulative_savings = [annual_savings * (m / 12) for m in range(1, int(payback * 12) + 2)]
        capex_line = [capex] * len(months)
        fig1, ax1 = plt.subplots()
        ax1.plot(months, cumulative_savings, label='Cumulative Savings')
        ax1.plot(months, capex_line, '--', label='CAPEX')
        ax1.axhline(y=capex, color='gray', linestyle='--')
        ax1.axvline(x=payback, color='gray', linestyle='--')
        ax1.text(payback, capex, f"Payback: {payback:.2f} yrs", ha='left', va='bottom')
        ax1.set_xlabel("Years")
        ax1.set_ylabel("USD")
        ax1.set_title("Payback Over Time")
        ax1.legend()
        st.pyplot(fig1)
    else:
        st.warning("Payback period is infinite — savings never recover CAPEX.")

    st.subheader("Fuel & CO₂ Savings")
    fig2, ax2 = plt.subplots()
    bars = [original_consumption_tpd, fuel_saved_tpd, co2_saved_tonnes]
    labels = ['Original Fuel Use (t/d)', 'Fuel Saved (t/d)', 'CO₂ Saved (t/d)']
    ax2.bar(labels, bars, color=['gray', 'green', 'blue'])
    for i, val in enumerate(bars):
        ax2.text(i, val + 0.5, f"{val:.1f}", ha='center')
    ax2.set_ylabel("Tonnes per Day")
    st.pyplot(fig2)

    st.subheader("EEXI Attainment vs IMO Standard")
    fig3, ax3 = plt.subplots()
    eexi_vals = [eexi, eexi_ref]
    bars3 = ax3.bar(['Attained EEXI', 'IMO Reference'], eexi_vals, color=['orange', 'red'])
    for bar in bars3:
        yval = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, f"{yval:.2f}", ha='center')
    ax3.set_ylabel("gCO₂/ton·nm")
    st.pyplot(fig3)

    st.subheader("Energy Efficiency Existing Ship Index (EEXI)")
    st.write(f"Attained EEXI: {eexi:.2f} gCO₂/ton·nm")
    st.write(f"IMO Compliant: {'Yes' if compliance else 'No'}")

    st.subheader("Percent-Based Fuel & Cost Savings Estimate")
    st.write(f"Daily Fuel Savings: {daily_savings:.2f} tonnes")
    st.write(f"Annual Fuel Savings: {annual_savings_tonnes:.2f} tonnes")
    st.write(f"Estimated Annual Cost Savings: ${cost_savings:,.2f}")

st.markdown("---")
st.markdown("**MAR 8088 - Group Project - Team A**")

