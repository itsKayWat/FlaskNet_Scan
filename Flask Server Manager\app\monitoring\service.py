from typing import Dict, List, Optional
import psutil
import os
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
import docker
from prometheus_client import Counter, Gauge, Histogram
import logging
from threading import Lock

@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_usage: Dict[str, float]
    network_io: Dict[str, Dict[str, int]]
    process_count: int
    load_average: List[float]

class MonitoringService:
    def __init__(self, app):
        self.app = app
        self.docker_client = docker.from_env()
        self._setup_metrics()
        self._cache = {}
        self._cache_lock = Lock()
        self._setup_logging()

    def _setup_metrics(self):
        """Initialize Prometheus metrics."""
        self.cpu_gauge = Gauge('system_cpu_usage', 'CPU usage percentage')
        self.memory_gauge = Gauge('system_memory_usage', 'Memory usage percentage')
        self.disk_gauge = Gauge('system_disk_usage', 'Disk usage percentage')
        self.request_counter = Counter('http_requests_total', 'Total HTTP requests')
        self.response_time_histogram = Histogram(
            'http_response_time_seconds',
            'HTTP response time in seconds'
        )

    def _setup_logging(self):
        """Setup monitoring logger."""
        self.logger = logging.getLogger('monitoring')
        handler = logging.FileHandler('logs/monitoring.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        with self._cache_lock:
            cache_key = 'system_metrics'
            cached = self._cache.get(cache_key)
            
            if cached and time.time() - cached['timestamp'] < 5:
                return cached['data']

            metrics = SystemMetrics(
                cpu_percent=psutil.cpu_percent(interval=1),
                memory_percent=psutil.virtual_memory().percent,
                disk_usage=self._get_disk_usage(),
                network_io=self._get_network_io(),
                process_count=len(psutil.pids()),
                load_average=os.getloadavg()
            )

            self._update_prometheus_metrics(metrics)
            self._cache[cache_key] = {
                'timestamp': time.time(),
                'data': metrics
            }

            return metrics

    def _get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage for all mounted partitions."""
        usage = {}
        for partition in psutil.disk_partitions():
            try:
                usage[partition.mountpoint] = psutil.disk_usage(
                    partition.mountpoint
                ).percent
            except PermissionError:
                continue
        return usage

    def _get_network_io(self) -> Dict[str, Dict[str, int]]:
        """Get network I/O statistics."""
        return {
            nic: stats._asdict()
            for nic, stats in psutil.net_io_counters(pernic=True).items()
        }

    def _update_prometheus_metrics(self, metrics: SystemMetrics):
        """Update Prometheus metrics."""
        self.cpu_gauge.set(metrics.cpu_percent)
        self.memory_gauge.set(metrics.memory_percent)
        self.disk_gauge.set(metrics.disk_usage.get('/', 0))

    def get_docker_metrics(self) -> List[Dict]:
        """Get metrics for all running Docker containers."""
        metrics = []
        for container in self.docker_client.containers.list():
            try:
                stats = container.stats(stream=False)
                metrics.append({
                    'id': container.id[:12],
                    'name': container.name,
                    'cpu': self._calculate_cpu_percent(stats),
                    'memory': self._calculate_memory_percent(stats),
                    'network': stats['networks'],
                    'status': container.status
                })
            except Exception as e:
                self.logger.error(f"Error getting container stats: {e}")
        return metrics

    def _calculate_cpu_percent(self, stats: Dict) -> float:
        """Calculate CPU percentage from Docker stats."""
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                   stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                      stats['precpu_stats']['system_cpu_usage']
        if system_delta > 0:
            return (cpu_delta / system_delta) * 100.0
        return 0.0

    def _calculate_memory_percent(self, stats: Dict) -> float:
        """Calculate memory percentage from Docker stats."""
        usage = stats['memory_stats']['usage']
        limit = stats['memory_stats']['limit']
        return (usage / limit) * 100.0

    def get_process_metrics(self, pid: Optional[int] = None) -> Dict:
        """Get detailed process metrics."""
        if pid:
            try:
                process = psutil.Process(pid)
                return self._get_process_info(process)
            except psutil.NoSuchProcess:
                return {}
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(self._get_process_info(proc))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    def _get_process_info(self, process: psutil.Process) -> Dict:
        """Get detailed information about a process."""
        with process.oneshot():
            return {
                'pid': process.pid,
                'name': process.name(),
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'status': process.status(),
                'create_time': datetime.fromtimestamp(process.create_time()).isoformat(),
                'num_threads': process.num_threads(),
                'num_fds': process.num_fds() if os.name != 'nt' else None,
                'io_counters': process.io_counters()._asdict() if process.io_counters() else None
            } 