# Paper Trading Checklist & Logging Template

Use this while running the bot in paper mode. Copy sections into a private log or spreadsheet.

---

## Daily / Session Log

**Date**:  
**Session start**:  
**Session end**:  
**Bot version / commit**:  
**Settings**:
- Mode: conservative / balanced / aggressive
- Risk: low / medium / high
- Threshold: ____
- Interval: ____ minutes
- Symbols: 

### Signals Generated
| Time | Pair | Direction | Confidence | Strength | Notes |
|------|------|-----------|------------|----------|-------|
|      |      |           |            |          |       |

### Trades Executed (Paper)
| Time | Pair | Side | Size | Entry | Exit | P&L | R-multiple | Notes |
|------|------|------|------|-------|------|-----|------------|-------|
|      |      |      |      |       |      |     |            |       |

### End-of-Session Summary
- Total signals: 
- Trades taken: 
- Win rate: 
- Net paper P&L: 
- Max drawdown this session: 
- Observations / regime notes: 
- Feedback given to bot (`/feedback`): 

---

## Weekly Review

**Week ending**:  

- Total closed trades: 
- Overall win rate: 
- Expectancy (avg R): 
- Best / worst pairs: 
- Confidence bucket performance (e.g. 85%+ vs 75-84%): 
- Market regimes observed (trend / range / high vol): 
- Changes to make next week: 

---

## Level 3 Exit Criteria (Personal Verification)

Before considering any live capital:

- [ ] At least 50–100+ closed paper trades
- [ ] Positive expectancy after realistic costs/slippage
- [ ] Performance reviewed across different market conditions
- [ ] Clear personal understanding of failure modes
- [ ] Credentials rotated and never re-committed
- [ ] Status server + monitoring reliable for the period

**Only you can mark these complete.**
