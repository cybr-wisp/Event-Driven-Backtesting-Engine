
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
from __future__ import annotations

from enum import Enum
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
    event_type: EventType = field(init=False)
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


# Data Clases
@dataclass(frozen=True, slots=True)
class MarketDataEvent(Event):
    """
        MarketDataEvent inherits from Event, plus new ones 
        frozen=True → you can’t modify it after creation
        slots=True → it uses less memory and you can’t add random new fields

        "BAR" (OHLCV)

        "QUOTE" (bid/ask)

        "TRADE" (last price/size)
    
    """
    event_type: EventType = field(default=EventType.MARKET_DATA, init=False)
    symbol: str = ""
    data_type: str = "BAR" #Later: Enum (BAR/QUOTE/TRADE)
    payload: Dict[str, Any] = field(default_factory=dict) 


@dataclass(frozen=True, slots=True)
class SignalEvent(Event):
    """
        Strategy emits this when it wants to BUY/SELL/HOLD a symbol.
        Portfolio consumes it and turns it into orders.
    """
    event_type: EventType = field(default=EventType.SIGNAL, init=False)
    symbol: str = ""
    action: SignalAction = SignalAction.HOLD
    strength: float = 1.0
    strategy_id: str = "default"
    signal_id: str = field(default_factory=lambda: uuid4().hex)

@dataclass(frozen=True, slots=True)
class OrderEvent(Event):
    """
    Portfolio emits this to request execution (create/modify/cancel).
    ExecutionHandler consumes it.
    """
    event_type: EventType = field(default=EventType.ORDER, init=False)
    symbol: str = ""
    side: OrderSide = OrderSide.BUY
    qty: float = 0.0
    order_type: OrderType = OrderType.MARKET
    limit_price: Optional[float] = None
    intent: OrderIntent = OrderIntent.CREATE
    order_id: str = field(default_factory=lambda: uuid4().hex)
    parent_signal_id: Optional[str] = None

@dataclass(frozen=True, slots=True)
class FillEvent(Event):
    """
    ExecutionHandler emits this when an order (fully or partially) fills.
    Portfolio + Accounting consume it.
    """
    event_type: EventType = field(default=EventType.FILL, init=False)
    order_id: str = ""
    symbol: str = ""
    side: OrderSide = OrderSide.BUY
    qty_filled: float = 0.0
    fill_price: float = 0.0
    commission: float = 0.0
    slippage: float = 0.0
    fill_id: str = field(default_factory=lambda: uuid4().hex)
    remaining_qty: Optional[float] = None

@dataclass(frozen=True, slots=True)
class PositionEvent(Event):
    """
    Accounting/Portfolio emits this after fills or mark-to-market updates.
    Useful for reporting + debugging.
    """
    event_type: EventType = field(default=EventType.POSITION, init=False)
    portfolio_id: str = "default"
    symbol: str = ""
    position_qty: float = 0.0
    avg_price: float = 0.0

@dataclass(frozen=True, slots=True)
class PnLEvent(Event):
    """
    Accounting emits this to report current cash/equity/pnl.
    """
    event_type: EventType = field(default=EventType.PNL, init=False)
    portfolio_id: str = "default"
    cash: float = 0.0
    equity: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0

@dataclass(frozen=True, slots=True)
class RiskEvent(Event):
    """
    RiskManager emits this when a rule triggers (warn/breach).
    Portfolio/Execution can respond (reduce exposure/cancel orders).
    """
    event_type: EventType = field(default=EventType.RISK, init=False)
    portfolio_id: str = "default"
    severity: RiskSeverity = RiskSeverity.INFO
    rule_id: str = ""
    action_required: RiskAction = RiskAction.NONE
    symbol: Optional[str] = None
    target_qty: Optional[float] = None
    reason: str = ""

@dataclass(frozen=True, slots=True)
class CorporateActionEvent(Event):
    """
    For splits/dividends/etc. Portfolio/Accounting consumes to adjust holdings.
    """
    event_type: EventType = field(default=EventType.CORPORATE_ACTION, init=False)
    symbol: str = ""
    action_type: CorporateActionType = CorporateActionType.SPLIT
    ts_effective: datetime = field(default_factory=datetime.utcnow)
    ratio: Optional[float] = None
    cash_amount: Optional[float] = None
    source: str = "data"

@dataclass(frozen=True, slots=True)
class LatencyEvent(Event):
    """
    Used to simulate delays. Scheduler/Engine consumes it and releases a delayed event.
    """
    event_type: EventType = field(default=EventType.LATENCY, init=False)
    stage: LatencyStage = LatencyStage.ORDER
    ts_ready: datetime = field(default_factory=datetime.utcnow)
    latency_ms: int = 0
    delayed_event_id: str = ""