
"""
    Simple FIFO event queue 

    - put(event): enqueue an event (assigns a monotonically increasing seq)
    - get(): dequeue next event (FIFO)
    - empty(): True if no events
    - len(queue): number of queued events

"""

# Imports
from __future__ import annotations

from collections import deque
from typing import Any, Deque, Optional
from dataclasses import replace

from events.events import Event


class EventQueue:
    def __init__(self) -> None:
        self._q = Deque[Event] = deque()
        self._next_seq = 0

    def put(self, event: Event) -> Event:
        """
        Enqueue an event and assign a sequence number.

        Because Events are frozen dataclasses, we can't do: event.seq = ...
        So we create a NEW event object with seq set using dataclasses.replace.
        """
        event_with_seq = replace(event, seq=self._next_seq)
        self._next_seq += 1
        self._q.append(event_with_seq)
        return event_with_seq
    
    def get(self) -> Event:
        # Dequeue the next event (FIFO). Raises IndexError if Queue is Empty 
        return self._q.popleft()

    def empty(self) -> bool:
        # Return True if the queue has no Events 
        return len(self._q) == 0
    
    def __len__(self) -> int:
        return len(self._q)

    def peek(self) -> Optional[Event]:
        # Return next event without removimg it, or None if Empty
        return self._q[0] if self._q else None