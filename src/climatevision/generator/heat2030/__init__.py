"""
Documentation =
https://localzero-generator.readthedocs.io/de/latest/sectors/heat.html
"""

# pyright: strict

from ..inputs import Inputs
from ..utils import div, MILLION
from ..heat2018.h18 import H18
from ..residences2030.r30 import R30
from ..business2030.b30 import B30
from ..agri2030.a30 import A30
from ..industry2030.i30 import I30
from ..electricity2030.electricity2030_core import EColVars2030

from .h30 import H30
from .dataclasses import (
    Vars0,
    Vars1,
    Vars2,
    Vars3,
    Vars4,
    Vars5,
    Vars6,
    Vars7,
    Vars8,
    Vars9,
    Vars10,
    Vars11,
    Vars12,
    Vars13,
    Vars14,
    Vars15,
)


def calc(
    inputs: Inputs,
    *,
    h18: H18,
    r30: R30,
    b30: B30,
    a30: A30,
    i30: I30,
    p_local_biomass_cogen: EColVars2030,
) -> H30:
    fact = inputs.fact
    ass = inputs.ass
    entries = inputs.entries

    h = Vars0()
    g = Vars1()
    g_storage = Vars2()
    g_planning = Vars3()
    d = Vars4()
    d_r = Vars4()
    d_b = Vars4()
    d_i = Vars4()
    d_a = Vars4()
    d_t = Vars4()
    p = Vars5()
    p_gas = Vars6()
    p_lpg = Vars7()
    p_fueloil = Vars8()
    p_opetpro = Vars9()
    p_coal = Vars6()
    p_heatnet = Vars10()
    p_heatnet_cogen = Vars9()
    p_heatnet_plant = Vars11()
    p_heatnet_lheatpump = Vars12()
    p_heatnet_geoth = Vars13()
    p_biomass = Vars14()
    p_ofossil = Vars15()
    p_orenew = Vars15()
    p_solarth = Vars15()
    p_heatpump = Vars15()

    ###########################
    ### Demand of Heat 2018 ###
    ###########################

    p_gas.CO2e_production_based_per_MWh = h18.p_gas.CO2e_production_based_per_MWh
    p_gas.CO2e_combustion_based_per_MWh = h18.p_gas.CO2e_combustion_based_per_MWh
    p_gas.energy = r30.s_gas.energy + b30.s_gas.energy
    p_gas.CO2e_production_based = p_gas.energy * p_gas.CO2e_production_based_per_MWh
    p_lpg.energy = r30.s_lpg.energy + b30.s_lpg.energy
    p_gas.CO2e_combustion_based = p_gas.CO2e_combustion_based_per_MWh * p_gas.energy
    p_gas.CO2e_total = p_gas.CO2e_production_based + p_gas.CO2e_combustion_based
    p.CO2e_total_2021_estimated = h18.p.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_lpg.CO2e_combustion_based_per_MWh = h18.p_lpg.CO2e_combustion_based_per_MWh
    g_storage.invest_per_x = fact("Fact_H_P_storage_specific_cost")

    g_planning.invest = (
        fact("Fact_H_P_planning_cost_basis")
        + fact("Fact_H_P_planning_cost_per_capita") * entries.m_population_com_2018
    )
    g_planning.invest_pa = g_planning.invest / entries.m_duration_target
    p_heatnet.energy = (
        r30.s_heatnet.energy + b30.s_heatnet.energy + i30.s_renew_heatnet.energy
    )
    g_storage.energy = p_heatnet.energy
    g_storage.pct_energy = fact("Fact_H_P_storage_specific_volume")
    g_storage.power_to_be_installed = g_storage.energy * g_storage.pct_energy
    p_heatnet_plant.invest_per_x = fact("Fact_H_P_heatnet_solarth_park_invest_203X")
    g_storage.invest = g_storage.invest_per_x * g_storage.power_to_be_installed
    p_heatnet_lheatpump.invest_per_x = fact("Fact_H_P_heatnet_lheatpump_invest_203X")
    g_storage.invest_com = g_storage.invest

    p_heatnet_plant.pct_energy = ass("Ass_H_P_heatnet_fraction_solarth_2050")

    p_heatnet_cogen.energy = (
        p_local_biomass_cogen.energy
        if (p_local_biomass_cogen.energy < p_heatnet.energy)
        else p_heatnet.energy
    )
    p_heatnet_plant.energy = (
        (p_heatnet.energy - p_heatnet_cogen.energy) * p_heatnet_plant.pct_energy
        if (p_heatnet_cogen.energy < p_heatnet.energy)
        else 0
    )
    g_planning.invest_com = g_planning.invest

    g_storage.invest_pa = g_storage.invest / entries.m_duration_target
    g_planning.invest_pa_com = g_planning.invest_pa

    g_storage.invest_pa_com = g_storage.invest_pa

    g_storage.pct_of_wage = fact("Fact_B_P_constr_main_revenue_pct_of_wage_2017")
    g.invest_com = g_storage.invest_com + g_planning.invest_com
    g_storage.ratio_wage_to_emplo = fact(
        "Fact_B_P_constr_main_ratio_wage_to_emplo_2017"
    )
    g_planning.cost_wage = g_planning.invest / fact("Fact_H_P_planning_duration")
    g_storage.cost_wage = g_storage.pct_of_wage * g_storage.invest_pa
    g_planning.ratio_wage_to_emplo = ass("Ass_T_C_yearly_costs_per_planer")
    g_storage.demand_emplo = div(g_storage.cost_wage, g_storage.ratio_wage_to_emplo)
    g_planning.demand_emplo = div(g_planning.cost_wage, g_planning.ratio_wage_to_emplo)
    g.invest_pa_com = g_storage.invest_pa_com + g_planning.invest_pa_com
    g_storage.demand_emplo_new = g_storage.demand_emplo

    g.invest_pa = g_storage.invest_pa + g_planning.invest_pa
    p_heatnet_plant.area_ha_available = p_heatnet_plant.energy / fact(
        "Fact_H_P_heatnet_solarth_park_yield_2025"
    )
    g.invest = g_storage.invest + g_planning.invest
    p_heatnet_plant.invest = (
        p_heatnet_plant.invest_per_x * p_heatnet_plant.area_ha_available
    )
    g_planning.pct_of_wage = ass("Ass_H_G_planning_cost_pct_of_wage")
    g.cost_wage = g_storage.cost_wage + g_planning.cost_wage
    g_planning.demand_emplo_new = g_planning.demand_emplo
    g.demand_emplo = g_storage.demand_emplo + g_planning.demand_emplo
    g.demand_emplo_new = g_storage.demand_emplo_new + g_planning.demand_emplo_new
    d_r.energy = (
        r30.s_biomass.energy
        + r30.s_heatnet.energy
        + r30.s_solarth.energy
        + r30.s_heatpump.energy
    )
    d_b.energy = (
        b30.s_biomass.energy
        + b30.s_heatnet.energy
        + b30.s_heatpump.energy
        + b30.s_solarth.energy
    )
    d_i.energy = i30.s_renew_biomass.energy + i30.s_renew_heatnet.energy
    d_a.energy = a30.s_biomass.energy + a30.s_heatpump.energy
    d_t.energy = 0.0
    d.energy = d_r.energy + d_b.energy + d_i.energy + d_a.energy
    p_heatnet_lheatpump.pct_energy = ass("Ass_H_P_heatnet_fraction_lheatpump_2050")
    p_fueloil.energy = r30.s_fueloil.energy + b30.s_fueloil.energy
    p_opetpro.energy = 0
    p_gas.cost_fuel_per_MWh = ass("Ass_R_S_gas_energy_cost_factor_2035")
    p_opetpro.CO2e_production_based_per_MWh = (
        h18.p_opetpro.CO2e_production_based_per_MWh
    )

    p_lpg.CO2e_combustion_based = p_lpg.CO2e_combustion_based_per_MWh * p_lpg.energy
    p_lpg.CO2e_total = p_lpg.CO2e_combustion_based
    p_coal.energy = r30.s_coal.energy + b30.s_coal.energy
    p_biomass.energy = (
        r30.s_biomass.energy
        + b30.s_biomass.energy
        + i30.s_renew_biomass.energy
        + a30.s_biomass.energy
    )
    p_fueloil.CO2e_combustion_based_per_MWh = (
        h18.p_fueloil.CO2e_combustion_based_per_MWh
    )
    p_fueloil.CO2e_combustion_based = (
        p_fueloil.CO2e_combustion_based_per_MWh * p_fueloil.energy
    )
    h.CO2e_total_2021_estimated = p.CO2e_total_2021_estimated

    p_fueloil.CO2e_total = p_fueloil.CO2e_combustion_based

    p_heatnet_lheatpump.full_load_hour = fact(
        "Fact_H_P_heatnet_lheatpump_full_load_hours"
    )
    p_heatnet_lheatpump.energy = (
        (p_heatnet.energy - p_heatnet_cogen.energy) * p_heatnet_lheatpump.pct_energy
        if (p_heatnet_cogen.energy < p_heatnet.energy)
        else 0
    )
    p_heatnet_geoth.invest_per_x = fact("Fact_H_P_heatnet_geoth_invest_203X")
    p_heatnet_geoth.full_load_hour = fact("Fact_H_P_heatnet_geoth_full_load_hours")
    p_heatnet_lheatpump.pct_of_wage = fact(
        "Fact_B_P_constr_main_revenue_pct_of_wage_2017"
    )
    p_heatnet_lheatpump.power_to_be_installed = div(
        p_heatnet_lheatpump.energy, p_heatnet_lheatpump.full_load_hour
    )
    p_heatnet_plant.invest_pa = p_heatnet_plant.invest / entries.m_duration_target
    p_heatnet_lheatpump.invest = (
        p_heatnet_lheatpump.invest_per_x * p_heatnet_lheatpump.power_to_be_installed
    )
    p_solarth.energy = r30.s_solarth.energy + b30.s_solarth.energy
    p_heatpump.energy = (
        r30.s_heatpump.energy + b30.s_heatpump.energy + a30.s_heatpump.energy
    )
    p_fueloil.cost_fuel_per_MWh = ass("Ass_R_S_fueloil_energy_cost_factor_2035")
    p_gas.cost_fuel = p_gas.energy * p_gas.cost_fuel_per_MWh / MILLION
    p_opetpro.CO2e_production_based = (
        p_opetpro.energy * p_opetpro.CO2e_production_based_per_MWh
    )
    p_opetpro.CO2e_combustion_based_per_MWh = (
        h18.p_opetpro.CO2e_combustion_based_per_MWh
    )
    p_opetpro.CO2e_combustion_based = (
        p_opetpro.CO2e_combustion_based_per_MWh * p_opetpro.energy
    )
    p_opetpro.CO2e_total = (
        p_opetpro.CO2e_production_based + p_opetpro.CO2e_combustion_based
    )
    p_coal.CO2e_production_based_per_MWh = h18.p_coal.CO2e_production_based_per_MWh
    p_gas.change_energy_MWh = p_gas.energy - h18.p_gas.energy
    p_gas.change_energy_pct = div(p_gas.change_energy_MWh, h18.p_gas.energy)
    p_gas.change_CO2e_t = p_gas.CO2e_total - h18.p_gas.CO2e_total
    p_gas.change_CO2e_pct = div(p_gas.change_CO2e_t, h18.p_gas.CO2e_total)
    p_gas.CO2e_total_2021_estimated = h18.p_gas.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_gas.cost_climate_saved = (
        (p_gas.CO2e_total_2021_estimated - p_gas.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p_orenew.energy = p_solarth.energy + p_heatpump.energy
    p_ofossil.energy = 0
    p_coal.CO2e_production_based = p_coal.energy * p_coal.CO2e_production_based_per_MWh
    p_coal.CO2e_combustion_based_per_MWh = h18.p_coal.CO2e_combustion_based_per_MWh

    p_coal.CO2e_combustion_based = p_coal.CO2e_combustion_based_per_MWh * p_coal.energy
    p_lpg.change_energy_MWh = p_lpg.energy - h18.p_lpg.energy
    p_lpg.change_energy_pct = div(p_lpg.change_energy_MWh, h18.p_lpg.energy)
    p_lpg.change_CO2e_t = p_lpg.CO2e_total - h18.p_lpg.CO2e_total
    p_lpg.change_CO2e_pct = div(p_lpg.change_CO2e_t, h18.p_lpg.CO2e_total)
    p_lpg.CO2e_total_2021_estimated = h18.p_lpg.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_lpg.cost_climate_saved = (
        (p_lpg.CO2e_total_2021_estimated - p_lpg.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p.energy = (
        p_gas.energy
        + p_lpg.energy
        + p_fueloil.energy
        + p_opetpro.energy
        + p_coal.energy
        + p_heatnet.energy
        + p_biomass.energy
        + p_ofossil.energy
        + p_orenew.energy
    )
    p_opetpro.pct_energy = div(p_opetpro.energy, p.energy)
    p_coal.cost_fuel_per_MWh = ass("Ass_R_S_coal_energy_cost_factor_2035")
    p_fueloil.cost_fuel = p_fueloil.energy * p_fueloil.cost_fuel_per_MWh / MILLION
    p_coal.CO2e_total = p_coal.CO2e_production_based + p_coal.CO2e_combustion_based
    p_heatnet_cogen.CO2e_production_based_per_MWh = fact(
        "Fact_H_P_biomass_ratio_CO2e_pb_to_fec_2018"
    )
    p_heatnet_cogen.CO2e_production_based = (
        p_heatnet_cogen.energy * p_heatnet_cogen.CO2e_production_based_per_MWh
    )
    p_fueloil.change_energy_MWh = p_fueloil.energy - h18.p_fueloil.energy
    p_fueloil.change_energy_pct = div(p_fueloil.change_energy_MWh, h18.p_fueloil.energy)
    p_fueloil.change_CO2e_t = p_fueloil.CO2e_total - h18.p_fueloil.CO2e_total
    p_fueloil.change_CO2e_pct = div(p_fueloil.change_CO2e_t, h18.p_fueloil.CO2e_total)
    p_fueloil.CO2e_total_2021_estimated = h18.p_fueloil.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_fueloil.cost_climate_saved = (
        (p_fueloil.CO2e_total_2021_estimated - p_fueloil.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p_lpg.pct_energy = div(p_lpg.energy, p.energy)
    p_coal.pct_energy = div(p_coal.energy, p.energy)
    p_heatnet_cogen.CO2e_combustion_based_per_MWh = fact(
        "Fact_H_P_heatnet_biomass_ratio_CO2e_cb_to_fec_2018"
    )
    p_heatnet_cogen.CO2e_combustion_based = (
        p_heatnet_cogen.CO2e_combustion_based_per_MWh * p_heatnet_cogen.energy
    )
    p_heatnet_cogen.CO2e_total = (
        p_heatnet_cogen.CO2e_production_based + p_heatnet_cogen.CO2e_combustion_based
    )
    p_heatnet.CO2e_total = p_heatnet_cogen.CO2e_total

    p_biomass.CO2e_production_based_per_MWh = fact(
        "Fact_H_P_biomass_ratio_CO2e_pb_to_fec_2018"
    )
    p_opetpro.change_energy_MWh = p_opetpro.energy - h18.p_opetpro.energy
    p_opetpro.change_energy_pct = div(p_opetpro.change_energy_MWh, h18.p_opetpro.energy)
    p_opetpro.change_CO2e_t = p_opetpro.CO2e_total - h18.p_opetpro.CO2e_total
    p_opetpro.change_CO2e_pct = div(p_opetpro.change_CO2e_t, h18.p_opetpro.CO2e_total)
    p_opetpro.CO2e_total_2021_estimated = h18.p_opetpro.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_opetpro.cost_climate_saved = (
        (p_opetpro.CO2e_total_2021_estimated - p_opetpro.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p.change_energy_MWh = p.energy - h18.p.energy
    p_heatnet.pct_energy = div(p_heatnet.energy, p.energy)
    p_biomass.cost_fuel_per_MWh = fact("Fact_R_S_wood_energy_cost_factor_2018")
    p_coal.cost_fuel = p_coal.energy * p_coal.cost_fuel_per_MWh / MILLION
    p_heatnet_lheatpump.invest_pa = (
        p_heatnet_lheatpump.invest / entries.m_duration_target
    )
    p_biomass.CO2e_production_based = 0 * p_biomass.CO2e_production_based_per_MWh
    p_biomass.CO2e_total = p_biomass.CO2e_production_based
    p_ofossil.CO2e_production_based_per_MWh = fact(
        "Fact_H_P_ofossil_ratio_CO2e_pb_to_fec_2018"
    )
    p_ofossil.CO2e_production_based = 0 * p_ofossil.CO2e_production_based_per_MWh
    p_coal.change_energy_MWh = p_coal.energy - h18.p_coal.energy
    p_coal.change_energy_pct = div(p_coal.change_energy_MWh, h18.p_coal.energy)
    p_coal.change_CO2e_t = p_coal.CO2e_total - h18.p_coal.CO2e_total
    p_coal.change_CO2e_pct = div(p_coal.change_CO2e_t, h18.p_coal.CO2e_total)
    p_coal.CO2e_total_2021_estimated = h18.p_coal.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_coal.cost_climate_saved = (
        (p_coal.CO2e_total_2021_estimated - p_coal.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )

    p_biomass.pct_energy = div(p_biomass.energy, p.energy)
    p_ofossil.CO2e_total = p_ofossil.CO2e_production_based

    p_heatnet.CO2e_combustion_based = p_heatnet_cogen.CO2e_combustion_based

    p_orenew.CO2e_production_based_per_MWh = fact(
        "Fact_H_P_orenew_ratio_CO2e_pb_to_fec_2018"
    )
    p_heatnet.change_energy_MWh = p_heatnet.energy - h18.p_heatnet.energy
    p_heatnet.change_energy_pct = div(p_heatnet.change_energy_MWh, h18.p_heatnet.energy)
    p_heatnet.change_CO2e_t = p_heatnet.CO2e_total - h18.p_heatnet.CO2e_total
    p_heatnet.change_CO2e_pct = div(p_heatnet.change_CO2e_t, h18.p_heatnet.CO2e_total)
    p_heatnet.CO2e_total_2021_estimated = h18.p_heatnet.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_heatnet.cost_climate_saved = (
        (p_heatnet.CO2e_total_2021_estimated - p_heatnet.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p_heatnet_geoth.pct_energy = ass("Ass_H_P_heatnet_fraction_geoth_2050")
    p_heatnet_geoth.energy = (
        (p_heatnet.energy - p_heatnet_cogen.energy) * p_heatnet_geoth.pct_energy
        if (p_heatnet_cogen.energy < p_heatnet.energy)
        else 0
    )
    p_heatnet_geoth.power_to_be_installed = div(
        p_heatnet_geoth.energy, p_heatnet_geoth.full_load_hour
    )
    p_heatnet_geoth.invest = (
        p_heatnet_geoth.invest_per_x * p_heatnet_geoth.power_to_be_installed
    )
    p_heatnet_geoth.pct_of_wage = fact("Fact_B_P_constr_main_revenue_pct_of_wage_2017")
    p_heatnet_geoth.invest_pa = p_heatnet_geoth.invest / entries.m_duration_target
    p_heatnet_plant.pct_of_wage = fact("Fact_B_P_constr_main_revenue_pct_of_wage_2017")
    p_heatnet_plant.cost_wage = p_heatnet_plant.pct_of_wage * p_heatnet_plant.invest_pa
    p_heatnet_lheatpump.cost_wage = (
        p_heatnet_lheatpump.pct_of_wage * p_heatnet_lheatpump.invest_pa
    )
    p_orenew.CO2e_production_based = 0 * p_orenew.CO2e_production_based_per_MWh
    p_heatnet_cogen.pct_energy = div(p_heatnet_cogen.energy, p_heatnet.energy)
    p_heatnet_plant.CO2e_production_based_per_MWh = fact(
        "Fact_H_P_orenew_ratio_CO2e_pb_to_fec_2018"
    )
    p_heatnet_plant.CO2e_production_based = (
        p_heatnet_plant.energy * p_heatnet_plant.CO2e_production_based_per_MWh
    )
    p.CO2e_combustion_based = (
        p_gas.CO2e_combustion_based
        + p_lpg.CO2e_combustion_based
        + p_fueloil.CO2e_combustion_based
        + p_opetpro.CO2e_combustion_based
        + p_coal.CO2e_combustion_based
        + p_heatnet.CO2e_combustion_based
    )
    h.CO2e_combustion_based = p.CO2e_combustion_based

    p_orenew.CO2e_total = p_orenew.CO2e_production_based + 0
    p_heatnet_cogen.change_energy_MWh = (
        p_heatnet_cogen.energy - h18.p_heatnet_cogen.energy
    )
    p_heatnet_cogen.change_energy_pct = div(
        p_heatnet_cogen.change_energy_MWh, h18.p_heatnet_cogen.energy
    )
    p_heatnet_cogen.change_CO2e_t = (
        p_heatnet_cogen.CO2e_total - h18.p_heatnet_cogen.CO2e_total
    )
    p_heatnet_cogen.change_CO2e_pct = div(
        p_heatnet_cogen.change_CO2e_t, h18.p_heatnet_cogen.CO2e_total
    )
    p_heatnet_cogen.CO2e_total_2021_estimated = h18.p_heatnet_cogen.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_heatnet_cogen.cost_climate_saved = (
        (p_heatnet_cogen.CO2e_total_2021_estimated - p_heatnet_cogen.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p_heatnet_plant.ratio_wage_to_emplo = fact(
        "Fact_B_P_constr_main_ratio_wage_to_emplo_2017"
    )
    p_heatnet_plant.demand_emplo = div(
        p_heatnet_plant.cost_wage, p_heatnet_plant.ratio_wage_to_emplo
    )
    p_heatnet_lheatpump.CO2e_production_based_per_MWh = fact(
        "Fact_H_P_orenew_ratio_CO2e_pb_to_fec_2018"
    )
    p_heatnet_lheatpump.ratio_wage_to_emplo = fact(
        "Fact_B_P_constr_main_ratio_wage_to_emplo_2017"
    )
    p_heatnet_plant.CO2e_total = p_heatnet_plant.CO2e_production_based
    p_heatnet_plant.change_energy_MWh = (
        p_heatnet_plant.energy - h18.p_heatnet_plant.energy
    )
    p_heatnet_plant.change_energy_pct = div(
        p_heatnet_plant.change_energy_MWh, h18.p_heatnet_plant.energy
    )
    p_heatnet_plant.change_CO2e_t = (
        p_heatnet_plant.CO2e_total - h18.p_heatnet_plant.CO2e_total
    )
    p_heatnet_plant.change_CO2e_pct = div(
        p_heatnet_plant.change_CO2e_t, h18.p_heatnet_plant.CO2e_total
    )
    p_heatnet_plant.CO2e_total_2021_estimated = h18.p_heatnet_plant.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_heatnet_plant.cost_climate_saved = (
        (p_heatnet_plant.CO2e_total_2021_estimated - p_heatnet_plant.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p_heatnet.invest = (
        p_heatnet_plant.invest + p_heatnet_lheatpump.invest + p_heatnet_geoth.invest
    )
    p_heatnet_plant.invest_pa_com = p_heatnet_plant.invest_pa
    p_heatnet_lheatpump.demand_emplo = div(
        p_heatnet_lheatpump.cost_wage, p_heatnet_lheatpump.ratio_wage_to_emplo
    )
    p_heatnet_plant.invest_com = p_heatnet_plant.invest
    p_heatnet.invest_pa = (
        p_heatnet_plant.invest_pa
        + p_heatnet_lheatpump.invest_pa
        + p_heatnet_geoth.invest_pa
    )
    p_heatnet_geoth.ratio_wage_to_emplo = fact(
        "Fact_B_P_constr_main_ratio_wage_to_emplo_2017"
    )
    p_heatnet_lheatpump.demand_emplo_new = p_heatnet_lheatpump.demand_emplo
    p_heatnet_geoth.cost_wage = p_heatnet_geoth.pct_of_wage * p_heatnet_geoth.invest_pa

    p_heatnet.invest_pa_com = p_heatnet.invest_pa

    p_heatnet_plant.demand_emplo_new = p_heatnet_plant.demand_emplo

    p_heatnet_geoth.demand_emplo = div(
        p_heatnet_geoth.cost_wage, p_heatnet_geoth.ratio_wage_to_emplo
    )
    p_heatnet_lheatpump.CO2e_production_based = (
        p_heatnet_lheatpump.energy * p_heatnet_lheatpump.CO2e_production_based_per_MWh
    )
    p_heatnet_lheatpump.demand_electricity = p_heatnet_lheatpump.energy / fact(
        "Fact_H_P_heatnet_lheatpump_apf"
    )
    p.demand_electricity = p_heatnet_lheatpump.demand_electricity
    p_heatnet_geoth.CO2e_production_based_per_MWh = fact(
        "Fact_H_P_orenew_ratio_CO2e_pb_to_fec_2018"
    )
    p_heatnet.demand_emplo = (
        p_heatnet_plant.demand_emplo
        + p_heatnet_lheatpump.demand_emplo
        + p_heatnet_geoth.demand_emplo
    )
    p_heatnet_lheatpump.CO2e_total = p_heatnet_lheatpump.CO2e_production_based

    p_heatnet_lheatpump.change_energy_MWh = (
        p_heatnet_lheatpump.energy - h18.p_heatnet_lheatpump.energy
    )
    p_heatnet_lheatpump.change_energy_pct = 0

    p_heatnet_lheatpump.change_CO2e_t = (
        p_heatnet_lheatpump.CO2e_total - h18.p_heatnet_lheatpump.CO2e_total
    )
    p_heatnet_lheatpump.change_CO2e_pct = 0

    p_heatnet_lheatpump.CO2e_total_2021_estimated = (
        h18.p_heatnet_lheatpump.CO2e_total * fact("Fact_M_CO2e_wo_lulucf_2021_vs_2018")
    )
    p_heatnet_lheatpump.cost_climate_saved = (
        (p_heatnet_lheatpump.CO2e_total_2021_estimated - p_heatnet_lheatpump.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p_heatnet.invest_com = p_heatnet.invest

    p_heatnet_lheatpump.invest_pa_com = p_heatnet_lheatpump.invest_pa

    p.invest = p_heatnet.invest

    p_heatnet_lheatpump.invest_com = p_heatnet_lheatpump.invest

    p.demand_emplo = p_heatnet.demand_emplo

    p_heatnet.cost_wage = (
        p_heatnet_plant.cost_wage
        + p_heatnet_lheatpump.cost_wage
        + p_heatnet_geoth.cost_wage
    )
    p_heatnet_geoth.demand_emplo_new = p_heatnet_geoth.demand_emplo

    p_heatnet.demand_emplo_new = (
        p_heatnet_plant.demand_emplo_new
        + p_heatnet_lheatpump.demand_emplo_new
        + p_heatnet_geoth.demand_emplo_new
    )

    p.demand_emplo_new = p_heatnet.demand_emplo_new

    p.invest_pa_com = p_heatnet.invest_pa_com

    p.invest_pa = p_heatnet.invest_pa

    p.invest_com = p_heatnet.invest_com

    p_heatnet_geoth.CO2e_production_based = (
        p_heatnet_geoth.energy * p_heatnet_geoth.CO2e_production_based_per_MWh
    )
    p.CO2e_total = (
        p_gas.CO2e_total
        + p_lpg.CO2e_total
        + p_fueloil.CO2e_total
        + p_opetpro.CO2e_total
        + p_coal.CO2e_total
        + p_heatnet.CO2e_total
        + p_biomass.CO2e_total
        + p_ofossil.CO2e_total
        + p_orenew.CO2e_total
    )
    p_heatnet.CO2e_production_based = (
        p_heatnet_cogen.CO2e_production_based
        + p_heatnet_plant.CO2e_production_based
        + p_heatnet_lheatpump.CO2e_production_based
        + p_heatnet_geoth.CO2e_production_based
    )
    p_heatnet_geoth.CO2e_total = p_heatnet_geoth.CO2e_production_based

    p_heatnet_geoth.change_energy_MWh = (
        p_heatnet_geoth.energy - h18.p_heatnet_geoth.energy
    )
    p_heatnet_geoth.change_energy_pct = 0
    p_heatnet_geoth.change_CO2e_t = (
        p_heatnet_geoth.CO2e_total - h18.p_heatnet_geoth.CO2e_total
    )
    p_heatnet_geoth.change_CO2e_pct = 0

    p_heatnet_geoth.CO2e_total_2021_estimated = h18.p_heatnet_geoth.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_heatnet_geoth.cost_climate_saved = (
        (p_heatnet_geoth.CO2e_total_2021_estimated - p_heatnet_geoth.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    h.invest_pa = g.invest_pa + p.invest_pa
    p_heatnet_geoth.invest_pa_com = p_heatnet_geoth.invest_pa

    h.invest_pa_com = g.invest_pa_com + p.invest_pa_com
    p_heatnet_geoth.invest_com = p_heatnet_geoth.invest

    p.cost_wage = p_heatnet.cost_wage

    h.cost_wage = g.cost_wage + p.cost_wage

    h.demand_emplo = g.demand_emplo + p.demand_emplo

    h.demand_emplo_new = g.demand_emplo_new + p.demand_emplo_new
    h.invest_com = g.invest_com + p.invest_com
    h.invest = g.invest + p.invest
    p.change_energy_pct = div(p.change_energy_MWh, h18.p.energy)
    p_fueloil.pct_energy = div(p_fueloil.energy, p.energy)
    p_ofossil.pct_energy = div(p_ofossil.energy, p.energy)
    p_biomass.cost_fuel = p_biomass.energy * p_biomass.cost_fuel_per_MWh / MILLION
    p.cost_fuel = (
        p_gas.cost_fuel + p_fueloil.cost_fuel + p_coal.cost_fuel + p_biomass.cost_fuel
    )
    p.cost_climate_saved = (
        (p.CO2e_total_2021_estimated - p.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p.change_CO2e_t = p.CO2e_total - h18.p.CO2e_total
    p.change_CO2e_pct = div(p.change_CO2e_t, h18.p.CO2e_total)
    p_biomass.change_energy_MWh = p_biomass.energy - h18.p_biomass.energy
    p_biomass.change_energy_pct = div(p_biomass.change_energy_MWh, h18.p_biomass.energy)
    p_biomass.change_CO2e_t = p_biomass.CO2e_total - h18.p_biomass.CO2e_total
    p_biomass.change_CO2e_pct = 0

    p_biomass.CO2e_total_2021_estimated = h18.p_biomass.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_biomass.cost_climate_saved = (
        (p_biomass.CO2e_total_2021_estimated - p_biomass.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p_orenew.pct_energy = div(p_orenew.energy, p.energy)
    h.CO2e_total = p.CO2e_total

    h.cost_climate_saved = p.cost_climate_saved

    h.change_CO2e_t = p.change_CO2e_t

    p_ofossil.change_energy_MWh = p_ofossil.energy - h18.p_ofossil.energy
    p_ofossil.change_energy_pct = div(p_ofossil.change_energy_MWh, h18.p_ofossil.energy)
    p_ofossil.change_CO2e_t = p_ofossil.CO2e_total - h18.p_ofossil.CO2e_total

    p_ofossil.change_CO2e_pct = 0
    p_ofossil.CO2e_total_2021_estimated = h18.p_ofossil.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_ofossil.cost_climate_saved = (
        (p_ofossil.CO2e_total_2021_estimated - p_ofossil.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    h.change_energy_pct = p.change_energy_pct
    p_gas.pct_energy = div(p_gas.energy, p.energy)
    p.CO2e_production_based = (
        p_gas.CO2e_production_based
        + p_opetpro.CO2e_production_based
        + p_coal.CO2e_production_based
        + p_heatnet.CO2e_production_based
        + p_biomass.CO2e_production_based
        + p_ofossil.CO2e_production_based
        + p_orenew.CO2e_production_based
    )
    h.CO2e_production_based = p.CO2e_production_based

    h.change_CO2e_pct = p.change_CO2e_pct
    p_orenew.change_energy_MWh = p_orenew.energy - h18.p_orenew.energy
    p_orenew.change_energy_pct = div(p_orenew.change_energy_MWh, h18.p_orenew.energy)
    p_orenew.change_CO2e_t = p_orenew.CO2e_total - h18.p_orenew.CO2e_total
    p_orenew.change_CO2e_pct = 0

    p_orenew.CO2e_total_2021_estimated = h18.p_orenew.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_orenew.cost_climate_saved = (
        (p_orenew.CO2e_total_2021_estimated - p_orenew.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p.pct_energy = (
        p_gas.pct_energy
        + p_lpg.pct_energy
        + p_fueloil.pct_energy
        + p_opetpro.pct_energy
        + p_coal.pct_energy
        + p_heatnet.pct_energy
        + p_biomass.pct_energy
        + p_ofossil.pct_energy
        + p_orenew.pct_energy
    )
    p_solarth.pct_energy = div(p_solarth.energy, p_orenew.energy)
    p_solarth.CO2e_production_based_per_MWh = fact(
        "Fact_H_P_orenew_ratio_CO2e_pb_to_fec_2018"
    )
    p_solarth.CO2e_production_based = 0 * p_solarth.CO2e_production_based_per_MWh
    p_solarth.CO2e_total = p_solarth.CO2e_production_based
    p_solarth.change_energy_MWh = p_solarth.energy - h18.p_solarth.energy
    p_solarth.change_energy_pct = div(p_solarth.change_energy_MWh, h18.p_solarth.energy)
    p_solarth.change_CO2e_t = p_solarth.CO2e_total - h18.p_solarth.CO2e_total
    p_solarth.change_CO2e_pct = 0
    p_solarth.CO2e_total_2021_estimated = h18.p_solarth.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_solarth.cost_climate_saved = (
        (p_solarth.CO2e_total_2021_estimated - p_solarth.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    h.change_energy_MWh = p.change_energy_MWh

    p_heatpump.pct_energy = div(p_heatpump.energy, p_orenew.energy)
    p_heatpump.CO2e_production_based_per_MWh = fact(
        "Fact_H_P_orenew_ratio_CO2e_pb_to_fec_2018"
    )
    p_heatpump.CO2e_production_based = 0 * p_heatpump.CO2e_production_based_per_MWh
    p_heatpump.CO2e_total = p_heatpump.CO2e_production_based

    p_heatpump.change_energy_MWh = p_heatpump.energy - h18.p_heatpump.energy
    p_heatpump.change_energy_pct = div(
        p_heatpump.change_energy_MWh, h18.p_heatpump.energy
    )
    p_heatpump.change_CO2e_t = p_heatpump.CO2e_total - h18.p_heatpump.CO2e_total
    p_heatpump.change_CO2e_pct = 0

    p_heatpump.CO2e_total_2021_estimated = h18.p_heatpump.CO2e_total * fact(
        "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
    )
    p_heatpump.cost_climate_saved = (
        (p_heatpump.CO2e_total_2021_estimated - p_heatpump.CO2e_total)
        * entries.m_duration_neutral
        * fact("Fact_M_cost_per_CO2e_2020")
    )

    g_planning.demand_emplo_com = g_planning.demand_emplo_new
    g.demand_emplo_com = g_planning.demand_emplo_com

    # TODO: Check demand_emplo_new in Heat with Hauke
    h.demand_emplo_com = g.demand_emplo_com

    p_fossil_change_CO2e_t = p.change_CO2e_t - p_heatnet.change_CO2e_t

    return H30(
        h=h,
        g=g,
        g_storage=g_storage,
        g_planning=g_planning,
        d=d,
        d_r=d_r,
        d_b=d_b,
        d_i=d_i,
        d_t=d_t,
        d_a=d_a,
        p=p,
        p_gas=p_gas,
        p_lpg=p_lpg,
        p_fueloil=p_fueloil,
        p_opetpro=p_opetpro,
        p_coal=p_coal,
        p_heatnet=p_heatnet,
        p_heatnet_cogen=p_heatnet_cogen,
        p_heatnet_plant=p_heatnet_plant,
        p_heatnet_lheatpump=p_heatnet_lheatpump,
        p_heatnet_geoth=p_heatnet_geoth,
        p_biomass=p_biomass,
        p_ofossil=p_ofossil,
        p_orenew=p_orenew,
        p_solarth=p_solarth,
        p_heatpump=p_heatpump,
        p_fossil_change_CO2e_t=p_fossil_change_CO2e_t,
    )
