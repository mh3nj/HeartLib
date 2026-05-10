# heartlib/networking/discovery.py
import socket
import json
import threading

class NetworkDiscovery:
    """Discover HeartLib servers on local network"""
    
    def __init__(self, port=8765, timeout=3):
        self.port = port
        self.timeout = timeout
        self.found_servers = []
    
    def discover(self):
        """Discover HeartLib servers on network"""
        self.found_servers = []
        
        # Create broadcast socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(self.timeout)
        
        # Send discovery broadcast
        discovery_msg = json.dumps({'type': 'discover'})
        
        try:
            sock.sendto(discovery_msg.encode(), ('<broadcast>', self.port))
            print(f"🔍 Sending discovery broadcast on port {self.port}")
            
            # Listen for responses
            start_time = threading.current_thread()
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    response = json.loads(data.decode())
                    if response.get('type') == 'discovery_response':
                        server_info = {
                            'ip': addr[0],
                            'port': addr[1],
                            'name': response.get('server_name', 'Unknown'),
                            'version': response.get('version', 'unknown')
                        }
                        if server_info not in self.found_servers:
                            self.found_servers.append(server_info)
                            print(f"   Found server: {server_info['name']} at {server_info['ip']}")
                except socket.timeout:
                    break
        except Exception as e:
            print(f"Discovery error: {e}")
        finally:
            sock.close()
        
        return self.found_servers
    
    def get_first_server(self):
        """Get first discovered server IP"""
        if self.found_servers:
            return self.found_servers[0]['ip']
        return None
    
    def get_servers(self):
        """Get all discovered servers"""
        return self.found_servers
