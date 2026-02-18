
"""
# Dictionary 
emit = put(event) into event_queue 
consumed = get(event) from event_queue -> handle(event)
"""

"""
---- Event Ownership ----
-> MarketDataEvent
Emitted by: DataHandler
Consumed by: Strategy, Portfolio (mark-to-market), Risk (optional)

-> SignalEvent
Emitted by: Strategy
Consumed by: Portfolio, Risk (pre-trade)

-> OrderEvent (create/modify/cancel)
Emitted by: Portfolio (and sometimes Risk as a “forced rebalance” generator)
Consumed by: ExecutionHandler

-> FillEvent
Emitted by: ExecutionHandler
Consumed by: Portfolio, Accounting / Ledger, Risk (post-trade)

-> PositionEvent / PnLEvent
Emitted by: Portfolio/Accounting (after fills + mark-to-market)
Consumed by: Metrics/Reporting, Risk (drawdown, leverage), maybe Strategy (if you allow it)

-> RiskEvent
Emitted by: RiskManager
Consumed by: Portfolio (reduce exposure), Execution (cancel orders)

-> CorporateActionEvent (flagship+)
Emitted by: CorporateActionHandler (or DataHandler)
Consumed by: Portfolio/Accounting (adjust shares/cost basis), Strategy (optional)

-> LatencyEvent (flagship+ realism)
Emitted by: “Simulator clock” / Execution simulator
Consumed by: Execution, maybe the event loop scheduler

Rule:
Strategy never emits orders. It emits signals. Portfolio translates signals → orders.

* Events are immutable payloads passed through the event_queue

"""

# Imports
from enum import Enum

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime # for timestamps
from typing import Any, Dict, Optional
from uuid import uuid4 # for unique IDs

"""

dataclass -> for clean immutable-ish event objects
uuid4() -> for unique IDs
datetime -> for timestamps
Optional -> because seq is often assigned when enqueuing, not at creation

"""


class EventType(str, Enum):
    MARKET_DATA = "MARKET_DATA"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"
    POSITION = "POSITION"
    PNL = "PNL"
    RISK = "RISK"
    CORPORATE_ACTION = "CORPORATE_ACTION"
    LATENCY = "LATENCY"

# Base Event
@dataclass(frozen=True, slots=True)
class Event:
    event_type: EventType
    ts_event: datetime
    # Automatically generate a unique ID for each event.
    # `default_factory` ensures a new UUID is created every time
    # an Event instance is constructed (not just once at import time).
    # `.hex` converts the UUID to a clean string without dashes.
    event_id: str = field(default_factory=lambda: uuid4().hex)
    seq: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# Classes
class SignalAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderIntent(str, Enum):
    CREATE = "CREATE"
    MODIFY = "MODIFY"
    CANCEL = "CANCEL"

class RiskSeverity(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    BREACH = "BREACH"

class RiskAction(str, Enum):
    NONE = "NONE"
    REDUCE = "REDUCE"
    HALT = "HALT"
    CANCEL_ORDERS = "CANCEL_ORDERS"

class CorporateActionType(str, Enum):
    SPLIT = "SPLIT"
    DIVIDEND = "DIVIDEND"
    MERGER = "MERGER"
    SPINOFF = "SPINOFF"

class LatencyStage(str, Enum):
    DATA = "DATA"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"
