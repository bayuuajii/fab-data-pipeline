import sqlite3

def calculate_yield():
    # Konek ke database lokal yang lu bikin kemarin
    conn = sqlite3.connect("fab_data.db")
    cursor = conn.cursor()

    # Query 1: Hitung total semua data (total siklus pabrik)
    cursor.execute("SELECT COUNT(*) FROM telemetry_logs")
    total_data = cursor.fetchone()[0]

    if total_data == 0:
        print("Database kosong. Belum ada data dari pabrik.")
        conn.close()
        return

    # Query 2: Hitung hanya data yang normal (IN_CONTROL)
    cursor.execute("SELECT COUNT(*) FROM telemetry_logs WHERE spc_status = 'IN_CONTROL'")
    in_control_data = cursor.fetchone()[0]

    # Kalkulasi Persentase Yield
    yield_percentage = (in_control_data / total_data) * 100

    print("\n=== [ SPC YIELD ANALYTICS REPORT ] ===")
    print(f"Total Siklus Mesin   : {total_data}")
    print(f"Siklus Normal (Aman) : {in_control_data}")
    print(f"Siklus Error (Rusak) : {total_data - in_control_data}")
    print(f"Persentase Yield     : {yield_percentage:.2f}%\n")
    
    if yield_percentage < 95.0:
        print("[WARNING] Yield di bawah standar 95%! Mesin butuh inspeksi.")
    else:
        print("[OK] Yield Optimal. Produksi berjalan efisien.")

    conn.close()

if __name__ == "__main__":
    calculate_yield()
