# Superflow Whitepaper

## Table of Contents

1. [Mathematical Models](#mathematical-models)
   - [Model 1: Theoretical Proof of Insider Advantage](Formula1.md)
   - [Model 2: Insider Advantage at Token Launch](Formula2.md)
   - [Model 3: Pre-Launch Advantage for Insiders](Formula3.md)
   - [Model 4: Advantage from Isolated Spot Markets and Synthetic Asset Solution](Formula4.md)
   - [Model 5: Mathematical Derivation of Insider Advantage and Market Equilibrium](Formula5.md)

2. [Glossary](#glossary)

## Mathematical Models

This whitepaper presents five mathematical models that analyze market inefficiencies in token launches and propose solutions:

1. **Model 1**: Theoretical proof analyzing insider trading advantages during token launches.
2. **Model 2**: Detailed examination of timing and information advantages in launch scenarios.
3. **Model 3**: Investigation of pre-launch preparation advantages (financial and psychological).
4. **Model 4**: Analysis of isolated spot markets and how synthetic assets provide solutions.
5. **Model 5**: Comprehensive mathematical derivation synthesizing insider advantage and market equilibrium restoration.

## Glossary

### Time Variables
- **t₀**: Token launch time (exact moment token becomes tradable)
- **t₋ₙ**: Pre-launch period before token launch
- **t₀ + δ**: Insider trading window (δ = 1 to 10 minutes)
- **t₀ + N**: General market awareness and public participation start time
- **tₘ**: Any future time point after launch

### Price Variables
- **P(t)**: Price function at time t
- **P(t₀)**: Initial launch price
- **P(t₀ + n)**: Price after n transactions (typically in isolated market context)
- **P_basis**: Cost basis price
- **P_synthetic**: Synthetic asset price
- **P_equilibrium**: Equilibrium price
- **P_spot**: Spot market price
- **F(t)**: Fair value function incorporating premium
- **V(t)**: Fair-value premium variable used in F(t)

### Quantity Variables
- **Q**: General quantity/volume
- **Qᵢ**: Quantity of transaction i
- **Q_short**: Short-selling quantity
- **Q_buy**: Buying quantity
- **Qₐ**: Quantity traded by insiders
- **Qₒ**: Quantity traded by outsiders

### Impact & Model Variables
- **N(Q)**: Price impact function for quantity Q
- **N(Qᵢ)**: Price impact of transaction i
- **I(t)**: Information set available at time t
- **α**: Measures the price impact of information I(t)
- **εₜ**: Random noise component in price model
- **β**: Normalization factor for arbitrage premium in F(t)
- **C_market**: Cost of market creation (often assumed ≈ 0)

### Advantage/Disadvantage & Behavioral Variables
- **Aₐ**: Insider advantage function
- **Dₒ**: Outsider disadvantage function
- **Rₐ**: Insider rationality factor
- **Rₒ**: Outsider rationality factor
- **ρₐ**: Insider perceived risk factor
- **ρₒ**: Outsider perceived risk factor
- **CFₐ**: Insider confidence factor (derived from ρₐ)
- **CFₒ**: Outsider confidence factor (derived from ρₒ)
- **Cₐ**: Insider capital
- **Cₒ**: Outsider capital
- **Gₐ**: Insider arbitrage gain/profit
- **Gₒ**: Outsider arbitrage gain/profit
- **U_F**: Founder Utility (in game theory context)

### Mathematical Operators
- **∑**: Summation operator
- **→**: Approaches/limits to
- **≈**: Approximately equal to
- **≫**: Much greater than
- **≪**: Much less than
- **E[ ]**: Expected value operator
- **lim**: Limit operator
- **·**: Multiplication operator
- **~**: Distributed as
- **≻**: Strictly preferred to (in game theory)

### Market Concepts
- **Insider**: Market participant with privileged information or access
- **Outsider**: Market participant without privileged information or access
- **FOMO**: Fear of Missing Out (psychological factor affecting Rₒ)
- **Synthetic Asset**: Derivative representation of an asset, enabling short-selling
- **Spot Market**: Market for immediate delivery of assets
- **Equilibrium**: Market state aiming for fairness and balanced participation
- **Liquidity**: Market's ability to absorb trading volume (includes buy and sell sides)
- **Arbitrage**: Risk-free (or low-risk) profit from price differences
- **Fair Value Premium**: Additional value component in synthetic assets (related to V(t))
- **Omni-Solver**: Proposed financial instrument/tool to create synthetics and restore equilibrium
