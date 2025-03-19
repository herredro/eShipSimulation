#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent))

from src.Simulation import Simulation
from src.Global import Global as G

def run_wait_time_experiment(num_boats_range=None, target_wait_time=20):
    """Run wait time optimization experiment."""
    if num_boats_range is None:
        num_boats_range = [1, 4, 10, 22, 46, 47, 48, 49, 50]
    
    print(f"EXPERIMENT WT central=True: to achieve wait_time={target_wait_time} in vary=0")
    sim = Simulation()
    
    for num_boats in num_boats_range:
        stats = sim.simpy(mode=True, num_boats=num_boats)
        wait_time_percentage = (stats.avg_wait_time / target_wait_time) * 100
        print(f"{num_boats}b's --> {wait_time_percentage:.1f}%")

def run_manual_simulation(num_boats):
    """Run manual simulation mode."""
    sim = Simulation()
    sim.cb.create_basic_boats(numBoats2create=num_boats)
    sim.cb.printboatlist()
    sim.cb.move_boat__input()

def run_automatic_simulation(num_boats, strategy='highest_demand'):
    """Run automatic simulation with specified strategy."""
    sim = Simulation()
    sim.cb.create_basic_boats(numBoats2create=num_boats)
    sim.cb.printboatlist()
    
    if strategy == 'highest_demand':
        strategy_func = sim.strategy.highest_demand
    else:
        strategy_func = sim.strategy.closest_neighbor
        
    for _ in range(int(G.rounds)):
        sim.cb.fleet_move_demand(strategy=strategy_func, pu_quant='max', do_quant='max')

def main():
    parser = argparse.ArgumentParser(description='eShip Simulation Runner')
    parser.add_argument('--mode', choices=['wait_time', 'manual', 'auto'], required=True,
                      help='Simulation mode to run')
    parser.add_argument('--boats', type=int, default=50,
                      help='Number of boats for manual/auto mode')
    parser.add_argument('--strategy', choices=['highest_demand', 'closest_neighbor'],
                      default='highest_demand',
                      help='Strategy for automatic mode')
    parser.add_argument('--target-wait-time', type=float, default=20,
                      help='Target wait time for wait_time experiment')
    
    args = parser.parse_args()
    
    if args.mode == 'wait_time':
        run_wait_time_experiment(target_wait_time=args.target_wait_time)
    elif args.mode == 'manual':
        run_manual_simulation(args.boats)
    elif args.mode == 'auto':
        run_automatic_simulation(args.boats, args.strategy)

if __name__ == "__main__":
    main() 