import simpy
import random
import numpy as np

# --- CONSOLIDATED PHASE 5: OPPORTUNITY COST EQUALIZATION ---
SIM_DURATION = 8760         # 1 year (hours)
NUM_BAYS = 20000            # 20,000 Parallel Microfluidic Bays
NUM_ROBOTS = 25             
ROBOT_SWAP_TIME = 0.05      

MAX_RACK_OUTPUT_L_HR = 0.25 
WEIBULL_SCALE = 4320.0      # 180-day lifespan via Orthogonal Core
WEIBULL_SHAPE = 1.5
SILO_CAPACITY_KG = 3000000.0 # 3,000 metric ton storage buffer

# Financials (Reflecting Closed-Loop Utility Reductions)
GLUCOSE_COST_PER_KG = 0.04  
RAW_SWAP_COST = 8.0         
CELL_RECLAIM_CREDIT = 3.00  
FACILITY_OVERHEAD = 350000.0 # Slashed via Lignin Co-Generation self-powering
CAPEX_PER_RACK = 100.0      
ROBOT_ARM_CAPEX = 120000.0 * NUM_ROBOTS

# Volumetric Conversions
BARREL_VOLUME_LITERS = 159
GALLONS_PER_BARREL = 42

class ProductionRack:
    def __init__(self, bay_id):
        self.bay_id = bay_id
        self.age = random.uniform(0, 300)
        self.output_yield = 1.0
        self.is_failed = False

    def calculate_decay(self):
        self.output_yield = np.exp(-((self.age / WEIBULL_SCALE) ** WEIBULL_SHAPE))
        if self.output_yield < 0.20:
            self.is_failed = True

class OpportunityCostSimulation:
    def __init__(self, env):
        self.env = env
        self.robot_fleet = simpy.Resource(env, capacity=NUM_ROBOTS)
        self.bays = [ProductionRack(i) for i in range(NUM_BAYS)]
        self.silo_inventory = SILO_CAPACITY_KG / 2.0
        
        self.total_liters_produced = 0.0
        self.total_glucose_consumed_kg = 0.0
        self.total_swaps_performed = 0
        self.accumulated_feedstock_cost = 0.0

    def run_supply_chain(self):
        while True:
            current_hour = self.env.now
            seasonality = np.sin(2 * np.pi * current_hour / 8760)
            
            if seasonality > 0.3: 
                incoming_feedstock_rate = 6500.0 
                feedstock_price_per_kg = 0.02    
            elif seasonality < -0.3: 
                incoming_feedstock_rate = 2000.0 
                feedstock_price_per_kg = 0.08    
            else: 
                incoming_feedstock_rate = 4500.0
                feedstock_price_per_kg = 0.04

            if current_hour % 24 == 0 and random.random() < 0.02:
                incoming_feedstock_rate = 0.0 
                feedstock_price_per_kg = 0.12 

            purchased_stock = incoming_feedstock_rate
            self.silo_inventory = min(SILO_CAPACITY_KG, self.silo_inventory + purchased_stock)
            self.accumulated_feedstock_cost += purchased_stock * feedstock_price_per_kg
            
            yield self.env.timeout(1.0)

    def run_production(self):
        while True:
            yield self.env.timeout(1.0)
            
            hourly_target_prod = sum([MAX_RACK_OUTPUT_L_HR * rack.output_yield for rack in self.bays if not rack.is_failed])
            required_glucose = hourly_target_prod * 3.5
            
            if self.silo_inventory >= required_glucose:
                self.silo_inventory -= required_glucose
                for rack in self.bays:
                    if not rack.is_failed:
                        rack.age += 1.0
                        rack.calculate_decay()
                        hourly_prod = MAX_RACK_OUTPUT_L_HR * rack.output_yield
                        self.total_liters_produced += hourly_prod
                        self.total_glucose_consumed_kg += hourly_prod * 3.5
                    else:
                        self.env.process(self.request_rack_replacement(rack))
            else:
                available_fraction = self.silo_inventory / max(1.0, required_glucose)
                self.silo_inventory = 0.0
                for rack in self.bays:
                    if not rack.is_failed:
                        rack.age += 1.0
                        rack.calculate_decay()
                        hourly_prod = MAX_RACK_OUTPUT_L_HR * rack.output_yield * available_fraction
                        self.total_liters_produced += hourly_prod
                        self.total_glucose_consumed_kg += hourly_prod * 3.5
                    else:
                        self.env.process(self.request_rack_replacement(rack))

    def request_rack_replacement(self, rack):
        request = self.robot_fleet.request()
        yield request
        yield self.env.timeout(ROBOT_SWAP_TIME)
        self.bays[rack.bay_id] = ProductionRack(rack.bay_id)
        self.total_swaps_performed += 1
        self.robot_fleet.release(request)

# --- RUN THE EQUALIZED SIMULATION ---
print("Simulating Phase 5: Testing Product-Slate Opportunity Cost Equalization...")
env = simpy.Environment()
factory = OpportunityCostSimulation(env)
env.process(factory.run_supply_chain())
env.process(factory.run_production())
env.run(until=SIM_DURATION)

# --- REAL-WORLD WHOLESALE FINANCIAL ENGINE ---
total_barrels = factory.total_liters_produced / BARREL_VOLUME_LITERS
total_gallons = total_barrels * GALLONS_PER_BARREL
total_liters = factory.total_liters_produced

net_maintenance_cost = factory.total_swaps_performed * (RAW_SWAP_COST - CELL_RECLAIM_CREDIT)
total_fixed_costs = (NUM_BAYS * CAPEX_PER_RACK) + ROBOT_ARM_CAPEX + FACILITY_OVERHEAD
total_operational_cost = factory.accumulated_feedstock_cost + net_maintenance_cost + total_fixed_costs

# Unit Cost Breakdowns
per_barrel_cost = total_operational_cost / max(1, total_barrels)
per_gallon_cost = per_barrel_cost / GALLONS_PER_BARREL
per_liter_cost = per_barrel_cost / BARREL_VOLUME_LITERS

# NEW: Forced Par Market Valuation (Wholesale gasoline off-the-shelf, no premium credits)
MARKET_PRICE_PER_BARREL = 100.80  # Equivalent to $2.40 per gallon wholesale spot price
net_profit = (total_barrels * MARKET_PRICE_PER_BARREL) - total_operational_cost
margin_per_barrel = MARKET_PRICE_PER_BARREL - per_barrel_cost

print("\n" + "="*50)
print("=== PHASE 5: OPPORTUNITY COST EQUALIZATION REPORT ===")
print("="*50)
print(f"Annual Production Vol   : {total_barrels:,.2f} Barrels/year ({total_gallons:,.2f} Gallons/yr)")
print(f"Total Combined Cost     : ${total_operational_cost:,.2f}")
print(f"Calculated Cost Metrics : ${per_barrel_cost:.2f} / bbl | ${per_gallon_cost:.2f} / gallon | ${per_liter_cost:.2f} / liter")
print(f"Target Wholesale Value  : ${MARKET_PRICE_PER_BARREL:.2f} / bbl ($2.40 / gallon wholesale par)")
print(f"Net Economic Margin     : ${margin_per_barrel:.2f} per barrel profit cushion")
if net_profit > 0:
    print(f"Financial Feasibility   : **ECONOMICALLY VIABLE AT PAR**")
    print(f"Net Realized Profit     : ${net_profit:,.2f}/year")
else:
    print(f"Financial Feasibility   : UNCOMPETITIVE [Deficit: ${abs(net_profit):,.2f}/year]")
print("="*50)
