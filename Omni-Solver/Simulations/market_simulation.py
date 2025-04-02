import numpy as np
import matplotlib.pyplot as plt
import random

class Market:
    """Represents the isolated spot market or a market with synthetics."""
    def __init__(self, initial_price=0.01, market_type='isolated'):
        self.current_price = initial_price
        self.time = 0
        self.transaction_log = [] # List of (time, agent_type, action, quantity, price, profit)
        self.market_type = market_type # 'isolated' or 'synthetic'
        print(f"Market initialized. Type: {self.market_type}, Initial Price: {self.current_price:.4f}")

    def price_impact(self, quantity):
        """Simple linear price impact function N(Q). Needs refinement."""
        # TODO: Implement a more realistic impact function based on formulas
        impact = quantity * 0.000001 # Placeholder
        # print(f"Quantity: {quantity}, Impact: {impact:.6f}")
        return impact

    def update_price(self, quantity, action):
        """Updates the market price based on a transaction."""
        if self.market_type == 'isolated' and action == 'sell':
            # In a purely isolated market, selling doesn't directly impact price
            # Price only moves up based on buys (Formula 4)
            pass
        elif self.market_type == 'synthetic' or action == 'buy':
            impact = self.price_impact(quantity)
            if action == 'buy':
                self.current_price += impact
            elif action == 'sell': # Only possible in synthetic market
                self.current_price -= impact
                if self.current_price < 0: self.current_price = 0 # Price can't be negative

    def get_price(self):
        return self.current_price

    def log_transaction(self, agent_type, action, quantity, price, profit):
        self.transaction_log.append({
            'time': self.time,
            'agent_type': agent_type,
            'action': action,
            'quantity': quantity,
            'price': price,
            'profit': profit
        })
        # print(f"Time: {self.time}, Agent: {agent_type}, Action: {action}, Qty: {quantity:.2f}, Price: {price:.4f}, Profit: {profit:.2f}")

    def advance_time(self):
        self.time += 1

class Agent:
    """Base class for market participants."""
    def __init__(self, agent_id, initial_capital, rationality_factor):
        self.agent_id = agent_id
        self.capital = initial_capital
        self.rationality = rationality_factor # R (0 to 1)
        self.tokens = 0
        self.cost_basis = 0
        self.realized_profit = 0
        self.entry_time = 0 # Time step when agent becomes active
        print(f"Agent {self.agent_id} created. Capital: {self.capital:.2f}, Rationality: {self.rationality:.2f}")

    def get_unrealized_profit(self, current_price):
        return (current_price * self.tokens) - (self.cost_basis * self.tokens)

    def get_total_value(self, current_price):
        return self.capital + (current_price * self.tokens)

    def decide_action(self, market_state):
        """Basic decision logic. To be overridden by subclasses."""
        # Simple random action based on rationality (placeholder)
        if random.random() < self.rationality:
            if random.random() < 0.5: # 50% chance to buy if rational
                return 'buy', self.capital * 0.1 * random.random() # Buy random % of capital
            else: # 50% chance to sell if rational
                return 'sell', self.tokens * 0.1 * random.random() # Sell random % of tokens
        else:
            return 'hold', 0

    def execute_trade(self, market, action, quantity):
        """Executes a trade on the market."""
        current_price = market.get_price()
        trade_profit = 0

        if action == 'buy':
            cost = quantity * current_price
            if cost <= self.capital and cost > 0:
                self.capital -= cost
                new_tokens = quantity
                # Update average cost basis
                self.cost_basis = ((self.cost_basis * self.tokens) + cost) / (self.tokens + new_tokens)
                self.tokens += new_tokens
                market.update_price(quantity, 'buy')
                market.log_transaction(type(self).__name__, 'buy', quantity, current_price, 0) # Profit realized on sell
                # print(f"Agent {self.agent_id} BUY: {quantity:.2f} @ {current_price:.4f}, New Tokens: {self.tokens:.2f}, New Capital: {self.capital:.2f}")
            else:
                action = 'hold' # Not enough capital or invalid quantity
                quantity = 0

        elif action == 'sell':
            if quantity <= self.tokens and quantity > 0:
                revenue = quantity * current_price
                profit_per_token = current_price - self.cost_basis
                trade_profit = profit_per_token * quantity
                self.realized_profit += trade_profit
                self.capital += revenue
                self.tokens -= quantity
                # Cost basis remains the same for remaining tokens
                if self.tokens == 0: self.cost_basis = 0
                market.update_price(quantity, 'sell')
                market.log_transaction(type(self).__name__, 'sell', quantity, current_price, trade_profit)
                # print(f"Agent {self.agent_id} SELL: {quantity:.2f} @ {current_price:.4f}, Profit: {trade_profit:.2f}, New Tokens: {self.tokens:.2f}, New Capital: {self.capital:.2f}")
            else:
                action = 'hold' # Not enough tokens or invalid quantity
                quantity = 0

        return action, quantity, current_price, trade_profit

class Insider(Agent):
    """Insider agent with advantages."""
    def __init__(self, agent_id, initial_capital=100000, rationality_factor=0.95, entry_time_delta=1):
        super().__init__(agent_id, initial_capital, rationality_factor)
        self.entry_time = entry_time_delta # Enters market at time t0 + delta
        print(f"Insider {self.agent_id} created. Entry Time: {self.entry_time}")

    def decide_action(self, market_state):
        """Insider decision logic (Formula 2 & 3)."""
        # High confidence (ρ_a low), high rationality (R_a high)
        # Knows launch time, likely initial demand -> Buys early aggressively
        current_time = market_state['time']
        current_price = market_state['price']

        # Aggressive buying in the initial window (t0 + delta)
        if current_time == self.entry_time:
            # Use a significant portion of capital, reflecting confidence & preparation
            buy_amount = self.capital * (0.8 + 0.1 * random.random()) # e.g., 80-90% of capital
            quantity_to_buy = buy_amount / current_price if current_price > 0 else float('inf')
            print(f"Insider {self.agent_id} initial aggressive buy decision: {quantity_to_buy:.2f} tokens")
            return 'buy', quantity_to_buy

        # TODO: Add logic for later selling based on perceived peak or target profit
        # Placeholder: maybe start selling small amounts after public enters?
        if current_time > market_state.get('public_entry_time', float('inf')) and self.tokens > 0:
             if random.random() < 0.2: # Small chance to sell some tokens
                 sell_quantity = self.tokens * (0.05 + 0.05 * random.random()) # Sell 5-10%
                 return 'sell', sell_quantity

        return 'hold', 0

class Outsider(Agent):
    """Outsider agent with disadvantages."""
    def __init__(self, agent_id, initial_capital=10000, rationality_factor=0.5, entry_time_n=20, fomo_factor=0.3):
        super().__init__(agent_id, initial_capital, rationality_factor)
        self.entry_time = entry_time_n # Enters market at time t0 + N
        self.fomo_factor = fomo_factor # Likelihood of irrational FOMO buying
        print(f"Outsider {self.agent_id} created. Entry Time: {self.entry_time}, FOMO Factor: {self.fomo_factor:.2f}")

    def decide_action(self, market_state):
        """Outsider decision logic (Formula 2 & 3)."""
        # Lower confidence (ρ_o high), lower rationality (R_o low)
        # Enters later, potentially influenced by FOMO
        current_time = market_state['time']
        current_price = market_state['price']

        if current_time < self.entry_time:
            return 'hold', 0 # Not active yet

        # Check for FOMO buy upon entry
        if current_time == self.entry_time and random.random() < self.fomo_factor:
            # Irrational FOMO buy
            buy_amount = self.capital * (0.3 + 0.4 * random.random()) # Buy 30-70% of capital impulsively
            quantity_to_buy = buy_amount / current_price if current_price > 0 else 0
            print(f"Outsider {self.agent_id} FOMO buy decision: {quantity_to_buy:.2f} tokens")
            return 'buy', quantity_to_buy

        # More standard, less confident trading otherwise
        # Placeholder: Use base Agent logic but with lower rationality impacting frequency/size
        if random.random() < self.rationality:
             # Less aggressive than insider
            if random.random() < 0.4: # Lower chance to buy
                buy_amount = self.capital * 0.05 * random.random() # Smaller % buy
                return 'buy', buy_amount / current_price if current_price > 0 else 0
            elif self.tokens > 0 and random.random() < 0.6: # Higher chance to sell if holding?
                sell_quantity = self.tokens * 0.05 * random.random() # Smaller % sell
                return 'sell', sell_quantity

        return 'hold', 0

# --- Simulation Setup ---
def run_simulation(market_type='isolated', num_insiders=5, num_outsiders=50, sim_duration=100, insider_entry_delta=1, public_entry_n=20):
    """Runs the market simulation."""
    market = Market(market_type=market_type)

    insiders = [Insider(f'I-{i}', entry_time_delta=insider_entry_delta) for i in range(num_insiders)]
    outsiders = [Outsider(f'O-{i}', entry_time_n=public_entry_n) for i in range(num_outsiders)]
    all_agents = insiders + outsiders

    price_history = []
    time_steps = []

    print("\n--- Starting Simulation ---")
    for t in range(sim_duration):
        market.advance_time()
        current_time = market.time
        current_price = market.get_price()
        price_history.append(current_price)
        time_steps.append(current_time)

        # print(f"\nTime Step: {current_time}, Price: {current_price:.4f}")

        market_state = {
            'time': current_time,
            'price': current_price,
            'public_entry_time': public_entry_n
        }

        # Shuffle agents to avoid order bias in each step
        random.shuffle(all_agents)

        active_agents_count = 0
        for agent in all_agents:
            if current_time >= agent.entry_time:
                active_agents_count += 1
                action, quantity = agent.decide_action(market_state)
                if action != 'hold' and quantity > 0:
                    agent.execute_trade(market, action, quantity)
                    # print(f"  Agent {agent.agent_id} action: {action}, qty: {quantity:.2f}")
                # else:
                    # print(f"  Agent {agent.agent_id} action: hold")

        # if current_time % 10 == 0:
        print(f"Time: {current_time:3d}, Price: {market.get_price():.6f}, Active Agents: {active_agents_count}")

    print("--- Simulation Ended ---")

    # --- Results Analysis ---
    print("\n--- Final Agent States ---")
    total_insider_profit = 0
    total_outsider_profit = 0
    final_price = market.get_price()

    for insider in insiders:
        profit = insider.realized_profit + insider.get_unrealized_profit(final_price)
        total_insider_profit += profit
        print(f"Insider {insider.agent_id}: Realized Profit={insider.realized_profit:.2f}, Unrealized Profit={insider.get_unrealized_profit(final_price):.2f}, Total Profit={profit:.2f}, Final Value={insider.get_total_value(final_price):.2f}")

    for outsider in outsiders:
        profit = outsider.realized_profit + outsider.get_unrealized_profit(final_price)
        total_outsider_profit += profit
        print(f"Outsider {outsider.agent_id}: Realized Profit={outsider.realized_profit:.2f}, Unrealized Profit={outsider.get_unrealized_profit(final_price):.2f}, Total Profit={profit:.2f}, Final Value={outsider.get_total_value(final_price):.2f}")

    avg_insider_profit = total_insider_profit / num_insiders if num_insiders > 0 else 0
    avg_outsider_profit = total_outsider_profit / num_outsiders if num_outsiders > 0 else 0

    print(f"\nAverage Insider Profit: {avg_insider_profit:.2f}")
    print(f"Average Outsider Profit: {avg_outsider_profit:.2f}")
    print(f"Final Market Price: {final_price:.6f}")

    # --- Plotting ---
    plt.figure(figsize=(12, 6))
    plt.plot(time_steps, price_history, label='Market Price')
    plt.axvline(x=insider_entry_delta, color='r', linestyle='--', label=f'Insider Entry (t={insider_entry_delta})')
    plt.axvline(x=public_entry_n, color='g', linestyle='--', label=f'Outsider Entry (t={public_entry_n})')
    plt.title(f'Market Simulation ({market_type.capitalize()} Market)')
    plt.xlabel('Time Steps')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'simulation/market_simulation_{market_type}.png')
    print(f"\nPlot saved to simulation/market_simulation_{market_type}.png")
    # plt.show() # Uncomment to display plot immediately

    return market.transaction_log

# --- Main Execution ---
if __name__ == "__main__":
    print("Running Isolated Market Simulation...")
    isolated_log = run_simulation(market_type='isolated')

    # print("\n\nRunning Synthetic Market Simulation...")
    # synthetic_log = run_simulation(market_type='synthetic')

    # TODO: Add comparison logic between isolated and synthetic runs 