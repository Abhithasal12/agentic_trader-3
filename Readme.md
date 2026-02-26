# SMC Multi-Timeframe Trading Bot

## Overview

This is a Smart Money Concepts (SMC) based multi-timeframe trading bot built on MetaTrader5.

The system uses structured price action logic across H4, M15, and M5 timeframes to execute high-quality trades. It avoids indicators and relies purely on market structure, liquidity behavior, and imbalance.

The bot is modular and divided into:

- Execution Engine (main.py)
- SMC Logic (smc_logic.py)
- Risk Management (risk.py)
- Trade Management (trade_manager.py)
- Configuration (config.py)

---

## Strategy Architecture

### Timeframe Structure

H4 → Higher timeframe bias  
M15 → Setup validation  
M5 → Entry confirmation  

---

## Trading Logic Flow

The bot executes trades only when ALL layers align.

### 1. H4 Bias

- Detect swing highs and swing lows
- Detect Break of Structure (BOS)
- Define directional bias:
  - Bullish BOS → bullish bias
  - Bearish BOS → bearish bias

If no clear BOS, no trade.

---

### 2. M15 Setup

The following must occur:

- Liquidity sweep
  - Sweep of lows for buy setups
  - Sweep of highs for sell setups

- Break of Structure in direction of H4 bias

- Valid Order Block detection
  - Bullish: last bearish candle before impulse
  - Bearish: last bullish candle before impulse

- Price must retrace into the Order Block zone

- Premium / Discount filter
  - Buy only in discount (below 50% of range)
  - Sell only in premium (above 50% of range)

If any condition fails → no trade.

---

### 3. M5 Entry

- Break of Structure in trade direction
- Fair Value Gap (FVG) detection
- Price must retrace inside FVG zone

Only then is a signal returned to the execution engine.

---

## Risk Management

Risk logic is handled separately:

- Fixed stop loss in points
- Fixed take profit in points
- Lot size calculated based on risk model
- Margin check before execution
- Global trade limits
- Per-symbol trade limits

The SMC engine only generates signals.  
Execution and risk are isolated for safety and modularity.

---

## Trade Execution Flow

1. Loop through enabled symbols
2. Check trade limits
3. Ensure no open position on symbol
4. Run SMC multi-timeframe analysis
5. If signal returned:
   - Calculate lot size
   - Check margin
   - Execute order
   - Record trade

---

## Key Features

- Multi-timeframe structure alignment
- Liquidity-based entries
- Order Block validation
- Fair Value Gap entry refinement
- Premium / Discount filtering
- Modular architecture
- Clean separation of concerns

---

## Files Structure

main.py  
Core engine and execution loop  

smc_logic.py  
All structural detection logic  

risk.py  
Lot sizing and margin checks  

trade_manager.py  
Trade tracking and limits  

config.py  
Symbol and strategy configuration  

---

## Current Strategy Layering

H4 → External structure bias  
M15 → Setup and positioning  
M5 → Execution precision  

The system prioritizes quality over frequency.

---

## Important Notes

- This bot trades less frequently by design.
- It waits for complete structural alignment.
- Removing filters increases trade frequency but reduces quality.
- The strategy is sensitive to spread and execution speed.

---

## Future Upgrades (Planned)

- Internal vs External structure separation
- Liquidity pool targeting for TP
- Kill zone session filter (London / NY)
- Limit order entry at FVG midpoint
- Adaptive stop placement based on structure
- Performance tracking dashboard
- Reinforcement learning optimization layer

---

## Disclaimer

This system is for educational and research purposes.  
Trading financial markets carries risk.  
Always test in demo before live deployment.