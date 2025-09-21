#!/usr/bin/env python3
"""
ELM327 OBD-II Scanner for 2009 Acura TSX
Reads DTCs and live data using python-OBD library
"""

import obd
import time
from datetime import datetime

def connect_elm327(port=None):
    """Connect to ELM327 adapter"""
    try:
        if port:
            connection = obd.OBD(port)
        else:
            connection = obd.OBD()  # Auto-detect port
        
        if connection.status() == obd.OBDStatus.CAR_CONNECTED:
            print("✓ Connected to vehicle")
            return connection
        else:
            print("✗ Failed to connect to vehicle")
            print(f"Status: {connection.status()}")
            return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def read_dtcs(connection):
    """Read Diagnostic Trouble Codes"""
    print("\n" + "="*50)
    print("DIAGNOSTIC TROUBLE CODES")
    print("="*50)
    
    try:
        # Read stored DTCs
        response = connection.query(obd.commands.GET_DTC)
        
        if response.value:
            print(f"Found {len(response.value)} stored codes:")
            for code, description in response.value:
                print(f"  {code}: {description}")
        else:
            print("No stored DTCs found")
            
        # Try to read pending codes
        try:
            if hasattr(obd.commands, 'GET_PENDING_DTC'):
                pending_response = connection.query(obd.commands.GET_PENDING_DTC)
            elif hasattr(obd.commands, 'PENDING_DTC'):
                pending_response = connection.query(obd.commands.PENDING_DTC)
            else:
                pending_response = None
                print("Pending DTC command not available in this library version")
            
            if pending_response and pending_response.value:
                print(f"\nFound {len(pending_response.value)} pending codes:")
                for code, description in pending_response.value:
                    print(f"  {code}: {description}")
            elif pending_response:
                print("No pending DTCs found")
        except Exception as e:
            print(f"Could not read pending DTCs: {e}")
            
    except Exception as e:
        print(f"Error reading DTCs: {e}")

def read_live_data(connection):
    """Read live engine data"""
    print("\n" + "="*50)
    print("LIVE DATA")
    print("="*50)
    
    # Define commands to read
    commands = [
        (obd.commands.RPM, "Engine RPM"),
        (obd.commands.SPEED, "Vehicle Speed"),
        (obd.commands.THROTTLE_POS, "Throttle Position"),
        (obd.commands.ENGINE_LOAD, "Engine Load"),
        (obd.commands.COOLANT_TEMP, "Coolant Temperature"),
        (obd.commands.INTAKE_TEMP, "Intake Air Temperature"),
        (obd.commands.MAF, "Mass Air Flow"),
        (obd.commands.FUEL_PRESSURE, "Fuel Pressure"),
        (obd.commands.O2_B1S1, "O2 Sensor Bank 1 Sensor 1"),
        (obd.commands.SHORT_FUEL_TRIM_1, "Short Term Fuel Trim Bank 1"),
        (obd.commands.LONG_FUEL_TRIM_1, "Long Term Fuel Trim Bank 1")
    ]
    
    print(f"Reading at {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 50)
    
    for cmd, description in commands:
        try:
            response = connection.query(cmd)
            if response.value is not None:
                print(f"{description:<30}: {response.value}")
            else:
                print(f"{description:<30}: Not available")
        except Exception as e:
            print(f"{description:<30}: Error - {e}")

def clear_dtcs(connection):
    """Clear stored DTCs"""
    print("\n" + "="*50)
    print("CLEARING DTCs")
    print("="*50)
    
    response = input("Are you sure you want to clear all DTCs? (y/N): ")
    if response.lower() == 'y':
        try:
            connection.query(obd.commands.CLEAR_DTC)
            print("DTCs cleared successfully")
            time.sleep(2)  # Wait for system to process
        except Exception as e:
            print(f"Error clearing DTCs: {e}")
    else:
        print("DTC clearing cancelled")

def read_vehicle_info(connection):
    """Read vehicle identification info"""
    print("\n" + "="*50)
    print("VEHICLE INFORMATION")
    print("="*50)
    
    info_commands = [
        (obd.commands.VIN, "VIN"),
        (obd.commands.ELM_VERSION, "ELM327 Version"),
        (obd.commands.ELM_VOLTAGE, "Battery Voltage")
    ]
    
    for cmd, description in info_commands:
        try:
            response = connection.query(cmd)
            if response.value is not None:
                print(f"{description:<20}: {response.value}")
        except Exception as e:
            print(f"{description:<20}: Error - {e}")

def main():
    """Main function"""
    print("ELM327 OBD-II Scanner for 2009 Acura TSX")
    print("========================================")
    
    # Connect to ELM327
    connection = connect_elm327()
    if not connection:
        print("Exiting...")
        return
    
    try:
        while True:
            print("\nSelect an option:")
            print("1. Read DTCs")
            print("2. Read Live Data")
            print("3. Clear DTCs")
            print("4. Vehicle Info")
            print("5. Exit")
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == '1':
                read_dtcs(connection)
            elif choice == '2':
                read_live_data(connection)
            elif choice == '3':
                clear_dtcs(connection)
            elif choice == '4':
                read_vehicle_info(connection)
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please enter 1-5.")
                
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        connection.close()
        print("Connection closed")

if __name__ == "__main__":
    # First install required library:
    # pip install obd
    main()