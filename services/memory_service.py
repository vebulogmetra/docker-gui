import gc
import psutil
import threading
import time
from typing import Dict, Any, Optional, Callable
from collections import OrderedDict
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib


class MemoryCache:
    def __init__(self, max_size: int = 100, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Key to search for
            
        Returns:
            Value from the cache or None if not found
        """
        with self.lock:
            if key in self.cache:
                # Check TTL
                if time.time() - self.timestamps[key] > self.ttl:
                    self._remove(key)
                    return None
                    
                # Move to the end (LRU)
                value = self.cache.pop(key)
                self.cache[key] = value
                return value
            return None
            
    def set(self, key: str, value: Any):
        """
        Set a value in the cache.
        
        Args:
            key: Key
            value: Value
        """
        with self.lock:
            # Remove if already exists
            if key in self.cache:
                self.cache.pop(key)
                
            # Add new value
            self.cache[key] = value
            self.timestamps[key] = time.time()
            
            # Check cache size
            if len(self.cache) > self.max_size:
                self._evict_oldest()
                
    def _remove(self, key: str):
        """Remove an element from the cache."""
        if key in self.cache:
            self.cache.pop(key)
            self.timestamps.pop(key, None)
            
    def _evict_oldest(self):
        """Remove the oldest element."""
        if self.cache:
            oldest_key = next(iter(self.cache))
            self._remove(oldest_key)
            
    def clear(self):
        """Clear the entire cache."""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
            
    def size(self) -> int:
        """Get the size of the cache."""
        return len(self.cache)
        
    def get_stats(self) -> Dict[str, Any]:
        """Get the statistics of the cache."""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'ttl': self.ttl,
                'keys': list(self.cache.keys())
            }


class MemoryManager:
    def __init__(self):
        self.process = psutil.Process()
        self.memory_threshold = 0.8  # 80% of available memory
        self.cleanup_callbacks = []
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: int = 30):
        """
        Start memory monitoring.
        
        Args:
            interval: Interval in seconds
        """
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_memory,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop memory monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
            
    def _monitor_memory(self, interval: int):
        """Memory monitoring."""
        while self.monitoring:
            try:
                memory_usage = self.get_memory_usage()
                
                if memory_usage['percent'] > self.memory_threshold * 100:
                    self._trigger_cleanup()
                    
                time.sleep(interval)
            except Exception as e:
                print(f"Ошибка мониторинга памяти: {e}")
                time.sleep(interval)
                
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get information about memory usage.
        
        Returns:
            Dictionary with memory information
        """
        try:
            memory_info = self.process.memory_info()
            system_memory = psutil.virtual_memory()
            
            return {
                'rss': memory_info.rss,  # Resident Set Size
                'vms': memory_info.vms,  # Virtual Memory Size
                'percent': self.process.memory_percent(),
                'system_total': system_memory.total,
                'system_available': system_memory.available,
                'system_percent': system_memory.percent
            }
        except Exception as e:
            print(f"Ошибка получения информации о памяти: {e}")
            return {
                'rss': 0,
                'vms': 0,
                'percent': 0,
                'system_total': 0,
                'system_available': 0,
                'system_percent': 0
            }
            
    def add_cleanup_callback(self, callback: Callable):
        """
        Add a callback for memory cleanup.
        
        Args:
            callback: Callback function
        """
        if callback not in self.cleanup_callbacks:
            self.cleanup_callbacks.append(callback)
            
    def remove_cleanup_callback(self, callback: Callable):
        """
        Remove a callback for memory cleanup.
        
        Args:
            callback: Callback function
        """
        if callback in self.cleanup_callbacks:
            self.cleanup_callbacks.remove(callback)
            
    def _trigger_cleanup(self):
        """Start the memory cleanup process."""
        print("Starting memory cleanup...")
        
        # Call all registered callbacks
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Ошибка в callback очистки памяти: {e}")
                
        # Force garbage collection
        gc.collect()
        
        print("Memory cleanup completed")
        
    def force_cleanup(self):
        """Force memory cleanup."""
        self._trigger_cleanup()
        
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        memory_usage = self.get_memory_usage()
        
        return {
            'process_memory': {
                'rss_mb': memory_usage['rss'] / 1024 / 1024,
                'vms_mb': memory_usage['vms'] / 1024 / 1024,
                'percent': memory_usage['percent']
            },
            'system_memory': {
                'total_gb': memory_usage['system_total'] / 1024 / 1024 / 1024,
                'available_gb': memory_usage['system_available'] / 1024 / 1024 / 1024,
                'percent': memory_usage['system_percent']
            },
            'threshold': self.memory_threshold * 100,
            'monitoring': self.monitoring
        }


class ResourcePool:
    def __init__(self, factory: Callable, max_size: int = 50):
        self.factory = factory
        self.max_size = max_size
        self.available = []
        self.in_use = set()
        self.lock = threading.RLock()
        
    def acquire(self) -> Any:
        """
        Get an object from the pool.
        
        Returns:
            Object from the pool
        """
        with self.lock:
            if self.available:
                obj = self.available.pop()
            else:
                obj = self.factory()
                
            self.in_use.add(obj)
            return obj
            
    def release(self, obj: Any):
        """
        Return an object to the pool.
        
        Args:
            obj: Object to return
        """
        with self.lock:
            if obj in self.in_use:
                self.in_use.remove(obj)
                
                if len(self.available) < self.max_size:
                    self.available.append(obj)
                    
    def clear(self):
        """Clear the pool."""
        with self.lock:
            self.available.clear()
            self.in_use.clear()
            
    def size(self) -> int:
        """Get the size of the pool."""
        with self.lock:
            return len(self.available) + len(self.in_use)


class MemoryService:
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.caches = {}
        self.resource_pools = {}
        
    def create_cache(self, name: str, max_size: int = 100, ttl: int = 300) -> MemoryCache:
        """
        Create a new cache.
        
        Args:
            name: Name of the cache
            max_size: Maximum size
            ttl: Time to live
            
        Returns:
            Created cache
        """
        cache = MemoryCache(max_size, ttl)
        self.caches[name] = cache
        return cache
        
    def get_cache(self, name: str) -> Optional[MemoryCache]:
        """
        Get a cache by name.
        
        Args:
            name: Name of the cache
            
        Returns:
            Cache or None if not found
        """
        return self.caches.get(name)
        
    def create_resource_pool(self, name: str, factory: Callable, max_size: int = 50) -> ResourcePool:
        """
        Create a resource pool.
        
        Args:
            name: Name of the pool
            factory: Function to create objects
            max_size: Maximum size of the pool
            
        Returns:
            Created resource pool
        """
        pool = ResourcePool(factory, max_size)
        self.resource_pools[name] = pool
        return pool
        
    def get_resource_pool(self, name: str) -> Optional[ResourcePool]:
        """
        Get a resource pool by name.
        
        Args:
            name: Name of the pool
            
        Returns:
            Resource pool or None if not found
        """
        return self.resource_pools.get(name)
        
    def start_memory_monitoring(self, interval: int = 30):
        """
        Start memory monitoring.
        
        Args:
            interval: Interval in seconds
        """
        self.memory_manager.start_monitoring(interval)
        
    def stop_memory_monitoring(self):
        """Stop memory monitoring."""
        self.memory_manager.stop_monitoring()
        
    def add_cleanup_callback(self, callback: Callable):
        """
        Add a callback for memory cleanup.
        
        Args:
            callback: Callback function
        """
        self.memory_manager.add_cleanup_callback(callback)
        
    def remove_cleanup_callback(self, callback: Callable):
        """
        Remove a callback for memory cleanup.
        
        Args:
            callback: Callback function
        """
        self.memory_manager.remove_cleanup_callback(callback)
        
    def cleanup_all(self):
        """Clear all caches and resource pools."""
        print("Starting full memory cleanup...")
        
        # Clear all caches
        for cache in self.caches.values():
            cache.clear()
            
        # Clear all resource pools
        for pool in self.resource_pools.values():
            pool.clear()
            
        # Force memory cleanup
        self.memory_manager.force_cleanup()
        
        print("Full memory cleanup completed")
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics of all components.
        
        Returns:
            Dictionary with statistics
        """
        cache_stats = {}
        for name, cache in self.caches.items():
            cache_stats[name] = cache.get_stats()
            
        pool_stats = {}
        for name, pool in self.resource_pools.items():
            pool_stats[name] = {
                'size': pool.size(),
                'max_size': pool.max_size
            }
            
        return {
            'memory': self.memory_manager.get_memory_stats(),
            'caches': cache_stats,
            'pools': pool_stats
        }
        
    def __del__(self):
        """Memory cleanup when the object is deleted."""
        self.stop_memory_monitoring()


# Global instance of the memory service
memory_service = MemoryService()
