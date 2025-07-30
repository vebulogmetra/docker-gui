import pytest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_docker_client():
    """Мок Docker клиента для unit тестов"""
    with patch('docker_api.docker.from_env') as mock_from_env:
        mock_client = MagicMock()
        mock_from_env.return_value = mock_client
        
        # Настройка мок данных для контейнеров
        mock_containers = [
            MagicMock(
                short_id="test_container_1",
                name="test_container_1",
                status="running",
                image=MagicMock(tags=["test_image:latest"], short_id="test_image_1"),
                attrs={
                    "HostConfig": {
                        "PortBindings": {
                            "80/tcp": [{"HostPort": "8080"}]
                        }
                    }
                }
            ),
            MagicMock(
                short_id="test_container_2", 
                name="test_container_2",
                status="exited",
                image=MagicMock(tags=["test_image:latest"], short_id="test_image_1"),
                attrs={
                    "HostConfig": {
                        "PortBindings": {}
                    }
                }
            )
        ]
        
        # Настройка мок данных для образов
        mock_images = [
            MagicMock(
                short_id="test_image_1",
                tags=["test_image:latest"],
                attrs={"Size": 1024*1024*100}  # 100MB
            ),
            MagicMock(
                short_id="test_image_2",
                tags=["test_image2:latest"],
                attrs={"Size": 1024*1024*50}  # 50MB
            )
        ]
        
        # Настройка мок данных для сетей
        mock_network_1 = MagicMock()
        mock_network_1.short_id = "test_network_1"
        mock_network_1.name = "bridge"
        mock_network_1.attrs = {"Driver": "bridge"}
        
        mock_network_2 = MagicMock()
        mock_network_2.short_id = "test_network_2"
        mock_network_2.name = "test_network"
        mock_network_2.attrs = {"Driver": "bridge"}
        
        mock_networks = [mock_network_1, mock_network_2]
        
        # Настройка мок данных для томов
        mock_volume_1 = MagicMock()
        mock_volume_1.name = "test_volume_1"
        mock_volume_1.attrs = {"Driver": "local"}
        
        mock_volume_2 = MagicMock()
        mock_volume_2.name = "test_volume_2"
        mock_volume_2.attrs = {"Driver": "local"}
        
        mock_volumes = [mock_volume_1, mock_volume_2]
        
        # Настройка методов клиента
        mock_client.containers.list.return_value = mock_containers
        mock_client.images.list.return_value = mock_images
        mock_client.networks.list.return_value = mock_networks
        mock_client.volumes.list.return_value = mock_volumes
        
        # Настройка методов для операций
        mock_client.containers.get.return_value = mock_containers[0]
        mock_client.images.get.return_value = mock_images[0]
        mock_client.networks.get.return_value = mock_networks[0]
        mock_client.volumes.get.return_value = mock_volumes[0]
        
        yield mock_client


@pytest.fixture
def mock_gtk_app():
    """Мок GTK приложения для тестирования"""
    # Создаем мок модуля gi
    mock_gi = MagicMock()
    mock_gtk = MagicMock()
    
    # Создаем мок окна
    mock_window = MagicMock()
    mock_window.show_all.return_value = None
    mock_window.destroy.return_value = None
    
    # Создаем мок приложения
    mock_app = MagicMock()
    mock_app.connect.return_value = None
    mock_app.run.return_value = 0
    mock_app.quit.return_value = None
    
    # Настройка мок виджетов
    mock_gtk.ApplicationWindow.return_value = mock_window
    mock_gtk.Application.return_value = mock_app
    
    # Мокаем весь модуль gi
    with patch.dict('sys.modules', {'gi': mock_gi, 'gi.repository': mock_gi, 'gi.repository.Gtk': mock_gtk}):
        yield mock_gtk


@pytest.fixture
def sample_docker_data():
    """Образцы данных Docker для тестирования"""
    return {
        "containers": [
            {
                "id": "test_container_1",
                "name": "test_container_1", 
                "status": "running",
                "image": "test_image:latest",
                "ports": "8080:80/tcp",
                "repository": "test_image",
                "tag": "latest"
            },
            {
                "id": "test_container_2",
                "name": "test_container_2",
                "status": "exited", 
                "image": "test_image:latest",
                "ports": "",
                "repository": "test_image",
                "tag": "latest"
            }
        ],
        "images": [
            {
                "id": "test_image_1",
                "repository": "test_image",
                "tag": "latest",
                "size": 1024*1024*100
            },
            {
                "id": "test_image_2", 
                "repository": "test_image2",
                "tag": "latest",
                "size": 1024*1024*50
            }
        ],
        "networks": [
            {
                "id": "test_network_1",
                "name": "bridge",
                "driver": "bridge"
            },
            {
                "id": "test_network_2",
                "name": "test_network",
                "driver": "bridge"
            }
        ],
        "volumes": [
            {
                "name": "test_volume_1",
                "driver": "local"
            },
            {
                "name": "test_volume_2",
                "driver": "local"
            }
        ]
    }


@pytest.fixture
def temp_docker_environment():
    """Временное Docker окружение для integration тестов"""
    # Этот фикстур будет использоваться для создания временных
    # Docker ресурсов для тестирования
    import docker
    
    client = docker.from_env()
    
    # Создаем временные ресурсы
    test_containers = []
    test_images = []
    test_networks = []
    test_volumes = []
    
    try:
        # Создаем тестовый образ
        test_image = client.images.pull("hello-world:latest")
        test_images.append(test_image)
        
        # Создаем тестовую сеть
        test_network = client.networks.create("test_network", driver="bridge")
        test_networks.append(test_network)
        
        # Создаем тестовый том
        test_volume = client.volumes.create("test_volume")
        test_volumes.append(test_volume)
        
        yield {
            "client": client,
            "containers": test_containers,
            "images": test_images,
            "networks": test_networks,
            "volumes": test_volumes
        }
        
    finally:
        # Очищаем тестовые ресурсы
        for container in test_containers:
            try:
                container.remove(force=True)
            except:
                pass
                
        for network in test_networks:
            try:
                network.remove()
            except:
                pass
                
        for volume in test_volumes:
            try:
                volume.remove()
            except:
                pass 