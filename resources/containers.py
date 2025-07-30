import threading
from typing import List, Dict, Any, Optional, Callable
from gi.repository import GLib

from core.resource_manager import ResourceManager
from core.base_operations import BaseOperations


class ContainerManager(ResourceManager):
    def __init__(self, docker_api, notification_service=None, cache_ttl: int = 15):
        super().__init__(docker_api, cache_ttl)
        self.notification_service = notification_service
        self.resource_type = "containers"
        self.containers = []
        self.filtered_containers = []
        
    def _load_resources(self):
        self.containers = self.docker_api.get_containers()
        self.resources = self.containers  # Synchronize with the base class
        self.filtered_containers = self.containers.copy()
        self.filtered_resources = self.filtered_containers  # Synchronize with the base class
    
    def _get_resource_id(self, resource: Dict[str, Any]) -> str:
        return resource.get('Id', '')
    
    def _resource_matches_search(self, resource: Dict[str, Any], query: str) -> bool:
        query = query.lower()
        return (
            query in resource.get('Names', [''])[0].lower() or
            query in resource.get('Image', '').lower() or
            query in resource.get('Status', '').lower() or
            query in resource.get('Id', '')[:12].lower()
        )
    
    def _resource_matches_filters(self, resource: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        # Filter by status
        if 'status' in filters and filters['status']:
            status_filter = filters['status'].lower()
            if status_filter not in resource.get('Status', '').lower():
                return False
        
        # Filter by image
        if 'image' in filters and filters['image']:
            image_filter = filters['image'].lower()
            if image_filter not in resource.get('Image', '').lower():
                return False
        
        return True
    
    def _perform_delete(self, resource_id: str):
        """Perform container deletion."""
        self.docker_api.delete_container(resource_id, force=True)
    
    def refresh(self, callback: Optional[Callable] = None, force: bool = False):
        """Refresh container data.

        Args:
            callback: Callback function to notify upon completion
            force: Force refresh, ignoring the cache
        """
        if callback:
            self.add_callback(lambda event_type, data: callback() if event_type == 'loading_complete' else None)
        
        super().refresh(force=force)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search containers by query.
        
        Args:
            query: Search query
            
        Returns:
            List of filtered containers
        """
        super().search(query)
        return self.get_filtered_resources()
    
    def filter(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter containers by criteria.
        
        Args:
            filters: Dictionary with filtering criteria
            
        Returns:
            List of filtered containers
        """
        super().filter(filters)
        return self.get_filtered_resources()
    
    def get_container(self, container_id: str) -> Optional[Dict[str, Any]]:
        """
        Get container by ID.
        
        Args:
            container_id: Container ID
            
        Returns:
            Container or None if not found
        """
        return self.get_resource(container_id)
    
    def start_container(self, container_id: str, callback: Optional[Callable] = None):
        """
        Start container.
        
        Args:
            container_id: Container ID
            callback: Callback function
        """
        def _start():
            try:
                self.docker_api.start_container(container_id)
                if self.notification_service:
                    self.notification_service.show_success("Контейнер запущен")
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'start', container_id, callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка запуска контейнера: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'start', container_id, str(e), callback)
        
        thread = threading.Thread(target=_start, daemon=True)
        thread.start()
    
    def stop_container(self, container_id: str, callback: Optional[Callable] = None):
        """
        Stop container.
        
        Args:
            container_id: Container ID
            callback: Callback function
        """
        def _stop():
            try:
                self.docker_api.stop_container(container_id)
                if self.notification_service:
                    self.notification_service.show_success("Контейнер остановлен")
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'stop', container_id, callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка остановки контейнера: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'stop', container_id, str(e), callback)
        
        thread = threading.Thread(target=_stop, daemon=True)
        thread.start()
    
    def restart_container(self, container_id: str, callback: Optional[Callable] = None):
        """
        Restart container.
        
        Args:
            container_id: Container ID
            callback: Callback function
        """
        def _restart():
            try:
                self.docker_api.restart_container(container_id)
                if self.notification_service:
                    self.notification_service.show_success("Контейнер перезапущен")
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'restart', container_id, callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка перезапуска контейнера: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'restart', container_id, str(e), callback)
        
        thread = threading.Thread(target=_restart, daemon=True)
        thread.start()
    
    def delete_container(self, container_id: str, force: bool = False, callback: Optional[Callable] = None):
        """
        Delete container.
        
        Args:
            container_id: Container ID
            force: Force deletion
            callback: Callback function
        """
        def _delete():
            try:
                self.docker_api.delete_container(container_id, force=force)
                if self.notification_service:
                    self.notification_service.show_success("Контейнер удален")
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'delete', container_id, callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка удаления контейнера: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'delete', container_id, str(e), callback)
        
        thread = threading.Thread(target=_delete, daemon=True)
        thread.start()
    
    def _on_operation_complete(self, operation: str, container_id: str, callback: Optional[Callable]):
        """Handler for the completion of the operation."""
        if callback:
            callback()
        self.refresh(force=True)  # Force update after the operation
    
    def _on_operation_error(self, operation: str, container_id: str, error: str, callback: Optional[Callable]):
        """Handler for the error of the operation."""
        if callback:
            callback()
        print(f"Error in {operation} operation for container {container_id}: {error}")
    
    def get_container_logs(self, container_id: str, tail: int = 100) -> str:
        """
        Get container logs.
        
        Args:
            container_id: Container ID
            tail: Number of last lines
            
        Returns:
            Container logs
        """
        try:
            return self.docker_api.get_container_logs(container_id, tail=tail)
        except Exception as e:
            print(f"Error getting container logs: {e}")
            return f"Ошибка получения логов: {str(e)}"
    
    def get_container_stats(self, container_id: str) -> Dict[str, Any]:
        """
        Get container statistics.
        
        Args:
            container_id: Container ID
            
        Returns:
            Container statistics
        """
        try:
            return self.docker_api.get_container_stats(container_id)
        except Exception as e:
            print(f"Error getting container stats: {e}")
            return {}
    
    def format_container_data(self, container: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format container data for display.
        
        Args:
            container: Raw container data
            
        Returns:
            Formatted container data
        """
        formatted = container.copy()
        
        # Format the name
        names = container.get('Names', [])
        if names:
            formatted['display_name'] = names[0].lstrip('/')
        else:
            formatted['display_name'] = container.get('Id', '')[:12]
        
        # Format the status
        status = container.get('Status', '')
        formatted['status_display'] = status
        formatted['status_color'] = BaseOperations.get_status_color(status)
        
        # Format the image
        image = container.get('Image', '')
        formatted['image_display'] = image
        
        # Format the ports
        ports = container.get('Ports', [])
        if ports:
            formatted['ports_display'] = ', '.join([p.get('PublicPort', '') for p in ports if p.get('PublicPort')])
        else:
            formatted['ports_display'] = 'Нет'
        
        # Format the size
        size_rw = container.get('SizeRw', 0)
        formatted['size_display'] = BaseOperations.format_size(size_rw)
        
        # Format the creation date
        created = container.get('Created', 0)
        formatted['created_display'] = BaseOperations.format_date(created)
        
        return formatted
    
    def get_all_containers_formatted(self) -> List[Dict[str, Any]]:
        """
        Get all containers in formatted view.
        
        Returns:
            List of formatted containers
        """
        return [self.format_container_data(container) for container in self.get_filtered_resources()]
    
    def get_running_containers_count(self) -> int:
        """
        Get the number of running containers.
        
        Returns:
            Number of running containers
        """
        return len([c for c in self.resources if 'Up' in c.get('Status', '')])
    
    def get_stopped_containers_count(self) -> int:
        """
        Get the number of stopped containers.
        
        Returns:
            Number of stopped containers
        """
        return len([c for c in self.resources if 'Exited' in c.get('Status', '')])
    
    def get_total_containers_count(self) -> int:
        """
        Get the total number of containers.
        
        Returns:
            Total number of containers
        """
        return len(self.resources)
