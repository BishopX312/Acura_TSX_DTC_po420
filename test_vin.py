#!/usr/bin/env python3
"""
VIN Diagnostic and Troubleshooting Tool
Tests various methods to retrieve VIN from OBD-II
"""

import obd
import time

def test_vin_command(connection):
    """Test the standard OBD VIN command"""
    print("="*50)
    print("TESTING STANDARD VIN COMMAND")
    print("="*50)
    
    try:
        # Test if VIN command exists
        if hasattr(obd.commands, 'VIN'):
            print("✓ VIN command exists in library")
            
            # Try to query VIN
            print("Attempting to read VIN...")
            response = connection.query(obd.commands.VIN)
            
            if response.value:
                print(f"✓ VIN Retrieved: {response.value}")
                return response.value
            else:
                print("✗ VIN command returned no data")
                print(f"Response: {response}")
        else:
            print("✗ VIN command not available in library")
            
    except Exception as e:
        print(f"✗ Error reading VIN: {e}")
    
    return None

def test_raw_vin_commands(connection):
    """Test raw VIN commands manually"""
    print("\n" + "="*50)
    print("TESTING RAW VIN COMMANDS")
    print("="*50)
    
    # Common VIN PIDs used by different manufacturers
    vin_pids = [
        ("0902", "Standard VIN Request (Mode 09, PID 02)"),
        ("0904", "Calibration ID"),
        ("090A", "ECU Name"),
    ]
    
    for pid, description in vin_pids:
        print(f"\nTesting {description}:")
        try:
            # Send raw command
            response = connection.query(obd.OBDCommand("VIN_TEST", 
                                                     description,
                                                     pid,
                                                     17,  # Expected bytes
                                                     obd.decoders.raw_string))
            
            if response.value:
                print(f"✓ Response: {response.value}")
            else:
                print(f"✗ No response for {pid}")
                
        except Exception as e:
            print(f"✗ Error with {pid}: {e}")

def test_elm327_info(connection):
    """Get ELM327 adapter information"""
    print("\n" + "="*50)
    print("ELM327 ADAPTER INFORMATION")
    print("="*50)
    
    info_commands = [
        (obd.commands.ELM_VERSION, "ELM327 Version"),
        (obd.commands.ELM_VOLTAGE, "Battery Voltage"),
    ]
    
    # Test if we can get protocol info
    try:
        # Try to get current protocol
        protocol_cmd = obd.OBDCommand("PROTOCOL", "Current Protocol", "ATDP", 1, obd.decoders.raw_string)
        protocol_response = connection.query(protocol_cmd)
        if protocol_response.value:
            print(f"Current Protocol: {protocol_response.value}")
    except:
        print("Could not determine current protocol")
    
    for cmd, description in info_commands:
        try:
            response = connection.query(cmd)
            if response.value is not None:
                print(f"{description}: {response.value}")
            else:
                print(f"{description}: Not available")
        except Exception as e:
            print(f"{description}: Error - {e}")

def test_supported_pids(connection):
    """Test which PIDs are supported"""
    print("\n" + "="*50)
    print("SUPPORTED PIDS TEST")
    print("="*50)
    
    try:
        # Test Mode 01 supported PIDs
        pids_01 = connection.query(obd.commands.PIDS_A)
        if pids_01.value:
            print(f"Mode 01 Supported PIDs: {pids_01.value}")
        
        # Test Mode 09 supported PIDs (where VIN usually lives)
        print("\nTesting Mode 09 (Vehicle Information) support...")
        mode09_cmd = obd.OBDCommand("MODE09_PIDS", "Mode 09 Supported PIDs", "0900", 4, obd.decoders.pid)
        pids_09 = connection.query(mode09_cmd)
        
        if pids_09.value:
            print(f"Mode 09 Supported PIDs: {pids_09.value}")
            if 2 in pids_09.value:  # PID 02 is VIN
                print("✓ VIN (PID 02) is supported!")
            else:
                print("✗ VIN (PID 02) is NOT supported")
        else:
            print("✗ Mode 09 not supported or no response")
            
    except Exception as e:
        print(f"Error testing supported PIDs: {e}")

def alternative_vin_methods():
    """Show alternative methods to get VIN"""
    print("\n" + "="*50)
    print("ALTERNATIVE VIN RETRIEVAL METHODS")
    print("="*50)
    
    print("Since OBD-II VIN retrieval failed, try these alternatives:")
    print()
    print("1. PHYSICAL LOCATION:")
    print("   - Dashboard (driver side, visible through windshield)")
    print("   - Driver door jamb sticker")
    print("   - Engine bay (firewall or strut tower)")
    print()
    print("2. HONDA-SPECIFIC TOOLS:")
    print("   - Honda HDS (Honda Diagnostic System)")
    print("   - Autel scanners with Honda protocols")
    print("   - Launch X431 series")
    print()
    print("3. ONLINE VIN LOOKUP:")
    print("   - Use license plate lookup services")
    print("   - Check vehicle registration documents")
    print()
    print("4. SMARTPHONE APPS:")
    print("   - Some apps can scan VIN barcodes from documents")
    print("   - Insurance company apps often store VIN")

def main():
    """Main diagnostic function"""
    print("VIN DIAGNOSTIC TOOL FOR 2009 ACURA TSX")
    print("="*60)
    
    # Connect to ELM327
    print("Connecting to ELM327...")
    try:
        connection = obd.OBD()
        if connection.status() != obd.OBDStatus.CAR_CONNECTED:
            print("✗ Failed to connect to vehicle")
            print("Make sure:")
            print("- ELM327 is plugged into OBD port")
            print("- Ignition is ON (engine doesn't need to be running)")
            print("- ELM327 drivers are installed")
            return
        else:
            print("✓ Connected to vehicle")
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return
    
    try:
        # Run all diagnostic tests
        vin = test_vin_command(connection)
        
        if not vin:
            test_raw_vin_commands(connection)
            test_elm327_info(connection)
            test_supported_pids(connection)
            alternative_vin_methods()
        
    finally:
        connection.close()
        print(f"\n{'='*60}")
        print("Diagnostic complete. Connection closed.")

if __name__ == "__main__":
    main()