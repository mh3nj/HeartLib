# heartlib/networking/sync_client.py
import socket
import json
from datetime import datetime

class SyncClient:
    """HeartLib sync client - runs on satellite devices"""
    
    def __init__(self, crud, server_host='localhost', server_port=8765):
        self.crud = crud
        self.server_host = server_host
        self.server_port = server_port
    
    def _create_sync_engine(self):
        """Create a sync engine with its own DB connection"""
        from database import DatabaseManager, CRUD
        from database.sync_engine import SyncEngine
        
        db_path = self.crud.db.db_path
        db_manager = DatabaseManager(db_path)
        crud = CRUD(db_manager)
        return SyncEngine(crud, device_id=f"client_{id(self)}")
    
    def sync(self):
        """Perform full sync with server - single request/response"""
        print(f"🔄 Syncing with {self.server_host}:{self.server_port}")
        
        sock = None
        try:
            # Create sync engine with its own connection
            sync_engine = self._create_sync_engine()
            
            # Connect to server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect((self.server_host, self.server_port))
            
            # Get local unsynced changes
            local_changes = sync_engine.get_unsynced_changes()
            print(f"📤 Sending {len(local_changes)} local changes to server")
            
            # Send full sync request (push + pull in one)
            sync_request = {
                'type': 'sync_full',
                'changes': local_changes,
                'client_id': id(self),
                'timestamp': datetime.now().timestamp()
            }
            sock.send(json.dumps(sync_request).encode('utf-8'))
            
            # Receive response
            response_data = sock.recv(8192).decode('utf-8')
            response = json.loads(response_data)
            
            if response.get('status') == 'ok' and response.get('type') == 'sync_full_response':
                # Check push result
                push_result = response.get('push_result', {})
                print(f"   Server applied {push_result.get('applied', 0)} of our changes")
                
                # Apply server changes locally
                remote_changes = response.get('changes', [])
                print(f"📥 Receiving {len(remote_changes)} changes from server")
                
                if remote_changes:
                    result = sync_engine.apply_remote_changes(remote_changes)
                    print(f"   Applied {result['applied']} changes locally")
                    if result['conflicts'] > 0:
                        print(f"   ⚠️ {result['conflicts']} conflicts detected")
                
                # Mark our changes as synced
                if local_changes:
                    change_ids = [c['id'] for c in local_changes]
                    sync_engine.mark_synced(change_ids)
                
                print("✅ Sync complete!")
                return True
            else:
                print(f"❌ Server error: {response.get('message', 'Unknown error')}")
                return False
            
        except ConnectionRefusedError:
            print("❌ Connection refused - is the server running?")
            return False
        except socket.timeout:
            print("❌ Sync timeout")
            return False
        except Exception as e:
            print(f"❌ Sync failed: {e}")
            return False
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass