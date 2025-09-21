import serial
ser = serial.Serial('COM3', 38400)  # Use your actual COM port
print("ELM327 connected successfully!")
ser.close()