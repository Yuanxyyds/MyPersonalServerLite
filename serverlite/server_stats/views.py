from django.http import JsonResponse
import psutil
import requests

PROXMOX_API_BASE = "https://proxmox.liustev6.ca/api2/json/nodes/"
PVE_TOKEN = "PVEAPIToken=root@pam!webserver=b6f3ecea-ba83-45ff-b0b3-159031fb54eb"


def fetch_node_stats(node_name):
    url = f"{PROXMOX_API_BASE}{node_name}/status"
    headers = {
        "Content-Type": "application/json",
        "Authorization": PVE_TOKEN,
    }

    try:
        response = requests.get(url, headers=headers, verify=False, timeout=3)
        response.raise_for_status()
        data = response.json()["data"]

        # Extract memory
        total_memory_gb = data["memory"]["total"] / (1024**3)
        used_memory_gb = data["memory"]["used"] / (1024**3)
        memory_usage_percent = used_memory_gb / total_memory_gb * 100

        # Extract CPU
        cpu_cores = data["cpuinfo"]["cores"]
        cpu_cpus = data["cpuinfo"]["cpus"]
        cpu_usage_percent = data["cpu"] * 100

        stats = {
            "status": "online",
            "memory": {
                "total": round(total_memory_gb, 2),
                "used": round(used_memory_gb, 2),
                "memory_usage_percent": round(memory_usage_percent, 3),
            },
            "cpu": {
                "cores": cpu_cores,
                "cpus": cpu_cpus,
                "cpu_usage_percent": round(cpu_usage_percent, 3),
            },
        }

        # Only include temps if we're running on this node (local only)
        if node_name == "local":
            temps = psutil.sensors_temperatures()
            if "k10temp" in temps:
                stats["cpu"]["cpu_temp"] = temps["k10temp"][0].current

        return stats

    except Exception as e:
        return {"status": "offline"}


def get_server_stats(request):
    nodes = ["local", "local2"]
    result = {}

    for node in nodes:
        result[node] = fetch_node_stats(node)

    return JsonResponse(result)
