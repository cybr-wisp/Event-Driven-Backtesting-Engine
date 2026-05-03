# MarketEvent → Strategy → SignalEvent → Portfolio → OrderEvent → Broker → FillEvent → Portfolio

"""
This module defines all event types used in the backtester.

Event types represent the different stages of the trading pipeline:
market data arrives, signals are generated, orders are created,
and fills are processed.
"""

from enum import Enum


# Market_Data = new price/candle/tick arrived
# Signal = strategy wants to buy/sell 
# Order = portfolio/execution system creates an order
# Fill = order was executed 


class EventType(Enum):

    MARKET_DATA = "MARKET_DATA"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"


"""
# To Add Later 
CANCEL_ORDER
ORDER_CANCELLED
ORDER_REJECTED
RISK_CHECK
HEARTBEAT
NEWS
CORPORATE_ACTION


"""