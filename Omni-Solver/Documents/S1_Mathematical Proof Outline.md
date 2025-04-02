# Section 1 - Mathematical Proof Outline

## Step 1: Define Market Participants and Information Sets

### Participants:
- **Insiders (I)**: Possess advanced information at time t₀
- **Outsiders (O)**: Receive information at time t₀ + N

### Information Set:
- Let I(t) represent information available at time t
- Insiders have I(t₀), while outsiders only have I(t₀ + N)

## Step 2: Information Asymmetry Opportunity (Economic Model)

Consider a simplified asset price model, where the price at any time t is:

P(t) = P(t₀) + α · I(t) + εₜ

Where:
- P(t₀) is the initial price
- α measures the price impact of information
- εₜ is a random noise component, εₜ ~ N(0, σ²)

### Economical Gain for Insiders (Gₐ):
Insiders trade at t₀:

Gₐ = E[P(t) - P(t₀) | I(t₀)] = α · I(t₀)

### Economical Gain for Outsiders (Gₒ):
Outsiders trade at t₀ + N:

Gₒ = E[P(t') - P(t) | I(t)], t' > t > t₀

Since by definition, I(t₀) is superior (earlier), we have:

Gₐ > Gₒ

Thus, insiders always have strictly greater expected gains due to information asymmetry.

## Step 3: Game-Theoretical Nash Equilibrium

Model the game with two strategies:
- **Ethical (E)**: Transparent & fair
- **Unethical (U)**: Exploitative, maximizing personal gain

### Payoff matrices (π) for Founders (F):

| Founder | Insider Behavior | Outsider Behavior |
|---------|-----------------|-------------------|
| Ethical | Low payoff | Low payoff |
| Unethical | High payoff (early exploitation) | Medium payoff (later market entry) |

### Rationality assumption (utility maximization):

U_F(U) > U_F(E)

Due to early access and information asymmetry.

Thus, Nash Equilibrium favors unethical behavior:

Ethical strategy is strictly dominated by unethical strategy for insiders, given isolated market structure:

U_F(U) ≻ U_F(E)

## Step 4: Structural Incentive for Unethical Behavior

Isolated spot markets allow infinite, zero-cost market creation (C_market = 0):

Let expected profit from market creation be Gₐ:

### Insiders:
Gₐ = α · I(t₀) - C_market > 0

### Outsiders:
Gₒ = α · I(t₀ + N) - C_market (t > t₀)

Given C_market = 0 and I(t₀) > I(t₀ + N), insiders consistently generate profit with no cost or risk:

Gₐ ≫ Gₒ

## Step 5: Impact of Financial Instrument ("Omni-Solver")

Introduce an Omni-Solver to price perpetual derivatives fairly:

### Fair value price F(t):

F(t) = P(t) + β · V(t)

where:
- V(t) is the fair-value premium derived from continuous open market participation
- β normalizes information asymmetry premium

Omni-Solver eliminates isolated information asymmetry opportunities (Gₐ ≈ Gₒ):

E[F(t₀) | I(t₀)] ≈ E[F(t) | I(t)], t ≥ t₀

This theoretically neutralizes insiders' asymmetric advantages, enforcing market fairness.

## Conclusion (Mathematical Justification)

mathematically demonstrate that isolated spot markets structurally incentivize unethical insider behavior by formally showing:

1. **Information Asymmetry**: Earlier market participation yields greater economical gains (Gₐ > Gₒ)
2. **Game-Theoretic Dominance**: Unethical behavior is rationally dominant due to immediate financial incentives
3. **Zero-Entry Cost Markets**: Incentivize repeated unethical behavior through minimal barriers
4. **Fairness via Financial Innovation**: The introduction of a tool like Omni-Solver theoretically equalizes expected returns and removes asymmetric insider advantages.

