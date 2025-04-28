#!/usr/bin/env python3
import docker
from typing import Any

class DockerAPI:
    """Класс для работы с Docker API"""
    def __init__(self):
        """Инициализация клиента Docker"""
        self.client = docker.from_env()

    def get_images(self) -> list[dict[str, Any]]:
        """Получение списка образов Docker"""
        images = self.client.images.list()
        result = []
        for image in images:
            image_id = image.short_id.replace("sha256:", "")
            # Получаем репозиторий и тег
            repo = "<none>"
            tag = "<none>"
            if image.tags:
                repo_tag = image.tags[0].split(":")
                repo = repo_tag[0]
                tag = repo_tag[1] if len(repo_tag) > 1 else "latest"
            # Получаем размер
            size = image.attrs["Size"]
            result.append({
                "id": image_id,
                "repository": repo,
                "tag": tag,
                "size": size
            })
        return result


    def get_containers(self, all: bool = True) -> list[dict[str, Any]]:
        """Получение списка контейнеров Docker"""
        containers = self.client.containers.list(all=all)
        result = []
        for container in containers:
            container_id = container.short_id
            name = container.name
            image = container.image.tags[0] if container.image.tags else container.image.short_id
            status = container.status

            # Получаем информацию о портах
            ports = []
            ports_info = container.attrs.get("HostConfig", {}).get("PortBindings", {})
            for container_port, host_ports in ports_info.items():
                if host_ports:
                    for host_port in host_ports:
                        ports.append(f"{host_port.get('HostPort', '')}:{container_port}")
            ports_str = ", ".join(ports) if ports else ""
            result.append({
                "id": container_id,
                "name": name,
                "image": image,
                "status": status,
                "ports": ports_str
            })
        return result


    def get_networks(self) -> list[dict[str, Any]]:
        """Получение списка сетей Docker"""
        networks = self.client.networks.list()
        result = []
        for network in networks:
            network_id = network.short_id
            name = network.name
            driver = network.attrs.get("Driver", "")
            result.append({
                "id": network_id,
                "name": name,
                "driver": driver
            })
        return result


    def get_volumes(self) -> list[dict[str, Any]]:
        """Получение списка томов Docker"""
        volumes = self.client.volumes.list()
        result = []
        for volume in volumes:
            name = volume.name
            driver = volume.attrs.get("Driver", "")
            result.append({
                "name": name,
                "driver": driver
            })
        return result


    def delete_image(self, image_id: str) -> bool:
        """Удаление образа Docker по ID"""
        try:
            self.client.images.remove(image_id)
            return True
        except Exception as e:
            print(f"Ошибка при удалении образа: {e}")
            return False


    def delete_images(self, image_ids: list[str]) -> dict[str, bool]:
        """Удаление нескольких образов Docker по их ID"""
        results = {}
        for image_id in image_ids:
            results[image_id] = self.delete_image(image_id)
        return results


    def stop_container(self, container_id: str) -> bool:
        """Остановка контейнера Docker по ID"""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            return True
        except Exception as e:
            print(f"Ошибка при остановке контейнера: {e}")
            return False


    def stop_containers(self, container_ids: list[str]) -> dict[str, bool]:
        """Остановка нескольких контейнеров Docker по их ID"""
        results = {}
        for container_id in container_ids:
            results[container_id] = self.stop_container(container_id)
        return results


    def delete_container(self, container_id: str, force: bool = False) -> bool:
        """Удаление контейнера Docker по ID"""
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            return True
        except Exception as e:
            print(f"Ошибка при удалении контейнера: {e}")
            return False


    def delete_containers(self, container_ids: list[str], force: bool = False) -> dict[str, bool]:
        """Удаление нескольких контейнеров Docker по их ID"""
        results = {}
        for container_id in container_ids:
            results[container_id] = self.delete_container(container_id, force)
        return results


    def delete_network(self, network_id: str) -> bool:
        """Удаление сети Docker по ID"""
        try:
            network = self.client.networks.get(network_id)
            network.remove()
            return True
        except Exception as e:
            print(f"Ошибка при удалении сети: {e}")
            return False


    def delete_networks(self, network_ids: list[str]) -> dict[str, bool]:
        """Удаление нескольких сетей Docker по их ID"""
        results = {}
        for network_id in network_ids:
            results[network_id] = self.delete_network(network_id)
        return results


    def delete_volume(self, volume_name: str) -> bool:
        """Удаление тома Docker по имени"""
        try:
            volume = self.client.volumes.get(volume_name)
            volume.remove()
            return True
        except Exception as e:
            print(f"Ошибка при удалении тома: {e}")
            return False


    def delete_volumes(self, volume_names: list[str]) -> dict[str, bool]:
        """Удаление нескольких томов Docker по их именам"""
        results = {}
        for volume_name in volume_names:
            results[volume_name] = self.delete_volume(volume_name)
        return results


    def prune_images(self) -> dict[str, Any]:
        """Очистка неиспользуемых образов Docker"""
        try:
            result = self.client.images.prune()
            return {
                "success": True,
                "deleted": result.get("ImagesDeleted", []),
                "space_reclaimed": result.get("SpaceReclaimed", 0)
            }
        except Exception as e:
            print(f"Ошибка при очистке образов: {e}")
            return {"success": False, "error": str(e)}


    def prune_containers(self) -> dict[str, Any]:
        """Очистка остановленных контейнеров Docker"""
        try:
            result = self.client.containers.prune()
            return {
                "success": True,
                "deleted": result.get("ContainersDeleted", []),
                "space_reclaimed": result.get("SpaceReclaimed", 0)
            }
        except Exception as e:
            print(f"Ошибка при очистке контейнеров: {e}")
            return {"success": False, "error": str(e)}


    def prune_networks(self) -> dict[str, Any]:
        """Очистка неиспользуемых сетей Docker"""
        try:
            result = self.client.networks.prune()
            return {
                "success": True,
                "deleted": result.get("NetworksDeleted", []),
            }
        except Exception as e:
            print(f"Ошибка при очистке сетей: {e}")
            return {"success": False, "error": str(e)}


    def prune_volumes(self) -> dict[str, Any]:
        """Очистка неиспользуемых томов Docker"""
        try:
            result = self.client.volumes.prune()
            return {
                "success": True,
                "deleted": result.get("VolumesDeleted", []),
                "space_reclaimed": result.get("SpaceReclaimed", 0)
            }
        except Exception as e:
            print(f"Ошибка при очистке томов: {e}")
            return {"success": False, "error": str(e)}


    def prune_system(self) -> dict[str, Any]:
        """Очистка всех неиспользуемых ресурсов Docker"""
        try:
            result = self.client.containers.prune()
            container_space = result.get("SpaceReclaimed", 0)
            
            result = self.client.images.prune()
            image_space = result.get("SpaceReclaimed", 0)
            
            result = self.client.networks.prune()
            
            result = self.client.volumes.prune()
            volume_space = result.get("SpaceReclaimed", 0)
            return {
                "success": True,
                "space_reclaimed": container_space + image_space + volume_space
            }
        except Exception as e:
            print(f"Ошибка при очистке системы: {e}")
            return {"success": False, "error": str(e)}


    def format_size(self, size_in_bytes: int) -> str:
        """Форматирует размер в байтах в человекочитаемый формат."""
        size = float(size_in_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
