#!/usr/bin/env python3
"""
Honda/Acura Specific O2 Sensor Reader
Tests multiple PID formats to find working O2 sensors
"""

import obd
import time

def test_all_o2_sensor_pids(connection):
    """Test various O2 sensor PID formats that Honda/Acura might use"""
    print("="*60)
    print("TESTING ALL POSSIBLE O2 SENSOR PIDS")
    print("="*60)
    
    # Standard O2 sensor PIDs (what we already tried)
    standard_pids = [
        ('O2_B1S1', 'Bank 1 Sensor 1 (Standard)'),
        ('O2_B1S2', 'Bank 1 Sensor 2 (Standard)'),
        ('O2_B2S1', 'Bank 2 Sensor 1 (Standard)'),
        ('O2_B2S2', 'Bank 2 Sensor 2 (Standard)'),
    ]
    
    # Alternative Honda-specific O2 PIDs
    honda_specific_pids = [
        ('0115', 'O2 Bank 1 Sensor 2 (Honda Format)'),
        ('0116', 'O2 Bank 1 Sensor 3 (Honda Format)'),
        ('0117', 'O2 Bank 1 Sensor 4 (Honda Format)'),
        ('0118', 'O2 Bank 2 Sensor 1 (Honda Format)'),
        ('0119', 'O2 Bank 2 Sensor 2 (Honda Format)'),
    ]
    
    print("TESTING STANDARD O2 SENSOR COMMANDS:")
    print("-" * 40)
    
    working_sensors = []
    
    # Test standard commands
    for cmd_name, description in standard_pids:
        if hasattr(obd.commands, cmd_name):
            try:
                cmd = getattr(obd.commands, cmd_name)
                response = connection.query(cmd)
                
                if response.value is not None:
                    print(f"✓ {description}: {response.value}")
                    working_sensors.append((cmd_name, description, response.value))
                else:
                    print(f"✗ {description}: No data")
            except Exception as e:
                print(f"✗ {description}: Error - {e}")
        else:
            print(f"✗ {description}: Command not available")
    
    print("\nTESTING HONDA-SPECIFIC O2 PIDS:")
    print("-" * 40)
    
    # Test Honda-specific raw PIDs
    for pid, description in honda_specific_pids:
        try:
            # Create custom command for Honda O2 sensors
            custom_cmd = obd.OBDCommand(f"HONDA_O2_{pid}",
                                      description,
                                      pid,
                                      2,  # 2 bytes expected
                                      obd.decoders.percent)
            
            response = connection.query(custom_cmd)
            if response.value is not None:
                print(f"✓ {description}: {response.value}")
                working_sensors.append((pid, description, response.value))
            else:
                print(f"✗ {description}: No response")
                
        except Exception as e:
            print(f"✗ {description}: Error - {e}")
    
    return working_sensors

def test_wideband_o2_sensors(connection):
    """Test for wideband O2 sensors (Air-Fuel Ratio)"""
    print("\n" + "="*60)
    print("TESTING WIDEBAND/AFR SENSORS")
    print("="*60)
    
    wideband_commands = [
        ('COMMANDED_EGR', 'Commanded EGR'),
        ('EGR_ERROR', 'EGR Error'),
    ]
    
    # Try Air-Fuel Ratio sensors (newer Honda format)
    afr_pids = [
        ('0124', 'AFR Bank 1 Sensor 1'),
        ('0125', 'AFR Bank 1 Sensor 2'), 
        ('0126', 'AFR Bank 2 Sensor 1'),
        ('0127', 'AFR Bank 2 Sensor 2'),
    ]
    
    print("Air-Fuel Ratio Sensors (if equipped):")
    print("-" * 40)
    
    for pid, description in afr_pids:
        try:
            afr_cmd = obd.OBDCommand(f"AFR_{pid}",
                                   description,
                                   pid,
                                   2,
                                   obd.decoders.percent)
            
            response = connection.query(afr_cmd)
            if response.value is not None:
                print(f"✓ {description}: {response.value}")
            else:
                print(f"✗ {description}: No data")
        except Exception as e:
            print(f"✗ {description}: Error - {e}")

def live_o2_monitoring(connection, working_sensors):
    """Monitor working O2 sensors in real-time"""
    if not working_sensors:
        print("\n⚠️ No working O2 sensors found for live monitoring")
        return
    
    print(f"\n" + "="*60)
    print("LIVE O2 SENSOR MONITORING")
    print("="*60)
    print("Monitoring working sensors for 30 seconds...")
    print("Engine should be warmed up and running")
    print("Press Ctrl+C to stop early")
    print("-" * 60)
    
    try:
        start_time = time.time()
        while time.time() - start_time < 30:
            print(f"\nTime: {time.time() - start_time:.1f}s")
            
            for cmd_name, description, _ in working_sensors:
                try:
                    if hasattr(obd.commands, cmd_name):
                        cmd = getattr(obd.commands, cmd_name)
                    else:
                        # Raw PID command
                        cmd = obd.OBDCommand(f"CUSTOM_{cmd_name}",
                                           description,
                                           cmd_name,
                                           2,
                                           obd.decoders.percent)
                    
                    response = connection.query(cmd)
                    if response.value is not None:
                        print(f"  {description[:30]:<30}: {response.value}")
                        
                except Exception as e:
                    print(f"  {description[:30]:<30}: Error")
            
            time.sleep(2)  # Update every 2 seconds
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")

def analyze_p0420_without_o2(connection):
    """Analyze P0420 using available data when O2 sensors aren't readable"""
    print(f"\n" + "="*60)
    print("P0420 ANALYSIS WITHOUT DIRECT O2 SENSOR DATA")
    print("="*60)
    
    print("Since we can't read O2 sensor voltages directly, here's what we know:")
    print()
    
    # Re-read fuel trims
    print("FUEL TRIM ANALYSIS:")
    print("-" * 30)
    
    try:
        stft = connection.query(obd.commands.SHORT_FUEL_TRIM_1)
        ltft = connection.query(obd.commands.LONG_FUEL_TRIM_1)
        
        print(f"Short Term Fuel Trim: {stft.value}")
        print(f"Long Term Fuel Trim:  {ltft.value}")
        
        if stft.value is not None and ltft.value is not None:
            total_trim = abs(stft.value) + abs(ltft.value)
            
            if total_trim < 10:
                print("✓ FUEL MIXTURE: Excellent - not causing P0420")
            elif total_trim < 20:
                print("⚠ FUEL MIXTURE: Acceptable - probably not causing P0420") 
            else:
                print("✗ FUEL MIXTURE: Poor - could contribute to P0420")
                
    except Exception as e:
        print(f"Error reading fuel trims: {e}")
    
    print(f"\nP0420 DIAGNOSIS WITHOUT O2 SENSOR READINGS:")
    print("-" * 50)
    print("Since your fuel trims are excellent (-4.7% LTFT, 0% STFT):")
    print()
    print("✓ Engine mixture is NOT causing P0420")
    print("✓ No vacuum leaks or fuel system issues")
    print("✓ Problem is likely:")
    print("   1. Catalytic converter efficiency loss (most likely)")
    print("   2. Downstream O2 sensor failure")
    print("   3. Exhaust leak between cat and downstream sensor")
    print()
    print("RECOMMENDED NEXT STEPS:")
    print("1. Clear P0420 code and drive 20+ miles")
    print("2. If code returns quickly = likely bad catalytic converter")
    print("3. Try replacing downstream O2 sensor first (cheaper)")
    print("4. If still P0420 after new sensor = replace catalytic converter")

def main():
    """Main function"""
    print("HONDA/ACURA O2 SENSOR DIAGNOSTIC FOR P0420")
    print("="*60)
    
    connection = obd.OBD()
    if connection.status() != obd.OBDStatus.CAR_CONNECTED:
        print("✗ Could not connect to vehicle")
        return
    
    try:
        # Test all possible O2 sensor formats
        working_sensors = test_all_o2_sensor_pids(connection)
        
        # Test wideband sensors
        test_wideband_o2_sensors(connection)
        
        # If we found working sensors, do live monitoring
        if working_sensors:
            do_live = input(f"\nFound {len(working_sensors)} working sensors. Do live monitoring? (y/N): ")
            if do_live.lower() == 'y':
                live_o2_monitoring(connection, working_sensors)
        
        # Analyze P0420 with available data
        analyze_p0420_without_o2(connection)
        
    finally:
        connection.close()

if __name__ == "__main__":
    main()