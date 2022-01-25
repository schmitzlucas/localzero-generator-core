"""Module refdata -- tools to read the reference data used by the generator.

"""
from dataclasses import dataclass
import os
import json
import sys

import pandas as pd

# TODO: Write small wrappers classes for each data source so that we can document
# the columns and get better type checking from pylance.

# The traffic dataset was paid for by GermanZero and therefore can only
# be used when the generator is run by members of GermanZero
PROPRIETARY_DATA_SOURCES = frozenset(["traffic"])


def _load(datadir: str, what: str, year: int = 2018) -> pd.DataFrame:
    repo = "proprietary" if what in PROPRIETARY_DATA_SOURCES else "public"
    return pd.read_csv(
        os.path.join(datadir, repo, what, str(year) + ".csv"), dtype={"ags": "str"}
    )


class RowNotFound(Exception):
    ags: str
    df: pd.DataFrame

    def __init__(self, ags, df):
        self.ags = ags
        self.df = df

    def __str__(self):
        return f"Could not find ags={self.ags} in dataframe\n{self.df}"


# TODO: Good error messages when field is not populated
# TODO: Good error messages when field name is mistyped


class Row:
    def __init__(self, df: pd.DataFrame, ags: str):
        try:
            # Basically this reduces the dataframe to a single row dataframe
            # and then takes the only dataframe row (a series object)
            # TODO: When we have time figure out what the actually best way
            # to go about all this is. Maybe we should consider dropping
            # pandas as a requirement? I mean all we do is load a few csvs
            # and extract a very small number of rows. pandas is total overkill
            # in particular when we are publishing a package for others to use
            # it's nice to have a small list of dependencies
            self._series = df[df["ags"] == ags].iloc[0]
        except:
            raise RowNotFound(ags=ags, df=df)

    # TODO: All of the accessors below should not cast so forcefully but
    # only convert into the python type when the pandas type matches

    def float(self, attr: str) -> float:
        return float(self._series[attr])  # type: ignore

    def int(self, attr: str) -> int:
        try:
            return int(self._series[attr])  # type: ignore
        except Exception as e:
            print("INT FAILED", self._series, attr, file=sys.stderr)
            raise e

    def str(self, attr: str) -> str:
        return str(self._series[attr])


class FactsAndAssumptions:
    def __init__(self, facts: pd.DataFrame, assumptions: pd.DataFrame):
        self._facts = facts
        self._assumptions = assumptions

    def fact(self, keyname: str) -> float:
        """Statistics about the past. Must be able to give a source for each fact."""
        # TODO: Kill the exception handler
        try:
            value = float(self._facts[self._facts["label"] == keyname]["value"])  # type: ignore
            return value

        except:
            print("could not find " + keyname, file=sys.stderr)
            return 1.0

    def ass(self, keyname: str) -> float:
        """Similar to fact, but these try to describe the future. And are therefore based on various assumptions."""
        # TODO: Kill the exception handler
        try:
            value = float(self._assumptions[self._assumptions["label"] == keyname]["value"])  # type: ignore
            return value

        except:
            print("could not find " + keyname, file=sys.stderr)
            return 1.0


def datadir_or_default(datadir: str | None = None) -> str:
    """Return the normalized absolute path to the data directory."""
    if datadir is None:
        return os.path.normpath(os.path.join(os.getcwd(), "data"))
    else:
        return os.path.abspath(datadir)


@dataclass
class Version:
    """This classes identifies a particular version of the reference data."""

    public: str  # The git hash of the public repository
    proprietary: str  # The git hash of the proprietary repository

    @classmethod
    def load(cls, name: str, datadir: str | None = None) -> "Version":
        fname = os.path.join(datadir_or_default(datadir), name + ".json")
        with open(fname) as fp:
            d = json.load(fp)
            return cls(public=d["public"], proprietary=d["proprietary"])


class RefData:
    """This class gives you a single handle around all the reference data."""

    def __init__(
        self,
        area: pd.DataFrame,
        area_kinds: pd.DataFrame,
        assumptions: pd.DataFrame,
        buildings: pd.DataFrame,
        destatis: pd.DataFrame,
        facts: pd.DataFrame,
        flats: pd.DataFrame,
        nat_agri: pd.DataFrame,
        nat_organic_agri: pd.DataFrame,
        nat_energy: pd.DataFrame,
        nat_res_buildings: pd.DataFrame,
        population: pd.DataFrame,
        renewable_energy: pd.DataFrame,
        traffic: pd.DataFrame,
    ):
        self._area = area
        self._area_kinds = area_kinds
        self._facts_and_assumptions = FactsAndAssumptions(facts, assumptions)
        self._buildings = buildings
        self._destatis = destatis
        self._flats = flats
        self._nat_agri = nat_agri
        self._nat_organic_agri = nat_organic_agri
        self._nat_energy = nat_energy
        self._nat_res_buildings = nat_res_buildings
        self._population = population
        self._renewable_energy = renewable_energy
        self._traffic = traffic

    def facts_and_assumptions(self) -> FactsAndAssumptions:
        return self._facts_and_assumptions

    def fact(self, keyname: str) -> float:
        return self._facts_and_assumptions.fact(keyname)

    def ass(self, keyname: str) -> float:
        return self._facts_and_assumptions.ass(keyname)

    def area(self, ags: str):
        """How many hectare of land are used for what (e.g. farmland, traffic, ...) in each community / administrative district and federal state."""
        return Row(self._area, ags)

    def area_kinds(self, ags: str):
        return Row(self._area_kinds, ags)

    def buildings(self, ags: str):
        """Number of flats. Number of buildings of different age brackets. Connections to heatnet."""
        return Row(self._buildings, ags)

    def destatis(self, ags: str):
        """TODO"""
        return Row(self._destatis, ags)

    def flats(self, ags: str):
        """TODO"""
        return Row(self._flats, ags)

    def nat_agri(self, ags: str):
        """TODO"""
        return Row(self._nat_agri, ags)

    def nat_organic_agri(self, ags: str):
        """TODO"""
        return Row(self._nat_organic_agri, ags)

    def nat_energy(self, ags: str):
        """TODO"""
        return Row(self._nat_energy, ags)

    def nat_res_buildings(self, ags: str):
        """TODO"""
        return Row(self._nat_res_buildings, ags)

    def population(self, ags: str):
        """How many residents live in each commmunity / administrative district and federal state."""
        return Row(self._population, ags)

    def renewable_energy(self, ags: str):
        """TODO"""
        return Row(self._renewable_energy, ags)

    def traffic(self, ags: str):
        """TODO"""
        return Row(self._traffic, ags)

    @classmethod
    def load(cls, datadir: str | None = None) -> "RefData":
        """Load all the reference data into memory.  This assumes that the working directory has a subdirectory
        called 'data' that contains the reference data in two subfolders one called 'public' and the other
        'proprietary'.

        If your data directory is somewhere else provide the full path to it.

        TODO: Provide a way to run this even when no proprietary data is available. As of right now unnecessary
        as we can't yet run the generator without the data.
        """
        datadir = datadir_or_default(datadir)
        d = cls(
            area=_load(datadir, "area"),
            area_kinds=_load(datadir, "area_kinds"),
            assumptions=_load(datadir, "assumptions"),
            buildings=_load(datadir, "buildings"),
            destatis=_load(datadir, "destatis"),
            facts=_load(datadir, "facts"),
            flats=_load(datadir, "flats"),
            nat_agri=_load(datadir, "nat_agri"),
            nat_organic_agri=_load(datadir, "nat_organic_agri", 2016),
            nat_energy=_load(datadir, "nat_energy"),
            nat_res_buildings=_load(datadir, "nat_res_buildings"),
            population=_load(datadir, "population"),
            renewable_energy=_load(datadir, "renewable_energy"),
            traffic=_load(datadir, "traffic"),
        )
        return d
