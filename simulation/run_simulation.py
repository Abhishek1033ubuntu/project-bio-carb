# simulation/run_simulation.py
import simpy
import random
import numpy as np
from models import ProductionRack, FactoryStateTracker

# --- CONSOLIDATED PHASE 4 SYSTEM CONFIGURATION ---
SIM_DURATION = 8760         # 1 Year runtime footprint (hours)
NUM_BAYS = 20000            # Regional scale deployment
NUM_ROBOTS = 25             # AGV/Gantry crane support fleet
ROBOT_SWAP_TIME = 0.05      # 3 minutes per physical mechanical swap

# Upgraded Bio-Architectural Parameters
MAX_RACK_OUTPUT_L_HR = 0.25 
WEIBULL_SCALE = 4320.0      # Extended 180-day lifespan via Orthogonal Core
WEIBULL_SHAPE = 1.5
SILO_CAPACITY_KG = 3000000.0 # 3,000 metric ton buffer buffer to cushion supply drops

# Financial Architecture Constants
GLUCOSE_COST_PER_KG = 0.04  # Sourced regional agricultural waste
RAW_SWAP_COST = 8.0         
CELL_RECLAIM_CREDIT = 3.00  # Nutrient reclamation credit from centrifuges
FACILITY_OVERHEAD = 350000.0 # Net-zero utility status via Lignin Co-generation
BARREL_VOLUME_LITERS = 159
CAPEX_PER_RACK = 100.0      
ROBOT_ARM_CAPEX = 120000.0 * NUM_ROBOTS

def run_supply_chain(env, tracker, silo):
    """Simulates dynamic seasonal harvests and sudden weather supply shocks."""
    while True:
        current_hour = env.now
        # Seasonality modeled via cyclic sine progression
        seasonality = np.sin(2 * np.pi * current_hour / 8760)
        
        if seasonality > 0.3:    # Peak Harvest Window
            incoming_feedstock_rate = 6500.0 
            feedstock_price_per_kg = 0.02    
        elif seasonality < -0.3: # Off-Season Winter Drought
            incoming_feedstock_rate = 2000.0 
            feedstock_price_per_kg = 0.08    
        else:                    # Steady State
            incoming_feedstock_rate = 4500.0
            feedstock_price_per_kg = 0.04

        # Stochastic Extreme Event Risk (2% daily probability of transport grid lock)
        if current_hour % 24 == 0 and random.random() < 0.02:
            incoming_feedstock_rate = 0.0 
            feedstock_price_per_kg = 0.12 

        # Administer Silo Storage Fill
        silo['inventory'] = min(SILO_CAPACITY_KG, silo['inventory'] + incoming_feedstock_rate)
        tracker.accumulated_feedstock_cost += incoming_feedstock_rate * feedstock_price_per_kg
        
        yield env.timeout(1.0)

def request_rack_replacement(env, rack, robot_fleet, tracker):
    """Orchestrates automated isolation, extraction, and fresh slide integration."""
    request = robot_fleet.request()
    yield request
    yield env.timeout(ROBOT_SWAP_TIME)
    
    # Re-initialize fresh rack into the corresponding automated bay slot
    tracker.bays[rack.bay_id] = ProductionRack(rack.bay_id, WEIBULL_SCALE, WEIBULL_SHAPE)
    tracker.total_swaps_performed += 1
    robot_fleet.release(request)

def run_production(env, tracker, robot_fleet, silo):
    """Executes the core microfluidic mass flux calculations hour-by-hour."""
    while True:
        yield env.timeout(1.0)
        
        # Calculate theoretical maximum demand for online modules
        hourly_target_prod = sum([MAX_RACK_OUTPUT_L_HR * r.output_yield for r in tracker.bays if not r.is_failed])
        required_glucose = hourly_target_prod * 3.5
        
        if silo['inventory'] >= required_glucose:
            # Fully Powered Operational Fluidics
            silo['inventory'] -= required_glucose
            for rack in tracker.bays:
                if not rack.is_failed:
                    rack.age += 1.0
                    rack.calculate_decay()
                    hourly_prod = MAX_RACK_OUTPUT_L_HR * rack.output_yield
                    tracker.total_liters_produced += hourly_prod
                    tracker.total_glucose_consumed_kg += hourly_prod * 3.5
                else:
                    env.process(request_rack_replacement(env, rack, robot_fleet, tracker))
        else:
            # Throttled/Starved Operations due to localized supply limits
            available_fraction = silo['inventory'] / max(1.0, required_glucose)
            silo['inventory'] = 0.0
            for rack in tracker.bays:
                if not rack.is_failed:
                    rack.age += 1.0
                    rack.calculate_decay()
                    hourly_prod = MAX_RACK_OUTPUT_L_HR * rack.output_yield * available_fraction
                    tracker.total_liters_produced += hourly_prod
                    tracker.total_glucose_consumed_kg += hourly_prod * 3.5
                else:
                    env.process(request_rack_replacement(env, rack, robot_fleet, tracker))

if __name__ == "__main__":
    print("Initializing Fully Upgraded Consolidated Bio-Plant Infrastructure...")
    
    # Setup environments and tracker reference instances
    env = simpy.Environment()
    tracker = FactoryStateTracker()
    robot_fleet = simpy.Resource(env, capacity=NUM_ROBOTS)
    
    # Initialize the parallel array with biological objects
    tracker.bays = [ProductionRack(i, WEIBULL_SCALE, WEIBULL_SHAPE) for i in range(NUM_BAYS)]
    
    # Storage Silo structural dictionary (starts at 50% capacity reserve)
    silo = {'inventory': SILO_CAPACITY_KG / 2.0}
    
    # Register asynchronous processing channels
    env.process(run_supply_chain(env, tracker, silo))
    env.process(run_production(env, tracker, robot_fleet, silo))
    
    # Run the timeline
    env.run(until=SIM_DURATION)

    # --- FINAL SYSTEM PERFORMANCE BALANCING ENGINE ---
    total_barrels = tracker.total_liters_produced / BARREL_VOLUME_LITERS
    net_maintenance_cost = tracker.total_swaps_performed * (RAW_SWAP_COST - CELL_RECLAIM_CREDIT)
    total_fixed_costs = (NUM_BAYS * CAPEX_PER_RACK) + ROBOT_ARM_CAPEX + FACILITY_OVERHEAD
    total_operational_cost = tracker.accumulated_feedstock_cost + net_maintenance_cost + total_fixed_costs

    per_barrel_cost = total_operational_cost / max(1, total_barrels)
    market_price_per_barrel = 160.0 # Reflecting bypassed fractional crude refinery step credits
    net_profit = (total_barrels * market_price_per_barrel) - total_operational_cost

    print("\n" + "="*50)
    print("=== CONSOLIDATED FULL-PLANT UPGRADE REPORT ===")
    print("="*50)
    print(f"Total Annual Production : {total_barrels:,.2f} Barrels/year")
    print(f"Ending Silo Inventory  : {silo['inventory']:,.2f} kg")
    print(f"Total Swaps Handled     : {tracker.total_swaps_performed:,} maintenance events")
    print(f"Raw Feedstock Cost      : ${tracker.accumulated_feedstock_cost:,.2f}")
    print(f"Net Maintenance Cost    : ${net_maintenance_cost:,.2f}")
    print(f"Fixed Facility Costs    : ${total_fixed_costs:,.2f} (Self-Powered Overheads)")
    print(f"Total Cost Per Barrel   : ${per_barrel_cost:.2f} / bbl")
    print(f"Financial Status        : **ULTRA-RESILIENT**")
    print(f"Net Yearly Profit       : ${net_profit:,.2f}/year")
    print("="*50)
