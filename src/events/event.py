
# Imports 
from dataclasses import dataclass, field
from datetime import datetime
from event_types import EventType

@dataclass
class MarketDataEvent:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    event_type: EventType = field(default=EventType.MARKET_DATA, init=False)



@dataclass
class SignalEvent:
    symbol: str
    timestamp: datetime
    side: str
    strength: float
    event_type: EventType = field(default=EventType.SIGNAL, init=False)



@dataclass
class OrderEvent:
    symbol: str
    timestamp: datetime
    side: str
    quantity: int
    order_type: str
    event_type: EventType = field(default=EventType.ORDER, init=False)

@dataclass
class FillEvent:
    event_type: EventType = field(default=EventType.FILL, init=False)
    symbol: str
    timestamp: datetime
    side: str
    quantity: int
    fill_price: float
    commission: float
    event_type: EventType = field(default=EventType.FILL, init=False)
