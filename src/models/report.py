from dataclasses import dataclass, field
from datetime import datetime
from .room import Room
from .client import Client
from enum import IntEnum, auto
from typing import List, Tuple
from enum import Enum


from typing import Optional, BinaryIO

@dataclass
class Report:
    class Service(IntEnum):
        UNKNOWN = auto()
        SERVICE = auto()
        MAINTENANCE = auto()
        CHECK_LIST = auto()

        def __str__(self) -> str:
            return SERVICE_NAMES[self]

        def get_description_text(self):
            return SERVICE_DESCRIPTION_TEXT[self]

        def get_description_points(self):
            return SERVICE_DESCRIPTION_POINTS[self]

        def for_button(self, text: str) -> tuple[str, IntEnum]:
            return (text, self)

    class ExtraService(IntEnum):
        UNKNOWN = auto()
        THERMAIL_INSULATOR_CHANGE_JOB = auto()
        NEW_POLYESTER_FILTERS_INSTALLATION = auto()
        COLD_FOG_MACHINE_DISINFECTIONS = auto()
        REPAIR_WORKS = auto()

        def __str__(self) -> str:
            return EXTRA_SERVICE_NAME[self]

        def get_description(self):
            return EXTRA_SERVICE_DESCRIPTION[self]

        def for_button(self, text: str) -> tuple[str, IntEnum]:
            return (text, self)


    class Type(str, Enum):
        UNKNOWN = "Unknown"
        FULL_MAINTENANCE= "Full Maintenance"
        SUPPORT = "Support"
        OTHER = "Other"

        def __str__(self) -> str:
            return str(self.value)

        def for_button(self, text: str) -> Tuple[str, ...]:
            return (text, self)



    class Factor(IntEnum):
        UNKNOWN = auto()
        DIFFICULT_ACCESS_TO_UNITS = auto()
        NO_ACCESS_TO_OBJECT = auto()
        CUSTOM_SIZES = auto()
        DAY_OFF_WORK = auto()
        WORKING_IN_ANOTHER_EMIRATE = auto()

        def __str__(self) -> str:
            return FACTOR_NAME[self]

        def get_descripiton(self):
            return FACTOR_DESCRIPTION[self]

        def for_button(self, text: str) -> tuple[str, IntEnum]:
            return (text, self)

    date: datetime = datetime.now()
    client: Client = field(default_factory=Client)
    service: Service = Service.UNKNOWN
    description: str = ""
    extra_services: list[ExtraService] = field(default_factory=list)
    other_extra_services: list[str] = field(default_factory=list)
    work_factors: list[Factor] = field(default_factory=list)

    rooms: list[Room] = field(default_factory=list)

    def __post_init__(self):
        self.add_room()

    def add_room(self):
        self.rooms.append(Room())

    def add_factor(self, factor: Factor) -> None:
        self.work_factors.append(factor)

    def pop_factor(self, factor: Factor) -> None:
        self.work_factors.remove(factor)

    def clear_extra_services(self) -> None:
        self.extra_services.clear()
        self.other_extra_services.clear()

    def clear_working_factors(self):
        self.work_factors.clear()



    def create_custom_nodes_list(master_names: list[str]):
        """
        Создает список словарей для мастеров
        """
        return [
            {
                "name": name,
                "button_text": name,
                "type": "DEFAULT"
            }
            for name in master_names
        ]
            
    def get_custom_nodes_list():
        return ["Alex W", "John Doe", "Jane Smith"]  # Пример списка мастеров


    def get_extra_services_descriptions(self) -> list[str]:
        extra_sevices_str = []
        for service in self.extra_services:
            extra_sevices_str.append(EXTRA_SERVICE_DESCRIPTION[service])

        return extra_sevices_str

    def get_work_factors_descriptions(self) -> list[str]:
        work_factors_str = []

        for factor in self.work_factors:
            work_factors_str.append(FACTOR_DESCRIPTION[factor])

        return work_factors_str

    async def dict_with_binary(self, bot, _) -> dict:  # Добавляем параметр _
        return {
            "Outline": {
                "date": self.date,
                "name": self.client.name,
                "phone_number": self.client.phone,
                "address": self.client.address,
                "description": {
                    "text": self.service.get_description_text(),
                    "points": self.service.get_description_points(),
                },
                "performed_service": _(str(self.service)), # Переводим услугу
                "report_service": str(self.service),
                "extra_services": self.get_extra_services_descriptions(),
                "work_factors": self.get_work_factors_descriptions(),
            },
            "Rooms": {
                "number_of_rooms": len(self.rooms),
                "rooms_list": [await room.dict_with_binary(bot, _) for room in self.rooms],  # Передаем _ дальше
            },
        }

SERVICE_NAMES = {
    Report.Service.UNKNOWN: "",
    Report.Service.SERVICE: "Service",
    Report.Service.MAINTENANCE: "Maintenance",
    Report.Service.CHECK_LIST: "Check list",
}

SERVICE_DESCRIPTION_TEXT = {
    Report.Service.SERVICE: "For the service team included:",
    Report.Service.MAINTENANCE: "Maintenance service included:",
    Report.Service.CHECK_LIST: "Minor repairs around the house, not related to the repair of air conditioners and ventilation",
}

SERVICE_DESCRIPTION_POINTS = {
    Report.Service.SERVICE: [
        "Deep cleaning of fan coil unit (VAV, blower fans, air-filter, evaporator coil, drain tray (if accessible))",
        "Check-up and adjustment of valves, fan belts, pulleys, coil, filter, strainer, pipe joints, insulation, bearings, drain trays, drain pipes and manometer tubes. VRV system errors and pressure check-up (as applicable to your type of property)",
        "Checking for noise, leaks, smell, vibration and general performance issues (for villas - refrigerant level check-up, board of roof-top AC unit control clean-up and check-up, controls calibrations checks)",
        "Check-up of thermostat (for villas – starters, relays and timers)",
        "Cleaning of above-ceiling areas (construction work left-overs clean-up, vacuum cleaning with special hose and brush, hand-washing with water)",
        "Disinfection with antibacterial detergent (ShieldMe)",
        "Using anti-dust protection curtains (Zipwall US)",
        "All works performed with german hand tools - DeWalt, Karcher.",
    ],
    Report.Service.MAINTENANCE: [
        "Deep cleaning of fan coil unit (VAV, blower fans, air-filter, evaporator coil, drain tray (if accessible))",
        "Check-up and adjustment of valves, fan belts, pulleys, coil, filter, strainer, pipe joints, insulation, bearings, drain trays, drain pipes and manometer tubes. VRV system errors and pressure check-up (as applicable to your type of property)",
        "Checking for noise, leaks, smell, vibration and general performance issues (for villas - refrigerant level check-up, board of roof-top AC unit control clean-up and check-up, controls calibrations checks)",
        "Check-up of thermostat (for villas – starters, relays and timers)",
        "Cleaning of above-ceiling areas (construction work left-overs clean-up, vacuum cleaning with special hose and brush, hand-washing with water)",
        "Disinfection with antibacterial detergent (ShieldMe)",
        "Using anti-dust protection curtains (Zipwall US)",
        "All works performed with german hand tools - DeWalt, Karcher.",
    ],
    Report.Service.CHECK_LIST: [],
}

EXTRA_SERVICE_NAME = {
    Report.ExtraService.UNKNOWN: "",
    Report.ExtraService.THERMAIL_INSULATOR_CHANGE_JOB: "Thermal insulator change job",
    Report.ExtraService.NEW_POLYESTER_FILTERS_INSTALLATION: "New polyester filters installation",
    Report.ExtraService.COLD_FOG_MACHINE_DISINFECTIONS: "Cold fog machine disinfections",
    Report.ExtraService.REPAIR_WORKS: "Repair Works",
}

EXTRA_SERVICE_DESCRIPTION = {
    Report.ExtraService.UNKNOWN: "",
    Report.ExtraService.THERMAIL_INSULATOR_CHANGE_JOB: "Thermal insulator change job",
    Report.ExtraService.NEW_POLYESTER_FILTERS_INSTALLATION: "fog machine sanitation with OxyPro 7.5 All Purpose Disinfectant Activated Stabilised Hydrogen Peroxide Concentrate",
    Report.ExtraService.COLD_FOG_MACHINE_DISINFECTIONS: "polyester or other recommended by us type of air filter installation/change/wash-through",
    Report.ExtraService.REPAIR_WORKS: "minor repair and maintenance works as described in detail in the invoice",
}

FACTOR_NAME = {
    Report.Factor.DIFFICULT_ACCESS_TO_UNITS: "Cumbersome and difficult access",
    Report.Factor.NO_ACCESS_TO_OBJECT: "NO_ACCESS_TO_OBJECT",
    Report.Factor.CUSTOM_SIZES: "CUSTOM_SIZES",
    Report.Factor.DAY_OFF_WORK: "DAY_OFF_WORK",
    Report.Factor.WORKING_IN_ANOTHER_EMIRATE: "WORKING_INT_ANOTHER_EMIRATE",
}

FACTOR_DESCRIPTION = {
    Report.Factor.DIFFICULT_ACCESS_TO_UNITS: "Cumbersome and otherwise difficult access to units (ceiling access panels located far from AC units, access panels being less than 60 cm and similar) which affected the overall time of works",
    Report.Factor.NO_ACCESS_TO_OBJECT: "Property access permit not applied for/provided/procured for by the Client in advance",
    Report.Factor.CUSTOM_SIZES: "Duct grills and/or diffusers are of the length more than 2 meters long and system has not been serviced for a long time",
    Report.Factor.DAY_OFF_WORK: "The works performed on a weekend or on a UAE National Holiday",
    Report.Factor.WORKING_IN_ANOTHER_EMIRATE: "The Client's premises are located outside Dubai, in other emirate",
}
