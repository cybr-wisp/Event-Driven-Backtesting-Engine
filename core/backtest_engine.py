"""
The Backtest Engine runs two nested loops conceptually:
Outer loop: keep stepping through market time (bars) until data is done.
Inner loop: after you inject a MarketDataEvent, drain the queue fully
-> (so the consequences of that bar complete: signals → orders → fills → accounting)

"""

import queue

class BacktestEngine:

    # Create the  
    self.event_queue = queue.Queue()


    // create queue 
from events.MarketDataEvent.emqueu.queu()
while queue is not empty {
    ququ.pop()

}



