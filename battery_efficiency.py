import streamlit as st
import matplotlib.pyplot as plt

...  # [Omitted unchanged function definitions for brevity]

if st.button("Calculate Results"):
    fuel_saved_tonnes, energy_saved_mj, co2_saved_tonnes, eff_ratio = calculate_bess_efficiency(
        battery_energy_kwh, sfoc_tonnes_per_kwh, fuel_energy_density, co2_factor)
    cii = calculate_cii(fuel_consumed_annual, co2_factor, dwt, distance_nm)
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
        st.write(f"Payback Period: {int(payback)} years")
        st.subheader("Payback Progress Over Time")
        months = [m / 12 for m in range(1, int(payback * 12) + 2)]
        cumulative_savings = [annual_savings * (m / 12) for m in range(1, int(payback * 12) + 2)]
        capex_line = [capex] * len(months)
        fig1, ax1 = plt.subplots()
        ax1.plot(months, cumulative_savings, label='Cumulative Savings')
        ax1.plot(months, capex_line, '--', label='CAPEX')
        max_val = max(cumulative_savings)
        max_month = months[cumulative_savings.index(max_val)]
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

