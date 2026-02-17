# Event-Driven Backtesting Engine

A reproducible, event-driven backtesting engine that simulates realistic trading:

**Market data → signals → orders → fills → portfolio accounting**  
with **costs/slippage**, **risk controls**, **reporting artifacts**, and **tests**.

This repo is intentionally built like a *mini trading platform simulator*: everything is an **event**, and components are **swappable** (data feed, strategy, execution model, portfolio/accounting).

---

## Why event-driven?

Event-driven architecture (EDA) means the system advances by **facts that happen** (“events”), not by direct function calls between big modules.

In this engine:
- a new bar arrives → `MarketEvent`
- the strategy reacts → `SignalEvent`
- the portfolio translates signals to orders → `OrderEvent`
- execution simulates fills → `FillEvent`
- the portfolio updates positions/cash/PnL → repeat

This design makes it straightforward to:
- add realism (costs, slippage, partial fills, latency stubs)
- run deterministic replays (reproducible results)
- swap modules without rewriting the whole codebase

---

## Features

### Core engine
- **Event model**: `MarketEvent`, `SignalEvent`, `OrderEvent`, `FillEvent`
- **Modular architecture**: `data/` `strategy/` `execution/` `portfolio/` `metrics/`
- **Simulation loop** with an event queue (in-memory first)

### Realism hooks (config-driven)
- Commission + slippage models
- Participation caps and optional partial fills *(WIP / incremental)*
- Shorting support (signals can be LONG/SHORT)

### Research hygiene
- Deterministic runs (seed + config snapshot + git commit)
- Date range control and clean experiment configs
- Baselines + multiple strategies on the same data

### Testing
- Unit tests for accounting correctness and execution behavior
- Regression-style “known scenario” tests to catch silent bugs

---

## Architecture

```mermaid
flowchart LR
  DATA[DataHandler] -->|MarketEvent| Q[(EventQueue)]
  Q --> STRAT[Strategy]
  STRAT -->|SignalEvent| Q
  Q --> PORT[Portfolio]
  PORT -->|OrderEvent| Q
  Q --> EXEC[ExecutionHandler]
  EXEC -->|FillEvent| Q
  Q --> PORT
  PORT --> METRICS[Metrics / Reporting]

  ----

  python -m venv .venv

# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

pip install -e ".[dev]"
pre-commit install
pytest