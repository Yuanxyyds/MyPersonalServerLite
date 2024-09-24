import datetime
from django.http import JsonResponse
import psutil
import requests


def get_server_stats(request):
    url = "https://proxmox.liustev6.ca/api2/json/nodes/local/status"  # Proxmox API URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": "PVEAPIToken=root@pam!webserver=b6f3ecea-ba83-45ff-b0b3-159031fb54eb",
    }

    response = requests.get(url, headers=headers, verify=False)
    print(response)

    data = response.json()["data"]

    # Extract Memory (in GB)
    total_memory_gb = data["memory"]["total"] / (1024**3)  # Convert bytes to GB
    used_memory_gb = data["memory"]["used"] / (1024**3)  # Convert bytes to GB
    memory_usage_percent = used_memory_gb / total_memory_gb  # Convert bytes to GB

    # Extract CPU Information
    cpu_cores = data["cpuinfo"]["cores"]
    cpu_cpus = data["cpuinfo"]["cpus"]
    cpu_usage_percent = data["cpu"] * 100
    temps = psutil.sensors_temperatures()
    # Return all extracted information as JSON
    return JsonResponse(
        {
            "memory": {
                "total": round(total_memory_gb, 2),
                "used": round(used_memory_gb, 2),
                "memory_usage_percent": round(memory_usage_percent, 3),
            },
            "cpu": {
                "cores": cpu_cores,
                "cpus": cpu_cpus,
                "cpu_temp": temps["k10temp"][0].current,
                "cpu_usage_percent": round(cpu_usage_percent, 3),
            },
        }
    )


def get_system_stats2(request):
    try:
        # CPU Usage (%)
        cpu_usage = psutil.cpu_percent(interval=1)

        # CPU temperature
        temps = psutil.sensors_temperatures()
        # You might need to adjust this depending on your system.
        if "coretemp" in temps:
            temp = temps["coretemp"][0].current
        else:
            temp = None

        # Memory (RAM) usage
        memory_info = psutil.virtual_memory()
        total_memory = memory_info.total / (1024**3)  # Convert to GB
        used_memory = memory_info.used / (1024**3)  # Convert to GB
        memory_percentage = memory_info.percent

        # Disk usage
        disk_info = psutil.disk_usage("/")
        total_disk = disk_info.total / (1024**3)  # Convert to GB
        used_disk = disk_info.used / (1024**3)  # Convert to GB
        disk_percentage = disk_info.percent

        return JsonResponse(
            {
                "cpu": {
                    "cpu_usage": cpu_usage,
                    "cpu_temp": temp,
                },
                "memory": {
                    "total": total_memory,
                    "used": used_memory,
                    "percent": memory_percentage,
                },
                "disk": {
                    "total": total_disk,
                    "used": used_disk,
                    "percent": disk_percentage,
                },
            },
            status=200,
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
