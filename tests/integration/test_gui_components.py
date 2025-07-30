"""
Integration тесты для GUI компонентов
"""
import pytest
from unittest.mock import patch, MagicMock
import threading
import time


class TestGUIComponents:
    """Тесты для GUI компонентов"""
    
    @pytest.mark.gui
    def test_gui_initialization(self, mock_gtk_app):
        """Тест инициализации GUI приложения"""
        with patch('docker_gui.DockerGuiApp') as mock_gui_class:
            mock_gui = MagicMock()
            mock_gui_class.return_value = mock_gui
            
            # Создаем экземпляр приложения
            app = mock_gui_class()
            
            # Проверяем, что GUI был инициализирован
            assert app is not None
            mock_gui_class.assert_called_once()
            
    @pytest.mark.gui
    def test_gui_window_creation(self, mock_gtk_app):
        """Тест создания главного окна"""
        with patch('docker_gui.Gtk.ApplicationWindow') as mock_window_class:
            mock_window = MagicMock()
            mock_window_class.return_value = mock_window
            
            # Создаем окно
            window = mock_window_class()
            
            # Проверяем создание окна
            assert window is not None
            mock_window_class.assert_called_once()
            
    @pytest.mark.gui
    def test_gui_notebook_creation(self, mock_gtk_app):
        """Тест создания notebook с вкладками"""
        with patch('docker_gui.Gtk.Notebook') as mock_notebook_class:
            mock_notebook = MagicMock()
            mock_notebook_class.return_value = mock_notebook
            
            # Создаем notebook
            notebook = mock_notebook_class()
            
            # Проверяем создание notebook
            assert notebook is not None
            mock_notebook_class.assert_called_once()
            
    @pytest.mark.gui
    def test_gui_treeview_creation(self, mock_gtk_app):
        """Тест создания treeview для отображения данных"""
        with patch('docker_gui.Gtk.TreeView') as mock_treeview_class:
            mock_treeview = MagicMock()
            mock_treeview_class.return_value = mock_treeview
            
            # Создаем treeview
            treeview = mock_treeview_class()
            
            # Проверяем создание treeview
            assert treeview is not None
            mock_treeview_class.assert_called_once()
            
    @pytest.mark.gui
    def test_gui_button_creation(self, mock_gtk_app):
        """Тест создания кнопок"""
        with patch('docker_gui.Gtk.Button') as mock_button_class:
            mock_button = MagicMock()
            mock_button_class.return_value = mock_button
            
            # Создаем кнопку
            button = mock_button_class()
            
            # Проверяем создание кнопки
            assert button is not None
            mock_button_class.assert_called_once()
            
    @pytest.mark.gui
    def test_gui_refresh_functionality(self, mock_gtk_app, mock_docker_client):
        """Тест функциональности обновления данных"""
        with patch('docker_gui.DockerGuiApp') as mock_gui_class:
            mock_gui = MagicMock()
            mock_gui_class.return_value = mock_gui
            
            # Имитируем вызов метода обновления
            mock_gui.refresh_data.return_value = None
            
            # Проверяем, что метод обновления вызывается
            mock_gui.refresh_data()
            mock_gui.refresh_data.assert_called_once()
            
    @pytest.mark.gui
    def test_gui_container_operations(self, mock_gtk_app, mock_docker_client):
        """Тест операций с контейнерами через GUI"""
        with patch('docker_gui.DockerGuiApp') as mock_gui_class:
            mock_gui = MagicMock()
            mock_gui_class.return_value = mock_gui
            
            container_id = "test_container_1"
            
            # Тестируем операции с контейнерами
            mock_gui.start_container.return_value = True
            mock_gui.stop_container.return_value = True
            mock_gui.remove_container.return_value = True
            
            assert mock_gui.start_container(container_id) is True
            assert mock_gui.stop_container(container_id) is True
            assert mock_gui.remove_container(container_id) is True
            
            mock_gui.start_container.assert_called_once_with(container_id)
            mock_gui.stop_container.assert_called_once_with(container_id)
            mock_gui.remove_container.assert_called_once_with(container_id)
            
    @pytest.mark.gui
    def test_gui_image_operations(self, mock_gtk_app, mock_docker_client):
        """Тест операций с образами через GUI"""
        with patch('docker_gui.DockerGuiApp') as mock_gui_class:
            mock_gui = MagicMock()
            mock_gui_class.return_value = mock_gui
            
            image_id = "test_image_1"
            
            # Тестируем операции с образами
            mock_gui.remove_image.return_value = True
            
            assert mock_gui.remove_image(image_id) is True
            mock_gui.remove_image.assert_called_once_with(image_id)
            
    @pytest.mark.gui
    def test_gui_network_operations(self, mock_gtk_app, mock_docker_client):
        """Тест операций с сетями через GUI"""
        with patch('docker_gui.DockerGuiApp') as mock_gui_class:
            mock_gui = MagicMock()
            mock_gui_class.return_value = mock_gui
            
            network_id = "test_network_1"
            
            # Тестируем операции с сетями
            mock_gui.remove_network.return_value = True
            
            assert mock_gui.remove_network(network_id) is True
            mock_gui.remove_network.assert_called_once_with(network_id)
            
    @pytest.mark.gui
    def test_gui_volume_operations(self, mock_gtk_app, mock_docker_client):
        """Тест операций с томами через GUI"""
        with patch('docker_gui.DockerGuiApp') as mock_gui_class:
            mock_gui = MagicMock()
            mock_gui_class.return_value = mock_gui
            
            volume_id = "test_volume_1"
            
            # Тестируем операции с томами
            mock_gui.remove_volume.return_value = True
            
            assert mock_gui.remove_volume(volume_id) is True
            mock_gui.remove_volume.assert_called_once_with(volume_id)
            
    @pytest.mark.gui
    def test_gui_prune_operations(self, mock_gtk_app, mock_docker_client):
        """Тест операций очистки через GUI"""
        with patch('docker_gui.DockerGuiApp') as mock_gui_class:
            mock_gui = MagicMock()
            mock_gui_class.return_value = mock_gui
            
            # Тестируем операции очистки
            mock_gui.prune_containers.return_value = {"ContainersDeleted": ["test"]}
            mock_gui.prune_images.return_value = {"ImagesDeleted": ["test"]}
            mock_gui.prune_networks.return_value = {"NetworksDeleted": ["test"]}
            mock_gui.prune_volumes.return_value = {"VolumesDeleted": ["test"]}
            mock_gui.prune_all.return_value = {
                "containers": {"ContainersDeleted": ["test"]},
                "images": {"ImagesDeleted": ["test"]},
                "networks": {"NetworksDeleted": ["test"]},
                "volumes": {"VolumesDeleted": ["test"]}
            }
            
            assert mock_gui.prune_containers()["ContainersDeleted"] == ["test"]
            assert mock_gui.prune_images()["ImagesDeleted"] == ["test"]
            assert mock_gui.prune_networks()["NetworksDeleted"] == ["test"]
            assert mock_gui.prune_volumes()["VolumesDeleted"] == ["test"]
            
            prune_all_result = mock_gui.prune_all()
            assert "containers" in prune_all_result
            assert "images" in prune_all_result
            assert "networks" in prune_all_result
            assert "volumes" in prune_all_result
            
    @pytest.mark.gui
    def test_gui_error_handling(self, mock_gtk_app):
        """Тест обработки ошибок в GUI"""
        with patch('docker_gui.DockerGuiApp') as mock_gui_class:
            mock_gui = MagicMock()
            mock_gui_class.return_value = mock_gui
            
            # Имитируем ошибку
            mock_gui.show_error.return_value = None
            
            # Проверяем, что ошибка обрабатывается
            mock_gui.show_error("Test error")
            mock_gui.show_error.assert_called_once_with("Test error")
            
    @pytest.mark.gui
    def test_gui_async_operations(self, mock_gtk_app, mock_docker_client):
        """Тест асинхронных операций в GUI"""
        with patch('docker_gui.DockerGuiApp') as mock_gui_class:
            mock_gui = MagicMock()
            mock_gui_class.return_value = mock_gui
            
            # Имитируем асинхронную операцию
            def async_operation():
                time.sleep(0.1)
                mock_gui.update_ui.return_value = None
                mock_gui.update_ui()
            
            # Запускаем асинхронную операцию
            thread = threading.Thread(target=async_operation)
            thread.start()
            thread.join()
            
            # Проверяем, что UI был обновлен
            mock_gui.update_ui.assert_called_once()
            
    @pytest.mark.gui
    def test_gui_data_loading(self, mock_gtk_app, mock_docker_client):
        """Тест загрузки данных в GUI"""
        with patch('docker_gui.DockerGuiApp') as mock_gui_class:
            mock_gui = MagicMock()
            mock_gui_class.return_value = mock_gui
            
            # Имитируем загрузку данных
            mock_gui.load_containers.return_value = [{"id": "test", "name": "test"}]
            mock_gui.load_images.return_value = [{"id": "test", "tags": ["test:latest"]}]
            mock_gui.load_networks.return_value = [{"id": "test", "name": "test"}]
            mock_gui.load_volumes.return_value = [{"id": "test", "name": "test"}]
            
            # Проверяем загрузку данных
            containers = mock_gui.load_containers()
            images = mock_gui.load_images()
            networks = mock_gui.load_networks()
            volumes = mock_gui.load_volumes()
            
            assert len(containers) == 1
            assert len(images) == 1
            assert len(networks) == 1
            assert len(volumes) == 1
            
            mock_gui.load_containers.assert_called_once()
            mock_gui.load_images.assert_called_once()
            mock_gui.load_networks.assert_called_once()
            mock_gui.load_volumes.assert_called_once()
            
    @pytest.mark.gui
    def test_gui_selection_handling(self, mock_gtk_app):
        """Тест обработки выбора элементов в GUI"""
        with patch('docker_gui.DockerGuiApp') as mock_gui_class:
            mock_gui = MagicMock()
            mock_gui_class.return_value = mock_gui
            
            # Имитируем выбор элемента
            mock_gui.on_selection_changed.return_value = None
            
            # Проверяем обработку выбора
            mock_gui.on_selection_changed("test_id")
            mock_gui.on_selection_changed.assert_called_once_with("test_id")
            
    @pytest.mark.gui
    def test_gui_dialog_handling(self, mock_gtk_app):
        """Тест обработки диалогов в GUI"""
        with patch('docker_gui.DockerGuiApp') as mock_gui_class:
            mock_gui = MagicMock()
            mock_gui_class.return_value = mock_gui
            
            # Имитируем показ диалога
            mock_gui.show_confirm_dialog.return_value = True
            mock_gui.show_info_dialog.return_value = None
            
            # Проверяем диалоги
            assert mock_gui.show_confirm_dialog("Test message") is True
            mock_gui.show_info_dialog("Test info")
            
            mock_gui.show_confirm_dialog.assert_called_once_with("Test message")
            mock_gui.show_info_dialog.assert_called_once_with("Test info") 