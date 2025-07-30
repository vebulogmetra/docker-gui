import threading
import time
from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib


class ResourceManager(ABC):
    def __init__(self, docker_api, cache_ttl: int = 30):
        self.docker_api = docker_api
        self.resources = []
        self.filtered_resources = []
        self.current_filters = {}
        self.current_search = ""
        self.is_loading = False
        self._callbacks = []
        
        # Caching system
        self.cache_ttl = cache_ttl
        self.last_cache_time = 0
        self.cache_valid = False
        
        # UI updates optimization
        self._update_timer = None
        self._pending_updates = False
        
    def add_callback(self, callback: Callable):
        """
        Add a callback for notifications of changes.
        
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
                print(f"Error in callback: {e}")
    
    def is_cache_valid(self) -> bool:
        """
        Check if the cache is valid.
        
        Returns:
            True if the cache is valid, False otherwise
        """
        if not self.cache_valid:
            return False
        
        current_time = time.time()
        return (current_time - self.last_cache_time) < self.cache_ttl
    
    def invalidate_cache(self):
        """Invalidate the cache."""
        self.cache_valid = False
        self.last_cache_time = 0
    
    def refresh(self, force: bool = False):
        """
        Update the resources asynchronously.
        
        Args:
            force: Force update, ignoring the cache
        """
        if self.is_loading:
            return
        
        # Check the cache, if not forced update
        if not force and self.is_cache_valid():
            self._notify_callbacks('cache_hit')
            return
            
        self.is_loading = True
        self._notify_callbacks('loading_started')
        
        def _refresh():
            try:
                self._load_resources()
                self.last_cache_time = time.time()
                self.cache_valid = True
                GLib.idle_add(self._on_refresh_complete)
            except Exception as e:
                GLib.idle_add(self._on_refresh_error, str(e))
        
        thread = threading.Thread(target=_refresh, daemon=True)
        thread.start()
    
    def schedule_ui_update(self):
        """
        Schedule UI update with debouncing.
        """
        if self._update_timer:
            try:
                GLib.source_remove(self._update_timer)
            except (ValueError, TypeError):
                # Ignore errors if the ID is not found
                pass
        
        if not self._pending_updates:
            self._pending_updates = True
            self._update_timer = GLib.timeout_add(100, self._perform_ui_update)
    
    def _perform_ui_update(self):
        """
        Perform UI update.
        """
        self._pending_updates = False
        self._update_timer = None
        self._notify_callbacks('ui_update')
        return False  # Stop the timer
    
    @abstractmethod
    def _load_resources(self):
        """
        Load resources from Docker API.
        Must be implemented in subclasses.
        """
        pass
    
    def _on_refresh_complete(self):
        """Handler for the completion of the update."""
        self.is_loading = False
        self._apply_filters_and_search()
        self._notify_callbacks('loading_complete')
        self.schedule_ui_update()
    
    def _on_refresh_error(self, error_message: str):
        """Handler for the error of the update."""
        self.is_loading = False
        self._notify_callbacks('loading_error', error_message)
        print(f"Error refreshing resources: {error_message}")
    
    def search(self, query: str):
        """
        Search for resources.
        
        Args:
            query: Search query
        """
        self.current_search = query
        self._apply_filters_and_search()
        self.schedule_ui_update()
    
    def filter(self, filters: Dict[str, Any]):
        """
        Filter resources.
        
        Args:
            filters: Dictionary with filtering criteria
        """
        self.current_filters = filters.copy()
        self._apply_filters_and_search()
        self.schedule_ui_update()
    
    def clear_filters(self):
        """Clear all filters."""
        self.current_filters = {}
        self._apply_filters_and_search()
        self.schedule_ui_update()
    
    def clear_search(self):
        """Clear the search query."""
        self.current_search = ""
        self._apply_filters_and_search()
        self.schedule_ui_update()
    
    def _apply_filters_and_search(self):
        """
        Apply filters and search to resources.
        """
        # Start with the full list of resources
        filtered = self.resources.copy()
        
        # Apply the search
        if self.current_search:
            filtered = self._apply_search(filtered, self.current_search)
        
        # Apply the filters
        if self.current_filters:
            filtered = self._apply_filters(filtered, self.current_filters)
        
        self.filtered_resources = filtered
    
    def _apply_search(self, resources: List[Any], query: str) -> List[Any]:
        """
        Apply search to the list of resources.
        
        Args:
            resources: List of resources to search
            query: Search query
            
        Returns:
            Filtered list of resources
        """
        if not query:
            return resources
        
        query = query.lower()
        return [
            resource for resource in resources
            if self._resource_matches_search(resource, query)
        ]
    
    def _apply_filters(self, resources: List[Any], filters: Dict[str, Any]) -> List[Any]:
        """
        Apply filters to the list of resources.
        
        Args:
            resources: List of resources to filter
            filters: Dictionary with filtering criteria
            
        Returns:
            Filtered list of resources
        """
        if not filters:
            return resources
        
        return [
            resource for resource in resources
            if self._resource_matches_filters(resource, filters)
        ]
    
    @abstractmethod
    def _resource_matches_search(self, resource: Any, query: str) -> bool:
        """
        Check if the resource matches the search query.
        
        Args:
            resource: Resource to check
            query: Search query
            
        Returns:
            True if the resource matches the query
        """
        pass
    
    @abstractmethod
    def _resource_matches_filters(self, resource: Any, filters: Dict[str, Any]) -> bool:
        """
        Check if the resource matches the filters.
        
        Args:
            resource: Resource to check
            filters: Dictionary with filtering criteria
            
        Returns:
            True if the resource matches the filters
        """
        pass
    
    def get_resource(self, resource_id: str) -> Optional[Any]:
        """
        Get a specific resource by ID.
        
        Args:
            resource_id: ID of the resource
            
        Returns:
            Resource or None if not found
        """
        for resource in self.resources:
            if self._get_resource_id(resource) == resource_id:
                return resource
        return None
    
    @abstractmethod
    def _get_resource_id(self, resource: Any) -> str:
        """
        Get the ID of the resource.
        
        Args:
            resource: Resource
            
        Returns:
            ID of the resource
        """
        pass
    
    def delete_resource(self, resource_id: str):
        """
        Delete a resource.
        
        Args:
            resource_id: ID of the resource to delete
        """
        def _delete():
            try:
                self._perform_delete(resource_id)
                self.invalidate_cache()  # Invalidate the cache after deletion
                GLib.idle_add(self._on_delete_complete, resource_id)
            except Exception as e:
                GLib.idle_add(self._on_delete_error, resource_id, str(e))
        
        thread = threading.Thread(target=_delete, daemon=True)
        thread.start()
    
    @abstractmethod
    def _perform_delete(self, resource_id: str):
        """
        Perform the deletion of the resource.
        
        Args:
            resource_id: ID of the resource to delete
        """
        pass
    
    def _on_delete_complete(self, resource_id: str):
        """Handler for the completion of the deletion."""
        self._notify_callbacks('delete_complete', resource_id)
        self.refresh(force=True)  # Force update after deletion
    
    def _on_delete_error(self, resource_id: str, error_message: str):
        """Handler for the error of the deletion."""
        self._notify_callbacks('delete_error', {'id': resource_id, 'error': error_message})
        print(f"Error deleting resource {resource_id}: {error_message}")
    
    def get_resources(self) -> List[Any]:
        """
        Get all resources.
        
        Returns:
            List of all resources
        """
        return self.resources.copy()
    
    def get_filtered_resources(self) -> List[Any]:
        """
        Get filtered resources.
        
        Returns:
            List of filtered resources
        """
        return self.filtered_resources.copy()
    
    def get_loading_status(self) -> bool:
        """
        Get the loading status.
        
        Returns:
            True if loading, False otherwise
        """
        return self.is_loading
    
    def get_cache_status(self) -> Dict[str, Any]:
        """
        Get the cache status.
        
        Returns:
            Dictionary with information about the cache
        """
        current_time = time.time()
        return {
            'valid': self.is_cache_valid(),
            'last_update': self.last_cache_time,
            'age': current_time - self.last_cache_time,
            'ttl': self.cache_ttl
        }
