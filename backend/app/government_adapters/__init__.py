from app.government_adapters.base_adapter import GovernmentPortalAdapter
from app.government_adapters.gst_adapter import GSTPortalAdapter
from app.government_adapters.udyam_adapter import UdyamPortalAdapter
from app.government_adapters.pan_adapter import PANPortalAdapter
from app.government_adapters.epfo_adapter import EPFOPortalAdapter
from app.government_adapters.esic_adapter import ESICPortalAdapter
from app.government_adapters.startup_india_adapter import StartupIndiaPortalAdapter, NSICPortalAdapter
from app.government_adapters.digilocker_adapter import DigiLockerAdapter
from app.government_adapters.blacklist_adapter import BlacklistDebarmentAdapter
from app.government_adapters.mca_adapter import MCAPortalAdapter

class AdapterRegistry:
    def __init__(self):
        self.gst = GSTPortalAdapter()
        self.udyam = UdyamPortalAdapter()
        self.pan = PANPortalAdapter()
        self.epfo = EPFOPortalAdapter()
        self.esic = ESICPortalAdapter()
        self.startup_india = StartupIndiaPortalAdapter()
        self.nsic = NSICPortalAdapter()
        self.digilocker = DigiLockerAdapter()
        self.blacklist = BlacklistDebarmentAdapter()
        self.mca = MCAPortalAdapter()

adapters = AdapterRegistry()

__all__ = [
    "GovernmentPortalAdapter",
    "GSTPortalAdapter",
    "UdyamPortalAdapter",
    "PANPortalAdapter",
    "EPFOPortalAdapter",
    "ESICPortalAdapter",
    "StartupIndiaPortalAdapter",
    "NSICPortalAdapter",
    "DigiLockerAdapter",
    "BlacklistDebarmentAdapter",
    "MCAPortalAdapter",
    "adapters"
]
