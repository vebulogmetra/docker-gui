import threading
from typing import List, Dict, Any, Optional, Callable
from gi.repository import GLib

from core.resource_manager import ResourceManager
from core.base_operations import BaseOperations


class VolumeManager(ResourceManager):
    def __init__(self, docker_api, notification_service=None, cache_ttl: int = 120):
        super().__init__(docker_api, cache_ttl)
        self.notification_service = notification_service
        self.resource_type = "volumes"
        self.volumes = []
        self.filtered_volumes = []
        
    def _load_resources(self):
        """Load volumes from the Docker API."""
        self.volumes = self.docker_api.get_volumes()
        self.resources = self.volumes  # Synchronize with the base class
        self.filtered_volumes = self.volumes.copy()
        self.filtered_resources = self.filtered_volumes  # Synchronize with the base class
    
    def _get_resource_id(self, resource: Dict[str, Any]) -> str:
        """Get the ID of the volume."""
        return resource.get('Name', '')
    
    def _resource_matches_search(self, resource: Dict[str, Any], query: str) -> bool:
        """Check if the volume matches the search query."""
        query = query.lower()
        return (
            query in resource.get('Name', '').lower() or
            query in resource.get('Driver', '').lower() or
            query in resource.get('Mountpoint', '').lower()
        )
    
    def _resource_matches_filters(self, resource: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if the volume matches the filters."""
        # Filter by driver
        if 'driver' in filters and filters['driver']:
            driver_filter = filters['driver'].lower()
            if driver_filter not in resource.get('Driver', '').lower():
                return False
        
        # Filter by status
        if 'status' in filters and filters['status']:
            status_filter = filters['status'].lower()
            if status_filter == 'used' and not resource.get('UsageData', {}).get('RefCount', 0):
                return False
            elif status_filter == 'unused' and resource.get('UsageData', {}).get('RefCount', 0):
                return False
        
        # Filter by type
        if 'type' in filters and filters['type']:
            type_filter = filters['type'].lower()
            if type_filter == 'local' and resource.get('Driver', '') != 'local':
                return False
            elif type_filter == 'remote' and resource.get('Driver', '') == 'local':
                return False
        
        return True
    
    def _perform_delete(self, resource_id: str):
        """Perform volume deletion."""
        self.docker_api.delete_volume(resource_id, force=True)
    
    def refresh(self, callback: Optional[Callable] = None, force: bool = False):
        """Refresh volume data.
        
        Args:
            callback: Callback function to notify upon completion
            force: Force refresh, ignoring the cache
        """
        if callback:
            self.add_callback(lambda event_type, data: callback() if event_type == 'loading_complete' else None)
        
        super().refresh(force=force)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search volumes by query.
        
        Args:
            query: Search query
            
        Returns:
            List of filtered volumes
        """
        super().search(query)
        return self.get_filtered_resources()
    
    def filter(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter volumes by criteria.
        
        Args:
            filters: Dictionary with filtering criteria
            
        Returns:
            List of filtered volumes
        """
        super().filter(filters)
        return self.get_filtered_resources()
    
    def get_volume(self, volume_name: str) -> Optional[Dict[str, Any]]:
        """
        Get volume by name.
        
        Args:
            volume_name: Volume name
            
        Returns:
            Volume or None if not found
        """
        return self.get_resource(volume_name)
    
    def create_volume(self, name: str, driver: str = "local", options: Dict[str, str] = None, callback: Optional[Callable] = None):
        """
        Create volume.
        
        Args:
            name: Volume name
            driver: Volume driver
            options: Additional options
            callback: Callback function
        """
        def _create():
            try:
                config = {
                    'Name': name,
                    'Driver': driver
                }
                if options:
                    config['DriverOpts'] = options
                
                self.docker_api.create_volume(config)
                if self.notification_service:
                    self.notification_service.show_success(f"Том {name} создан")
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'create', name, callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка создания тома: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'create', name, str(e), callback)
        
        thread = threading.Thread(target=_create, daemon=True)
        thread.start()
    
    def delete_volume(self, volume_name: str, force: bool = False, callback: Optional[Callable] = None):
        """
        Delete volume.
        
        Args:
            volume_name: Volume name
            force: Force deletion
            callback: Callback function
        """
        def _delete():
            try:
                self.docker_api.delete_volume(volume_name, force=force)
                if self.notification_service:
                    self.notification_service.show_success("Том удален")
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'delete', volume_name, callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка удаления тома: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'delete', volume_name, str(e), callback)
        
        thread = threading.Thread(target=_delete, daemon=True)
        thread.start()
    
    def inspect_volume(self, volume_name: str) -> Dict[str, Any]:
        """
        Inspect volume.
        
        Args:
            volume_name: Volume name
            
        Returns:
            Detailed information about the volume
        """
        try:
            return self.docker_api.inspect_volume(volume_name)
        except Exception as e:
            print(f"Error inspecting volume {volume_name}: {e}")
            return {}
    
    def prune_volumes(self, callback: Optional[Callable] = None):
        """
        Prune unused volumes.
        
        Args:
            callback: Callback function
        """
        def _prune():
            try:
                result = self.docker_api.prune_volumes()
                if self.notification_service:
                    deleted_count = len(result.get('VolumesDeleted', []))
                    freed_space = result.get('SpaceReclaimed', 0)
                    self.notification_service.show_success(
                        f"Удалено {deleted_count} томов, освобождено {BaseOperations.format_size(freed_space)}"
                    )
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'prune', 'volumes', callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка очистки томов: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'prune', 'volumes', str(e), callback)
        
        thread = threading.Thread(target=_prune, daemon=True)
        thread.start()
    
    def _on_operation_complete(self, operation: str, volume_name: str, callback: Optional[Callable]):
        """Handler for the completion of the operation."""
        if callback:
            callback()
        self.refresh(force=True)  # Force update after the operation
    
    def _on_operation_error(self, operation: str, volume_name: str, error: str, callback: Optional[Callable]):
        """Handler for the error of the operation."""
        if callback:
            callback()
        print(f"Error in {operation} operation for volume {volume_name}: {error}")
    
    def format_volume_data(self, volume: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format volume data for display.
        
        Args:
            volume: Raw volume data
            
        Returns:
            Formatted volume data
        """
        formatted = volume.copy()
        
        # Format the name
        formatted['display_name'] = volume.get('Name', '')
        
        # Format the driver
        formatted['driver_display'] = volume.get('Driver', '')
        
        # Format the mountpoint
        formatted['mountpoint_display'] = volume.get('Mountpoint', '')
        
        # Format the size
        usage_data = volume.get('UsageData', {})
        size = usage_data.get('Size', 0)
        formatted['size_display'] = BaseOperations.format_size(size)
        
        # Format the creation date
        created = volume.get('CreatedAt', '')
        formatted['created_display'] = BaseOperations.format_date(created)
        
        # Usage status
        ref_count = usage_data.get('RefCount', 0)
        if ref_count > 0:
            formatted['status_display'] = f"Используется ({ref_count})"
            formatted['status_color'] = "success"
        else:
            formatted['status_display'] = "Не используется"
            formatted['status_color'] = "warning"
        
        # Volume type
        driver = volume.get('Driver', '')
        if driver == 'local':
            formatted['type_display'] = 'Локальный'
        else:
            formatted['type_display'] = 'Удаленный'
        
        # Options
        options = volume.get('Options', {})
        if options:
            formatted['options_display'] = ', '.join([f"{k}={v}" for k, v in options.items()])
        else:
            formatted['options_display'] = 'Нет'
        
        return formatted
    
    def get_all_volumes_formatted(self) -> List[Dict[str, Any]]:
        """
        Get all volumes in formatted view.
        
        Returns:
            List of formatted volumes
        """
        return [self.format_volume_data(volume) for volume in self.get_filtered_resources()]
    
    def get_total_volumes_count(self) -> int:
        """
        Get the total number of volumes.
        
        Returns:
            Total number of volumes
        """
        return len(self.resources)
    
    def get_used_volumes_count(self) -> int:
        """
        Get the number of used volumes.
        
        Returns:
            Number of used volumes
        """
        return len([vol for vol in self.resources if vol.get('UsageData', {}).get('RefCount', 0) > 0])
    
    def get_unused_volumes_count(self) -> int:
        """
        Get the number of unused volumes.
        
        Returns:
            Number of unused volumes
        """
        return len([vol for vol in self.resources if vol.get('UsageData', {}).get('RefCount', 0) == 0])
    
    def get_local_volumes_count(self) -> int:
        """
        Get the number of local volumes.
        
        Returns:
            Number of local volumes
        """
        return len([vol for vol in self.resources if vol.get('Driver', '') == 'local'])
    
    def get_remote_volumes_count(self) -> int:
        """
        Get the number of remote volumes.
        
        Returns:
            Number of remote volumes
        """
        return len([vol for vol in self.resources if vol.get('Driver', '') != 'local'])
    
    def get_total_size(self) -> int:
        """
        Get the total size of all volumes.
        
        Returns:
            Total size in bytes
        """
        return sum(vol.get('UsageData', {}).get('Size', 0) for vol in self.resources)
    
    def get_volumes_by_driver(self, driver: str) -> List[Dict[str, Any]]:
        """
        Get volumes by driver.
        
        Args:
            driver: Volume driver
            
        Returns:
            List of volumes with the specified driver
        """
        return [vol for vol in self.resources if vol.get('Driver', '') == driver]
