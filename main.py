#!/usr/bin/env python3
import sys
import os
import threading
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docker_api import DockerAPI
from services.docker_service import DockerService
from services.notification_service import NotificationService
from services.memory_service import memory_service
from resources import ContainerManager, ImageManager, NetworkManager, VolumeManager
from ui.themes.theme_manager import ThemeManager
from ui.components.dashboard import Dashboard
from ui.components.status_bar import StatusBar
from ui.components.loading_indicator import LoadingIndicator, StatusIndicator
from ui.components.virtual_list import performance_monitor


class DockerGUIApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="com.docker.gui",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        
        self.window = None
        self.docker_api = None
        self.docker_service = None
        self.notification_service = None
        self.theme_manager = None
        
        # Resource managers
        self.container_manager = None
        self.image_manager = None
        self.network_manager = None
        self.volume_manager = None
        
        # UI components
        self.dashboard = None
        self.status_bar = None
        self.loading_indicator = None
        self.status_indicator = None
        
        # Current section
        self.current_section = "dashboard"
        
        # Loading state
        self.is_loading = False
        
        # Initialize optimization services
        self._setup_optimization_services()
        
    def _setup_optimization_services(self):
        """Setup optimization services."""
        # Start memory monitoring
        memory_service.start_memory_monitoring(interval=60)
        
        # Add callback for memory cleanup
        memory_service.add_cleanup_callback(self._cleanup_memory)
        
        # Create caches for different types of data
        self.containers_cache = memory_service.create_cache("containers", max_size=50, ttl=30)
        self.images_cache = memory_service.create_cache("images", max_size=100, ttl=60)
        self.networks_cache = memory_service.create_cache("networks", max_size=20, ttl=120)
        self.volumes_cache = memory_service.create_cache("volumes", max_size=20, ttl=120)
        
        print("Сервисы оптимизации инициализированы")
        
    def _cleanup_memory(self):
        """Callback for memory cleanup."""
        print("Memory cleanup in progress...")
        
        # Invalidate caches of resource managers
        if self.container_manager:
            self.container_manager.invalidate_cache()
        if self.image_manager:
            self.image_manager.invalidate_cache()
        if self.network_manager:
            self.network_manager.invalidate_cache()
        if self.volume_manager:
            self.volume_manager.invalidate_cache()
            
        # Force garbage collection
        import gc
        gc.collect()
        
        print("Очистка памяти завершена")
        
    def do_activate(self):
        """Application activation."""
        performance_monitor.start_timer("app_activation")
        
        if not self.window:
            self._setup_services()
            self._create_window()
            self._setup_ui()
            self._load_initial_data()
        
        self.window.present()
        
        activation_time = performance_monitor.end_timer("app_activation")
        print(f"Время активации приложения: {activation_time:.2f} мс")
    
    def _setup_services(self):
        """Setup services."""
        performance_monitor.start_timer("services_setup")
        
        try:
            # Initialize Docker API with optimized settings
            self.docker_api = DockerAPI(max_workers=4)
            
            # Initialize services
            self.docker_service = DockerService(self.docker_api)
            self.notification_service = NotificationService()
            
            # Initialize resource managers with optimized cache settings
            self.container_manager = ContainerManager(
                self.docker_service, self.notification_service, cache_ttl=15
            )
            self.image_manager = ImageManager(
                self.docker_service, self.notification_service, cache_ttl=60
            )
            self.network_manager = NetworkManager(
                self.docker_service, self.notification_service, cache_ttl=120
            )
            self.volume_manager = VolumeManager(
                self.docker_service, self.notification_service, cache_ttl=120
            )
            
            # Setup callbacks for resource managers
            self._setup_resource_callbacks()
            
            # Initialize theme manager (will be done after window creation)
            self.theme_manager = None
            
            setup_time = performance_monitor.end_timer("services_setup")
            print(f"Время настройки сервисов: {setup_time:.2f} мс")
            
        except Exception as e:
            print(f"Ошибка настройки сервисов: {e}")
            self._show_error(f"Ошибка инициализации: {str(e)}")
    
    def _setup_resource_callbacks(self):
        """Setup callbacks for resource managers."""
        self.container_manager.add_callback(self._on_container_event)
        self.image_manager.add_callback(self._on_image_event)
        self.network_manager.add_callback(self._on_network_event)
        self.volume_manager.add_callback(self._on_volume_event)
    
    def _on_container_event(self, event_type: str, data=None):
        """Handler for container events."""
        if event_type == "updated":
            GLib.idle_add(self._on_containers_updated)
        elif event_type == "error":
            GLib.idle_add(self._show_error, f"Ошибка контейнеров: {data}")
    
    def _on_image_event(self, event_type: str, data=None):
        """Handler for image events."""
        if event_type == "updated":
            GLib.idle_add(self._on_images_updated)
        elif event_type == "error":
            GLib.idle_add(self._show_error, f"Ошибка образов: {data}")
    
    def _on_network_event(self, event_type: str, data=None):
        """Handler for network events."""
        if event_type == "updated":
            GLib.idle_add(self._on_networks_updated)
        elif event_type == "error":
            GLib.idle_add(self._show_error, f"Ошибка сетей: {data}")
    
    def _on_volume_event(self, event_type: str, data=None):
        """Handler for volume events."""
        if event_type == "updated":
            GLib.idle_add(self._on_volumes_updated)
        elif event_type == "error":
            GLib.idle_add(self._show_error, f"Ошибка томов: {data}")
    
    def _create_window(self):
        """Create the main window."""
        performance_monitor.start_timer("window_creation")
        
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title("Docker GUI - Оптимизированная версия")
        self.window.set_default_size(1200, 800)
        self.window.set_resizable(True)
        
        # Setup actions
        self._setup_actions()
        
        # Create the main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.window.set_child(main_box)
        
        # Create the toolbar
        toolbar = self._create_toolbar()
        main_box.append(toolbar)
        
        # Create the navigation panel
        nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        nav_box.set_size_request(-1, 50)
        nav_box.add_css_class("navigation-panel")
        main_box.append(nav_box)
        
        # Create the navigation buttons
        self._create_navigation_buttons(nav_box)
        
        # Create the main content container
        self.content_stack = Gtk.Stack()
        self.content_stack.set_vexpand(True)
        self.content_stack.set_hexpand(True)
        main_box.append(self.content_stack)
        
        # Create the status bar
        self.status_bar = StatusBar()
        main_box.append(self.status_bar)
        
        window_creation_time = performance_monitor.end_timer("window_creation")
        print(f"Время создания окна: {window_creation_time:.2f} мс")
    
    def _setup_actions(self):
        """Setup application actions."""
        # Action for dark theme
        dark_action = Gio.SimpleAction.new("dark-theme", None)
        dark_action.connect("activate", self._on_dark_theme)
        self.add_action(dark_action)
        
        # Action for light theme
        light_action = Gio.SimpleAction.new("light-theme", None)
        light_action.connect("activate", self._on_light_theme)
        self.add_action(light_action)
        
        # Action for refreshing all data
        refresh_action = Gio.SimpleAction.new("refresh-all", None)
        refresh_action.connect("activate", self._on_refresh_all)
        self.add_action(refresh_action)
        
        # Action for system cleanup
        prune_action = Gio.SimpleAction.new("prune-all", None)
        prune_action.connect("activate", self._on_prune_all)
        self.add_action(prune_action)
        
        # Action for application information
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.add_action(about_action)
    
    def _setup_ui(self):
        """Setup the user interface."""
        performance_monitor.start_timer("ui_setup")
        
        # Initialize the theme manager
        self.theme_manager = ThemeManager(self)
        
        # Create sections
        self._create_dashboard()
        self._create_containers_section()
        self._create_images_section()
        self._create_networks_section()
        self._create_volumes_section()
        
        # Show the dashboard by default
        self.content_stack.set_visible_child_name("dashboard")
        
        ui_setup_time = performance_monitor.end_timer("ui_setup")
        print(f"Время настройки UI: {ui_setup_time:.2f} мс")
    
    def _create_toolbar(self):
        """Create the toolbar."""
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.add_css_class("toolbar")
        toolbar.set_margin_start(10)
        toolbar.set_margin_end(10)
        toolbar.set_margin_top(5)
        toolbar.set_margin_bottom(5)
        
        # Refresh button
        refresh_button = Gtk.Button()
        refresh_button.set_icon_name("view-refresh-symbolic")
        refresh_button.set_tooltip_text("Обновить все данные")
        refresh_button.connect("clicked", lambda btn: self._on_refresh_all(None, None))
        toolbar.append(refresh_button)
        
        # Prune button
        prune_button = Gtk.Button()
        prune_button.set_icon_name("edit-delete-symbolic")
        prune_button.set_tooltip_text("Очистить неиспользуемые ресурсы")
        prune_button.connect("clicked", lambda btn: self._on_prune_all(None, None))
        toolbar.append(prune_button)
        
        # Separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        toolbar.append(separator)
        
        # Dark theme button
        dark_button = Gtk.Button()
        dark_button.set_icon_name("weather-clear-night-symbolic")
        dark_button.set_tooltip_text("Темная тема")
        dark_button.connect("clicked", lambda btn: self._on_dark_theme(None, None))
        toolbar.append(dark_button)
        
        # Light theme button
        light_button = Gtk.Button()
        light_button.set_icon_name("weather-clear-symbolic")
        light_button.set_tooltip_text("Светлая тема")
        light_button.connect("clicked", lambda btn: self._on_light_theme(None, None))
        toolbar.append(light_button)
        
        # Separator
        separator2 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        toolbar.append(separator2)
        
        # Information button
        about_button = Gtk.Button()
        about_button.set_icon_name("help-about-symbolic")
        about_button.set_tooltip_text("О приложении")
        about_button.connect("clicked", lambda btn: self._on_about(None, None))
        toolbar.append(about_button)
        
        return toolbar
    
    def _create_navigation_buttons(self, parent):
        """Create the navigation buttons."""
        # Dashboard button
        dashboard_button = Gtk.Button(label="Dashboard")
        dashboard_button.add_css_class("nav-button")
        dashboard_button.connect("clicked", self._on_navigation_clicked, "dashboard")
        parent.append(dashboard_button)
        
        # Containers button
        containers_button = Gtk.Button(label="Containers")
        containers_button.add_css_class("nav-button")
        containers_button.connect("clicked", self._on_navigation_clicked, "containers")
        parent.append(containers_button)
        
        # Images button
        images_button = Gtk.Button(label="Images")
        images_button.add_css_class("nav-button")
        images_button.connect("clicked", self._on_navigation_clicked, "images")
        parent.append(images_button)
        
        # Networks button
        networks_button = Gtk.Button(label="Networks")
        networks_button.add_css_class("nav-button")
        networks_button.connect("clicked", self._on_navigation_clicked, "networks")
        parent.append(networks_button)
        
        # Volumes button
        volumes_button = Gtk.Button(label="Volumes")
        volumes_button.add_css_class("nav-button")
        volumes_button.connect("clicked", self._on_navigation_clicked, "volumes")
        parent.append(volumes_button)
    
    def _create_dashboard(self):
        """Create the dashboard."""
        def navigation_callback(section):
            self._on_navigation_clicked(None, section)
        
        self.dashboard = Dashboard(
            container_manager=self.container_manager,
            image_manager=self.image_manager,
            network_manager=self.network_manager,
            volume_manager=self.volume_manager,
            navigation_callback=navigation_callback
        )
        self.content_stack.add_named(self.dashboard, "dashboard")
    
    def _create_containers_section(self):
        """Create the containers section."""
        from ui.components.containers_view import ContainersView
        containers_view = ContainersView(self.container_manager)
        self.content_stack.add_named(containers_view, "containers")
    
    def _create_images_section(self):
        """Create the images section."""
        from ui.components.images_view import ImagesView
        images_view = ImagesView(self.image_manager)
        self.content_stack.add_named(images_view, "images")
    
    def _create_networks_section(self):
        """Create the networks section."""
        from ui.components.networks_view import NetworksView
        networks_view = NetworksView(self.network_manager)
        self.content_stack.add_named(networks_view, "networks")
    
    def _create_volumes_section(self):
        """Create the volumes section."""
        from ui.components.volumes_view import VolumesView
        volumes_view = VolumesView(self.volume_manager)
        self.content_stack.add_named(volumes_view, "volumes")
    
    def _load_initial_data(self):
        """Load initial data."""
        performance_monitor.start_timer("initial_data_load")
        
        def _load():
            try:
                # Load data asynchronously
                self.container_manager.refresh()
                self.image_manager.refresh()
                self.network_manager.refresh()
                self.volume_manager.refresh()
                
                # Update status
                GLib.idle_add(self._update_status)
                
                load_time = performance_monitor.end_timer("initial_data_load")
                print(f"Время загрузки начальных данных: {load_time:.2f} мс")
                
            except Exception as e:
                GLib.idle_add(self._show_error, f"Ошибка загрузки данных: {str(e)}")
        
        # Run in a separate thread
        import threading
        thread = threading.Thread(target=_load, daemon=True)
        thread.start()
    
    def _refresh_all_data(self):
        """Update all data."""
        performance_monitor.start_timer("refresh_all_data")
        
        def _refresh():
            try:
                self.container_manager.refresh(force=True)
                self.image_manager.refresh(force=True)
                self.network_manager.refresh(force=True)
                self.volume_manager.refresh(force=True)
                
                refresh_time = performance_monitor.end_timer("refresh_all_data")
                print(f"Время обновления всех данных: {refresh_time:.2f} мс")
                
            except Exception as e:
                GLib.idle_add(self._show_error, f"Ошибка обновления: {str(e)}")
        
        thread = threading.Thread(target=_refresh, daemon=True)
        thread.start()
    
    def _update_status(self):
        """Update the connection status."""
        try:
            is_connected = self.docker_api.ping()
            if is_connected:
                self.status_bar.set_docker_status(True, "Connected")
            else:
                self.status_bar.set_docker_status(False, "Disconnected")
        except Exception as e:
            self.status_bar.show_error(f"Error: {str(e)}")
    
    def _on_navigation_clicked(self, button, section):
        """Handler for navigation click."""
        self.current_section = section
        self.content_stack.set_visible_child_name(section)
        
        # Update data for the selected section
        if section == "containers":
            self.container_manager.refresh()
        elif section == "images":
            self.image_manager.refresh()
        elif section == "networks":
            self.network_manager.refresh()
        elif section == "volumes":
            self.volume_manager.refresh()
    
    def _on_containers_updated(self):
        """Handler for container updates."""
        self._update_containers_view()
    
    def _on_images_updated(self):
        """Handler for image updates."""
        self._update_images_view()
    
    def _on_networks_updated(self):
        """Handler for network updates."""
        self._update_networks_view()
    
    def _on_volumes_updated(self):
        """Handler for volume updates."""
        self._update_volumes_view()
    
    def _on_refresh_containers(self, button):
        """Update containers."""
        self.container_manager.refresh(force=True)
    
    def _on_refresh_images(self, button):
        """Update images."""
        self.image_manager.refresh(force=True)
    
    def _on_refresh_networks(self, button):
        """Update networks."""
        self.network_manager.refresh(force=True)
    
    def _on_refresh_volumes(self, button):
        """Update volumes."""
        self.volume_manager.refresh(force=True)
    
    def _on_dark_theme(self, action, param):
        """Switch to dark theme."""
        if self.theme_manager:
            self.theme_manager.apply_theme("dark")
    
    def _on_light_theme(self, action, param):
        """Switch to light theme."""
        if self.theme_manager:
            self.theme_manager.apply_theme("light")
    
    def _on_refresh_all(self, action, param):
        """Update all data."""
        self._refresh_all_data()
    
    def _on_prune_all(self, action, param):
        """Cleanup all unused resources."""
        self._perform_prune()
    
    def _perform_prune(self):
        """Perform system cleanup."""
        def _prune():
            try:
                self._show_loading("Очистка системы...")

                containers_result = self.docker_api.prune_containers()
                images_result = self.docker_api.prune_images()
                networks_result = self.docker_api.prune_networks()
                volumes_result = self.docker_api.prune_volumes()
                
                # Count results
                total_deleted = (
                    len(containers_result.get("ContainersDeleted", [])) +
                    len(images_result.get("ImagesDeleted", [])) +
                    len(networks_result.get("NetworksDeleted", [])) +
                    len(volumes_result.get("VolumesDeleted", []))
                )
                
                total_space = (
                    containers_result.get("SpaceReclaimed", 0) +
                    images_result.get("SpaceReclaimed", 0) +
                    volumes_result.get("SpaceReclaimed", 0)
                )
                
                # Update data
                self.container_manager.refresh(force=True)
                self.image_manager.refresh(force=True)
                self.network_manager.refresh(force=True)
                self.volume_manager.refresh(force=True)
                
                GLib.idle_add(self._hide_loading)
                GLib.idle_add(
                    self.notification_service.show_info,
                    f"Очистка завершена",
                    f"Удалено {total_deleted} ресурсов, освобождено {self.docker_api.format_size(total_space)}"
                )
                
            except Exception as e:
                GLib.idle_add(self._hide_loading)
                GLib.idle_add(self._show_error, f"Ошибка очистки: {str(e)}")
        
        thread = threading.Thread(target=_prune, daemon=True)
        thread.start()
    
    def _on_about(self, action, param):
        """Show application information."""
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_transient_for(self.window)
        about_dialog.set_modal(True)
        about_dialog.set_program_name("Docker GUI")
        about_dialog.set_version("0.1.0")
        about_dialog.set_copyright("© 2025 Artem Golubev")
        about_dialog.set_comments("Application for managing Docker")
        about_dialog.set_website("https://github.com/vebulogmetra/docker-gui")
        about_dialog.set_website_label("GitHub")
        
        # Add performance information
        stats = memory_service.get_stats()
        perf_stats = performance_monitor.get_metrics()
        
        about_text = f"""
Статистика памяти:
• Использование: {stats['memory']['process_memory']['rss_mb']:.1f} MB
• Системная память: {stats['memory']['system_memory']['percent']:.1f}%

Метрики производительности:
• Среднее время активации: {perf_stats.get('app_activation', {}).get('average', 0):.1f} мс
• Среднее время настройки сервисов: {perf_stats.get('services_setup', {}).get('average', 0):.1f} мс
        """
        
        about_dialog.set_comments(about_text)
        
        about_dialog.connect("close-request", lambda dialog: dialog.destroy())
        about_dialog.present()
    
    def _show_error_dialog(self, message):
        """Show error dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Ошибка",
            secondary_text=message
        )
        dialog.connect("close-request", lambda dialog: dialog.destroy())
        dialog.present()
    
    def _show_loading(self, message: str):
        """Show loading indicator."""
        if not self.loading_indicator:
            self.loading_indicator = LoadingIndicator()
            self.window.get_child().append(self.loading_indicator)
        self.loading_indicator.show_loading(message)
    
    def _hide_loading(self):
        """Hide loading indicator."""
        if self.loading_indicator:
            self.loading_indicator.hide_loading()
    
    def _show_error(self, message: str):
        """Show error."""
        self.notification_service.show_error("Ошибка", message)
    
    def _show_cache_status(self, message: str):
        """Show cache status."""
        self.status_bar.set_status_message(message)
    
    def _update_containers_view(self):
        """Update the containers view."""
        if self.current_section == "containers":
            # Update will be done automatically through callbacks
            pass
    
    def _update_images_view(self):
        """Update the images view."""
        if self.current_section == "images":
            # Update will be done automatically through callbacks
            pass
    
    def _update_networks_view(self):
        """Update the networks view."""
        if self.current_section == "networks":
            # Update will be done automatically through callbacks
            pass
    
    def _update_volumes_view(self):
        """Update the volumes view."""
        if self.current_section == "volumes":
            # Update will be done automatically through callbacks
            pass
    
    def do_shutdown(self):
        """Shutdown the application."""
        print("Завершение работы приложения...")

        memory_service.stop_memory_monitoring()
        
        # Cleanup all resources
        memory_service.cleanup_all()
        
        # Output final statistics
        final_stats = memory_service.get_stats()
        final_perf_stats = performance_monitor.get_metrics()
        
        print("=== ФИНАЛЬНАЯ СТАТИСТИКА ===")
        print(f"Использование памяти: {final_stats['memory']['process_memory']['rss_mb']:.1f} MB")
        print(f"Системная память: {final_stats['memory']['system_memory']['percent']:.1f}%")
        print("Метрики производительности:")
        for metric, data in final_perf_stats.items():
            print(f"  {metric}: {data['average']:.1f} мс (среднее)")
        
        try:
            # Try to call the parent method
            super().do_shutdown()
        except (TypeError, AttributeError):
            # If it doesn't work, just shut down
            pass


def main():
    """Main application function."""
    app = DockerGUIApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    main()
