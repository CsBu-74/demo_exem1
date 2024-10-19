from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
import psutil


from security import authorize
app = FastAPI()


# Пример API для получения информации о CPU с авторизацией
@app.get("/cpu")
def get_cpu_info(username: str = Depends(authorize)):
    cpu_info = {
        "cpu_percent": psutil.cpu_percent(interval=1, percpu=True),
        "cpu_count": psutil.cpu_count(logical=True),
        "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
    }
    return cpu_info

# Пример API для получения информации о RAM с авторизацией
@app.get("/memory")
def get_memory_info(username: str = Depends(authorize)):
    memory = psutil.virtual_memory()
    memory_info = {
        "total": memory.total,
        "used": memory.used,
        "available": memory.available,
        "percent": memory.percent
    }
    return memory_info

# Пример API для информации о дисках с авторизацией
@app.get("/disk")
def get_disk_info(username: str = Depends(authorize)):
    disk_partitions = psutil.disk_partitions()
    disk_info = {}
    for partition in disk_partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info[partition.device] = {
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent
            }
        except PermissionError:
            disk_info[partition.device] = "Доступ запрещён"
    return disk_info

# Пример API для информации о сети с авторизацией
@app.get("/network")
def get_network_info(username: str = Depends(authorize)):
    net_io = psutil.net_io_counters()
    network_info = {
        "bytes_sent": net_io.bytes_sent,
        "bytes_recv": net_io.bytes_recv,
        "packets_sent": net_io.packets_sent,
        "packets_recv": net_io.packets_recv,
    }
    return network_info

# Общая сводка состояния системы с авторизацией
@app.get("/summary")
def get_system_summary(username: str = Depends(authorize)):
    summary = {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "network": psutil.net_io_counters()._asdict()
    }
    return summary

# API для перенаправления на дашборд
@app.get("/dashboard")
def get_dashboard_link(username: str = Depends(authorize)):
    return RedirectResponse(url="http://127.0.0.1:8050")


# Запускаем сервер FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
