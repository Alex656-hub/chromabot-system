"""Utility script to inspect raw serial output from the Arduino sensor."""

import sys
import time
import serial


def main(port: str = "COM3") -> None:
    try:
        ser = serial.Serial(port, 9600, timeout=2)
    except serial.SerialException as exc:  # type: ignore[attr-defined]
        print(f"[ERROR] No se pudo abrir el puerto {port}: {exc}")
        return

    try:
        time.sleep(2)
        print("=== Datos al abrir el puerto ===")
        while ser.in_waiting:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                print(line)

        ser.write(b"GET_STATUS\n")
        time.sleep(1)
        print("=== Respuesta a GET_STATUS ===")
        while ser.in_waiting:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                print(line)
    finally:
        ser.close()


if __name__ == "__main__":
    port_arg = sys.argv[1] if len(sys.argv) > 1 else "COM3"
    main(port_arg)
