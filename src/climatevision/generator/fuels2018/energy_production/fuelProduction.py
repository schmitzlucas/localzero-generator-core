# pyright: strict

from dataclasses import dataclass


@dataclass(kw_only=True)
class FuelProduction:
    CO2e_production_based: float
    CO2e_production_based_per_MWh: float
    CO2e_combustion_based: float
    CO2e_combustion_based_per_MWh: float
    CO2e_total: float
    energy: float

    def __init__(
        self,
        energy: float,
        CO2e_production_based_per_MWh: float = 0,
        CO2e_combustion_based_per_MWh: float = 0,
    ):
        self.energy = energy

        self.CO2e_production_based_per_MWh = CO2e_production_based_per_MWh
        self.CO2e_combustion_based_per_MWh = CO2e_combustion_based_per_MWh

        self.CO2e_production_based = CO2e_production_based_per_MWh * energy
        self.CO2e_combustion_based = CO2e_combustion_based_per_MWh * energy

        self.CO2e_total = self.CO2e_production_based + self.CO2e_combustion_based


@dataclass(kw_only=True)
class TotalFuelProduction:
    CO2e_production_based: float
    CO2e_combustion_based: float
    CO2e_total: float
    energy: float

    def __init__(self, *fuel_productions: FuelProduction):
        self.CO2e_production_based = sum(
            p.CO2e_production_based for p in fuel_productions
        )
        self.CO2e_combustion_based = sum(
            p.CO2e_combustion_based for p in fuel_productions
        )
        self.energy = sum(p.energy for p in fuel_productions)
        self.CO2e_total = self.CO2e_production_based + self.CO2e_combustion_based
