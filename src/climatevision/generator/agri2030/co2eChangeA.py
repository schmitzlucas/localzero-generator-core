# pyright: strict

from dataclasses import dataclass, InitVar

from ..inputs import Inputs
from ..utils import div
from ..agri2018.a18 import A18

from .energy_demand import CO2eChangePOperation, CO2eChangeP
from .energy_source import CO2eChangeS
from .energy_general import CO2eChangeG


@dataclass(kw_only=True)
class CO2eChangeA:
    CO2e_combustion_based: float = 0
    CO2e_production_based: float = 0
    CO2e_total: float = 0
    CO2e_total_2021_estimated: float = 0
    change_CO2e_pct: float = 0
    change_CO2e_t: float = 0
    change_energy_MWh: float = 0
    change_energy_pct: float = 0
    cost_climate_saved: float = 0
    cost_wage: float = 0
    demand_emplo: float = 0
    demand_emplo_com: float = 0
    demand_emplo_new: float = 0
    invest: float = 0
    invest_com: float = 0
    invest_outside: float = 0
    invest_pa: float = 0
    invest_pa_com: float = 0
    invest_pa_outside: float = 0

    inputs: InitVar[Inputs]
    what: InitVar[str]
    a18: InitVar[A18]
    p_operation: InitVar[CO2eChangePOperation]
    p: InitVar[CO2eChangeP]
    g: InitVar[CO2eChangeG]
    s: InitVar[CO2eChangeS]

    def __post_init__(
        self,
        inputs: Inputs,
        what: str,
        a18: A18,
        p_operation: CO2eChangePOperation,
        p: CO2eChangeP,
        g: CO2eChangeG,
        s: CO2eChangeS,
    ):

        self.CO2e_production_based = p.CO2e_production_based
        self.CO2e_combustion_based = s.CO2e_combustion_based
        self.CO2e_total = g.CO2e_total + p.CO2e_total + s.CO2e_total

        self.CO2e_total_2021_estimated = getattr(a18, what).CO2e_total * inputs.fact(
            "Fact_M_CO2e_wo_lulucf_2021_vs_2018"
        )

        self.invest_pa_outside = g.invest_pa_outside
        self.invest_outside = g.invest_outside
        self.invest_com = g.invest_com
        self.invest = g.invest + s.invest + p.invest
        self.invest_pa_com = g.invest_pa_com
        self.invest_pa = self.invest / inputs.entries.m_duration_target

        self.change_CO2e_t = self.CO2e_total - getattr(a18, what).CO2e_total
        self.change_CO2e_pct = div(self.change_CO2e_t, a18.a.CO2e_total)
        self.change_energy_MWh = p_operation.change_energy_MWh
        self.change_energy_pct = p_operation.change_energy_pct

        self.demand_emplo = g.demand_emplo + p.demand_emplo + s.demand_emplo
        self.demand_emplo_new = (
            g.demand_emplo_new + p.demand_emplo_new + s.demand_emplo_new
        )
        self.demand_emplo_com = g.demand_emplo_com

        self.cost_climate_saved = (
            (self.CO2e_total_2021_estimated - self.CO2e_total)
            * inputs.entries.m_duration_neutral
            * inputs.fact("Fact_M_cost_per_CO2e_2020")
        )

        self.cost_wage = g.cost_wage + p.cost_wage + s.cost_wage
