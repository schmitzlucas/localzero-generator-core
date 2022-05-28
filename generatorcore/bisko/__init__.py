from dataclasses import dataclass, field

from generatorcore.inputs import Inputs

from ..utils import div
from .. import (
    agri2018,
    electricity2018,
    business2018,
    fuels2018,
    heat2018,
    industry2018,
    lulucf2018,
    residences2018,
    transport2018,
)


@dataclass
class EnergySourceCalcIntermediate:
    """
    This class is a contains all relevant parameters for the conversion calculation from the "Einflussbilanz" to the "BISKO Bilanz" (See Readme) for a single energy source
    like petrol or electricity. Einflussbilanz attributes (eb-prefix) are saved intermediatly for conveniance. 
    """
    #New attributes for Bisko:
    energy: float = field(init=False)
    CO2e_cb: float = field(init=False) 
    CO2e_pb: float = field(init=False)

    # Variables that are calculated for the Einflussbilanz (eb)
    eb_energy_from_same_sector: float
    eb_energy_from_agri: float | None = None
    eb_CO2e_cb_from_same_sector: float | None = None    
    eb_CO2e_cb_from_heat: float | None = None
    eb_CO2e_cb_from_elec: float | None = None
    eb_CO2e_cb_from_fuels: float | None = None
    eb_CO2e_cb_from_agri: float | None = None
    eb_CO2e_pb_from_heat: float | None = None

    def __post_init__(self):
        def sum_over_none_and_float(*args: float | None) -> float:
            return_float: float = 0
            for elem in args:
                if elem is None:
                    continue
                return_float += elem

            return return_float

        # automatically sum over all cb_based emissions
        self.CO2e_cb = sum_over_none_and_float(
            self.eb_CO2e_cb_from_same_sector,
            self.eb_CO2e_cb_from_heat,
            self.eb_CO2e_cb_from_elec,
            self.eb_CO2e_cb_from_fuels,
            self.eb_CO2e_cb_from_agri,
        )
        self.energy = sum_over_none_and_float(
            self.eb_energy_from_same_sector, self.eb_energy_from_agri
        )

        self.CO2e_pb = sum_over_none_and_float(self.eb_CO2e_pb_from_heat)


@dataclass
class Sums:
    """
    This class represents a sum over instances of class EnergySourceCalcIntermediate. 
    """
    # energy consumption
    energy: float
    energy_from_same_eb_sector: float
    energy_from_eb_agri_sector: float

    # combustion based Emissions
    CO2e_cb: float
    eb_CO2e_from_same_sector: float
    eb_CO2e_cb_from_agri: float
    eb_CO2e_cb_from_heat: float
    eb_CO2e_cb_from_elec: float
    eb_CO2e_cb_from_fuels: float

    # production based Emissions
    CO2e_pb: float
    eb_CO2e_pb_from_heat: float

    @classmethod
    def calc(cls, *args: EnergySourceCalcIntermediate):
        energy = sum([elem.energy if elem.energy != None else 0 for elem in args])
        energy_from_same_eb_sector = sum(
            [
                elem.eb_energy_from_same_sector
                if elem.eb_energy_from_same_sector != None
                else 0
                for elem in args
            ]
        )
        energy_from_eb_agri_sector = sum(
            [
                elem.eb_energy_from_agri if elem.eb_energy_from_agri != None else 0
                for elem in args
            ]
        )
        CO2e_cb = sum([elem.CO2e_cb if elem.CO2e_cb != None else 0 for elem in args])
        eb_CO2e_from_same_sector = sum(
            [
                elem.eb_CO2e_cb_from_same_sector
                if elem.eb_CO2e_cb_from_same_sector != None
                else 0
                for elem in args
            ]
        )
        eb_CO2e_cb_from_agri = sum(
            [
                elem.eb_CO2e_cb_from_agri if elem.eb_CO2e_cb_from_agri != None else 0
                for elem in args
            ]
        )
        eb_CO2e_cb_from_heat = sum(
            [
                elem.eb_CO2e_cb_from_heat if elem.eb_CO2e_cb_from_heat != None else 0
                for elem in args
            ]
        )
        eb_CO2e_cb_from_elec = sum(
            [
                elem.eb_CO2e_cb_from_elec if elem.eb_CO2e_cb_from_elec != None else 0
                for elem in args
            ]
        )
        eb_CO2e_cb_from_fuels = sum(
            [
                elem.eb_CO2e_cb_from_fuels if elem.eb_CO2e_cb_from_fuels != None else 0
                for elem in args
            ]
        )
        CO2e_pb = sum([elem.CO2e_pb if elem.CO2e_pb != None else 0 for elem in args])
        eb_CO2e_pb_from_heat = sum(
            [
                elem.eb_CO2e_pb_from_heat if elem.eb_CO2e_pb_from_heat != None else 0
                for elem in args
            ]
        )

        return cls(
            energy=energy,
            energy_from_same_eb_sector=energy_from_same_eb_sector,
            energy_from_eb_agri_sector=energy_from_eb_agri_sector,
            CO2e_cb=CO2e_cb,
            eb_CO2e_from_same_sector=eb_CO2e_from_same_sector,
            eb_CO2e_cb_from_agri=eb_CO2e_cb_from_agri,
            eb_CO2e_cb_from_heat=eb_CO2e_cb_from_heat,
            eb_CO2e_cb_from_elec=eb_CO2e_cb_from_elec,
            eb_CO2e_cb_from_fuels=eb_CO2e_cb_from_fuels,
            CO2e_pb=CO2e_pb,
            eb_CO2e_pb_from_heat=eb_CO2e_pb_from_heat,
        )


@dataclass
class EnergySource:
    """
    This class is used as a result class only taking the relevant attributes from class EnergySourceCalcIntermediate for the result dict.
    """
    # energy consumption
    energy: float = 0

    # combustion based Emissions
    CO2e_cb: float = 0

    # production based Emissions
    CO2e_pb: float | None = None

    def __init__(self, energy_source_intermediate: EnergySourceCalcIntermediate):
        self.energy = energy_source_intermediate.energy
        self.CO2e_cb = energy_source_intermediate.CO2e_cb
        self.CO2e_pb = energy_source_intermediate.CO2e_pb


@dataclass
class BiskoSector:
    # shared BISKO sector variables
    total: Sums

    lpg: EnergySource
    gas: EnergySource
    elec: EnergySource


@dataclass
class BiskoPrivResidences(BiskoSector):
    """
    Bisko Sector for private residences.
    """
    petrol: EnergySource
    fueloil: EnergySource
    coal: EnergySource
    heatnet: EnergySource
    biomass: EnergySource
    solarth: EnergySource
    heatpump: EnergySource

    @classmethod
    def calc_priv_residences_bisko(
        cls,
        r18: residences2018.R18,
        h18: heat2018.H18,
        f18: fuels2018.F18,
        e18: electricity2018.E18,
    ) -> "BiskoPrivResidences":

        petrol = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=r18.s_petrol.energy,
            eb_CO2e_cb_from_same_sector=r18.s_petrol.CO2e_total,
            eb_CO2e_cb_from_fuels=f18.p_petrol.CO2e_production_based
            * div(f18.d_r.energy, f18.d.energy),
        )
        fueloil = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=r18.s_fueloil.energy,
            eb_CO2e_cb_from_same_sector=r18.s_fueloil.CO2e_total,
            eb_CO2e_cb_from_heat=h18.p_fueloil.CO2e_combustion_based
            * div(h18.d_r.energy, h18.d.energy),
        )
        coal = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=r18.s_coal.energy,
            eb_CO2e_cb_from_same_sector=r18.s_coal.CO2e_total,
            eb_CO2e_cb_from_heat=h18.p_coal.CO2e_combustion_based
            * div(h18.d_r.energy, h18.d.energy),
            eb_CO2e_pb_from_heat=h18.p_coal.CO2e_production_based
            * div(h18.d_r.energy, h18.d.energy),
        )
        lpg = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=r18.s_lpg.energy,
            eb_CO2e_cb_from_same_sector=r18.s_lpg.CO2e_total,
            eb_CO2e_cb_from_heat=h18.p_lpg.CO2e_combustion_based
            * div(h18.d_r.energy, h18.d.energy),
        )
        gas = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=r18.s_gas.energy,
            eb_CO2e_cb_from_same_sector=r18.s_gas.CO2e_total,
            eb_CO2e_cb_from_heat=h18.p_gas.CO2e_combustion_based
            * div(h18.d_r.energy, h18.d.energy),
            eb_CO2e_pb_from_heat=h18.p_gas.CO2e_production_based
            * div(h18.d_r.energy, h18.d.energy),
        )
        heatnet = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=r18.s_heatnet.energy,
            eb_CO2e_cb_from_same_sector=r18.s_heatnet.CO2e_total,
            eb_CO2e_cb_from_heat=h18.p_heatnet.CO2e_combustion_based
            * div(h18.d_r.energy, h18.d.energy),
        )
        biomass = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=r18.s_biomass.energy,
            eb_CO2e_cb_from_same_sector=r18.s_biomass.CO2e_total,
            eb_CO2e_pb_from_heat=h18.p_biomass.CO2e_production_based
            * div(h18.d_r.energy, h18.d.energy),
        )
        solarth = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=r18.s_solarth.energy,
            eb_CO2e_cb_from_same_sector=r18.s_solarth.CO2e_total,
            eb_CO2e_pb_from_heat=h18.p_solarth.CO2e_production_based
            * div(h18.d_r.energy, h18.d.energy),
        )
        heatpump = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=r18.s_heatpump.energy,
            eb_CO2e_cb_from_same_sector=r18.s_heatpump.CO2e_total,
            eb_CO2e_pb_from_heat=h18.p_heatpump.CO2e_production_based
            * div(h18.d_r.energy, h18.d.energy),
        )
        elec = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=r18.s_elec.energy,
            eb_CO2e_cb_from_same_sector=r18.s_elec.CO2e_total,
            eb_CO2e_cb_from_elec=e18.p.CO2e_total * div(e18.d_r.energy, e18.d.energy),
        )

        total = Sums.calc(
            petrol, fueloil, coal, lpg, gas, heatnet, biomass, solarth, heatpump, elec
        )

        return cls(
            petrol=EnergySource(petrol),
            fueloil=EnergySource(fueloil),
            coal=EnergySource(coal),
            lpg=EnergySource(lpg),
            gas=EnergySource(gas),
            heatnet=EnergySource(heatnet),
            biomass=EnergySource(biomass),
            solarth=EnergySource(solarth),
            heatpump=EnergySource(heatpump),
            elec=EnergySource(elec),
            total=total,
        )


@dataclass
class BiskoBuissenesses(BiskoSector):
    petrol: EnergySource
    diesel: EnergySource
    jetfuel: EnergySource
    fueloil: EnergySource
    coal: EnergySource
    heatnet: EnergySource
    biomass: EnergySource
    solarth: EnergySource
    heatpump: EnergySource

    @classmethod
    def calc_buissenesses_bisko(
        cls,
        b18: business2018.B18,
        h18: heat2018.H18,
        f18: fuels2018.F18,
        e18: electricity2018.E18,
        a18: agri2018.A18,
    ) -> "BiskoBuissenesses":

        petrol = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=b18.s_petrol.energy,
            eb_energy_from_agri=a18.s_petrol.energy,
            eb_CO2e_cb_from_same_sector=b18.s_petrol.CO2e_total,
            eb_CO2e_cb_from_agri=a18.s_petrol.CO2e_total,
            eb_CO2e_cb_from_fuels=f18.p_petrol.CO2e_production_based
            * div(f18.d_b.energy + f18.d_a.energy, f18.d.energy),
        )
        diesel = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=b18.s_diesel.energy,
            eb_energy_from_agri=a18.s_diesel.energy,
            eb_CO2e_cb_from_same_sector=b18.s_diesel.CO2e_total,
            eb_CO2e_cb_from_agri=a18.s_diesel.CO2e_total,
            eb_CO2e_cb_from_fuels=f18.p_diesel.CO2e_production_based
            * div(f18.d_b.energy + f18.d_a.energy, f18.d.energy),
        )
        jetfuel = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=b18.s_jetfuel.energy,
            eb_CO2e_cb_from_same_sector=b18.s_jetfuel.CO2e_total,
            eb_CO2e_cb_from_fuels=f18.p_jetfuel.CO2e_production_based
            * div(f18.d_b.energy, f18.d.energy),
        )
        # TODO: fix h.18.a_t....
        fueloil = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=b18.s_fueloil.energy,
            eb_energy_from_agri=a18.s_fueloil.energy,
            eb_CO2e_cb_from_same_sector=b18.s_fueloil.CO2e_total,
            eb_CO2e_cb_from_agri=a18.s_fueloil.CO2e_combustion_based,
            eb_CO2e_cb_from_heat=h18.p_fueloil.CO2e_combustion_based
            * div(h18.d_b.energy + h18.a_t.energy, h18.d.energy),
        )
        coal = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=b18.s_coal.energy,
            eb_CO2e_cb_from_same_sector=b18.s_coal.CO2e_total,
            eb_CO2e_cb_from_heat=h18.p_coal.CO2e_combustion_based
            * div(h18.d_b.energy, h18.d.energy),
            eb_CO2e_pb_from_heat=h18.p_coal.CO2e_production_based
            * div(h18.d_b.energy, h18.d.energy),
        )
        lpg = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=b18.s_lpg.energy,
            eb_energy_from_agri=a18.s_lpg.energy,
            eb_CO2e_cb_from_same_sector=b18.s_lpg.CO2e_total,
            eb_CO2e_cb_from_agri=a18.s_lpg.CO2e_total,
            eb_CO2e_cb_from_heat=h18.p_lpg.CO2e_combustion_based
            * div(h18.d_b.energy + h18.a_t.energy, h18.d.energy),
        )
        gas = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=b18.s_gas.energy,
            eb_energy_from_agri=a18.s_gas.energy,
            eb_CO2e_cb_from_same_sector=b18.s_gas.CO2e_total,
            eb_CO2e_cb_from_agri=a18.s_gas.CO2e_total,
            eb_CO2e_cb_from_heat=h18.p_gas.CO2e_combustion_based
            * div(h18.d_b.energy + h18.a_t.energy, h18.d.energy),
            eb_CO2e_pb_from_heat=h18.p_gas.CO2e_production_based
            * div(h18.d_b.energy + h18.a_t.energy, h18.d.energy),
        )
        heatnet = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=b18.s_heatnet.energy,
            eb_CO2e_cb_from_same_sector=b18.s_heatnet.CO2e_total,
            eb_CO2e_cb_from_heat=h18.p_heatnet.CO2e_combustion_based
            * div(h18.d_b.energy, h18.d.energy),
        )
        biomass = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=b18.s_biomass.energy,
            eb_energy_from_agri=a18.s_biomass.energy,
            eb_CO2e_cb_from_same_sector=b18.s_biomass.CO2e_total,
            eb_CO2e_cb_from_agri=a18.s_biomass.CO2e_total,
            eb_CO2e_pb_from_heat=h18.p_biomass.CO2e_production_based
            * div(h18.d_b.energy + h18.a_t.energy, h18.d.energy),
        )
        solarth = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=b18.s_solarth.energy,
            eb_CO2e_cb_from_same_sector=b18.s_solarth.CO2e_total,
            eb_CO2e_pb_from_heat=h18.p_solarth.CO2e_production_based
            * div(h18.d_b.energy, h18.d.energy),
        )
        heatpump = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=b18.s_heatpump.energy,
            eb_CO2e_cb_from_same_sector=b18.s_heatpump.CO2e_total,
            eb_CO2e_pb_from_heat=h18.p_heatpump.CO2e_production_based
            * div(h18.d_b.energy, h18.d.energy),
        )
        elec = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=b18.s_elec.energy,
            eb_energy_from_agri=a18.s_elec.energy,
            eb_CO2e_cb_from_same_sector=b18.s_elec.CO2e_total,
            eb_CO2e_cb_from_agri=a18.s_elec.CO2e_total,
            eb_CO2e_cb_from_elec=e18.p.CO2e_total
            * div(e18.d_b.energy + e18.d_a.energy, e18.d.energy),
        )

        total = Sums.calc(
            petrol,
            diesel,
            jetfuel,
            fueloil,
            coal,
            lpg,
            gas,
            heatnet,
            biomass,
            solarth,
            heatpump,
            elec,
        )

        return cls(
            petrol=EnergySource(petrol),
            diesel=EnergySource(diesel),
            jetfuel=EnergySource(jetfuel),
            fueloil=EnergySource(fueloil),
            coal=EnergySource(coal),
            lpg=EnergySource(lpg),
            gas=EnergySource(gas),
            heatnet=EnergySource(heatnet),
            biomass=EnergySource(biomass),
            solarth=EnergySource(solarth),
            heatpump=EnergySource(heatpump),
            elec=EnergySource(elec),
            total=total,
        )


@dataclass
class BiskoTransport(BiskoSector):
    """
    Bisko sector for transportation.
    """
    petrol: EnergySource
    diesel: EnergySource
    jetfuel: EnergySource
    bioethanol: EnergySource
    biodiesel: EnergySource
    biogas: EnergySource

    @classmethod
    def calc_transport_bisko(
        cls,
        inputs: Inputs,
        t18: transport2018.T18,
        h18: heat2018.H18,
        f18: fuels2018.F18,
        e18: electricity2018.E18,
    ) -> "BiskoTransport":

        fact = inputs.fact
        ass = inputs.ass

        petrol = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=t18.s_petrol.energy,
            eb_CO2e_cb_from_same_sector=t18.s_petrol.energy
            * fact("Fact_T_S_petrol_EmFa_tank_wheel_2018"),
            eb_CO2e_cb_from_fuels=f18.p_petrol.CO2e_production_based
            * div(f18.d_t.energy, f18.d.energy),
        )
        diesel = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=t18.s_diesel.energy,
            eb_CO2e_cb_from_same_sector=t18.s_diesel.energy
            * fact("Fact_T_S_diesel_EmFa_tank_wheel_2018"),
            eb_CO2e_cb_from_fuels=f18.p_diesel.CO2e_production_based
            * div(f18.d_t.energy + f18.d_a.energy, f18.d.energy),
        )
        jetfuel = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=t18.s_jetfuel.energy,
            eb_CO2e_cb_from_same_sector=t18.s_jetfuel.energy
            * fact("Fact_T_S_jetfuel_EmFa_tank_wheel_2018"),
            eb_CO2e_cb_from_fuels=f18.p_jetfuel.CO2e_production_based
            * div(f18.d_t.energy, f18.d.energy),
        )
        bioethanol = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=t18.s_bioethanol.energy,
            eb_CO2e_cb_from_same_sector=t18.s_bioethanol.energy
            * ass("Ass_T_S_bioethanol_EmFa_tank_wheel"),
            eb_CO2e_cb_from_fuels=f18.p_bioethanol.CO2e_production_based
            * div(f18.d_t.energy, f18.d.energy),
        )
        biodiesel = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=t18.s_biodiesel.energy,
            eb_CO2e_cb_from_same_sector=t18.s_biodiesel.energy
            * ass("Ass_T_S_biodiesel_EmFa_tank_wheel"),
            eb_CO2e_cb_from_fuels=f18.p_biodiesel.CO2e_production_based
            * div(f18.d_t.energy, f18.d.energy),
        )
        biogas = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=t18.s_biogas.energy,
            eb_CO2e_cb_from_same_sector=t18.s_biogas.energy
            * ass("Ass_T_S_biogas_EmFa_tank_wheel"),
            eb_CO2e_cb_from_fuels=f18.p_biogas.CO2e_production_based
            * div(f18.d_t.energy, f18.d.energy),
        )
        lpg = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=t18.s_lpg.energy,
            eb_CO2e_cb_from_same_sector=t18.s_lpg.energy
            * fact("Fact_T_S_lpg_EmFa_tank_wheel_2018"),
            eb_CO2e_cb_from_heat=h18.p_lpg.CO2e_combustion_based
            * div(h18.d_t.energy, h18.d.energy),
        )
        gas = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=t18.s_gas.energy,
            eb_CO2e_cb_from_same_sector=t18.s_gas.energy
            * fact("Fact_T_S_cng_EmFa_tank_wheel_2018"),
            eb_CO2e_cb_from_heat=h18.p_gas.CO2e_combustion_based
            * div(h18.d_t.energy, h18.d.energy),
            eb_CO2e_pb_from_heat=h18.p_gas.CO2e_production_based
            * div(h18.d_t.energy, h18.d.energy),
        )
        elec = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=t18.s_elec.energy,
            eb_CO2e_cb_from_same_sector=t18.s_elec.energy
            * fact("Fact_T_S_electricity_EmFa_tank_wheel_2018"),
            eb_CO2e_cb_from_elec=e18.p.CO2e_total * div(e18.d_t.energy, e18.d.energy),
        )

        total = Sums.calc(
            petrol, diesel, jetfuel, bioethanol, biodiesel, biogas, lpg, gas, elec
        )

        return cls(
            petrol=EnergySource(petrol),
            diesel=EnergySource(diesel),
            jetfuel=EnergySource(jetfuel),
            bioethanol=EnergySource(bioethanol),
            biodiesel=EnergySource(biodiesel),
            biogas=EnergySource(biogas),
            lpg=EnergySource(lpg),
            gas=EnergySource(gas),
            elec=EnergySource(elec),
            total=total,
        )


@dataclass
class SubSector:
    CO2e_cb: float
    CO2e_pb: float

    @classmethod
    def calc_sum(cls, *args: "SubSector") -> "SubSector":
        CO2e_cb: float = sum(
            [elem.CO2e_cb if elem.CO2e_cb != None else 0 for elem in args]
        )
        CO2e_pb: float = sum(
            [elem.CO2e_pb if elem.CO2e_pb != None else 0 for elem in args]
        )
        return cls(CO2e_cb=CO2e_cb, CO2e_pb=CO2e_pb)


@dataclass
class BiskoIndustry(BiskoSector):
    """
    Bisko sector for industry. We are currently not able to calculate any single energy source emissions in the eb_industry sector.
    Therefore it is not possible to calculate bisko single energy source emissions, except from single energy source emissions coming from other "Einflussbilanz" sectors.
    Instead the emissions are only calculated for the industry sub sectors.
    """
    diesel: EnergySource
    fueloil: EnergySource
    coal: EnergySource
    other_fossil: EnergySource
    heatnet: EnergySource
    biomass: EnergySource
    solarth: EnergySource
    heatpump: EnergySource

    miner: SubSector
    chemistry: SubSector
    metal: SubSector
    other: SubSector

    total_production: SubSector
    total_industry: SubSector

    @classmethod
    def calc_industry_bisko(
        cls,
        i18: industry2018.I18,
        h18: heat2018.H18,
        f18: fuels2018.F18,
        e18: electricity2018.E18,
    ) -> "BiskoIndustry":
        # Bereitstellung
        diesel = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=i18.s_fossil_diesel.energy,
            eb_CO2e_cb_from_fuels=f18.p_diesel.CO2e_production_based
            * div(f18.d_i.energy, f18.d.energy),
        )
        fueloil = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=i18.s_fossil_fueloil.energy,
            eb_CO2e_cb_from_heat=h18.p_fueloil.CO2e_combustion_based
            * div(h18.d_i.energy, h18.d.energy),
        )
        coal = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=i18.s_fossil_coal.energy,
            eb_CO2e_cb_from_heat=h18.p_coal.CO2e_combustion_based
            * div(h18.d_i.energy, h18.d.energy),
            eb_CO2e_pb_from_heat=h18.p_coal.CO2e_production_based
            * div(h18.d_i.energy, h18.d.energy),
        )
        lpg = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=i18.s_fossil_lpg.energy,
            eb_CO2e_cb_from_heat=h18.p_lpg.CO2e_combustion_based
            * div(h18.d_i.energy, h18.d.energy),
        )
        gas = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=i18.s_fossil_gas.energy,
            eb_CO2e_cb_from_heat=h18.p_gas.CO2e_combustion_based
            * div(h18.d_i.energy, h18.d.energy),
            eb_CO2e_pb_from_heat=h18.p_gas.CO2e_production_based
            * div(h18.d_i.energy, h18.d.energy),
        )
        other_fossil = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=i18.s_fossil_ofossil.energy
            + i18.s_fossil_opetpro.energy,
            eb_CO2e_cb_from_heat=h18.p_opetpro.CO2e_combustion_based,
            eb_CO2e_pb_from_heat=h18.p_opetpro.CO2e_production_based
            + h18.p_ofossil.CO2e_production_based,
        )

        heatnet = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=i18.s_renew_heatnet.energy,
            eb_CO2e_cb_from_heat=h18.p_heatnet.CO2e_combustion_based
            * div(h18.d_i.energy, h18.d.energy),
        )
        biomass = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=i18.s_renew_biomass.energy,
            eb_CO2e_pb_from_heat=h18.p_biomass.CO2e_production_based
            * div(h18.d_i.energy, h18.d.energy),
        )
        solarth = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=i18.s_renew_solarth.energy,
            eb_CO2e_pb_from_heat=h18.p_solarth.CO2e_production_based
            * div(h18.d_i.energy, h18.d.energy),
        )
        heatpump = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=i18.s_renew_heatpump.energy,
            eb_CO2e_pb_from_heat=h18.p_heatpump.CO2e_production_based
            * div(h18.d_i.energy, h18.d.energy),
        )
        elec = EnergySourceCalcIntermediate(
            eb_energy_from_same_sector=i18.s_renew_elec.energy,
            eb_CO2e_cb_from_elec=e18.p.CO2e_total * div(e18.d_i.energy, e18.d.energy),
        )
        # total Bereitstellung
        total_supply = Sums.calc(
            diesel,
            fueloil,
            coal,
            lpg,
            gas,
            other_fossil,
            heatnet,
            biomass,
            solarth,
            heatpump,
            elec,
        )

        miner = SubSector(
            CO2e_cb=i18.p_miner.CO2e_combustion_based,
            CO2e_pb=i18.p_miner.CO2e_production_based,
        )
        chem = SubSector(
            CO2e_cb=i18.p_chem.CO2e_combustion_based,
            CO2e_pb=i18.p_chem.CO2e_production_based,
        )
        metal = SubSector(
            CO2e_cb=i18.p_metal.CO2e_combustion_based,
            CO2e_pb=i18.p_metal.CO2e_production_based,
        )
        other = SubSector(
            CO2e_cb=i18.p_other.CO2e_combustion_based,
            CO2e_pb=i18.p_other.CO2e_production_based,
        )

        total_production = SubSector.calc_sum(miner, chem, metal, other)
        total_industry = SubSector(
            CO2e_cb=total_production.CO2e_cb + total_supply.CO2e_cb,
            CO2e_pb=total_production.CO2e_pb + total_supply.CO2e_pb,
        )

        return cls(
            diesel=EnergySource(diesel),
            fueloil=EnergySource(fueloil),
            coal=EnergySource(coal),
            lpg=EnergySource(lpg),
            gas=EnergySource(gas),
            other_fossil=EnergySource(other_fossil),
            heatnet=EnergySource(heatnet),
            biomass=EnergySource(biomass),
            solarth=EnergySource(solarth),
            heatpump=EnergySource(heatpump),
            elec=EnergySource(elec),
            total=total_supply,
            miner=miner,
            chemistry=chem,
            metal=metal,
            other=other,
            total_production=total_production,
            total_industry=total_industry,
        )


@dataclass
class ProductionBasedEmission:
    CO2e_pb: float

    @classmethod
    def calc_sum(cls, *args: "ProductionBasedEmission") -> "ProductionBasedEmission":
        CO2e_pb = sum([elem.CO2e_pb for elem in args])
        return cls(CO2e_pb=CO2e_pb)


@dataclass
class BiskoProductionBasedOnly:
    """
    This super class contains shared production based only attributes.  
    """
    total: ProductionBasedEmission


@dataclass
class BiskoAgriculture(BiskoProductionBasedOnly):

    forest: ProductionBasedEmission
    manure: ProductionBasedEmission
    soil: ProductionBasedEmission
    other: ProductionBasedEmission

    @classmethod
    def calc_bisko_agri(cls, a18: agri2018.A18) -> "BiskoAgriculture":
        forest = ProductionBasedEmission(CO2e_pb=a18.p_fermen.CO2e_production_based)
        manure = ProductionBasedEmission(CO2e_pb=a18.p_manure.CO2e_production_based)
        soil = ProductionBasedEmission(CO2e_pb=a18.p_soil.CO2e_production_based)
        other = ProductionBasedEmission(CO2e_pb=a18.p_other.CO2e_production_based)

        total = ProductionBasedEmission.calc_sum(forest, manure, soil, other)

        return cls(forest=forest, manure=manure, soil=soil, other=other, total=total)


@dataclass
class BiskoLULUCF(BiskoProductionBasedOnly):

    forest: ProductionBasedEmission
    crop: ProductionBasedEmission
    grass: ProductionBasedEmission
    grove: ProductionBasedEmission
    wet: ProductionBasedEmission
    water: ProductionBasedEmission
    settlement: ProductionBasedEmission
    other: ProductionBasedEmission
    wood: ProductionBasedEmission

    @classmethod
    def calc_bisko_lulucf(cls, l18: lulucf2018.L18) -> "BiskoLULUCF":
        forest = ProductionBasedEmission(CO2e_pb=l18.g_forest.CO2e_production_based)
        crop = ProductionBasedEmission(CO2e_pb=l18.g_crop.CO2e_production_based)
        grass = ProductionBasedEmission(CO2e_pb=l18.g_grass.CO2e_production_based)
        grove = ProductionBasedEmission(CO2e_pb=l18.g_grove.CO2e_production_based)
        wet = ProductionBasedEmission(CO2e_pb=l18.g_wet.CO2e_production_based)
        water = ProductionBasedEmission(CO2e_pb=l18.g_water.CO2e_production_based)
        settlement = ProductionBasedEmission(
            CO2e_pb=l18.g_settlement.CO2e_production_based
        )
        other = ProductionBasedEmission(CO2e_pb=l18.g_other.CO2e_production_based)
        wood = ProductionBasedEmission(CO2e_pb=l18.g_wood.CO2e_production_based)

        total = ProductionBasedEmission.calc_sum(
            forest, crop, grass, grove, wet, water, settlement, other, wood
        )

        return cls(
            forest=forest,
            crop=crop,
            grass=grass,
            grove=grove,
            wet=wet,
            water=water,
            settlement=settlement,
            other=other,
            wood=wood,
            total=total,
        )


@dataclass
class Bisko:
    priv_residences: BiskoPrivResidences
    buissenesses: BiskoBuissenesses
    transport: BiskoTransport
    industry: BiskoIndustry

    agri: BiskoAgriculture
    lulucf: BiskoLULUCF

    total_energy: float
    total_CO2e_combustion_based: float
    total_CO2e_production_based: float

    bisko_quality: float

    @classmethod
    def calc(
        cls,
        inputs: Inputs,
        *,
        a18: agri2018.A18,
        b18: business2018.B18,
        e18: electricity2018.E18,
        f18: fuels2018.F18,
        h18: heat2018.H18,
        i18: industry2018.I18,
        l18: lulucf2018.L18,
        r18: residences2018.R18,
        t18: transport2018.T18,
    ) -> "Bisko":

        priv_residences_bisko = BiskoPrivResidences.calc_priv_residences_bisko(r18=r18, h18=h18, f18=f18, e18=e18)
        buissenesses_bisko = BiskoBuissenesses.calc_buissenesses_bisko(b18=b18, h18=h18, f18=f18, e18=e18, a18=a18)
        transport_bisko = BiskoTransport.calc_transport_bisko(
            inputs=inputs, t18=t18, h18=h18, f18=f18, e18=e18
        )
        industry_bisko = BiskoIndustry.calc_industry_bisko(
            i18=i18, h18=h18, f18=f18, e18=e18
        )
        agri_bisko = BiskoAgriculture.calc_bisko_agri(a18=a18)
        lulucf_bisko = BiskoLULUCF.calc_bisko_lulucf(l18=l18)

        total_energy = (
            priv_residences_bisko.total.energy
            + buissenesses_bisko.total.energy
            + transport_bisko.total.energy
            + industry_bisko.total.energy
        )
        total_CO2e_combustion_based = (
            priv_residences_bisko.total.CO2e_cb
            + buissenesses_bisko.total.CO2e_cb
            + transport_bisko.total.CO2e_cb
            + industry_bisko.total.CO2e_cb
        )
        total_CO2e_production_based = (
            priv_residences_bisko.total.CO2e_pb
            + buissenesses_bisko.total.CO2e_pb
            + transport_bisko.total.CO2e_pb
            + industry_bisko.total.CO2e_pb
            + agri_bisko.total.CO2e_pb
            + lulucf_bisko.total.CO2e_pb
        )

        bisko_quality = transport_bisko.total.energy * div(0.5, total_energy)

        return cls(
            priv_residences=priv_residences_bisko,
            buissenesses=buissenesses_bisko,
            transport=transport_bisko,
            industry=industry_bisko,
            agri=agri_bisko,
            lulucf=lulucf_bisko,
            total_energy=total_energy,
            total_CO2e_combustion_based=total_CO2e_combustion_based,
            total_CO2e_production_based=total_CO2e_production_based,
            bisko_quality=bisko_quality,
        )
