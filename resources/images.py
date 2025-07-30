import threading
from typing import List, Dict, Any, Optional, Callable
from gi.repository import GLib

from core.resource_manager import ResourceManager
from core.base_operations import BaseOperations


class ImageManager(ResourceManager):
    def __init__(self, docker_api, notification_service=None, cache_ttl: int = 60):
        super().__init__(docker_api, cache_ttl)
        self.notification_service = notification_service
        self.resource_type = "images"
        self.images = []
        self.filtered_images = []
        
    def _load_resources(self):
        """Load images from the Docker API."""
        self.images = self.docker_api.get_images()
        self.resources = self.images  # Synchronize with the base class
        self.filtered_images = self.images.copy()
        self.filtered_resources = self.filtered_images  # Synchronize with the base class
    
    def _get_resource_id(self, resource: Dict[str, Any]) -> str:
        """Get the ID of the image."""
        return resource.get('Id', '')
    
    def _resource_matches_search(self, resource: Dict[str, Any], query: str) -> bool:
        """Check if the image matches the search query."""
        query = query.lower()
        return (
            query in resource.get('RepoTags', [''])[0].lower() if resource.get('RepoTags') else False or
            query in resource.get('Id', '')[:12].lower() or
            query in str(resource.get('Size', '')).lower()
        )
    
    def _resource_matches_filters(self, resource: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if the image matches the filters."""
        # Filter by size
        if 'size' in filters and filters['size']:
            size_filter = filters['size'].lower()
            if size_filter not in str(resource.get('Size', '')).lower():
                return False
        
        # Filter by tag
        if 'tag' in filters and filters['tag']:
            tag_filter = filters['tag'].lower()
            repo_tags = resource.get('RepoTags', [])
            if not any(tag_filter in tag.lower() for tag in repo_tags):
                return False
        
        return True
    
    def _perform_delete(self, resource_id: str):
        """Perform image deletion."""
        self.docker_api.delete_image(resource_id, force=True)
    
    def refresh(self, callback: Optional[Callable] = None, force: bool = False):
        """Refresh image data.
        
        Args:
            callback: Callback function to notify upon completion
            force: Force refresh, ignoring the cache
        """
        if callback:
            self.add_callback(lambda event_type, data: callback() if event_type == 'loading_complete' else None)
        
        super().refresh(force=force)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search images by query.
        
        Args:
            query: Search query
            
        Returns:
            List of filtered images
        """
        super().search(query)
        return self.get_filtered_resources()
    
    def filter(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter images by criteria.
        
        Args:
            filters: Dictionary with filtering criteria
            
        Returns:
            List of filtered images
        """
        super().filter(filters)
        return self.get_filtered_resources()
    
    def get_image(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        Get image by ID.
        
        Args:
            image_id: Image ID
            
        Returns:
            Image or None if not found
        """
        return self.get_resource(image_id)
    
    def delete_image(self, image_id: str, force: bool = False, callback: Optional[Callable] = None):
        """
        Delete image.
        
        Args:
            image_id: Image ID
            force: Force deletion
            callback: Callback function
        """
        def _delete():
            try:
                self.docker_api.delete_image(image_id, force=force)
                if self.notification_service:
                    self.notification_service.show_success("Образ удален")
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'delete', image_id, callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка удаления образа: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'delete', image_id, str(e), callback)
        
        thread = threading.Thread(target=_delete, daemon=True)
        thread.start()
    
    def pull_image(self, image_name: str, callback: Optional[Callable] = None):
        """
        Load image.
        
        Args:
            image_name: Name of the image to load
            callback: Callback function
        """
        def _pull():
            try:
                self.docker_api.pull_image(image_name)
                if self.notification_service:
                    self.notification_service.show_success(f"Образ {image_name} загружен")
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'pull', image_name, callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка загрузки образа: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'pull', image_name, str(e), callback)
        
        thread = threading.Thread(target=_pull, daemon=True)
        thread.start()
    
    def build_image(self, dockerfile_path: str, tag: str, callback: Optional[Callable] = None):
        """
        Build image.
        
        Args:
            dockerfile_path: Path to Dockerfile
            tag: Tag for the image
            callback: Callback function
        """
        def _build():
            try:
                self.docker_api.build_image(dockerfile_path, tag)
                if self.notification_service:
                    self.notification_service.show_success(f"Образ {tag} собран")
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'build', tag, callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка сборки образа: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'build', tag, str(e), callback)
        
        thread = threading.Thread(target=_build, daemon=True)
        thread.start()
    
    def tag_image(self, image_id: str, repository: str, tag: str, callback: Optional[Callable] = None):
        """
        Tag image.
        
        Args:
            image_id: Image ID
            repository: Repository
            tag: Tag
            callback: Callback function
        """
        def _tag():
            try:
                self.docker_api.tag_image(image_id, repository, tag)
                if self.notification_service:
                    self.notification_service.show_success(f"Образ тегирован как {repository}:{tag}")
                self.invalidate_cache()  # Invalidate the cache after the change
                GLib.idle_add(self._on_operation_complete, 'tag', f"{repository}:{tag}", callback)
            except Exception as e:
                if self.notification_service:
                    self.notification_service.show_error(f"Ошибка тегирования образа: {str(e)}")
                GLib.idle_add(self._on_operation_error, 'tag', f"{repository}:{tag}", str(e), callback)
        
        thread = threading.Thread(target=_tag, daemon=True)
        thread.start()
    
    def _on_operation_complete(self, operation: str, image_id: str, callback: Optional[Callable]):
        """Handler for the completion of the operation."""
        if callback:
            callback()
        self.refresh(force=True)  # Force update after the operation
    
    def _on_operation_error(self, operation: str, image_id: str, error: str, callback: Optional[Callable]):
        """Handler for the error of the operation."""
        if callback:
            callback()
        print(f"Error in {operation} operation for image {image_id}: {error}")
    
    def format_image_data(self, image: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format image data for display.
        
        Args:
            image: Raw image data
            
        Returns:
            Formatted image data
        """
        formatted = image.copy()
        
        # Format the tags
        repo_tags = image.get('RepoTags', [])
        if repo_tags:
            formatted['display_name'] = repo_tags[0]
            formatted['tags_display'] = ', '.join(repo_tags)
        else:
            formatted['display_name'] = f"<none>:<none>"
            formatted['tags_display'] = "Нет тегов"
        
        # Format the size
        size = image.get('Size', 0)
        formatted['size_display'] = BaseOperations.format_size(size)
        
        # Format the creation date
        created = image.get('Created', 0)
        formatted['created_display'] = BaseOperations.format_date(created)
        
        # Short ID
        formatted['short_id'] = image.get('Id', '')[:12]
        
        # Number of layers
        formatted['layers_count'] = len(image.get('Layers', []))
        
        return formatted
    
    def get_all_images_formatted(self) -> List[Dict[str, Any]]:
        """
        Get all images in formatted view.
        
        Returns:
            List of formatted images
        """
        return [self.format_image_data(image) for image in self.get_filtered_resources()]
    
    def get_total_images_count(self) -> int:
        """
        Get the total number of images.
        
        Returns:
            Total number of images
        """
        return len(self.resources)
    
    def get_dangling_images_count(self) -> int:
        """
        Get the number of dangling images.
        
        Returns:
            Number of dangling images
        """
        return len([img for img in self.resources if not img.get('RepoTags')])
    
    def get_total_size(self) -> int:
        """
        Get the total size of all images.
        
        Returns:
            Total size in bytes
        """
        return sum(img.get('Size', 0) for img in self.resources)
