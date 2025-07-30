"""
Unit тесты для Docker API клиента
"""
import pytest
from unittest.mock import patch, MagicMock
import docker_api


class TestDockerAPI:
    """Тесты для класса DockerAPI"""
    
    def test_init(self, mock_docker_client):
        """Тест инициализации DockerAPI"""
        api = docker_api.DockerAPI()
        assert api.client is not None
        
    def test_get_containers(self, mock_docker_client):
        """Тест получения списка контейнеров"""
        api = docker_api.DockerAPI()
        containers = api.get_containers()
        
        assert len(containers) == 2
        assert containers[0]["id"] == "test_container_1"
        assert containers[0]["status"] == "running"
        assert containers[1]["id"] == "test_container_2"
        assert containers[1]["status"] == "exited"
        
        # Проверяем, что был вызван метод list
        mock_docker_client.containers.list.assert_called_once()
        
    def test_get_images(self, mock_docker_client):
        """Тест получения списка образов"""
        api = docker_api.DockerAPI()
        images = api.get_images()
        
        assert len(images) == 2
        assert images[0]["id"] == "test_image_1"
        assert images[0]["repository"] == "test_image"
        assert images[1]["id"] == "test_image_2"
        assert images[1]["repository"] == "test_image2"
        
        mock_docker_client.images.list.assert_called_once()
        
    def test_get_networks(self, mock_docker_client):
        """Тест получения списка сетей"""
        api = docker_api.DockerAPI()
        networks = api.get_networks()
        
        assert len(networks) == 2
        assert networks[0]["id"] == "test_network_1"
        assert networks[0]["name"] == "bridge"
        assert networks[1]["id"] == "test_network_2"
        assert networks[1]["name"] == "test_network"
        
        mock_docker_client.networks.list.assert_called_once()
        
    def test_get_volumes(self, mock_docker_client):
        """Тест получения списка томов"""
        api = docker_api.DockerAPI()
        volumes = api.get_volumes()
        
        assert len(volumes) == 2
        assert volumes[0]["name"] == "test_volume_1"
        assert volumes[1]["name"] == "test_volume_2"
        
        mock_docker_client.volumes.list.assert_called_once()
        
    def test_stop_container(self, mock_docker_client):
        """Тест остановки контейнера"""
        api = docker_api.DockerAPI()
        container_id = "test_container_1"
        
        # Настройка мока для stop
        mock_container = MagicMock()
        mock_docker_client.containers.get.return_value = mock_container
        
        result = api.stop_container(container_id)
        
        assert result is True
        mock_docker_client.containers.get.assert_called_once_with(container_id)
        mock_container.stop.assert_called_once()
        
    def test_delete_container(self, mock_docker_client):
        """Тест удаления контейнера"""
        api = docker_api.DockerAPI()
        container_id = "test_container_1"
        
        mock_container = MagicMock()
        mock_docker_client.containers.get.return_value = mock_container
        
        result = api.delete_container(container_id)
        
        assert result is True
        mock_docker_client.containers.get.assert_called_once_with(container_id)
        mock_container.remove.assert_called_once()
        
    def test_delete_image(self, mock_docker_client):
        """Тест удаления образа"""
        api = docker_api.DockerAPI()
        image_id = "test_image_1"
        
        # Настройка мока для remove
        mock_docker_client.images.remove.return_value = None
        
        result = api.delete_image(image_id)
        
        assert result is True
        mock_docker_client.images.remove.assert_called_once_with(image_id)
        
    def test_delete_network(self, mock_docker_client):
        """Тест удаления сети"""
        api = docker_api.DockerAPI()
        network_id = "test_network_1"
        
        mock_network = MagicMock()
        mock_docker_client.networks.get.return_value = mock_network
        
        result = api.delete_network(network_id)
        
        assert result is True
        mock_docker_client.networks.get.assert_called_once_with(network_id)
        mock_network.remove.assert_called_once()
        
    def test_delete_volume(self, mock_docker_client):
        """Тест удаления тома"""
        api = docker_api.DockerAPI()
        volume_name = "test_volume_1"
        
        mock_volume = MagicMock()
        mock_docker_client.volumes.get.return_value = mock_volume
        
        result = api.delete_volume(volume_name)
        
        assert result is True
        mock_docker_client.volumes.get.assert_called_once_with(volume_name)
        mock_volume.remove.assert_called_once()
        
    def test_prune_containers(self, mock_docker_client):
        """Тест очистки контейнеров"""
        api = docker_api.DockerAPI()
        
        # Настройка мока для prune
        mock_docker_client.containers.prune.return_value = {
            "ContainersDeleted": ["test_container_2"],
            "SpaceReclaimed": 1024*1024*50
        }
        
        result = api.prune_containers()
        
        assert result["deleted"] == ["test_container_2"]
        assert result["space_reclaimed"] == 1024*1024*50
        mock_docker_client.containers.prune.assert_called_once()
        
    def test_prune_images(self, mock_docker_client):
        """Тест очистки образов"""
        api = docker_api.DockerAPI()
        
        mock_docker_client.images.prune.return_value = {
            "ImagesDeleted": ["test_image_2"],
            "SpaceReclaimed": 1024*1024*50
        }
        
        result = api.prune_images()
        
        assert result["deleted"] == ["test_image_2"]
        assert result["space_reclaimed"] == 1024*1024*50
        mock_docker_client.images.prune.assert_called_once()
        
    def test_prune_networks(self, mock_docker_client):
        """Тест очистки сетей"""
        api = docker_api.DockerAPI()
        
        mock_docker_client.networks.prune.return_value = {
            "NetworksDeleted": ["test_network_2"]
        }
        
        result = api.prune_networks()
        
        assert result["deleted"] == ["test_network_2"]
        mock_docker_client.networks.prune.assert_called_once()
        
    def test_prune_volumes(self, mock_docker_client):
        """Тест очистки томов"""
        api = docker_api.DockerAPI()
        
        mock_docker_client.volumes.prune.return_value = {
            "VolumesDeleted": ["test_volume_2"],
            "SpaceReclaimed": 1024*1024*25
        }
        
        result = api.prune_volumes()
        
        assert result["deleted"] == ["test_volume_2"]
        assert result["space_reclaimed"] == 1024*1024*25
        mock_docker_client.volumes.prune.assert_called_once()
        
    def test_prune_system(self, mock_docker_client):
        """Тест полной очистки системы"""
        api = docker_api.DockerAPI()
        
        # Настройка моков для всех prune операций
        mock_docker_client.containers.prune.return_value = {
            "ContainersDeleted": ["test_container_2"],
            "SpaceReclaimed": 1024*1024*50
        }
        mock_docker_client.images.prune.return_value = {
            "ImagesDeleted": ["test_image_2"],
            "SpaceReclaimed": 1024*1024*50
        }
        mock_docker_client.networks.prune.return_value = {
            "NetworksDeleted": ["test_network_2"]
        }
        mock_docker_client.volumes.prune.return_value = {
            "VolumesDeleted": ["test_volume_2"],
            "SpaceReclaimed": 1024*1024*25
        }
        
        result = api.prune_system()
        
        assert "space_reclaimed" in result
        assert result["success"] is True
        
        mock_docker_client.containers.prune.assert_called_once()
        mock_docker_client.images.prune.assert_called_once()
        mock_docker_client.networks.prune.assert_called_once()
        mock_docker_client.volumes.prune.assert_called_once()
        
    def test_error_handling_stop_container(self, mock_docker_client):
        """Тест обработки ошибок при остановке контейнера"""
        api = docker_api.DockerAPI()
        container_id = "invalid_container"
        
        # Настройка мока для вызова исключения
        mock_docker_client.containers.get.side_effect = Exception("Container not found")
        
        result = api.stop_container(container_id)
        
        assert result is False
        
    def test_error_handling_delete_container(self, mock_docker_client):
        """Тест обработки ошибок при удалении контейнера"""
        api = docker_api.DockerAPI()
        container_id = "invalid_container"
        
        mock_docker_client.containers.get.side_effect = Exception("Container not found")
        
        result = api.delete_container(container_id)
        
        assert result is False
        
    def test_error_handling_delete_image(self, mock_docker_client):
        """Тест обработки ошибок при удалении образа"""
        api = docker_api.DockerAPI()
        image_id = "invalid_image"
        
        mock_docker_client.images.remove.side_effect = Exception("Image not found")
        
        result = api.delete_image(image_id)
        
        assert result is False
        
    def test_error_handling_delete_network(self, mock_docker_client):
        """Тест обработки ошибок при удалении сети"""
        api = docker_api.DockerAPI()
        network_id = "invalid_network"
        
        mock_docker_client.networks.get.side_effect = Exception("Network not found")
        
        result = api.delete_network(network_id)
        
        assert result is False
        
    def test_error_handling_delete_volume(self, mock_docker_client):
        """Тест обработки ошибок при удалении тома"""
        api = docker_api.DockerAPI()
        volume_name = "invalid_volume"
        
        mock_docker_client.volumes.get.side_effect = Exception("Volume not found")
        
        result = api.delete_volume(volume_name)
        
        assert result is False
        
    def test_error_handling_prune_containers(self, mock_docker_client):
        """Тест обработки ошибок при очистке контейнеров"""
        api = docker_api.DockerAPI()
        
        mock_docker_client.containers.prune.side_effect = Exception("Prune failed")
        
        result = api.prune_containers()
        
        assert result["success"] is False
        
    def test_error_handling_prune_images(self, mock_docker_client):
        """Тест обработки ошибок при очистке образов"""
        api = docker_api.DockerAPI()
        
        mock_docker_client.images.prune.side_effect = Exception("Prune failed")
        
        result = api.prune_images()
        
        assert result["success"] is False
        
    def test_error_handling_prune_networks(self, mock_docker_client):
        """Тест обработки ошибок при очистке сетей"""
        api = docker_api.DockerAPI()
        
        mock_docker_client.networks.prune.side_effect = Exception("Prune failed")
        
        result = api.prune_networks()
        
        assert result["success"] is False
        
    def test_error_handling_prune_volumes(self, mock_docker_client):
        """Тест обработки ошибок при очистке томов"""
        api = docker_api.DockerAPI()
        
        mock_docker_client.volumes.prune.side_effect = Exception("Prune failed")
        
        result = api.prune_volumes()
        
        assert result["success"] is False
        
    def test_format_size(self):
        """Тест форматирования размера"""
        api = docker_api.DockerAPI()
        
        # Тестируем различные размеры
        assert api.format_size(1024) == "1.00 KB"
        assert api.format_size(1024*1024) == "1.00 MB"
        assert api.format_size(1024*1024*1024) == "1.00 GB"
        assert api.format_size(1024*1024*1024*1024) == "1.00 TB"
        
    def test_delete_multiple_containers(self, mock_docker_client):
        """Тест удаления нескольких контейнеров"""
        api = docker_api.DockerAPI()
        container_ids = ["test_container_1", "test_container_2"]
        
        # Настройка моков
        mock_container1 = MagicMock()
        mock_container2 = MagicMock()
        mock_docker_client.containers.get.side_effect = [mock_container1, mock_container2]
        
        result = api.delete_containers(container_ids)
        
        assert result["test_container_1"] is True
        assert result["test_container_2"] is True
        assert mock_docker_client.containers.get.call_count == 2
        
    def test_delete_multiple_images(self, mock_docker_client):
        """Тест удаления нескольких образов"""
        api = docker_api.DockerAPI()
        image_ids = ["test_image_1", "test_image_2"]
        
        # Настройка моков
        mock_docker_client.images.remove.side_effect = [None, Exception("Image not found")]
        
        result = api.delete_images(image_ids)
        
        assert result["test_image_1"] is True
        assert result["test_image_2"] is False
        assert mock_docker_client.images.remove.call_count == 2 