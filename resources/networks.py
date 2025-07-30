import threading
from typing import List, Dict, Any, Optional, Callable
from gi.repository import GLib

from core.resource_manager import ResourceManager
from core.base_operations import BaseOperations


class NetworkManager(ResourceManager):
    def __init__(self, docker_api, notification_service=None, cache_ttl: int = 120):
        super().__init__(docker_api, cache_ttl)
        self.notification_service = notification_service
        self.resource_type = "networks"
        self.networks = []
        self.filtered_networks = []
        
    def _load_resources(self):
        """Load networks from the Docker API."""
        self.networks = self.docker_api.get_networks()
        self.resources = self.networks  # Synchronize with the base class
        self.filtered_networks = self.networks.copy()
        self.filtered_resources = self.filtered_networks  # Synchronize with the base class
    
    def _get_resource_id(self, resource: Dict[str, Any]) -> str:
        """Get the ID of the network."""
        return resource.get('Id', '')
    
    def _resource_matches_search(self, resource: Dict[str, Any], query: str) -> bool:
        """Check if the network matches the search query."""
        query = query.lower()
        return (
            query in resource.get('Name', '').lower() or
            query in resource.get('Driver', '').lower() or
            query in resource.get('Scope', '').lower() or
            query in resource.get('Id', '')[:12].lower()
        )
    
    def _resource_matches_filters(self, resource: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if the network matches the filters."""
        # Filter by driver
        if 'driver' in filters and filters['driver']:
            driver_filter = filters['driver'].lower()
            if driver_filter not in resource.get('Driver', '').lower():
                return False
        
        # Filter by scope
        if 'scope' in filters and filters['scope']:
            scope_filter = filters['scope'].lower()
            if scope_filter not in resource.get('Scope', '').lower():
                return False
        
        # Filter by type
        if 'type' in filters and filters['type']:
            type_filter = filters['type'].lower()
            if type_filter == 'builtin' and not resource.get('Internal', False):
                return False
            elif type_filter == 'custom' and resource.get('Internal', False):
                return False
        
        return True
    
    def _perform_delete(self, resource_id: str):
        """Perform network deletion."""
        self.docker_api.delete_network(resource_id)
    
    def refresh(self, callback: Optional[Callable] = None, force: bool = False):
        """Refresh network data.
        
        Args:
            callback: Callback function to notify upon completion
            force: Force refresh, ignoring the cache
        """
        if callback:
            self.add_callback(lambda event_type, data: callback() if event_type == 'loading_complete' else None)
        
        super().refresh(force=force)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search networks by query.
        
        Args:
            query: Search query
            
        Returns:
            List of filtered networks
        """
        super().search(query)
        return self.get_filtered_resources()
    
    def filter(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter networks by criteria.
        
        Args:
            filters: Dictionary with filtering criteria
            
        Returns:
            List of filtered networks
        """
        super().filter(filters)
        return self.get_filtered_resources()
    
    def get_network(self, network_id: str) -> Optional[Dict[str, Any]]:
        """
        Get network by ID.
        
        Args:
            network_id: Network ID
            
        Returns:
            Network or None if not found
        """
        return self.get_resource(network_id)
    
    def create_network(self, name: str, driver: str = "bridge", subnet: str = None, callback: Optional[Callable] = None):
        """
        Create network.
        
        Args:
            name: Name of the network
            driver: Network driver
            subnet: Subnet
            callback: Callback function
        """
        def _create():
            try:
                config = {
                    'Name': name,
                    'Driver': driver
                }
                if subnet:
                    config['IPAM'] = {
                        'Config': [{'Subnet': subnet}]
                    }
                
                self.docker_api.create_network(config)
                if self.notification_service:
                    self.notification_service.show_success(f"Сеть {name} создана")
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'create', name, callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка создания сети: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'create', name, str(e), callback)
        
        thread = threading.Thread(target=_create, daemon=True)
        thread.start()
    
    def delete_network(self, network_id: str, callback: Optional[Callable] = None):
        """
        Delete network.
        
        Args:
            network_id: Network ID
            callback: Callback function
        """
        def _delete():
            try:
                self.docker_api.delete_network(network_id)
                if self.notification_service:
                    self.notification_service.show_success("Сеть удалена")
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'delete', network_id, callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка удаления сети: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'delete', network_id, str(e), callback)
        
        thread = threading.Thread(target=_delete, daemon=True)
        thread.start()
    
    def connect_container(self, network_id: str, container_id: str, callback: Optional[Callable] = None):
        """
        Connect container to network.
        
        Args:
            network_id: Network ID
            container_id: Container ID
            callback: Callback function
        """
        def _connect():
            try:
                self.docker_api.connect_container_to_network(network_id, container_id)
                if self.notification_service:
                    self.notification_service.show_success("Контейнер подключен к сети")
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'connect', f"{network_id}:{container_id}", callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка подключения контейнера: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'connect', f"{network_id}:{container_id}", str(e), callback)
        
        thread = threading.Thread(target=_connect, daemon=True)
        thread.start()
    
    def disconnect_container(self, network_id: str, container_id: str, callback: Optional[Callable] = None):
        """
        Disconnect container from network.
        
        Args:
            network_id: Network ID
            container_id: Container ID
            callback: Callback function
        """
        def _disconnect():
            try:
                self.docker_api.disconnect_container_from_network(network_id, container_id)
                if self.notification_service:
                    self.notification_service.show_success("Контейнер отключен от сети")
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'disconnect', f"{network_id}:{container_id}", callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка отключения контейнера: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'disconnect', f"{network_id}:{container_id}", str(e), callback)
        
        thread = threading.Thread(target=_disconnect, daemon=True)
        thread.start()
    
    def _on_operation_complete(self, operation: str, network_id: str, callback: Optional[Callable]):
        """Handler for the completion of the operation."""
        if callback:
            callback()
        self.refresh(force=True)  # Force update after the operation
    
    def _on_operation_error(self, operation: str, network_id: str, error: str, callback: Optional[Callable]):
        """Handler for the error of the operation."""
        if callback:
            callback()
        print(f"Error in {operation} operation for network {network_id}: {error}")
    
    def format_network_data(self, network: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format network data for display.
        
        Args:
            network: Raw network data
            
        Returns:
            Formatted network data
        """
        formatted = network.copy()
        
        # Format the name
        formatted['display_name'] = network.get('Name', '')
        
        # Format the driver
        formatted['driver_display'] = network.get('Driver', '')
        
        # Format the scope
        formatted['scope_display'] = network.get('Scope', '')
        
        # Format the subnets
        ipam_config = network.get('IPAM', {}).get('Config', [])
        if ipam_config:
            subnets = [config.get('Subnet', '') for config in ipam_config if config.get('Subnet')]
            formatted['subnets_display'] = ', '.join(subnets)
        else:
            formatted['subnets_display'] = 'Нет'
        
        # Format the gateways
        if ipam_config:
            gateways = [config.get('Gateway', '') for config in ipam_config if config.get('Gateway')]
            formatted['gateways_display'] = ', '.join(gateways)
        else:
            formatted['gateways_display'] = 'Нет'
        
        # Format the creation date
        created = network.get('Created', '')
        formatted['created_display'] = BaseOperations.format_date(created)
        
        # Short ID
        formatted['short_id'] = network.get('Id', '')[:12]
        
        # Type of network
        if network.get('Internal', False):
            formatted['type_display'] = 'Внутренняя'
        else:
            formatted['type_display'] = 'Внешняя'
        
        # Number of connected containers
        containers = network.get('Containers', {})
        formatted['containers_count'] = len(containers)
        
        return formatted
    
    def get_all_networks_formatted(self) -> List[Dict[str, Any]]:
        """
        Get all networks in formatted view.
        
        Returns:
            List of formatted networks
        """
        return [self.format_network_data(network) for network in self.get_filtered_resources()]
    
    def get_total_networks_count(self) -> int:
        """
        Get the total number of networks.
        
        Returns:
            Total number of networks
        """
        return len(self.resources)
    
    def get_builtin_networks_count(self) -> int:
        """
        Get the number of built-in networks.
        
        Returns:
            Number of built-in networks
        """
        return len([net for net in self.resources if net.get('Internal', False)])
    
    def get_custom_networks_count(self) -> int:
        """
        Get the number of custom networks.
        
        Returns:
            Number of custom networks
        """
        return len([net for net in self.resources if not net.get('Internal', False)])
    
    def get_networks_by_driver(self, driver: str) -> List[Dict[str, Any]]:
        """
        Get networks by driver.
        
        Args:
            driver: Network driver
            
        Returns:
            List of networks with the specified driver
        """
        return [net for net in self.resources if net.get('Driver', '') == driver]
