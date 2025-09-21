#!/usr/bin/env python3
"""
OBD Commands Discovery Tool
Lists all available commands in python-OBD library
"""

import obd
import inspect

def list_all_commands():
    """List all available OBD commands"""
    print("="*60)
    print("AVAILABLE OBD COMMANDS IN PYTHON-OBD")
    print("="*60)
    
    # Get all attributes of obd.commands
    commands_dict = {}
    
    for attr_name in dir(obd.commands):
        # Skip private attributes
        if not attr_name.startswith('_'):
            attr_value = getattr(obd.commands, attr_name)
            # Check if it's an OBD command (has certain properties)
            if hasattr(attr_value, 'name') and hasattr(attr_value, 'desc'):
                commands_dict[attr_name] = attr_value
    
    # Sort commands alphabetically
    sorted_commands = sorted(commands_dict.items())
    
    print(f"Found {len(sorted_commands)} OBD commands:\n")
    
    # Group commands by category for better readability
    categories = {
        'Engine': [],
        'Fuel': [],
        'Temperature': [],
        'Pressure': [],
        'Sensors': [],
        'Emission': [],
        'System': [],
        'Other': []
    }
    
    for cmd_name, cmd_obj in sorted_commands:
        # Categorize commands based on name patterns
        name_lower = cmd_name.lower()
        desc_lower = cmd_obj.desc.lower()
        
        if any(keyword in name_lower for keyword in ['rpm', 'load', 'timing']):
            categories['Engine'].append((cmd_name, cmd_obj))
        elif any(keyword in name_lower for keyword in ['fuel', 'trim']):
            categories['Fuel'].append((cmd_name, cmd_obj))
        elif any(keyword in name_lower for keyword in ['temp', 'coolant', 'intake_temp']):
            categories['Temperature'].append((cmd_name, cmd_obj))
        elif any(keyword in name_lower for keyword in ['pressure', 'vacuum']):
            categories['Pressure'].append((cmd_name, cmd_obj))
        elif any(keyword in name_lower for keyword in ['o2', 'sensor', 'maf']):
            categories['Sensors'].append((cmd_name, cmd_obj))
        elif any(keyword in name_lower for keyword in ['dtc', 'monitor', 'emission']):
            categories['Emission'].append((cmd_name, cmd_obj))
        elif any(keyword in name_lower for keyword in ['elm', 'status', 'vin']):
            categories['System'].append((cmd_name, cmd_obj))
        else:
            categories['Other'].append((cmd_name, cmd_obj))
    
    # Print categorized commands
    for category, commands in categories.items():
        if commands:
            print(f"\n{category.upper()} COMMANDS:")
            print("-" * 40)
            for cmd_name, cmd_obj in commands:
                print(f"  {cmd_name:<25} : {cmd_obj.desc}")

def search_commands(search_term):
    """Search for commands containing specific term"""
    print(f"\nSearching for commands containing '{search_term}':")
    print("-" * 50)
    
    found = False
    for attr_name in dir(obd.commands):
        if not attr_name.startswith('_'):
            attr_value = getattr(obd.commands, attr_name)
            if hasattr(attr_value, 'name') and hasattr(attr_value, 'desc'):
                if (search_term.upper() in attr_name.upper() or 
                    search_term.upper() in attr_value.desc.upper()):
                    print(f"  {attr_name:<25} : {attr_value.desc}")
                    found = True
    
    if not found:
        print(f"  No commands found containing '{search_term}'")

def test_command_exists(command_name):
    """Test if a specific command exists"""
    print(f"\nTesting command: {command_name}")
    print("-" * 30)
    
    if hasattr(obd.commands, command_name):
        cmd = getattr(obd.commands, command_name)
        print(f"✓ Command exists: {cmd.desc}")
        print(f"  PID: {getattr(cmd, 'pid', 'N/A')}")
        print(f"  Bytes: {getattr(cmd, 'bytes', 'N/A')}")
    else:
        print(f"✗ Command '{command_name}' does not exist")

def main():
    """Main function with interactive menu"""
    while True:
        print("\n" + "="*60)
        print("OBD COMMANDS DISCOVERY TOOL")
        print("="*60)
        print("1. List all available commands")
        print("2. Search commands by keyword")
        print("3. Test specific command")
        print("4. Show fuel trim commands specifically")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            list_all_commands()
        elif choice == '2':
            search_term = input("Enter search term: ").strip()
            if search_term:
                search_commands(search_term)
        elif choice == '3':
            cmd_name = input("Enter command name (e.g., RPM): ").strip()
            if cmd_name:
                test_command_exists(cmd_name)
        elif choice == '4':
            print("\nFUEL TRIM RELATED COMMANDS:")
            print("-" * 30)
            fuel_commands = ['SHORT_FUEL_TRIM_1', 'LONG_FUEL_TRIM_1', 
                           'SHORT_FUEL_TRIM_2', 'LONG_FUEL_TRIM_2',
                           'FUEL_PRESSURE', 'FUEL_RAIL_PRESSURE']
            for cmd in fuel_commands:
                test_command_exists(cmd)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()