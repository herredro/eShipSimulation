# eShip Simulation

A Python-based ship routing simulation system for passenger transportation.

## Project Structure

```
eShipSimulation/
├── src/                    # Source code
│   ├── Algorithms/        # Routing algorithms
│   ├── GUI/              # Graphical interface
│   └── *.py              # Core simulation files
├── tests/                 # Test scenarios and experiments
├── config/               # Configuration files
├── csv/                  # Data files
├── main.py              # Main entry point
└── requirements.txt     # Python dependencies
```

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
.\venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The simulation can be run in different modes using the main.py script:

### Wait Time Experiment
```bash
python main.py --mode wait_time [--target-wait-time 20]
```
Runs experiments to find optimal number of boats for target wait time.

### Manual Mode
```bash
python main.py --mode manual [--boats 50]
```
Runs simulation in manual control mode.

### Automatic Mode
```bash
python main.py --mode auto [--boats 50] [--strategy highest_demand|closest_neighbor]
```
Runs simulation in automatic mode with specified strategy.

## Configuration

Main simulation parameters can be configured in `src/Global.py`:
- `SIMTIME`: Duration of simulation (default: 720 units)
- `NUM_BOATS`: Number of boats (default: 90)
- `CAPACITY`: Boat capacity (default: 10)
- `num_stations`: Number of stations (default: 20) 