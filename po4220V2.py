#!/usr/bin/env python3
"""
P0420 Diagnostic Tool for 2009 Acura TSX
Analyzes catalytic converter efficiency and related parameters
"""

import obd
import time
from datetime import datetime

def analyze_p0420(connection):
    """Comprehensive P0420 analysis"""
    print("="*60)
    print("P0420 CATALYST EFFICIENCY DIAGNOSTIC")
    print("="*60)
    print("Code: P0420 - Catalyst System Efficiency Below Threshold")
    print("Location: Bank 1 (Cylinder side with #1 cylinder)")
    print()
    
    print("WHAT THIS MEANS:")
    print("- Catalytic converter not cleaning exhaust efficiently")
    print("- Downstream O2 sensor detecting insufficient conversion")
    print("- May cause emissions test failure")
    print("- Usually not drivability issue initially")
    print()

def read_o2_sensors(connection):
    """Read all O2 sensor data"""
    print("="*60)
    print("OXYGEN SENSOR ANALYSIS")
    print("="*60)
    
    o2_commands = [
        (obd.commands.O2_B1S1, "Bank 1 Sensor 1 (Upstream/Pre-Cat)", "Pre-catalytic converter"),
        (obd.commands.O2_B1S2, "Bank 1 Sensor 2 (Downstream/Post-Cat)", "Post-catalytic converter"),
    ]
    
    # Try to add Bank 2 sensors if they exist (V6 engines)
    if hasattr(obd.commands, 'O2_B2S1'):
        o2_commands.extend([
            (obd.commands.O2_B2S1, "Bank 2 Sensor 1 (Upstream)", "Pre-catalytic converter"),
            (obd.commands.O2_B2S2, "Bank 2 Sensor 2 (Downstream)", "Post-catalytic converter"),
        ])
    
    print("Reading O2 sensor voltages (engine should be warmed up and running):")
    print("-" * 60)
    
    for cmd, description, location in o2_commands:
        try:
            response = connection.query(cmd)
            if response.value is not None:
                voltage = response.value.voltage if hasattr(response.value, 'voltage') else response.value
                print(f"{description:<35}: {voltage}")
                
                # Analyze voltage patterns
                if "Upstream" in description or "Pre-Cat" in description:
                    if voltage < 0.1:
                        print(f"  └─ Analysis: Very lean (possible vacuum leak)")
                    elif voltage > 0.9:
                        print(f"  └─ Analysis: Very rich (possible fuel system issue)")
                    else:
                        print(f"  └─ Analysis: Normal switching range")
                else:  # Downstream sensor
                    if voltage < 0.6:
                        print(f"  └─ Analysis: Cat working (voltage should be stable ~0.6-0.8V)")
                    else:
                        print(f"  └─ Analysis: ⚠️ High voltage suggests cat inefficiency")
            else:
                print(f"{description:<35}: Not available")
                
        except Exception as e:
            print(f"{description:<35}: Error - {e}")
    
    print("\nIMPORTANT O2 SENSOR NOTES:")
    print("- Upstream sensors should switch rapidly (0.1V - 0.9V)")
    print("- Downstream sensors should be stable (~0.6-0.8V)")
    print("- If downstream follows upstream closely = bad cat")

def read_fuel_trim(connection):
    """Read fuel trim values"""
    print("\n" + "="*60)
    print("FUEL TRIM ANALYSIS")
    print("="*60)
    
    fuel_commands = [
        (obd.commands.SHORT_FUEL_TRIM_1, "Short Term Fuel Trim Bank 1"),
        (obd.commands.LONG_FUEL_TRIM_1, "Long Term Fuel Trim Bank 1"),
    ]
    
    # Add Bank 2 if available (V6)
    if hasattr(obd.commands, 'SHORT_FUEL_TRIM_2'):
        fuel_commands.extend([
            (obd.commands.SHORT_FUEL_TRIM_2, "Short Term Fuel Trim Bank 2"),
            (obd.commands.LONG_FUEL_TRIM_2, "Long Term Fuel Trim Bank 2"),
        ])
    
    print("Fuel trim values (+ = adding fuel, - = removing fuel):")
    print("-" * 60)
    
    for cmd, description in fuel_commands:
        try:
            response = connection.query(cmd)
            if response.value is not None:
                trim_percent = response.value
                print(f"{description:<35}: {trim_percent}")
                
                # Analyze fuel trim
                if abs(trim_percent) > 25:
                    print(f"  └─ ⚠️ HIGH TRIM: Possible fuel system or sensor issue")
                elif abs(trim_percent) > 10:
                    print(f"  └─ ELEVATED: Monitor for trends")
                else:
                    print(f"  └─ NORMAL: Within acceptable range")
                    
        except Exception as e:
            print(f"{description:<35}: Error - {e}")
    
    print("\nFUEL TRIM INTERPRETATION:")
    print("- Normal range: -10% to +10%")
    print("- High positive: Engine running lean (adding fuel)")
    print("- High negative: Engine running rich (removing fuel)")
    print("- Extreme values can damage catalytic converter")

def read_catalyst_temp(connection):
    """Try to read catalyst temperature if available"""
    print("\n" + "="*60)
    print("CATALYST TEMPERATURE (if available)")
    print("="*60)
    
    temp_commands = [
        "CATALYST_TEMP_B1S1",
        "CAT_TEMP_B1",
        "CATALYST_TEMP",
    ]
    
    found_temp = False
    for cmd_name in temp_commands:
        if hasattr(obd.commands, cmd_name):
            try:
                cmd = getattr(obd.commands, cmd_name)
                response = connection.query(cmd)
                if response.value is not None:
                    print(f"Catalyst Temperature ({cmd_name}): {response.value}")
                    found_temp = True
                    
                    # Analyze temperature
                    if hasattr(response.value, 'celsius'):
                        temp_c = response.value.celsius
                        if temp_c > 800:
                            print("  └─ ⚠️ HIGH TEMP: Possible engine running rich")
                        elif temp_c < 300:
                            print("  └─ LOW TEMP: Cat may not be reaching operating temp")
                        else:
                            print("  └─ NORMAL OPERATING RANGE")
                    break
            except Exception as e:
                print(f"Error reading {cmd_name}: {e}")
                continue
    
    if not found_temp:
        print("Catalyst temperature data not available with this scanner")
        print("This is normal - most basic ELM327 adapters don't support cat temp")

def p0420_recommendations():
    """Provide P0420 specific recommendations"""
    print("\n" + "="*60)
    print("P0420 REPAIR RECOMMENDATIONS")
    print("="*60)
    
    print("STEP 1: VERIFY THE CODE")
    print("- Clear the code and drive 20-30 miles")
    print("- If it returns immediately = likely bad cat")
    print("- If it takes several drive cycles = possible other causes")
    print()
    
    print("STEP 2: CHECK THESE FIRST (cheaper fixes):")
    print("- Downstream O2 sensor (Bank 1, Sensor 2)")
    print("- Exhaust leaks between engine and cat")
    print("- Air filter (dirty filter can affect mixture)")
    print("- Fuel injector cleaning")
    print()
    
    print("STEP 3: ADVANCED DIAGNOSTICS:")
    print("- O2 sensor switching test with scanner")
    print("- Catalytic converter efficiency test")
    print("- Check for oil consumption (blue smoke)")
    print()
    
    print("STEP 4: IF CAT REPLACEMENT NEEDED:")
    print("- OEM Honda cat: $800-1200 (best longevity)")
    print("- Aftermarket CARB compliant: $300-600")
    print("- Labor: 2-4 hours ($200-400)")
    print()
    
    print("⚠️  IMPORTANT FOR 2009 TSX:")
    print("- California emissions (CARB) compliant cat required")
    print("- Some cheap cats will trigger P0420 again quickly")
    print("- Address root cause or new cat will fail too")

def main():
    """Main P0420 diagnostic routine"""
    print("P0420 CATALYST DIAGNOSTIC FOR 2009 ACURA TSX")
    print("=" * 60)
    
    connection = obd.OBD()
    if connection.status() != obd.OBDStatus.CAR_CONNECTED:
        print("✗ Could not connect to vehicle")
        print("Make sure engine is running and warmed up for best results")
        return
    
    try:
        analyze_p0420(connection)
        
        input("\nPress Enter to continue with live data analysis...")
        
        print("\n🔥 ENGINE SHOULD BE RUNNING AND WARMED UP FOR ACCURATE READINGS")
        input("Start engine and let warm up for 5+ minutes, then press Enter...")
        
        read_o2_sensors(connection)
        read_fuel_trim(connection)
        read_catalyst_temp(connection)
        p0420_recommendations()
        
    finally:
        connection.close()

if __name__ == "__main__":
    main()