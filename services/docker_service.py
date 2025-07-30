import threading
from typing import List, Dict, Any, Optional, Callable
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib


class DockerService:
    def __init__(self, docker_api):
        self.docker_api = docker_api
        self._callbacks = []
        self._cache = {}
        self._cache_timeout = 30  # seconds
        self._last_cache_update = {}
        
    def add_callback(self, callback: Callable):
        """
        Add a callback for notifications about changes.
        
        Args:
            callback: Callback function
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """
        Remove a callback.
        
        Args:
            callback: Callback function to remove
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _notify_callbacks(self, event_type: str, data: Any = None):
        """
        Notify all registered callbacks.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        for callback in self._callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                print(f"Error in Docker service callback: {e}")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Check if the cache is valid.
        
        Args:
            cache_key: Cache key
            
        Returns:
            True if the cache is valid
        """
        if cache_key not in self._last_cache_update:
            return False
        
        import time
        current_time = time.time()
        last_update = self._last_cache_update[cache_key]
        
        return (current_time - last_update) < self._cache_timeout
    
    def _update_cache(self, cache_key: str, data: Any):
        """
        Update the cache.
        
        Args:
            cache_key: Cache key
            data: Data to cache
        """
        import time
        self._cache[cache_key] = data
        self._last_cache_update[cache_key] = time.time()
    
    def _clear_cache(self, cache_key: str = None):
        """
        Clear the cache.
        
        Args:
            cache_key: Cache key to clear (None to clear all cache)
        """
        if cache_key:
            self._cache.pop(cache_key, None)
            self._last_cache_update.pop(cache_key, None)
        else:
            self._cache.clear()
            self._last_cache_update.clear()
    
    # Methods for working with containers
    
    def get_containers(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get a list of containers.
        
        Args:
            use_cache: Use cache
            
        Returns:
            List of containers
        """
        cache_key = "containers"
        
        if use_cache and self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            containers = self.docker_api.get_containers()
            self._update_cache(cache_key, containers)
            self._notify_callbacks('containers_updated', containers)
            return containers
        except Exception as e:
            self._notify_callbacks('containers_error', str(e))
            raise
    
    def get_container(self, container_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a container.
        
        Args:
            container_id: ID of the container
            
        Returns:
            Information about the container or None
        """
        try:
            return self.docker_api.get_container(container_id)
        except Exception as e:
            self._notify_callbacks('container_error', {'id': container_id, 'error': str(e)})
            raise
    
    def start_container(self, container_id: str):
        """
        Start a container.
        
        Args:
            container_id: ID of the container
        """
        try:
            self.docker_api.start_container(container_id)
            self._clear_cache("containers")
            self._notify_callbacks('container_started', container_id)
        except Exception as e:
            self._notify_callbacks('container_start_error', {'id': container_id, 'error': str(e)})
            raise
    
    def stop_container(self, container_id: str):
        """
        Stop a container.
        
        Args:
            container_id: ID of the container
        """
        try:
            self.docker_api.stop_container(container_id)
            self._clear_cache("containers")
            self._notify_callbacks('container_stopped', container_id)
        except Exception as e:
            self._notify_callbacks('container_stop_error', {'id': container_id, 'error': str(e)})
            raise
    
    def restart_container(self, container_id: str):
        """
        Restart a container.
        
        Args:
            container_id: ID of the container
        """
        try:
            self.docker_api.restart_container(container_id)
            self._clear_cache("containers")
            self._notify_callbacks('container_restarted', container_id)
        except Exception as e:
            self._notify_callbacks('container_restart_error', {'id': container_id, 'error': str(e)})
            raise
    
    def delete_container(self, container_id: str, force: bool = False):
        """
        Delete a container.
        
        Args:
            container_id: ID of the container
            force: Force deletion
        """
        try:
            self.docker_api.delete_container(container_id, force)
            self._clear_cache("containers")
            self._notify_callbacks('container_deleted', container_id)
        except Exception as e:
            self._notify_callbacks('container_delete_error', {'id': container_id, 'error': str(e)})
            raise
    
    def get_container_logs(self, container_id: str, tail: int = 100) -> str:
        """
        Get the logs of a container.
        
        Args:
            container_id: ID of the container
            tail: Number of last lines
            
        Returns:
            Logs of the container
        """
        try:
            return self.docker_api.get_container_logs(container_id, tail)
        except Exception as e:
            self._notify_callbacks('container_logs_error', {'id': container_id, 'error': str(e)})
            raise
    
    # Methods for working with images
    
    def get_images(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get a list of images.
        
        Args:
            use_cache: Use cache
            
        Returns:
            List of images
        """
        cache_key = "images"
        
        if use_cache and self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            images = self.docker_api.get_images()
            self._update_cache(cache_key, images)
            self._notify_callbacks('images_updated', images)
            return images
        except Exception as e:
            self._notify_callbacks('images_error', str(e))
            raise
    
    def delete_image(self, image_id: str, force: bool = False):
        """
        Delete an image.
        
        Args:
            image_id: ID of the image
            force: Force deletion
        """
        try:
            self.docker_api.delete_image(image_id, force)
            self._clear_cache("images")
            self._notify_callbacks('image_deleted', image_id)
        except Exception as e:
            self._notify_callbacks('image_delete_error', {'id': image_id, 'error': str(e)})
            raise
    
    def pull_image(self, image_name: str):
        """
        Pull an image.
        
        Args:
            image_name: Name of the image
        """
        try:
            self.docker_api.pull_image(image_name)
            self._clear_cache("images")
            self._notify_callbacks('image_pulled', image_name)
        except Exception as e:
            self._notify_callbacks('image_pull_error', {'name': image_name, 'error': str(e)})
            raise
    
    # Methods for working with networks
    
    def get_networks(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get a list of networks.
        
        Args:
            use_cache: Use cache
            
        Returns:
            List of networks
        """
        cache_key = "networks"
        
        if use_cache and self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            networks = self.docker_api.get_networks()
            self._update_cache(cache_key, networks)
            self._notify_callbacks('networks_updated', networks)
            return networks
        except Exception as e:
            self._notify_callbacks('networks_error', str(e))
            raise
    
    def delete_network(self, network_id: str):
        """
        Delete a network.
        
        Args:
            network_id: ID of the network
        """
        try:
            self.docker_api.delete_network(network_id)
            self._clear_cache("networks")
            self._notify_callbacks('network_deleted', network_id)
        except Exception as e:
            self._notify_callbacks('network_delete_error', {'id': network_id, 'error': str(e)})
            raise
    
    # Methods for working with volumes
    
    def get_volumes(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get a list of volumes.
        
        Args:
            use_cache: Use cache
            
        Returns:
            List of volumes
        """
        cache_key = "volumes"
        
        if use_cache and self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            volumes = self.docker_api.get_volumes()
            self._update_cache(cache_key, volumes)
            self._notify_callbacks('volumes_updated', volumes)
            return volumes
        except Exception as e:
            self._notify_callbacks('volumes_error', str(e))
            raise
    
    def delete_volume(self, volume_name: str):
        """
        Delete a volume.
        
        Args:
            volume_name: Name of the volume
        """
        try:
            self.docker_api.delete_volume(volume_name)
            self._clear_cache("volumes")
            self._notify_callbacks('volume_deleted', volume_name)
        except Exception as e:
            self._notify_callbacks('volume_delete_error', {'name': volume_name, 'error': str(e)})
            raise
    
    # Methods for working with the system
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about the Docker system.
        
        Returns:
            Information about the system
        """
        try:
            return self.docker_api.get_system_info()
        except Exception as e:
            self._notify_callbacks('system_info_error', str(e))
            raise
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """
        Get information about the disk usage.
        
        Returns:
            Information about the disk usage
        """
        try:
            return self.docker_api.get_disk_usage()
        except Exception as e:
            self._notify_callbacks('disk_usage_error', str(e))
            raise
    
    def prune_system(self, prune_type: str = "all"):
        """
        Clean up unused resources.
        
        Args:
            prune_type: Type of cleanup ("all", "containers", "images", "networks", "volumes")
        """
        try:
            if prune_type == "all":
                self.docker_api.prune_all()
            elif prune_type == "containers":
                self.docker_api.prune_containers()
            elif prune_type == "images":
                self.docker_api.prune_images()
            elif prune_type == "networks":
                self.docker_api.prune_networks()
            elif prune_type == "volumes":
                self.docker_api.prune_volumes()
            
            # Clear the entire cache after cleanup
            self._clear_cache()
            self._notify_callbacks('system_pruned', prune_type)
        except Exception as e:
            self._notify_callbacks('prune_error', {'type': prune_type, 'error': str(e)})
            raise
    
    # Asynchronous methods
    
    def refresh_all_data(self):
        """
        Update all data asynchronously.
        """
        def _refresh():
            try:
                # Update all data types
                self.get_containers(use_cache=False)
                self.get_images(use_cache=False)
                self.get_networks(use_cache=False)
                self.get_volumes(use_cache=False)
                
                GLib.idle_add(self._notify_callbacks, 'all_data_refreshed')
            except Exception as e:
                GLib.idle_add(self._notify_callbacks, 'refresh_error', str(e))
        
        thread = threading.Thread(target=_refresh, daemon=True)
        thread.start()
    
    def set_cache_timeout(self, timeout: int):
        """
        Set the cache timeout.
        
        Args:
            timeout: Cache timeout in seconds
        """
        self._cache_timeout = timeout
    
    def clear_all_cache(self):
        """
        Clear the entire cache.
        """
        self._clear_cache()
        self._notify_callbacks('cache_cleared')
