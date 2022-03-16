# pyright: strict

from dataclasses import dataclass, asdict
from ..inputs import Inputs
from ..utils import div
from ..transport2018 import T18
from .air import AirDomestic, AirInternational, Air

# from .transport import Transport
from .investmentaction import InvestmentAction
from .road import (
    Road,
    RoadBus,
    RoadCar,
    RoadGoods,
    RoadGoodsLightDuty,
    RoadGoodsMediumAndHeavyDuty,
    RoadPeople,
    RoadSum,
    RoadInvestmentAction,
)


@dataclass
class RailPeople:
    # Used by rail_ppl_distance and rail_ppl_metro
    base_unit: float
    change_CO2e_pct: float
    change_CO2e_t: float
    change_energy_MWh: float
    change_energy_pct: float
    change_km: float
    CO2e_combustion_based: float
    CO2e_total_2021_estimated: float
    CO2e_total: float
    cost_climate_saved: float
    cost_wage: float
    demand_electricity: float
    demand_emplo_new: float
    demand_emplo: float
    emplo_existing: float
    energy: float
    invest_pa: float
    invest_per_x: float
    invest: float
    mileage: float
    pct_of_wage: float
    ratio_wage_to_emplo: float
    transport_capacity_pkm: float

    @classmethod
    def calc_metro(
        cls, inputs: Inputs, *, t18: T18, total_transport_capacity_pkm: float
    ) -> "RailPeople":
        ass = inputs.ass
        entries = inputs.entries
        fact = inputs.fact

        transport_capacity_pkm = div(
            total_transport_capacity_pkm * t18.rail_ppl_metro.transport_capacity_pkm,
            (
                t18.road_bus.transport_capacity_pkm
                + t18.rail_ppl_distance.transport_capacity_pkm
                + t18.rail_ppl_metro.transport_capacity_pkm
            ),
        ) * (
            ass("Ass_T_D_trnsprt_ppl_city_pt_frac_2050")
            if entries.t_rt3 == "city"
            else ass("Ass_T_D_trnsprt_ppl_smcty_pt_frac_2050")
            if entries.t_rt3 == "smcty"
            else ass("Ass_T_D_trnsprt_ppl_rural_pt_frac_2050")
            if entries.t_rt3 == "rural"
            else ass("Ass_T_D_trnsprt_ppl_nat_pt_frac_2050")
        )
        mileage = transport_capacity_pkm / ass("Ass_T_D_lf_Rl_Metro_2050")
        demand_electricity = mileage * ass("Ass_T_S_Rl_Metro_SEC_fzkm_2050")
        CO2e_combustion_based = demand_electricity * fact(
            "Fact_T_S_electricity_EmFa_tank_wheel_2018"
        )
        base_unit = (mileage - t18.rail_ppl_metro.mileage) / fact(
            "Fact_T_D_rail_metro_ratio_mlg_to_vehicle"
        )
        energy = demand_electricity
        change_energy_MWh = energy - t18.rail_ppl_metro.energy
        CO2e_total = CO2e_combustion_based
        change_km = transport_capacity_pkm - t18.rail_ppl_metro.transport_capacity_pkm
        invest_per_x = fact("Fact_T_D_rail_metro_vehicle_invest")
        ratio_wage_to_emplo = ass("Ass_T_D_bus_metro_wage_driver")
        demand_emplo = mileage / fact("Fact_T_D_metro_ratio_mlg_to_driver")
        emplo_existing = t18.rail_ppl_metro.mileage / fact(
            "Fact_T_D_metro_ratio_mlg_to_driver"
        )
        demand_emplo_new = demand_emplo - emplo_existing
        cost_wage = ratio_wage_to_emplo * demand_emplo_new
        invest = base_unit * invest_per_x + cost_wage * entries.m_duration_target
        change_energy_pct = div(change_energy_MWh, t18.rail_ppl_metro.energy)
        change_CO2e_t = CO2e_combustion_based - t18.rail_ppl_metro.CO2e_combustion_based
        change_CO2e_pct = (
            0  # div(rail_ppl_metro.change_CO2e_t, t18.rail_ppl_metro.CO2e_cb)
        )
        CO2e_total_2021_estimated = t18.rail_ppl_metro.CO2e_combustion_based * fact(
            "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
        )
        cost_climate_saved = (
            (CO2e_total_2021_estimated - CO2e_combustion_based)
            * entries.m_duration_neutral
            * fact("Fact_M_cost_per_CO2e_2020")
        )
        invest_pa = invest / entries.m_duration_target
        pct_of_wage = div(cost_wage, invest_pa)
        return cls(
            base_unit=base_unit,
            change_CO2e_pct=change_CO2e_pct,
            change_CO2e_t=change_CO2e_t,
            change_energy_MWh=change_energy_MWh,
            change_energy_pct=change_energy_pct,
            change_km=change_km,
            CO2e_combustion_based=CO2e_combustion_based,
            CO2e_total_2021_estimated=CO2e_total_2021_estimated,
            CO2e_total=CO2e_total,
            cost_climate_saved=cost_climate_saved,
            cost_wage=cost_wage,
            demand_electricity=demand_electricity,
            demand_emplo_new=demand_emplo_new,
            demand_emplo=demand_emplo,
            emplo_existing=emplo_existing,
            energy=energy,
            invest_pa=invest_pa,
            invest_per_x=invest_per_x,
            invest=invest,
            mileage=mileage,
            pct_of_wage=pct_of_wage,
            ratio_wage_to_emplo=ratio_wage_to_emplo,
            transport_capacity_pkm=transport_capacity_pkm,
        )

    @classmethod
    def calc_distance(
        cls, inputs: Inputs, *, t18: T18, total_transport_capacity_pkm: float
    ) -> "RailPeople":
        fact = inputs.fact
        ass = inputs.ass
        entries = inputs.entries

        transport_capacity_pkm = div(
            total_transport_capacity_pkm * t18.rail_ppl_distance.transport_capacity_pkm,
            t18.road_bus.transport_capacity_pkm
            + t18.rail_ppl_distance.transport_capacity_pkm
            + t18.rail_ppl_metro.transport_capacity_pkm,
        ) * (
            ass("Ass_T_D_trnsprt_ppl_city_pt_frac_2050")
            if entries.t_rt3 == "city"
            else ass("Ass_T_D_trnsprt_ppl_smcty_pt_frac_2050")
            if entries.t_rt3 == "smcty"
            else ass("Ass_T_D_trnsprt_ppl_rural_pt_frac_2050")
            if entries.t_rt3 == "rural"
            else ass("Ass_T_D_trnsprt_ppl_nat_pt_frac_2050")
        )
        demand_electricity = transport_capacity_pkm * ass(
            "Ass_T_S_Rl_Train_ppl_long_elec_SEC_2050"
        )
        CO2e_combustion_based = demand_electricity * fact(
            "Fact_T_S_electricity_EmFa_tank_wheel_2018"
        )
        mileage = transport_capacity_pkm / fact(
            "Fact_T_D_rail_ppl_ratio_pkm_to_fzkm_2018"
        )
        base_unit = (mileage - t18.rail_ppl_distance.mileage) / fact(
            "Fact_T_D_rail_ppl_ratio_mlg_to_vehicle"
        )
        demand_emplo = mileage / fact("Fact_T_D_rail_ratio_mlg_to_driver")

        emplo_existing = t18.rail_ppl_distance.mileage / fact(
            "Fact_T_D_rail_ratio_mlg_to_driver"
        )
        demand_emplo_new = demand_emplo - emplo_existing
        energy = demand_electricity
        CO2e_total = CO2e_combustion_based
        change_energy_MWh = energy - t18.rail_ppl_distance.energy
        change_km = (
            transport_capacity_pkm - t18.rail_ppl_distance.transport_capacity_pkm
        )
        ratio_wage_to_emplo = ass("Ass_T_D_rail_wage_driver")
        cost_wage = ratio_wage_to_emplo * demand_emplo_new
        invest_per_x = fact("Fact_T_D_rail_ppl_vehicle_invest")
        change_energy_pct = div(change_energy_MWh, t18.rail_ppl_distance.energy)
        change_CO2e_t = (
            CO2e_combustion_based - t18.rail_ppl_distance.CO2e_combustion_based
        )
        change_CO2e_pct = div(
            change_CO2e_t, t18.rail_ppl_distance.CO2e_combustion_based
        )
        CO2e_total_2021_estimated = t18.rail_ppl_distance.CO2e_combustion_based * fact(
            "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
        )
        cost_climate_saved = (
            (CO2e_total_2021_estimated - CO2e_combustion_based)
            * entries.m_duration_neutral
            * fact("Fact_M_cost_per_CO2e_2020")
        )
        invest = base_unit * invest_per_x + cost_wage * entries.m_duration_target
        invest_pa = invest / entries.m_duration_target
        pct_of_wage = div(cost_wage, invest_pa)
        return cls(
            base_unit=base_unit,
            change_CO2e_pct=change_CO2e_pct,
            change_CO2e_t=change_CO2e_t,
            change_energy_MWh=change_energy_MWh,
            change_energy_pct=change_energy_pct,
            change_km=change_km,
            CO2e_combustion_based=CO2e_combustion_based,
            CO2e_total_2021_estimated=CO2e_total_2021_estimated,
            CO2e_total=CO2e_total,
            cost_climate_saved=cost_climate_saved,
            cost_wage=cost_wage,
            demand_electricity=demand_electricity,
            demand_emplo_new=demand_emplo_new,
            demand_emplo=demand_emplo,
            emplo_existing=emplo_existing,
            energy=energy,
            invest_pa=invest_pa,
            invest_per_x=invest_per_x,
            invest=invest,
            mileage=mileage,
            pct_of_wage=pct_of_wage,
            ratio_wage_to_emplo=ratio_wage_to_emplo,
            transport_capacity_pkm=transport_capacity_pkm,
        )


@dataclass
class RailPeopleMetroActionInfra:
    # Used by rail_ppl_metro_action_infra
    base_unit: float
    cost_wage: float
    demand_emplo: float
    demand_emplo_new: float
    emplo_existing: float
    invest: float
    invest_com: float
    invest_pa: float
    invest_pa_com: float
    invest_per_x: float
    pct_of_wage: float
    ratio_wage_to_emplo: float

    @classmethod
    def calc(
        cls, inputs: Inputs, *, metro_transport_capacity_pkm: float
    ) -> "RailPeopleMetroActionInfra":
        ass = inputs.ass
        fact = inputs.fact
        entries = inputs.entries

        invest_per_x = ass("Ass_T_C_cost_per_trnsprt_ppl_metro")
        invest = metro_transport_capacity_pkm * invest_per_x
        base_unit = 0
        invest_com = invest * ass("Ass_T_C_ratio_public_sector_100")
        invest_pa = invest / entries.m_duration_target
        pct_of_wage = fact("Fact_T_D_constr_roadrail_revenue_pct_of_wage_2018")
        invest_pa_com = invest_com / entries.m_duration_target
        cost_wage = invest_pa * pct_of_wage
        ratio_wage_to_emplo = fact("Fact_T_D_constr_roadrail_ratio_wage_to_emplo_2018")
        emplo_existing = 0  # nicht existent oder ausgelastet

        demand_emplo = cost_wage / ratio_wage_to_emplo
        demand_emplo_new = demand_emplo

        return cls(
            base_unit=base_unit,
            cost_wage=cost_wage,
            demand_emplo=demand_emplo,
            demand_emplo_new=demand_emplo_new,
            emplo_existing=emplo_existing,
            invest=invest,
            invest_com=invest_com,
            invest_pa=invest_pa,
            invest_pa_com=invest_pa_com,
            invest_per_x=invest_per_x,
            pct_of_wage=pct_of_wage,
            ratio_wage_to_emplo=ratio_wage_to_emplo,
        )


@dataclass
class RailPeopleSum:
    # Used by rail_ppl
    base_unit: float
    change_CO2e_pct: float
    change_CO2e_t: float
    change_energy_MWh: float
    change_energy_pct: float
    change_km: float
    CO2e_combustion_based: float
    CO2e_total_2021_estimated: float
    CO2e_total: float
    cost_climate_saved: float
    cost_wage: float
    demand_electricity: float
    demand_emplo_new: float
    demand_emplo: float
    emplo_existing: float
    energy: float
    invest_com: float
    invest_pa_com: float
    invest_pa: float
    invest: float
    mileage: float
    transport_capacity_pkm: float

    @classmethod
    def calc(
        cls,
        inputs: Inputs,
        *,
        t18: T18,
        rail_ppl_metro: RailPeople,
        rail_ppl_distance: RailPeople,
        rail_ppl_metro_action_infra: RailPeopleMetroActionInfra,
    ) -> "RailPeopleSum":
        fact = inputs.fact
        entries = inputs.entries

        CO2e_total_2021_estimated = t18.rail_ppl.CO2e_combustion_based * fact(
            "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
        )
        demand_electricity = (
            rail_ppl_distance.demand_electricity + rail_ppl_metro.demand_electricity
        )
        CO2e_combustion_based = (
            rail_ppl_distance.CO2e_combustion_based
            + rail_ppl_metro.CO2e_combustion_based
        )
        base_unit = (
            rail_ppl_distance.base_unit
            + rail_ppl_metro.base_unit
            + 0  # rail_ppl_metro_action_infra.base_unit
        )  # SUM(rail_ppl_distance.base_unit:DO259)
        transport_capacity_pkm = (
            rail_ppl_distance.transport_capacity_pkm
            + rail_ppl_metro.transport_capacity_pkm
        )
        change_CO2e_t = CO2e_combustion_based - t18.rail_ppl.CO2e_combustion_based
        change_CO2e_pct = div(change_CO2e_t, t18.rail_ppl.CO2e_combustion_based)
        invest_com = rail_ppl_metro_action_infra.invest_com
        mileage = rail_ppl_distance.mileage + rail_ppl_metro.mileage
        change_energy_MWh = (
            rail_ppl_distance.change_energy_MWh + rail_ppl_metro.change_energy_MWh
        )
        invest = (
            rail_ppl_distance.invest
            + rail_ppl_metro.invest
            + rail_ppl_metro_action_infra.invest
        )
        emplo_existing = (
            rail_ppl_distance.emplo_existing
            + rail_ppl_metro.emplo_existing
            + rail_ppl_metro_action_infra.emplo_existing
        )
        energy = rail_ppl_distance.energy + rail_ppl_metro.energy
        cost_climate_saved = (
            (CO2e_total_2021_estimated - CO2e_combustion_based)
            * entries.m_duration_neutral
            * fact("Fact_M_cost_per_CO2e_2020")
        )
        CO2e_total = rail_ppl_distance.CO2e_total + rail_ppl_metro.CO2e_total
        change_energy_pct = div(change_energy_MWh, t18.rail_ppl.energy)
        change_km = rail_ppl_distance.change_km + rail_ppl_metro.change_km
        invest_pa = (
            rail_ppl_distance.invest_pa
            + rail_ppl_metro.invest_pa
            + rail_ppl_metro_action_infra.invest_pa
        )
        invest_pa_com = rail_ppl_metro_action_infra.invest_pa_com
        cost_wage = (
            rail_ppl_distance.cost_wage
            + rail_ppl_metro.cost_wage
            + rail_ppl_metro_action_infra.cost_wage
        )
        demand_emplo_new = (
            rail_ppl_distance.demand_emplo_new
            + rail_ppl_metro.demand_emplo_new
            + rail_ppl_metro_action_infra.demand_emplo_new
        )
        demand_emplo = (
            rail_ppl_distance.demand_emplo
            + rail_ppl_metro.demand_emplo
            + rail_ppl_metro_action_infra.demand_emplo
        )

        return cls(
            base_unit=base_unit,
            change_CO2e_pct=change_CO2e_pct,
            change_CO2e_t=change_CO2e_t,
            change_energy_MWh=change_energy_MWh,
            change_energy_pct=change_energy_pct,
            change_km=change_km,
            CO2e_combustion_based=CO2e_combustion_based,
            CO2e_total_2021_estimated=CO2e_total_2021_estimated,
            CO2e_total=CO2e_total,
            cost_climate_saved=cost_climate_saved,
            cost_wage=cost_wage,
            demand_electricity=demand_electricity,
            demand_emplo_new=demand_emplo_new,
            demand_emplo=demand_emplo,
            emplo_existing=emplo_existing,
            energy=energy,
            invest_com=invest_com,
            invest_pa_com=invest_pa_com,
            invest_pa=invest_pa,
            invest=invest,
            mileage=mileage,
            transport_capacity_pkm=transport_capacity_pkm,
        )


@dataclass
class RailGoods:
    # Used by rail_gds
    CO2e_combustion_based: float
    CO2e_total: float
    CO2e_total_2021_estimated: float
    base_unit: float
    change_CO2e_pct: float
    change_CO2e_t: float
    change_energy_MWh: float
    change_energy_pct: float
    change_km: float
    cost_climate_saved: float
    cost_wage: float
    demand_electricity: float
    demand_emplo: float
    demand_emplo_new: float
    emplo_existing: float
    energy: float
    invest: float
    invest_pa: float
    invest_per_x: float
    pct_of_wage: float
    mileage: float
    ratio_wage_to_emplo: float
    transport_capacity_tkm: float

    @classmethod
    def calc(cls, inputs: Inputs, *, t18: T18) -> "RailGoods":
        ass = inputs.ass
        fact = inputs.fact
        entries = inputs.entries

        transport_capacity_tkm = t18.rail_gds.transport_capacity_tkm * (
            ass("Ass_T_D_trnsprt_gds_Rl_2050")
            / fact("Fact_T_D_Rl_train_nat_trnsprt_gds_2018")
        )
        demand_electricity = transport_capacity_tkm * ass(
            "Ass_T_S_Rl_Train_gds_elec_SEC_2050"
        )
        CO2e_combustion_based = demand_electricity * fact(
            "Fact_T_S_electricity_EmFa_tank_wheel_2018"
        )
        mileage = transport_capacity_tkm / fact(
            "Fact_T_D_rail_gds_ratio_tkm_to_fzkm_2018"
        )
        CO2e_total_2021_estimated = t18.rail_gds.CO2e_combustion_based * fact(
            "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
        )
        cost_climate_saved = (
            (CO2e_total_2021_estimated - CO2e_combustion_based)
            * entries.m_duration_neutral
            * fact("Fact_M_cost_per_CO2e_2020")
        )
        ratio_wage_to_emplo = ass("Ass_T_D_rail_wage_driver")
        demand_emplo = mileage / fact("Fact_T_D_rail_ratio_mlg_to_driver")
        emplo_existing = t18.rail_gds.mileage / fact(
            "Fact_T_D_rail_ratio_mlg_to_driver"
        )
        change_km = transport_capacity_tkm - t18.rail_gds.transport_capacity_tkm
        demand_emplo_new = demand_emplo - emplo_existing

        energy = demand_electricity  # SUM(rail_gds.demand_electricity:BJ260)
        CO2e_total = CO2e_combustion_based
        change_energy_MWh = energy - t18.rail_gds.energy
        change_energy_pct = div(change_energy_MWh, t18.rail_gds.energy)
        change_CO2e_t = CO2e_combustion_based - t18.rail_gds.CO2e_combustion_based
        change_CO2e_pct = div(change_CO2e_t, t18.rail_gds.CO2e_combustion_based)
        base_unit = change_km / fact("Fact_T_D_rail_gds_ratio_mlg_to_vehicle")
        invest_per_x = fact("Fact_T_D_rail_gds_vehicle_invest")
        cost_wage = ratio_wage_to_emplo * demand_emplo_new
        invest = base_unit * invest_per_x + cost_wage * entries.m_duration_target
        invest_pa = invest / entries.m_duration_target
        pct_of_wage = div(cost_wage, invest_pa)

        return cls(
            CO2e_combustion_based=CO2e_combustion_based,
            CO2e_total=CO2e_total,
            CO2e_total_2021_estimated=CO2e_total_2021_estimated,
            base_unit=base_unit,
            change_CO2e_pct=change_CO2e_pct,
            change_CO2e_t=change_CO2e_t,
            change_energy_MWh=change_energy_MWh,
            change_energy_pct=change_energy_pct,
            change_km=change_km,
            cost_climate_saved=cost_climate_saved,
            cost_wage=cost_wage,
            demand_electricity=demand_electricity,
            demand_emplo=demand_emplo,
            demand_emplo_new=demand_emplo_new,
            emplo_existing=emplo_existing,
            energy=energy,
            invest=invest,
            invest_pa=invest_pa,
            invest_per_x=invest_per_x,
            pct_of_wage=pct_of_wage,
            mileage=mileage,
            ratio_wage_to_emplo=ratio_wage_to_emplo,
            transport_capacity_tkm=transport_capacity_tkm,
        )


@dataclass
class ShipDomestic:
    # Used by ship_dmstc
    base_unit: float
    change_CO2e_pct: float
    change_CO2e_t: float
    change_energy_MWh: float
    change_energy_pct: float
    change_km: float
    CO2e_combustion_based: float
    CO2e_total_2021_estimated: float
    CO2e_total: float
    cost_climate_saved: float
    cost_wage: float
    demand_ediesel: float
    demand_emplo_new: float
    demand_emplo: float
    emplo_existing: float
    energy: float
    invest_pa: float
    invest_per_x: float
    invest: float
    pct_of_wage: float
    ratio_wage_to_emplo: float
    transport_capacity_tkm: float

    @classmethod
    def calc(cls, inputs: Inputs, *, t18: T18) -> "ShipDomestic":
        fact = inputs.fact
        ass = inputs.ass
        entries = inputs.entries

        transport_capacity_tkm = (
            ass("Ass_T_D_trnsprt_gds_ship_2050")
            * entries.m_population_com_203X
            / entries.m_population_nat
        )
        demand_ediesel = (
            ass("Ass_T_D_Shp_dmstc_nat_EB_2050")
            * entries.m_population_com_203X
            / entries.m_population_nat
        )
        CO2e_combustion_based = demand_ediesel * ass(
            "Ass_T_S_diesel_EmFa_tank_wheel_2050"
        )
        CO2e_total_2021_estimated = t18.ship_dmstc.CO2e_combustion_based * fact(
            "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
        )
        cost_climate_saved = (
            (CO2e_total_2021_estimated - CO2e_combustion_based)
            * entries.m_duration_neutral
            * fact("Fact_M_cost_per_CO2e_2020")
        )
        ratio_wage_to_emplo = ass("Ass_T_D_shp_wage_driver")
        demand_emplo = transport_capacity_tkm / fact("Fact_T_D_shp_ratio_mlg_to_driver")
        emplo_existing = t18.ship_dmstc.transport_capacity_tkm / fact(
            "Fact_T_D_shp_ratio_mlg_to_driver"
        )
        demand_emplo_new = demand_emplo - emplo_existing
        change_km = transport_capacity_tkm - t18.ship_dmstc.transport_capacity_tkm
        energy = demand_ediesel
        CO2e_total = CO2e_combustion_based
        change_energy_MWh = energy - t18.ship_dmstc.energy
        change_energy_pct = div(change_energy_MWh, t18.ship_dmstc.energy)
        change_CO2e_t = CO2e_combustion_based - t18.ship_dmstc.CO2e_combustion_based
        change_CO2e_pct = div(change_CO2e_t, t18.ship_dmstc.CO2e_combustion_based)
        base_unit = change_km / fact("Fact_T_D_Shp_dmstc_nat_ratio_mlg_to_vehicle")
        invest_per_x = fact("Fact_T_D_Shp_dmstc_vehicle_invest")
        cost_wage = ratio_wage_to_emplo * demand_emplo_new
        invest = base_unit * invest_per_x + cost_wage * entries.m_duration_target
        invest_pa = invest / entries.m_duration_target
        pct_of_wage = div(cost_wage, invest_pa)

        return cls(
            base_unit=base_unit,
            change_CO2e_pct=change_CO2e_pct,
            change_CO2e_t=change_CO2e_t,
            change_energy_MWh=change_energy_MWh,
            change_energy_pct=change_energy_pct,
            change_km=change_km,
            CO2e_combustion_based=CO2e_combustion_based,
            CO2e_total_2021_estimated=CO2e_total_2021_estimated,
            CO2e_total=CO2e_total,
            cost_climate_saved=cost_climate_saved,
            cost_wage=cost_wage,
            demand_ediesel=demand_ediesel,
            demand_emplo_new=demand_emplo_new,
            demand_emplo=demand_emplo,
            emplo_existing=emplo_existing,
            energy=energy,
            invest_pa=invest_pa,
            invest_per_x=invest_per_x,
            invest=invest,
            pct_of_wage=pct_of_wage,
            ratio_wage_to_emplo=ratio_wage_to_emplo,
            transport_capacity_tkm=transport_capacity_tkm,
        )


@dataclass
class ShipDomesticActionInfra:
    # Used by ship_dmstc_action_infra
    CO2e_total_2021_estimated: float
    cost_climate_saved: float
    cost_wage: float
    demand_ediesel: float
    demand_emplo: float
    demand_emplo_new: float
    invest: float
    invest_com: float
    invest_pa: float
    invest_pa_com: float
    pct_of_wage: float
    ratio_wage_to_emplo: float

    @classmethod
    def calc(cls, inputs: Inputs) -> "ShipDomesticActionInfra":
        fact = inputs.fact
        ass = inputs.ass
        entries = inputs.entries

        invest = (
            ass("Ass_T_C_invest_water_ways")
            * entries.m_population_com_203X
            / entries.m_population_nat
        )
        invest_com = invest * ass("Ass_T_C_ratio_public_sector_100")
        demand_ediesel = 0
        pct_of_wage = fact("Fact_T_D_constr_roadrail_revenue_pct_of_wage_2018")
        invest_pa = invest / entries.m_duration_target
        cost_wage = invest_pa * pct_of_wage
        ratio_wage_to_emplo = fact("Fact_T_D_constr_roadrail_ratio_wage_to_emplo_2018")
        invest_pa_com = invest_com / entries.m_duration_target
        demand_emplo = div(
            cost_wage,
            ratio_wage_to_emplo,
        )
        demand_emplo_new = demand_emplo
        CO2e_total_2021_estimated = 0
        cost_climate_saved = 0

        return cls(
            CO2e_total_2021_estimated=CO2e_total_2021_estimated,
            cost_climate_saved=cost_climate_saved,
            cost_wage=cost_wage,
            demand_ediesel=demand_ediesel,
            demand_emplo=demand_emplo,
            demand_emplo_new=demand_emplo_new,
            invest=invest,
            invest_com=invest_com,
            invest_pa=invest_pa,
            invest_pa_com=invest_pa_com,
            pct_of_wage=pct_of_wage,
            ratio_wage_to_emplo=ratio_wage_to_emplo,
        )


@dataclass
class ShipInternational:
    # Used by ship_inter
    change_CO2e_pct: float
    change_CO2e_t: float
    change_energy_MWh: float
    change_energy_pct: float
    change_km: float
    CO2e_combustion_based: float
    CO2e_total_2021_estimated: float
    CO2e_total: float
    cost_climate_saved: float
    demand_ediesel: float
    energy: float
    transport_capacity_tkm: float

    @classmethod
    def calc(cls, inputs: Inputs, *, t18: T18) -> "ShipInternational":
        fact = inputs.fact
        ass = inputs.ass
        entries = inputs.entries

        CO2e_total_2021_estimated = t18.ship_inter.CO2e_combustion_based * fact(
            "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
        )
        demand_ediesel = (
            ass("Ass_T_D_Shp_sea_nat_EB_2050")
            * entries.m_population_com_203X
            / entries.m_population_nat
        )
        CO2e_combustion_based = demand_ediesel * ass(
            "Ass_T_S_diesel_EmFa_tank_wheel_2050"
        )
        cost_climate_saved = (
            (CO2e_total_2021_estimated - CO2e_combustion_based)
            * entries.m_duration_neutral
            * fact("Fact_M_cost_per_CO2e_2020")
        )
        energy = demand_ediesel
        CO2e_total = CO2e_combustion_based
        change_energy_MWh = energy - t18.ship_inter.energy
        change_energy_pct = div(change_energy_MWh, t18.ship_inter.energy)
        change_CO2e_t = CO2e_combustion_based - t18.ship_inter.CO2e_combustion_based
        change_CO2e_pct = div(change_CO2e_t, t18.ship_inter.CO2e_combustion_based)
        transport_capacity_tkm = t18.ship_inter.transport_capacity_tkm * div(
            energy, t18.ship_inter.energy
        )
        change_km = transport_capacity_tkm - t18.ship_inter.transport_capacity_tkm

        return cls(
            change_CO2e_pct=change_CO2e_pct,
            change_CO2e_t=change_CO2e_t,
            change_energy_MWh=change_energy_MWh,
            change_energy_pct=change_energy_pct,
            change_km=change_km,
            CO2e_combustion_based=CO2e_combustion_based,
            CO2e_total_2021_estimated=CO2e_total_2021_estimated,
            CO2e_total=CO2e_total,
            cost_climate_saved=cost_climate_saved,
            demand_ediesel=demand_ediesel,
            energy=energy,
            transport_capacity_tkm=transport_capacity_tkm,
        )


@dataclass
class Ship:
    # Used by ship
    change_CO2e_pct: float
    change_CO2e_t: float
    change_energy_MWh: float
    change_energy_pct: float
    CO2e_combustion_based: float
    CO2e_total_2021_estimated: float
    CO2e_total: float
    cost_climate_saved: float
    demand_ediesel: float
    demand_emplo_new: float
    demand_emplo: float
    energy: float
    transport_capacity_tkm: float

    base_unit: float
    cost_wage: float
    emplo_existing: float
    invest: float
    invest_com: float
    invest_pa: float
    invest_pa_com: float

    @classmethod
    def calc(
        cls,
        *,
        t18: T18,
        ship_inter: ShipInternational,
        ship_dmstc: ShipDomestic,
        ship_dmstc_action_infra: ShipDomesticActionInfra,
    ) -> "Ship":
        invest = ship_dmstc_action_infra.invest + ship_dmstc.invest
        invest_com = ship_dmstc_action_infra.invest_com
        demand_ediesel = (
            ship_dmstc.demand_ediesel
            + ship_dmstc_action_infra.demand_ediesel
            + ship_inter.demand_ediesel
        )
        CO2e_combustion_based = (
            ship_dmstc.CO2e_combustion_based + ship_inter.CO2e_combustion_based
        )
        energy = demand_ediesel
        transport_capacity_tkm = (
            ship_dmstc.transport_capacity_tkm + ship_inter.transport_capacity_tkm
        )
        CO2e_total = CO2e_combustion_based
        change_energy_MWh = energy - t18.ship.energy
        change_energy_pct = div(change_energy_MWh, t18.ship.energy)
        change_CO2e_t = CO2e_combustion_based - t18.ship.CO2e_combustion_based
        change_CO2e_pct = div(change_CO2e_t, t18.ship.CO2e_combustion_based)
        emplo_existing = ship_dmstc.emplo_existing
        base_unit = ship_dmstc.base_unit
        invest_pa = ship_dmstc_action_infra.invest_pa + ship_dmstc.invest_pa
        invest_pa_com = ship_dmstc_action_infra.invest_pa_com
        cost_wage = ship_dmstc.cost_wage + ship_dmstc_action_infra.cost_wage
        demand_emplo_new = (
            ship_dmstc.demand_emplo_new + ship_dmstc_action_infra.demand_emplo_new
        )
        demand_emplo = ship_dmstc.demand_emplo + ship_dmstc_action_infra.demand_emplo
        CO2e_total_2021_estimated = (
            ship_dmstc.CO2e_total_2021_estimated
            + ship_dmstc_action_infra.CO2e_total_2021_estimated
            + ship_inter.CO2e_total_2021_estimated
        )
        cost_climate_saved = (
            ship_dmstc.cost_climate_saved
            + ship_dmstc_action_infra.cost_climate_saved
            + ship_inter.cost_climate_saved
        )
        return cls(
            CO2e_combustion_based=CO2e_combustion_based,
            CO2e_total=CO2e_total,
            CO2e_total_2021_estimated=CO2e_total_2021_estimated,
            base_unit=base_unit,
            change_CO2e_pct=change_CO2e_pct,
            change_CO2e_t=change_CO2e_t,
            change_energy_MWh=change_energy_MWh,
            change_energy_pct=change_energy_pct,
            cost_climate_saved=cost_climate_saved,
            cost_wage=cost_wage,
            demand_ediesel=demand_ediesel,
            demand_emplo=demand_emplo,
            demand_emplo_new=demand_emplo_new,
            emplo_existing=emplo_existing,
            energy=energy,
            invest=invest,
            invest_com=invest_com,
            invest_pa=invest_pa,
            invest_pa_com=invest_pa_com,
            transport_capacity_tkm=transport_capacity_tkm,
        )


@dataclass
class OtherFoot:
    # Used by other_foot
    CO2e_total: float
    CO2e_total_2021_estimated: float
    change_km: float
    cost_climate_saved: float
    invest: float
    invest_com: float
    invest_pa: float
    invest_pa_com: float
    transport_capacity_pkm: float

    @classmethod
    def calc(
        cls, inputs: Inputs, *, t18: T18, total_transport_capacity_pkm: float
    ) -> "OtherFoot":
        ass = inputs.ass
        fact = inputs.fact
        entries = inputs.entries

        transport_capacity_pkm = total_transport_capacity_pkm * (
            ass("Ass_T_D_trnsprt_ppl_city_foot_frac_2050")
            if entries.t_rt3 == "city"
            else ass("Ass_T_D_trnsprt_ppl_smcty_foot_frac_2050")
            if entries.t_rt3 == "smcty"
            else ass("Ass_T_D_trnsprt_ppl_rural_foot_frac_2050")
            if entries.t_rt3 == "rural"
            else ass("Ass_T_D_trnsprt_ppl_nat_foot_frac_2050")
        )
        change_km = transport_capacity_pkm - t18.other_foot.transport_capacity_pkm

        CO2e_total_2021_estimated = t18.other_foot.CO2e_combustion_based * fact(
            "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
        )
        cost_climate_saved = (
            (CO2e_total_2021_estimated)
            * entries.m_duration_neutral
            * fact("Fact_M_cost_per_CO2e_2020")
        )
        return cls(
            CO2e_total=0,
            CO2e_total_2021_estimated=CO2e_total_2021_estimated,
            change_km=change_km,
            cost_climate_saved=cost_climate_saved,
            invest=0,
            invest_com=0,
            invest_pa=0,
            invest_pa_com=0,
            transport_capacity_pkm=transport_capacity_pkm,
        )


@dataclass
class OtherCycle:
    # Used by other_cycl
    CO2e_total: float
    CO2e_total_2021_estimated: float
    base_unit: float
    change_km: float
    cost_climate_saved: float
    invest: float
    invest_com: float
    invest_pa: float
    invest_pa_com: float
    invest_per_x: float
    transport_capacity_pkm: float

    @classmethod
    def calc(
        cls, inputs: Inputs, t18: T18, total_transport_capacity_pkm: float
    ) -> "OtherCycle":
        fact = inputs.fact
        ass = inputs.ass
        entries = inputs.entries

        transport_capacity_pkm = total_transport_capacity_pkm * (
            ass("Ass_T_D_trnsprt_ppl_city_cycl_frac_2050")
            if entries.t_rt3 == "city"
            else ass("Ass_T_D_trnsprt_ppl_smcty_cycl_frac_2050")
            if entries.t_rt3 == "smcty"
            else ass("Ass_T_D_trnsprt_ppl_rural_cycl_frac_2050")
            if entries.t_rt3 == "rural"
            else ass("Ass_T_D_trnsprt_ppl_nat_cycl_frac_2050")
        )

        invest_per_x = fact("Fact_T_D_cycl_vehicle_invest_hannah")
        base_unit = (
            transport_capacity_pkm
            * ass("Ass_T_D_cycl_ratio_cargo_to_bikes")
            / ass("Ass_T_D_cycl_cargo_mlg")
        )
        invest = base_unit * invest_per_x
        CO2e_total_2021_estimated = t18.other_cycl.CO2e_combustion_based * fact(
            "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
        )
        cost_climate_saved = (
            (CO2e_total_2021_estimated)
            * entries.m_duration_neutral
            * fact("Fact_M_cost_per_CO2e_2020")
        )
        invest_com = 0
        invest_pa = invest / entries.m_duration_target
        change_km = transport_capacity_pkm - t18.other_cycl.transport_capacity_pkm
        invest_pa_com = invest_com / entries.m_duration_target
        CO2e_total = 0

        return cls(
            CO2e_total=CO2e_total,
            CO2e_total_2021_estimated=CO2e_total_2021_estimated,
            base_unit=base_unit,
            change_km=change_km,
            cost_climate_saved=cost_climate_saved,
            invest=invest,
            invest_com=invest_com,
            invest_pa=invest_pa,
            invest_pa_com=invest_pa_com,
            invest_per_x=invest_per_x,
            transport_capacity_pkm=transport_capacity_pkm,
        )


@dataclass
class GPlanning:
    # Used by g_planning
    cost_wage: float
    demand_emplo: float
    demand_emplo_com: float
    demand_emplo_new: float
    invest: float
    invest_com: float
    invest_pa: float
    invest_pa_com: float
    ratio_wage_to_emplo: float

    @classmethod
    def calc(
        cls,
        inputs: Inputs,
        road_bus_action_infra: InvestmentAction,
        road_gds_mhd_action_wire: InvestmentAction,
        road_action_charger: InvestmentAction,
        rail_ppl_metro_action_infra: RailPeopleMetroActionInfra,
        rail_action_invest_infra: InvestmentAction,
        other_cycl: OtherCycle,
    ) -> "GPlanning":
        ass = inputs.ass
        entries = inputs.entries

        ratio_wage_to_emplo = ass("Ass_T_C_yearly_costs_per_planer")
        invest = ass("Ass_T_C_planer_cost_per_invest_cost") * (
            road_bus_action_infra.invest
            + road_gds_mhd_action_wire.invest
            + road_action_charger.invest
            + rail_ppl_metro_action_infra.invest
            + rail_action_invest_infra.invest
            + other_cycl.invest
        )
        invest_com = invest * ass("Ass_T_C_ratio_public_sector_100")
        invest_pa_com = invest_com / entries.m_duration_target
        invest_pa = invest / entries.m_duration_target
        cost_wage = invest_pa
        demand_emplo = div(cost_wage, ratio_wage_to_emplo)
        demand_emplo_new = demand_emplo
        demand_emplo_com = demand_emplo_new

        return cls(
            cost_wage=cost_wage,
            demand_emplo=demand_emplo,
            demand_emplo_com=demand_emplo_com,
            demand_emplo_new=demand_emplo_new,
            invest=invest,
            invest_com=invest_com,
            invest_pa=invest_pa,
            invest_pa_com=invest_pa_com,
            ratio_wage_to_emplo=ratio_wage_to_emplo,
        )


@dataclass
class EnergySum:
    # Used by s, s_diesel, s_emethan, s_jetfuel, s_petrol, s_fueloil, s_lpg, s_gas, s_biogas, s_bioethanol, s_biodiesel, s_elec, s_hydrogen
    energy: float


@dataclass
class G:
    # Used by g
    cost_wage: float
    demand_emplo: float
    demand_emplo_com: float
    demand_emplo_new: float
    invest: float
    invest_com: float
    invest_pa: float
    invest_pa_com: float


@dataclass
class Rail:
    # Used by rail
    CO2e_combustion_based: float
    CO2e_total: float
    CO2e_total_2021_estimated: float
    base_unit: float
    change_CO2e_pct: float
    change_CO2e_t: float
    change_energy_MWh: float
    change_energy_pct: float
    cost_climate_saved: float
    cost_wage: float
    demand_electricity: float
    demand_emplo: float
    demand_emplo_new: float
    energy: float
    invest: float
    invest_com: float
    invest_pa: float
    invest_pa_com: float
    mileage: float
    transport_capacity_pkm: float
    transport_capacity_tkm: float

    @classmethod
    def calc(
        cls,
        inputs: Inputs,
        *,
        t18: T18,
        rail_ppl: RailPeopleSum,
        rail_gds: RailGoods,
        rail_action_invest_infra: InvestmentAction,
        rail_action_invest_station: InvestmentAction,
    ) -> "Rail":
        demand_electricity = rail_ppl.demand_electricity + rail_gds.demand_electricity
        energy = demand_electricity
        change_energy_MWh = energy - t18.rail.energy
        CO2e_combustion_based = (
            rail_ppl.CO2e_combustion_based + rail_gds.CO2e_combustion_based
        )
        change_CO2e_t = CO2e_combustion_based - t18.rail.CO2e_combustion_based
        change_CO2e_pct = div(change_CO2e_t, t18.rail.CO2e_combustion_based)
        change_energy_pct = div(change_energy_MWh, t18.rail.energy)
        CO2e_total = CO2e_combustion_based
        transport_capacity_pkm = rail_ppl.transport_capacity_pkm
        invest_com = (
            rail_action_invest_infra.invest_com
            + rail_action_invest_station.invest_com
            + rail_ppl.invest_com
        )
        demand_emplo_new = (
            rail_action_invest_infra.demand_emplo_new
            + rail_action_invest_station.demand_emplo_new
            + rail_ppl.demand_emplo_new
            + rail_gds.demand_emplo_new
        )
        invest_pa_com = (
            rail_action_invest_infra.invest_pa_com
            + rail_action_invest_station.invest_pa_com
            + rail_ppl.invest_pa_com
        )
        mileage = rail_ppl.mileage + rail_gds.mileage
        transport_capacity_tkm = rail_gds.transport_capacity_tkm
        CO2e_total_2021_estimated = (
            rail_ppl.CO2e_total_2021_estimated + rail_gds.CO2e_total_2021_estimated
        )
        cost_climate_saved = rail_ppl.cost_climate_saved + rail_gds.cost_climate_saved
        base_unit = rail_ppl.base_unit + rail_gds.base_unit
        invest_pa = (
            rail_action_invest_infra.invest_pa
            + rail_action_invest_station.invest_pa
            + rail_ppl.invest_pa
            + rail_gds.invest_pa
        )
        demand_emplo = (
            rail_action_invest_infra.demand_emplo
            + rail_action_invest_station.demand_emplo
            + rail_ppl.demand_emplo
            + rail_gds.demand_emplo
        )
        cost_wage = (
            rail_action_invest_infra.cost_wage
            + rail_action_invest_station.cost_wage
            + rail_ppl.cost_wage
            + rail_gds.cost_wage
        )
        invest = (
            rail_action_invest_infra.invest
            + rail_action_invest_station.invest
            + rail_ppl.invest
            + rail_gds.invest
        )

        return cls(
            CO2e_combustion_based=CO2e_combustion_based,
            CO2e_total=CO2e_total,
            CO2e_total_2021_estimated=CO2e_total_2021_estimated,
            base_unit=base_unit,
            change_CO2e_pct=change_CO2e_pct,
            change_CO2e_t=change_CO2e_t,
            change_energy_MWh=change_energy_MWh,
            change_energy_pct=change_energy_pct,
            cost_climate_saved=cost_climate_saved,
            cost_wage=cost_wage,
            demand_electricity=demand_electricity,
            demand_emplo=demand_emplo,
            demand_emplo_new=demand_emplo_new,
            energy=energy,
            invest=invest,
            invest_com=invest_com,
            invest_pa=invest_pa,
            invest_pa_com=invest_pa_com,
            mileage=mileage,
            transport_capacity_pkm=transport_capacity_pkm,
            transport_capacity_tkm=transport_capacity_tkm,
        )


@dataclass
class Other:
    # Used by other
    CO2e_total: float
    CO2e_total_2021_estimated: float
    base_unit: float
    change_km: float
    cost_climate_saved: float
    cost_wage: float
    demand_emplo: float
    demand_emplo_new: float
    invest: float
    invest_com: float
    invest_pa: float
    invest_pa_com: float
    transport_capacity_pkm: float

    @classmethod
    def calc(
        cls,
        inputs: Inputs,
        *,
        other_foot: OtherFoot,
        other_cycl: OtherCycle,
        other_foot_action_infra: InvestmentAction,
        other_cycl_action_infra: InvestmentAction,
    ) -> "Other":
        CO2e_total = 0
        invest_com = (
            other_foot.invest_com
            + other_cycl.invest_com
            + other_foot_action_infra.invest_com
            + other_cycl_action_infra.invest_com
        )
        CO2e_total_2021_estimated = (
            other_foot.CO2e_total_2021_estimated + other_cycl.CO2e_total_2021_estimated
        )
        cost_climate_saved = (
            other_foot.cost_climate_saved + other_cycl.cost_climate_saved
        )
        invest = (
            other_foot.invest
            + other_cycl.invest
            + other_foot_action_infra.invest
            + other_cycl_action_infra.invest
        )
        invest_pa_com = (
            other_foot.invest_pa_com
            + other_cycl.invest_pa_com
            + other_foot_action_infra.invest_pa_com
            + other_cycl_action_infra.invest_pa_com
        )
        demand_emplo_new = (
            other_foot_action_infra.demand_emplo_new
            + other_cycl_action_infra.demand_emplo_new
        )
        transport_capacity_pkm = (
            other_foot.transport_capacity_pkm + other_cycl.transport_capacity_pkm
        )
        change_km = other_foot.change_km + other_cycl.change_km
        cost_wage = (
            other_foot_action_infra.cost_wage + other_cycl_action_infra.cost_wage
        )
        other_cycl_action_infra.invest_pa = (
            other_cycl_action_infra.invest / inputs.entries.m_duration_target
        )
        other_cycl_action_infra.demand_emplo = div(
            other_cycl_action_infra.cost_wage,
            other_cycl_action_infra.ratio_wage_to_emplo,
        )
        demand_emplo = (
            other_foot_action_infra.demand_emplo + other_cycl_action_infra.demand_emplo
        )
        invest_pa = (
            other_foot.invest_pa
            + other_cycl.invest_pa
            + other_foot_action_infra.invest_pa
            + other_cycl_action_infra.invest_pa
        )
        base_unit = other_cycl.base_unit

        return cls(
            CO2e_total=CO2e_total,
            CO2e_total_2021_estimated=CO2e_total_2021_estimated,
            base_unit=base_unit,
            change_km=change_km,
            cost_climate_saved=cost_climate_saved,
            cost_wage=cost_wage,
            demand_emplo=demand_emplo,
            demand_emplo_new=demand_emplo_new,
            invest=invest,
            invest_com=invest_com,
            invest_pa=invest_pa,
            invest_pa_com=invest_pa_com,
            transport_capacity_pkm=transport_capacity_pkm,
        )


@dataclass
class T:
    # Used by t
    CO2e_combustion_based: float
    CO2e_total: float
    CO2e_total_2021_estimated: float
    change_CO2e_pct: float
    change_CO2e_t: float
    change_energy_MWh: float
    change_energy_pct: float
    cost_climate_saved: float
    cost_wage: float
    demand_ediesel: float
    demand_ejetfuel: float
    demand_electricity: float
    demand_emplo: float
    demand_emplo_com: float
    demand_emplo_new: float
    demand_epetrol: float
    demand_hydrogen: float
    energy: float
    invest: float
    invest_com: float
    invest_pa: float
    invest_pa_com: float
    transport_capacity_pkm: float
    transport_capacity_tkm: float

    @classmethod
    def calc(
        cls,
        *,
        t18: T18,
        total_transport_capacity_pkm: float,
        air: Air,
        rail: Rail,
        road: RoadSum,
        ship: Ship,
        other: Other,
        g: G,
    ) -> "T":
        demand_ejetfuel = air.demand_ejetfuel
        demand_epetrol = road.demand_epetrol
        demand_hydrogen = road.demand_hydrogen
        demand_electricity = road.demand_electricity + rail.demand_electricity
        demand_ediesel = road.demand_ediesel + ship.demand_ediesel
        energy = (
            demand_electricity
            + demand_epetrol
            + demand_ediesel
            + demand_ejetfuel
            + demand_hydrogen
        )
        CO2e_combustion_based = (
            air.CO2e_combustion_based
            + road.CO2e_combustion_based
            + rail.CO2e_combustion_based
            + ship.CO2e_combustion_based
        )
        change_energy_MWh = energy - t18.t.energy
        CO2e_total = CO2e_combustion_based
        transport_capacity_tkm = (
            air.transport_capacity_tkm
            + road.transport_capacity_tkm
            + rail.transport_capacity_tkm
            + ship.transport_capacity_tkm
        )
        change_CO2e_t = CO2e_combustion_based - t18.t.CO2e_combustion_based
        change_CO2e_pct = div(change_CO2e_t, t18.t.CO2e_combustion_based)
        change_energy_pct = div(change_energy_MWh, t18.t.energy)
        invest_com = (
            g.invest_com
            + road.invest_com
            + rail.invest_com
            + ship.invest_com
            + other.invest_com
            + air.invest_com
        )
        invest_pa_com = (
            g.invest_pa_com
            + road.invest_pa_com
            + rail.invest_pa_com
            + ship.invest_pa_com
            + other.invest_pa_com
            + air.invest_pa_com
        )
        CO2e_total_2021_estimated = (
            air.CO2e_total_2021_estimated
            + road.CO2e_total_2021_estimated
            + rail.CO2e_total_2021_estimated
            + ship.CO2e_total_2021_estimated
            + other.CO2e_total_2021_estimated
        )
        cost_climate_saved = (
            air.cost_climate_saved
            + road.cost_climate_saved
            + rail.cost_climate_saved
            + ship.cost_climate_saved
            + other.cost_climate_saved
        )
        invest = (
            road.invest
            + rail.invest
            + ship.invest
            + other.invest
            + air.invest
            + g.invest
        )
        cost_wage = (
            g.cost_wage
            + road.cost_wage
            + rail.cost_wage
            + ship.cost_wage
            + other.cost_wage
        )
        demand_emplo = (
            g.demand_emplo
            + air.demand_emplo
            + road.demand_emplo
            + rail.demand_emplo
            + ship.demand_emplo
            + other.demand_emplo
        )
        demand_emplo_new = (
            g.demand_emplo_new
            + air.demand_emplo_new
            + road.demand_emplo_new
            + rail.demand_emplo_new
            + ship.demand_emplo_new
            + other.demand_emplo_new
        )
        invest_pa = (
            road.invest_pa
            + rail.invest_pa
            + ship.invest_pa
            + other.invest_pa
            + air.invest_pa
            + g.invest_pa
        )
        demand_emplo_com = g.demand_emplo_com

        return cls(
            CO2e_combustion_based=CO2e_combustion_based,
            CO2e_total=CO2e_total,
            CO2e_total_2021_estimated=CO2e_total_2021_estimated,
            change_CO2e_pct=change_CO2e_pct,
            change_CO2e_t=change_CO2e_t,
            change_energy_MWh=change_energy_MWh,
            change_energy_pct=change_energy_pct,
            cost_climate_saved=cost_climate_saved,
            cost_wage=cost_wage,
            demand_ediesel=demand_ediesel,
            demand_ejetfuel=demand_ejetfuel,
            demand_electricity=demand_electricity,
            demand_emplo=demand_emplo,
            demand_emplo_com=demand_emplo_com,
            demand_emplo_new=demand_emplo_new,
            demand_epetrol=demand_epetrol,
            demand_hydrogen=demand_hydrogen,
            energy=energy,
            invest=invest,
            invest_com=invest_com,
            invest_pa=invest_pa,
            invest_pa_com=invest_pa_com,
            transport_capacity_pkm=total_transport_capacity_pkm,
            transport_capacity_tkm=transport_capacity_tkm,
        )


@dataclass
class T30:
    air_inter: AirInternational
    air_dmstc: AirDomestic
    road_ppl: RoadPeople
    road_car: RoadCar
    road_car_it_ot: Road
    road_car_ab: Road
    road_bus: RoadBus
    road_gds: RoadGoods
    road_gds_ldt: RoadGoodsLightDuty
    road_gds_ldt_it_ot: Road
    road_gds_ldt_ab: Road
    road_gds_mhd: RoadGoodsMediumAndHeavyDuty
    road_gds_mhd_it_ot: Road
    road_gds_mhd_ab: Road
    road_gds_mhd_action_wire: InvestmentAction
    rail_ppl: RailPeopleSum
    rail_ppl_distance: RailPeople
    rail_ppl_metro: RailPeople
    rail_gds: RailGoods
    ship: Ship
    ship_dmstc: ShipDomestic
    ship_dmstc_action_infra: ShipDomesticActionInfra
    ship_inter: ShipInternational
    other_foot: OtherFoot
    other_foot_action_infra: InvestmentAction
    other_cycl: OtherCycle
    other_cycl_action_infra: InvestmentAction
    g_planning: GPlanning
    s: EnergySum
    s_diesel: EnergySum
    s_emethan: EnergySum
    s_jetfuel: EnergySum
    s_petrol: EnergySum
    s_fueloil: EnergySum
    s_lpg: EnergySum
    s_gas: EnergySum
    s_biogas: EnergySum
    s_bioethanol: EnergySum
    s_biodiesel: EnergySum
    s_elec: EnergySum
    s_hydrogen: EnergySum
    g: G
    t: T
    air: Air
    road: RoadSum
    rail: Rail
    other: Other
    rail_action_invest_infra: InvestmentAction
    rail_action_invest_station: InvestmentAction
    rail_ppl_metro_action_infra: RailPeopleMetroActionInfra
    road_action_charger: RoadInvestmentAction
    road_bus_action_infra: InvestmentAction

    def dict(self):
        return asdict(self)


def calc(inputs: Inputs, *, t18: T18) -> T30:
    ass = inputs.ass
    entries = inputs.entries

    # --- Air ---
    air_dmstc = AirDomestic.calc(inputs, t18)
    air_inter = AirInternational.calc(inputs, t18)
    air = Air.calc(t18, domestic=air_dmstc, international=air_inter)

    # First we estimate the total required transport capacity in the target year (excluding air).
    total_transport_capacity_pkm = entries.m_population_com_203X * (
        ass("Ass_T_D_ratio_trnsprt_ppl_to_ppl_city")
        if entries.t_rt3 == "city"
        else ass("Ass_T_D_ratio_trnsprt_ppl_to_ppl_smcity")
        if entries.t_rt3 == "smcty"
        else ass("Ass_T_D_ratio_trnsprt_ppl_to_ppl_rural")
        if entries.t_rt3 == "rural"
        else ass("Ass_T_D_trnsprt_ppl_nat") / entries.m_population_nat
    )

    # -- Road ---
    road_car_it_ot = Road.calc_car_it_ot(
        inputs, t18=t18, total_transport_capacity_pkm=total_transport_capacity_pkm
    )
    road_car_ab = Road.calc_car_ab(
        inputs, t18=t18, total_transport_capacity_pkm=total_transport_capacity_pkm
    )
    road_car = RoadCar.calc(inputs, t18=t18, it_ot=road_car_it_ot, ab=road_car_ab)
    road_action_charger = RoadInvestmentAction.calc_car_action_charger(
        inputs, car_base_unit=road_car.base_unit
    )
    road_bus = RoadBus.calc(
        inputs, t18=t18, total_transport_capacity_pkm=total_transport_capacity_pkm
    )
    road_bus_action_infra = RoadBus.calc_action_infra(
        inputs, bus_transport_capacity_pkm=road_bus.transport_capacity_pkm
    )
    road_ppl = RoadPeople.calc(
        inputs,
        t18=t18,
        car=road_car,
        bus=road_bus,
        road_bus_action_infra=road_bus_action_infra,
    )
    road_gds_ldt_it_ot = Road.calc_goods_lightduty_it_ot(inputs, t18=t18)
    road_gds_ldt_ab = Road.calc_goods_lightduty_ab(inputs, t18=t18)
    road_gds_ldt = RoadGoodsLightDuty.calc(
        inputs,
        t18=t18,
        it_ot=road_gds_ldt_it_ot,
        ab=road_gds_ldt_ab,
    )
    road_gds_mhd_ab = Road.calc_goods_medium_and_heavy_duty_ab(inputs, t18=t18)
    road_gds_mhd_it_ot = Road.calc_goods_medium_and_heavy_duty_it_ot(inputs, t18=t18)
    road_gds_mhd = RoadGoodsMediumAndHeavyDuty.calc(
        inputs, t18=t18, it_ot=road_gds_mhd_it_ot, ab=road_gds_mhd_ab
    )
    road_gds_mhd_action_wire = RoadGoodsMediumAndHeavyDuty.calc_action_wire(inputs)
    road_gds = RoadGoods.calc(
        t18=t18,
        ldt=road_gds_ldt,
        mhd=road_gds_mhd,
        road_gds_mhd_action_wire=road_gds_mhd_action_wire,
    )
    road = RoadSum.calc(
        t18=t18,
        goods=road_gds,
        people=road_ppl,
        road_action_charger=road_action_charger,
    )

    # --- Rail ---
    rail_ppl_metro = RailPeople.calc_metro(
        inputs, t18=t18, total_transport_capacity_pkm=total_transport_capacity_pkm
    )
    rail_ppl_distance = RailPeople.calc_distance(
        inputs, t18=t18, total_transport_capacity_pkm=total_transport_capacity_pkm
    )
    rail_action_invest_infra = InvestmentAction.calc_rail_action_invest_infra(inputs)
    rail_action_invest_station = InvestmentAction.calc_rail_action_invest_station(
        inputs
    )
    rail_ppl_metro_action_infra = RailPeopleMetroActionInfra.calc(
        inputs, metro_transport_capacity_pkm=rail_ppl_metro.transport_capacity_pkm
    )
    rail_ppl = RailPeopleSum.calc(
        inputs,
        t18=t18,
        rail_ppl_metro=rail_ppl_metro,
        rail_ppl_distance=rail_ppl_distance,
        rail_ppl_metro_action_infra=rail_ppl_metro_action_infra,
    )
    rail_gds = RailGoods.calc(inputs, t18=t18)
    rail = Rail.calc(
        inputs,
        t18=t18,
        rail_ppl=rail_ppl,
        rail_gds=rail_gds,
        rail_action_invest_infra=rail_action_invest_infra,
        rail_action_invest_station=rail_action_invest_station,
    )

    # --- Ship ---
    ship_dmstc = ShipDomestic.calc(inputs, t18=t18)
    ship_inter = ShipInternational.calc(inputs, t18=t18)
    ship_dmstc_action_infra = ShipDomesticActionInfra.calc(inputs)
    ship = Ship.calc(
        t18=t18,
        ship_inter=ship_inter,
        ship_dmstc=ship_dmstc,
        ship_dmstc_action_infra=ship_dmstc_action_infra,
    )

    # --- Other ---
    other_cycl = OtherCycle.calc(
        inputs, t18, total_transport_capacity_pkm=total_transport_capacity_pkm
    )
    other_cycl_action_infra = InvestmentAction.calc_other_cycl_action_infra(
        inputs, cycle_transport_capacity_pkm=other_cycl.transport_capacity_pkm
    )
    other_foot = OtherFoot.calc(
        inputs, t18=t18, total_transport_capacity_pkm=total_transport_capacity_pkm
    )
    other_foot_action_infra = InvestmentAction.calc_other_foot_action_infra(inputs)
    other = Other.calc(
        inputs,
        other_foot=other_foot,
        other_cycl=other_cycl,
        other_cycl_action_infra=other_cycl_action_infra,
        other_foot_action_infra=other_foot_action_infra,
    )

    # --- Planning and other aggregates ---
    g_planning = GPlanning.calc(
        inputs,
        road_bus_action_infra=road_bus_action_infra,
        road_gds_mhd_action_wire=road_gds_mhd_action_wire,
        road_action_charger=road_action_charger,
        rail_ppl_metro_action_infra=rail_ppl_metro_action_infra,
        rail_action_invest_infra=rail_action_invest_infra,
        other_cycl=other_cycl,
    )
    # TODO: This Seems to be a pointless rename?
    g = G(
        invest_com=g_planning.invest_com,
        invest_pa_com=g_planning.invest_pa_com,
        demand_emplo=g_planning.demand_emplo,
        cost_wage=g_planning.cost_wage,
        invest_pa=g_planning.invest_pa,
        invest=g_planning.invest,
        demand_emplo_new=g_planning.demand_emplo_new,
        demand_emplo_com=g_planning.demand_emplo_new,
    )
    t = T.calc(
        t18=t18,
        total_transport_capacity_pkm=total_transport_capacity_pkm,
        air=air,
        rail=rail,
        road=road,
        ship=ship,
        other=other,
        g=g,
    )
    s_petrol = EnergySum(t.demand_epetrol)
    s_jetfuel = EnergySum(t.demand_ejetfuel)
    s_diesel = EnergySum(t.demand_ediesel)
    s_elec = EnergySum(t.demand_electricity)
    s_hydrogen = EnergySum(t.demand_hydrogen)

    s_emethan = EnergySum(0)
    s_fueloil = EnergySum(0)
    s_lpg = EnergySum(0)
    s_gas = EnergySum(0)
    s_biogas = EnergySum(0)
    s_bioethanol = EnergySum(0)
    s_biodiesel = EnergySum(0)

    s = EnergySum(
        s_petrol.energy
        + s_jetfuel.energy
        + s_diesel.energy
        + s_elec.energy
        + s_hydrogen.energy
        + s_emethan.energy
    )

    # --- Populate result ---
    return T30(
        air_dmstc=air_dmstc,
        air_inter=air_inter,
        air=air,
        road_car_it_ot=road_car_it_ot,
        road_car_ab=road_car_ab,
        road_car=road_car,
        road_bus=road_bus,
        road_bus_action_infra=road_bus_action_infra,
        road_action_charger=road_action_charger,
        road_ppl=road_ppl,
        road_gds_ldt_it_ot=road_gds_ldt_it_ot,
        road_gds_ldt_ab=road_gds_ldt_ab,
        road_gds_ldt=road_gds_ldt,
        road_gds_mhd_ab=road_gds_mhd_ab,
        road_gds_mhd_it_ot=road_gds_mhd_it_ot,
        road_gds_mhd=road_gds_mhd,
        road_gds=road_gds,
        road_gds_mhd_action_wire=road_gds_mhd_action_wire,
        road=road,
        rail_ppl_metro=rail_ppl_metro,
        rail_ppl_distance=rail_ppl_distance,
        rail_ppl=rail_ppl,
        rail_ppl_metro_action_infra=rail_ppl_metro_action_infra,
        rail_action_invest_infra=rail_action_invest_infra,
        rail_action_invest_station=rail_action_invest_station,
        rail_gds=rail_gds,
        rail=rail,
        ship_dmstc=ship_dmstc,
        ship_inter=ship_inter,
        ship_dmstc_action_infra=ship_dmstc_action_infra,
        ship=ship,
        other_cycl=other_cycl,
        other_cycl_action_infra=other_cycl_action_infra,
        other_foot=other_foot,
        other_foot_action_infra=other_foot_action_infra,
        other=other,
        g_planning=g_planning,
        g=g,
        t=t,
        s_petrol=s_petrol,
        s_jetfuel=s_jetfuel,
        s_diesel=s_diesel,
        s_elec=s_elec,
        s_hydrogen=s_hydrogen,
        s_emethan=s_emethan,
        s=s,
        s_fueloil=s_fueloil,
        s_lpg=s_lpg,
        s_gas=s_gas,
        s_biogas=s_biogas,
        s_bioethanol=s_bioethanol,
        s_biodiesel=s_biodiesel,
    )