# Section 2 - Mathematical Model: Insider Advantage at Token Launch

## Step 1: Setup the Timeline and Market Participants

### Time Definitions

- **t₀**: Token launch (exact moment token becomes tradable)
- **t₀ + δ**: Insider trading window (δ = 1 to 10 minutes)
  - Only insiders or informed actors know exactly when, where, and which token will launch
- **t₀ + N**: General market awareness and public participation starts (N ≫ δ)

### Market Participants

1. **Insiders (I)**
   - Know token identity
   - Know launch exact time (t₀)
   - Know initial demand (D)

2. **Outsiders (O)**
   - Uncertain token identity/time
   - Participate at t₀ + N

## Step 2: Define Insider Advantage Formally

### Advantage 1: Time (First-Mover Advantage)

Insiders can buy exactly at t₀ + δ, while outsiders can only enter at t₀ + N.

Assume:
- Initial price at launch: P(t₀)
- Price rises to P(t₀ + N) due to insider demand

**Profit for insiders (Gₐ):**

Gₐ = Qₐ · [P(t₀ + N) - P(t₀ + δ)]

where Qₐ is insider's quantity bought at lower prices.

### Advantage 2: Certainty of Information (Confidence)

Insiders accurately predict:
- Token legitimacy (which token is real)
- Amount of capital other insiders will deploy
- Expected initial price rise due to insider demand

**Expected Utility Functions:**

Insider expected utility:
E[Uₐ] = Qₐ · [P(t₀ + N) - P(t₀ + δ)] · (1 - ρₐ)

where ρₐ is insiders' perceived risk (very low).

Outsider expected utility:
E[Uₒ] = Qₒ · [P(t₀ + N') - P(t₀ + N)] · (1 - ρₒ)

where:
- Qₒ ≪ Qₐ: Outsiders typically buy smaller amounts initially (due to uncertainty)
- ρₒ ≫ ρₐ: Outsiders perceive greater risk due to lack of insider certainty
- N' > N: Outsiders wait additional confirmation periods

## Step 3: Empirical Example: Libra Launch Scenario

### Hypothetical Example: Libra Token

1. Launch price at t₀ (exact insider launch): $0.01
2. Insiders enter aggressively within 1-10 minutes
3. Price at t₀ + 10 mins rises to $0.05 due to insider demand
4. Public enters at t₀ + 1 hour, price rises to $0.10

### Profit Calculations

**Insiders' Gain:**
- Qₐ = 10,000,000 tokens at average price $0.02
- Cost: 10,000,000 × $0.02 = $200,000
- Value at public entry: 10,000,000 × $0.10 = $1,000,000
- Profit Gₐ = $1,000,000 - $200,000 = $800,000

**Outsiders' Gain:**
- Qₒ = 1,000,000 tokens at price $0.10
- Cost: 1,000,000 × $0.10 = $100,000
- Value shortly after: 1,000,000 × $0.08 = $80,000
- Loss Gₒ = $80,000 - $100,000 = -$20,000

## Step 4: Statistical Confidence Advantage

### Confidence Factors

- Insiders: CFₐ = (1 - ρₐ) ≈ 0.99 (high confidence)
- Outsiders: CFₒ = (1 - ρₒ) ≈ 0.5 (low confidence)

### Position Sizing

Insiders size aggressively:
Qₐ = CFₐ · Cₐ (very large quantity)

Outsiders size conservatively:
Qₒ = CFₒ · Cₒ (much smaller)

Therefore: Qₐ ≫ Qₒ

## Step 5: Generalization and Formalization of Advantage

### Profit Functions

**Insider profit function:**
Gₐ(Qₐ, t₀ + δ) = Qₐ · [E(P(t₀ + N)) - P(t₀ + δ)], Qₐ ≫ 0

**Outsider profit function:**
Gₒ(Qₒ, t₀ + N) = Qₒ · [E(P(t₀ + N')) - P(t₀ + N)], Qₒ ≪ Qₐ

### Profitability Inequality
Gₐ(Qₐ, t₀ + δ) ≫ Gₒ(Qₒ, t₀ + N)

## Conclusion

This mathematical approach demonstrates that isolated crypto token launches significantly favor insiders due to two fundamental structural advantages:

1. **Timing advantage**: Ability to trade immediately at t₀
2. **Confidence advantage**: Certainty of legitimacy, timing, and expected demand

These advantages systematically enable insiders to profit at the expense of outsiders, who typically bear the cost of entering later at higher prices or after price peaks.

This formal proof highlights the need for innovative financial instruments, like your proposed Omni-Solver, that neutralize these informational asymmetries by providing fair & accessible derivatives for broader market participation.