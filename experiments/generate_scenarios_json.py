
import json
import os
import sys
from pathlib import Path

# Add current directory to path to allow import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import scenario_generator
except ImportError:
    # If running from root, try experiments.scenario_generator
    sys.path.append(str(Path.cwd() / 'experiments'))
    import scenario_generator

def main():
    # Generate 1 of each type
    print("Generating scenarios...")
    instances = scenario_generator.generate_all_scenarios(2)
    
    # Convert to dictionary format like sample.json
    output_data = {}
    for name, data in instances:
        output_data[name] = {
            "data": data
        }
    
    # Save to data/generated_scenarios.json
    output_path = Path('data/generated_scenarios.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Successfully saved {len(instances)} scenarios to {output_path}")

if __name__ == "__main__":
    main()
