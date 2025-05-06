import streamlit as st
import matplotlib.pyplot as plt

def calculate_bess_efficiency(battery_energy_kwh, sfoc_tonnes_per_kwh, fuel_energy_density_mj_per_tonne, co2_emission_factor_tonnes_per_tonnefuel):
    fuel_saved_tonnes = battery_energy_kwh * sfoc_tonnes_per_kwh
    energy_saved_mj = fuel_saved_tonnes * fuel_energy_density_mj_per_tonne
    co2_saved_tonnes = fuel_saved_tonnes * co2_emission_factor_tonnes_per_tonnefuel
    battery_energy_mj = battery_energy_kwh * 3.6
    efficiency_ratio = energy_saved_mj / battery_energy_mj if battery_energy_mj > 0 else 0
    return fuel_saved_tonnes, energy_saved_mj, co2_saved_tonnes, efficiency_ratio

# (rest of code continues...)