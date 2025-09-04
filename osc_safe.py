# osc_safe.py — tiny, safe OSC sender with lazy resolve + optional background refresh
import socket, threading, time
from pythonosc import udp_client

class OSCSafeClient:
    def __init__(self, host: str, port: int, refresh_sec: int = 0):
        """
        host: hostname or IP (IP is most reliable)
        port: UDP port
        refresh_sec: 0 = no background re-resolve; >0 = periodically re-resolve host
        """
        self.host = host
        self.port = port
        self.refresh_sec = refresh_sec
        self._client = None
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thr = None

    def _resolve(self):
        try:
            # Prefer IPv4 UDP
            info = socket.getaddrinfo(self.host, self.port, socket.AF_INET, socket.SOCK_DGRAM)
            ip, port = info[0][4]
            return ip, port
        except Exception as e:
            print(f"[OSCSafe] resolve failed for {self.host}:{self.port} -> {e}")
            return None

    def _make(self):
        tgt = self._resolve()
        if not tgt: return None
        ip, port = tgt
        try:
            c = udp_client.SimpleUDPClient(ip, port)
            print(f"[OSCSafe] ready → {ip}:{port}")
            return c
        except Exception as e:
            print(f"[OSCSafe] create client failed for {ip}:{port} -> {e}")
            return None

    def start(self):
        with self._lock:
            if self._client is None:
                self._client = self._make()
        if self.refresh_sec > 0 and (self._thr is None or not self._thr.is_alive()):
            self._thr = threading.Thread(target=self._refresher, daemon=True)
            self._thr.start()

    def _refresher(self):
        while not self._stop.is_set():
            time.sleep(self.refresh_sec)
            with self._lock:
                self._client = self._make()

    def send(self, address: str, value):
        with self._lock:
            c = self._client or self._make()
            self._client = c
        if not c:
            print(f"[OSCSafe] DROP {address}={value} (no client)")
            return False
        try:
            c.send_message(address, value)
            return True
        except Exception as e:
            print(f"[OSCSafe] send failed {address} -> {e}")
            with self._lock:
                self._client = None  # force remake next time
            return False

    def stop(self):
        self._stop.set()
