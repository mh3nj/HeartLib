# heartlib/networking/sync_server.py
import socket
import json
import threading
from datetime import datetime

class SyncServer:
    """HeartLib sync server - runs on main library computer"""
    
    def __init__(self, crud, host='localhost', port=8765):
        self.crud = crud
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
    
    def start(self):
        """Start the sync server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"🔄 HeartLib Sync Server running on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"📱 Client connected from {address}")
                    handler = threading.Thread(target=self._handle_client, args=(client_socket, address))
                    handler.daemon = True
                    handler.start()
                except Exception as e:
                    if self.running:
                        print(f"Server accept error: {e}")
        except Exception as e:
            print(f"Failed to start server: {e}")
    
    def _handle_client(self, client_socket, address):
        """Handle a single client connection - supports multiple requests"""
        try:
            # Create a fresh database connection for this thread
            from database import DatabaseManager, CRUD
            from database.sync_engine import SyncEngine
            
            db_path = self.crud.db.db_path
            db_manager = DatabaseManager(db_path)
            crud = CRUD(db_manager)
            sync_engine = SyncEngine(crud, device_id=f"server_{address[1]}")
            
            client_socket.settimeout(30)
            
            # Keep connection alive for multiple requests
            while True:
                try:
                    data = client_socket.recv(8192).decode('utf-8')
                    if not data:
                        break
                    
                    request = json.loads(data)
                    request_type = request.get('type')
                    
                    if request_type == 'sync_pull':
                        changes = sync_engine.get_all_changes_for_sync()
                        response = {
                            'status': 'ok',
                            'type': 'sync_pull_response',
                            'changes': changes,
                            'count': len(changes)
                        }
                        client_socket.send(json.dumps(response).encode('utf-8'))
                        print(f"📤 Sent {len(changes)} changes to {address}")
                    
                    elif request_type == 'sync_push':
                        result = sync_engine.apply_remote_changes(request.get('changes', []))
                        response = {
                            'status': 'ok',
                            'type': 'sync_push_response',
                            'result': result
                        }
                        client_socket.send(json.dumps(response).encode('utf-8'))
                        print(f"📥 Applied {result['applied']} changes from {address}")
                    
                    elif request_type == 'discover':
                        response = {
                            'status': 'ok',
                            'type': 'discovery_response',
                            'server_name': socket.gethostname(),
                            'version': '2.0'
                        }
                        client_socket.send(json.dumps(response).encode('utf-8'))
                        print(f"🔍 Discovery from {address}")
                    
                    elif request_type == 'sync_full':
                        # Full sync in one request - both push and pull
                        # First apply client changes
                        push_result = sync_engine.apply_remote_changes(request.get('changes', []))
                        # Then get server changes
                        server_changes = sync_engine.get_all_changes_for_sync()
                        response = {
                            'status': 'ok',
                            'type': 'sync_full_response',
                            'push_result': push_result,
                            'changes': server_changes,
                            'count': len(server_changes)
                        }
                        client_socket.send(json.dumps(response).encode('utf-8'))
                        print(f"🔄 Full sync completed with {address}")
                        print(f"   Applied client changes: {push_result['applied']}")
                        print(f"   Sending server changes: {len(server_changes)}")
                    
                    else:
                        response = {'status': 'error', 'message': f'Unknown request type: {request_type}'}
                        client_socket.send(json.dumps(response).encode('utf-8'))
                
                except socket.timeout:
                    break
                except json.JSONDecodeError:
                    break
                except Exception as e:
                    print(f"Error processing request: {e}")
                    break
                    
        except Exception as e:
            print(f"Error handling {address}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def stop(self):
        """Stop the sync server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print("🔄 Sync Server stopped")