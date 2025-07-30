#!/usr/bin/env python3
import docker
import time
from typing import Any
from concurrent.futures import ThreadPoolExecutor, as_completed

class DockerAPI:
    def __init__(self, max_workers: int = 4):
        self.client = docker.from_env()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._connection_cache = {}
        self._last_ping = 0
        self._ping_interval = 30
        
    def ping(self) -> bool:
        """Check connection to Docker daemon with caching"""
        current_time = time.time()
        
        # Use cached result if not too much time has passed
        if current_time - self._last_ping < self._ping_interval:
            return self._connection_cache.get('ping', False)
        
        try:
            self.client.ping()
            self._connection_cache['ping'] = True
            self._last_ping = current_time
            return True
        except Exception:
            self._connection_cache['ping'] = False
            self._last_ping = current_time
            return False

    def get_images(self) -> list[dict[str, Any]]:
        """Get list of Docker images with optimization"""
        try:
            images = self.client.images.list()
            result = []
            
            for image in images:
                image_id = image.short_id.replace("sha256:", "")
                
                # Optimized tag retrieval
                repo = "<none>"
                tag = "<none>"
                if image.tags:
                    repo_tag = image.tags[0].split(":")
                    repo = repo_tag[0]
                    tag = repo_tag[1] if len(repo_tag) > 1 else "latest"
                
                # Get attributes once
                attrs = image.attrs
                size = attrs.get("Size", 0)
                created = attrs.get("Created", "")
                repo_tags = image.tags if image.tags else ["<none>"]
                
                result.append({
                    "Id": image_id,
                    "id": image_id,
                    "Repository": repo,
                    "repository": repo,
                    "Tag": tag,
                    "tag": tag,
                    "Size": size,
                    "size": size,
                    "Created": created,
                    "created": created,
                    "RepoTags": repo_tags
                })
            
            return result
        except Exception as e:
            print(f"Ошибка получения образов: {e}")
            return []

    def get_containers(self, all: bool = True) -> list[dict[str, Any]]:
        """Get list of Docker containers with optimization"""
        try:
            containers = self.client.containers.list(all=all)
            result = []
            
            for container in containers:
                container_id = container.short_id
                name = container.name
                image = container.image.tags[0] if container.image.tags else container.image.short_id
                status = container.status

                # Optimized port retrieval
                ports = []
                try:
                    ports_info = container.attrs.get("HostConfig", {}).get("PortBindings", {})
                    for container_port, host_ports in ports_info.items():
                        if host_ports:
                            for host_port in host_ports:
                                ports.append(f"{host_port.get('HostPort', '')}:{container_port}")
                except Exception:
                    pass  # Ignore port retrieval errors
                
                ports_str = ", ".join(ports) if ports else ""
                
                result.append({
                    "Id": container_id,
                    "id": container_id,
                    "Names": [name],
                    "name": name,
                    "Image": image,
                    "image": image,
                    "State": status,
                    "Status": status,
                    "status": status,
                    "Ports": ports,
                    "ports": ports_str
                })
            
            return result
        except Exception as e:
            print(f"Ошибка получения контейнеров: {e}")
            return []

    def get_networks(self) -> list[dict[str, Any]]:
        """Get list of Docker networks with optimization"""
        try:
            networks = self.client.networks.list()
            result = []
            
            for network in networks:
                network_id = network.short_id
                name = network.name
                
                # Get attributes once
                attrs = network.attrs
                driver = attrs.get("Driver", "")
                scope = attrs.get("Scope", "")
                
                result.append({
                    "Id": network_id,
                    "id": network_id,
                    "Name": name,
                    "name": name,
                    "Driver": driver,
                    "driver": driver,
                    "Scope": scope,
                    "scope": scope
                })
            
            return result
        except Exception as e:
            print(f"Ошибка получения сетей: {e}")
            return []

    def get_volumes(self) -> list[dict[str, Any]]:
        """Get list of Docker volumes with optimization"""
        try:
            volumes = self.client.volumes.list()
            result = []
            
            for volume in volumes:
                volume_id = volume.short_id
                name = volume.name
                
                # Get attributes once
                attrs = volume.attrs
                driver = attrs.get("Driver", "")
                mountpoint = attrs.get("Mountpoint", "")
                
                result.append({
                    "Name": name,
                    "name": name,
                    "Driver": driver,
                    "driver": driver,
                    "Mountpoint": mountpoint,
                    "mountpoint": mountpoint
                })
            
            return result
        except Exception as e:
            print(f"Ошибка получения томов: {e}")
            return []

    def get_system_info(self) -> dict[str, Any]:
        """Get system information about Docker with caching"""
        try:
            info = self.client.info()
            return {
                "Containers": info.get("Containers", 0),
                "Images": info.get("Images", 0),
                "Networks": len(info.get("NetworkSettings", {}).get("Networks", {})),
                "Volumes": len(self.client.volumes.list()),
                "DockerRootDir": info.get("DockerRootDir", ""),
                "ServerVersion": info.get("ServerVersion", ""),
                "OperatingSystem": info.get("OperatingSystem", ""),
                "Architecture": info.get("Architecture", "")
            }
        except Exception as e:
            print(f"Ошибка получения информации о системе: {e}")
            return {
                "Containers": 0,
                "Images": 0,
                "Networks": 0,
                "Volumes": 0,
                "DockerRootDir": "",
                "ServerVersion": "",
                "OperatingSystem": "",
                "Architecture": ""
            }

    # Asynchronous methods for non-blocking operations
    def get_images_async(self, callback):
        """Asynchronous image retrieval"""
        def _get_images():
            try:
                result = self.get_images()
                callback(True, result)
            except Exception as e:
                callback(False, str(e))
        
        self.executor.submit(_get_images)

    def get_containers_async(self, callback, all: bool = True):
        """Asynchronous container retrieval"""
        def _get_containers():
            try:
                result = self.get_containers(all)
                callback(True, result)
            except Exception as e:
                callback(False, str(e))
        
        self.executor.submit(_get_containers)

    def get_networks_async(self, callback):
        """Asynchronous network retrieval"""
        def _get_networks():
            try:
                result = self.get_networks()
                callback(True, result)
            except Exception as e:
                callback(False, str(e))
        
        self.executor.submit(_get_networks)

    def get_volumes_async(self, callback):
        """Asynchronous volume retrieval"""
        def _get_volumes():
            try:
                result = self.get_volumes()
                callback(True, result)
            except Exception as e:
                callback(False, str(e))
        
        self.executor.submit(_get_volumes)

    def get_system_info_async(self, callback):
        """Asynchronous system information retrieval"""
        def _get_system_info():
            try:
                result = self.get_system_info()
                callback(True, result)
            except Exception as e:
                callback(False, str(e))
        
        self.executor.submit(_get_system_info)

    # Optimized deletion methods
    def delete_image(self, image_id: str) -> bool:
        """Delete image with optimization"""
        try:
            image = self.client.images.get(image_id)
            image.remove(force=True)
            return True
        except Exception as e:
            print(f"Ошибка удаления образа {image_id}: {e}")
            return False

    def delete_images(self, image_ids: list[str]) -> dict[str, bool]:
        """Batch deletion of images with parallel processing"""
        results = {}
        
        def delete_single_image(img_id):
            try:
                image = self.client.images.get(img_id)
                image.remove(force=True)
                return img_id, True
            except Exception as e:
                print(f"Ошибка удаления образа {img_id}: {e}")
                return img_id, False
        
        # Parallel deletion
        futures = [self.executor.submit(delete_single_image, img_id) for img_id in image_ids]
        
        for future in as_completed(futures):
            img_id, success = future.result()
            results[img_id] = success
        
        return results

    def delete_container(self, container_id: str, force: bool = False) -> bool:
        """Delete container with optimization"""
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            return True
        except Exception as e:
            print(f"Ошибка удаления контейнера {container_id}: {e}")
            return False

    def delete_containers(self, container_ids: list[str], force: bool = False) -> dict[str, bool]:
        """Batch deletion of containers with parallel processing"""
        results = {}
        
        def delete_single_container(cont_id):
            try:
                container = self.client.containers.get(cont_id)
                container.remove(force=force)
                return cont_id, True
            except Exception as e:
                print(f"Ошибка удаления контейнера {cont_id}: {e}")
                return cont_id, False
        
        # Parallel deletion
        futures = [self.executor.submit(delete_single_container, cont_id) for cont_id in container_ids]
        
        for future in as_completed(futures):
            cont_id, success = future.result()
            results[cont_id] = success
        
        return results

    def stop_container(self, container_id: str) -> bool:
        """Stop container with optimization"""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            return True
        except Exception as e:
            print(f"Ошибка остановки контейнера {container_id}: {e}")
            return False

    def stop_containers(self, container_ids: list[str]) -> dict[str, bool]:
        """Batch stop of containers with parallel processing"""
        results = {}
        
        def stop_single_container(cont_id):
            try:
                container = self.client.containers.get(cont_id)
                container.stop()
                return cont_id, True
            except Exception as e:
                print(f"Ошибка остановки контейнера {cont_id}: {e}")
                return cont_id, False
        
        # Parallel stop
        futures = [self.executor.submit(stop_single_container, cont_id) for cont_id in container_ids]
        
        for future in as_completed(futures):
            cont_id, success = future.result()
            results[cont_id] = success
        
        return results

    def delete_network(self, network_id: str) -> bool:
        """Delete network with optimization"""
        try:
            network = self.client.networks.get(network_id)
            network.remove()
            return True
        except Exception as e:
            print(f"Ошибка удаления сети {network_id}: {e}")
            return False

    def delete_networks(self, network_ids: list[str]) -> dict[str, bool]:
        """Batch deletion of networks with parallel processing"""
        results = {}
        
        def delete_single_network(net_id):
            try:
                network = self.client.networks.get(net_id)
                network.remove()
                return net_id, True
            except Exception as e:
                print(f"Ошибка удаления сети {net_id}: {e}")
                return net_id, False
        
        # Parallel deletion
        futures = [self.executor.submit(delete_single_network, net_id) for net_id in network_ids]
        
        for future in as_completed(futures):
            net_id, success = future.result()
            results[net_id] = success
        
        return results

    def delete_volume(self, volume_name: str) -> bool:
        """Delete volume with optimization"""
        try:
            volume = self.client.volumes.get(volume_name)
            volume.remove()
            return True
        except Exception as e:
            print(f"Ошибка удаления тома {volume_name}: {e}")
            return False

    def delete_volumes(self, volume_names: list[str]) -> dict[str, bool]:
        """Batch deletion of volumes with parallel processing"""
        results = {}
        
        def delete_single_volume(vol_name):
            try:
                volume = self.client.volumes.get(vol_name)
                volume.remove()
                return vol_name, True
            except Exception as e:
                print(f"Ошибка удаления тома {vol_name}: {e}")
                return vol_name, False
        
        # Parallel deletion
        futures = [self.executor.submit(delete_single_volume, vol_name) for vol_name in volume_names]
        
        for future in as_completed(futures):
            vol_name, success = future.result()
            results[vol_name] = success
        
        return results

    # Методы очистки
    def prune_images(self) -> dict[str, Any]:
        """Cleanup unused images"""
        try:
            result = self.client.images.prune()
            return {
                "ImagesDeleted": result.get("ImagesDeleted", []),
                "SpaceReclaimed": result.get("SpaceReclaimed", 0)
            }
        except Exception as e:
            print(f"Ошибка очистки образов: {e}")
            return {"ImagesDeleted": [], "SpaceReclaimed": 0}

    def prune_containers(self) -> dict[str, Any]:
        """Cleanup stopped containers"""
        try:
            result = self.client.containers.prune()
            return {
                "ContainersDeleted": result.get("ContainersDeleted", []),
                "SpaceReclaimed": result.get("SpaceReclaimed", 0)
            }
        except Exception as e:
            print(f"Ошибка очистки контейнеров: {e}")
            return {"ContainersDeleted": [], "SpaceReclaimed": 0}

    def prune_networks(self) -> dict[str, Any]:
        """Cleanup unused networks"""
        try:
            result = self.client.networks.prune()
            return {
                "NetworksDeleted": result.get("NetworksDeleted", [])
            }
        except Exception as e:
            print(f"Ошибка очистки сетей: {e}")
            return {"NetworksDeleted": []}

    def prune_volumes(self) -> dict[str, Any]:
        """Cleanup unused volumes"""
        try:
            result = self.client.volumes.prune()
            return {
                "VolumesDeleted": result.get("VolumesDeleted", []),
                "SpaceReclaimed": result.get("SpaceReclaimed", 0)
            }
        except Exception as e:
            print(f"Ошибка очистки томов: {e}")
            return {"VolumesDeleted": [], "SpaceReclaimed": 0}

    def prune_system(self) -> dict[str, Any]:
        """Full system cleanup"""
        try:
            result = self.client.containers.prune()
            images_result = self.client.images.prune()
            networks_result = self.client.networks.prune()
            volumes_result = self.client.volumes.prune()
            
            return {
                "ContainersDeleted": result.get("ContainersDeleted", []),
                "ImagesDeleted": images_result.get("ImagesDeleted", []),
                "NetworksDeleted": networks_result.get("NetworksDeleted", []),
                "VolumesDeleted": volumes_result.get("VolumesDeleted", []),
                "SpaceReclaimed": (
                    result.get("SpaceReclaimed", 0) +
                    images_result.get("SpaceReclaimed", 0) +
                    volumes_result.get("SpaceReclaimed", 0)
                )
            }
        except Exception as e:
            print(f"Ошибка полной очистки системы: {e}")
            return {
                "ContainersDeleted": [],
                "ImagesDeleted": [],
                "NetworksDeleted": [],
                "VolumesDeleted": [],
                "SpaceReclaimed": 0
            }

    def format_size(self, size_in_bytes: int) -> str:
        """Formatting size to readable view"""
        if size_in_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_in_bytes >= 1024 and i < len(size_names) - 1:
            size_in_bytes /= 1024.0
            i += 1
        
        return f"{size_in_bytes:.1f} {size_names[i]}"

    def __del__(self):
        """Resource cleanup when object is deleted"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
