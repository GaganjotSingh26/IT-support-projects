"""
IT System Monitoring Dashboard
Author: Gaganjot Singh | Gothenburg, Sweden
"""
import psutil, time, datetime, os, csv

THRESHOLDS = {"cpu_percent": 80.0, "memory_percent": 85.0, "disk_percent": 90.0}
LOG_FILE    = "logs/alerts.csv"
REPORT_FILE = "reports/daily_report.html"
CHECK_INTERVAL_SECONDS = 5

def get_system_stats():
    net = psutil.net_io_counters()
    return {
        "timestamp":       datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_percent":     psutil.cpu_percent(interval=1),
        "memory_percent":  psutil.virtual_memory().percent,
        "memory_used_gb":  round(psutil.virtual_memory().used / (1024**3), 2),
        "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "disk_percent":    psutil.disk_usage("/").percent,
        "disk_used_gb":    round(psutil.disk_usage("/").used / (1024**3), 2),
        "disk_total_gb":   round(psutil.disk_usage("/").total / (1024**3), 2),
        "net_sent_mb":     round(net.bytes_sent / (1024**2), 2),
        "net_recv_mb":     round(net.bytes_recv / (1024**2), 2),
    }

def check_alerts(stats):
    alerts = []
    for metric, threshold in THRESHOLDS.items():
        if stats.get(metric, 0) > threshold:
            alerts.append({
                "timestamp": stats["timestamp"], "metric": metric,
                "value": stats[metric], "threshold": threshold,
                "severity": "CRITICAL" if stats[metric] > threshold + 10 else "WARNING",
            })
    return alerts

def log_alerts(alerts):
    os.makedirs("logs", exist_ok=True)
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp","metric","value","threshold","severity"])
        if not file_exists:
            writer.writeheader()
        writer.writerows(alerts)

def print_dashboard(stats, alerts):
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 55)
    print("  IT SYSTEM MONITOR  —  Gaganjot Singh")
    print(f"  {stats['timestamp']}")
    print("=" * 55)
    print(f"  CPU Usage        : {stats['cpu_percent']:>6.1f}%")
    print(f"  Memory Usage     : {stats['memory_percent']:>6.1f}%  ({stats['memory_used_gb']} / {stats['memory_total_gb']} GB)")
    print(f"  Disk Usage       : {stats['disk_percent']:>6.1f}%  ({stats['disk_used_gb']} / {stats['disk_total_gb']} GB)")
    print(f"  Network Sent     : {stats['net_sent_mb']:>8.2f} MB")
    print(f"  Network Received : {stats['net_recv_mb']:>8.2f} MB")
    print("-" * 55)
    if alerts:
        print(f"  ⚠  {len(alerts)} ALERT(S):")
        for a in alerts:
            print(f"     [{a['severity']}] {a['metric']} = {a['value']}% (limit: {a['threshold']}%)")
    else:
        print("  ✓  All systems normal")
    print("=" * 55)
    print(f"  Refreshing every {CHECK_INTERVAL_SECONDS}s  |  Ctrl+C to stop & generate report")

def generate_html_report(history):
    os.makedirs("reports", exist_ok=True)
    avg_cpu  = round(sum(s["cpu_percent"] for s in history) / len(history), 1)
    avg_mem  = round(sum(s["memory_percent"] for s in history) / len(history), 1)
    avg_disk = round(sum(s["disk_percent"] for s in history) / len(history), 1)
    rows = "".join(f"<tr><td>{s['timestamp']}</td><td>{s['cpu_percent']}%</td><td>{s['memory_percent']}%</td><td>{s['disk_percent']}%</td></tr>" for s in history[-20:])
    html = f"""<!DOCTYPE html><html><head><title>IT Monitor Report</title>
<style>body{{font-family:Arial;margin:40px}} h1{{color:#1A3A5C}} table{{border-collapse:collapse;width:100%}} th{{background:#1A3A5C;color:white;padding:10px}} td{{padding:8px;border-bottom:1px solid #ddd}}</style>
</head><body>
<h1>IT System Monitoring Report</h1>
<p>Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
<p>Avg CPU: <b>{avg_cpu}%</b> &nbsp;|&nbsp; Avg Memory: <b>{avg_mem}%</b> &nbsp;|&nbsp; Avg Disk: <b>{avg_disk}%</b></p>
<table><tr><th>Timestamp</th><th>CPU</th><th>Memory</th><th>Disk</th></tr>{rows}</table>
</body></html>"""
    with open(REPORT_FILE, "w") as f:
        f.write(html)
    print(f"\n  Report saved to {REPORT_FILE}")

def main():
    print("Starting IT System Monitor... (Ctrl+C to stop)")
    history = []
    try:
        while True:
            stats = get_system_stats()
            alerts = check_alerts(stats)
            history.append(stats)
            if alerts:
                log_alerts(alerts)
            print_dashboard(stats, alerts)
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n\nStopping monitor...")
        if history:
            generate_html_report(history)

if __name__ == "__main__":
    main()
