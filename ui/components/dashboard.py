import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

from .status_card import StatusCard


class Dashboard(Gtk.Box):
    def __init__(self, container_manager=None, image_manager=None, network_manager=None, volume_manager=None, navigation_callback=None, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16, **kwargs)
        
        self.container_manager = container_manager
        self.image_manager = image_manager
        self.network_manager = network_manager
        self.volume_manager = volume_manager
        
        self.navigation_callback = navigation_callback
        self.status_cards = {}
        
        self.add_css_class("dashboard")
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_top(16)
        self.set_margin_bottom(16)
        
        self._build_dashboard()
    
    def _build_dashboard(self):
        """Build the dashboard layout."""
        
        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.add_css_class("dashboard-header")
        
        # Title
        title_label = Gtk.Label(label="Docker System Overview")
        title_label.add_css_class("dashboard-title")
        title_label.set_halign(Gtk.Align.START)
        title_label.set_hexpand(True)
        header_box.append(title_label)
        
        # Refresh button
        refresh_button = Gtk.Button()
        refresh_button.add_css_class("dashboard-refresh")
        refresh_button.set_icon_name("view-refresh-symbolic")
        refresh_button.connect("clicked", self._on_refresh_clicked)
        header_box.append(refresh_button)
        
        self.append(header_box)
        
        # Statistics grid
        self.stats_grid = Gtk.Grid()
        self.stats_grid.add_css_class("dashboard-stats")
        self.stats_grid.set_column_spacing(16)
        self.stats_grid.set_row_spacing(16)
        self.append(self.stats_grid)
        
        # Create status cards
        self._create_status_cards()
        
        # Load initial data
        self.refresh_data()
    
    def _create_status_cards(self):
        """Create status cards for different statistics."""
        
        # Images card
        images_card = StatusCard("Images", "0", "applications-graphics")
        images_card.make_clickable(self._on_card_clicked)
        self.status_cards["images"] = images_card
        self.stats_grid.attach(images_card, 0, 0, 1, 1)
        
        # Containers card
        containers_card = StatusCard("Containers", "0", "applications-system")
        containers_card.make_clickable(self._on_card_clicked)
        self.status_cards["containers"] = containers_card
        self.stats_grid.attach(containers_card, 1, 0, 1, 1)
        
        # Running containers card
        running_card = StatusCard("Running", "0", "media-playback-start")
        self.status_cards["running"] = running_card
        self.stats_grid.attach(running_card, 2, 0, 1, 1)
        
        # Networks card
        networks_card = StatusCard("Networks", "0", "network-server")
        networks_card.make_clickable(self._on_card_clicked)
        self.status_cards["networks"] = networks_card
        self.stats_grid.attach(networks_card, 0, 1, 1, 1)
        
        # Volumes card
        volumes_card = StatusCard("Volumes", "0", "drive-harddisk")
        volumes_card.make_clickable(self._on_card_clicked)
        self.status_cards["volumes"] = volumes_card
        self.stats_grid.attach(volumes_card, 1, 1, 1, 1)
        
        # Stopped containers card
        stopped_card = StatusCard("Stopped", "0", "media-playback-pause")
        self.status_cards["stopped"] = stopped_card
        self.stats_grid.attach(stopped_card, 2, 1, 1, 1)
    
    def _on_card_clicked(self, card_type):
        """Handle card click events."""
        if self.navigation_callback:
            self.navigation_callback(card_type)
    
    def refresh_data(self):
        """Refresh dashboard data."""
        def _refresh():
            try:
                if self.container_manager:
                    self.container_manager.refresh()
                if self.image_manager:
                    self.image_manager.refresh()
                if self.network_manager:
                    self.network_manager.refresh()
                if self.volume_manager:
                    self.volume_manager.refresh()
                
                GLib.idle_add(self._update_ui)
                
            except Exception as e:
                GLib.idle_add(self._show_error, str(e))
        
        import threading
        thread = threading.Thread(target=_refresh, daemon=True)
        thread.start()
    
    def _update_ui(self):
        """Update UI with current data."""
        try:
            if self.container_manager:
                total_containers = self.container_manager.get_total_containers_count()
                running_containers = self.container_manager.get_running_containers_count()
                stopped_containers = self.container_manager.get_stopped_containers_count()
                
                self.update_status_card("containers", str(total_containers))
                self.update_status_card("running", str(running_containers))
                self.update_status_card("stopped", str(stopped_containers))
            
            if self.image_manager:
                total_images = self.image_manager.get_total_images_count()
                self.update_status_card("images", str(total_images))
            
            if self.network_manager:
                total_networks = self.network_manager.get_total_networks_count()
                self.update_status_card("networks", str(total_networks))
            
            if self.volume_manager:
                total_volumes = self.volume_manager.get_total_volumes_count()
                self.update_status_card("volumes", str(total_volumes))
                
        except Exception as e:
            print(f"Error updating dashboard UI: {e}")
    
    def _show_error(self, error):
        """Show error message."""
        print(f"Dashboard error: {error}")
    
    def _on_refresh_clicked(self, button):
        """Handle refresh button click."""
        self.refresh_data()
    
    def get_status_cards(self):
        """Get all status cards."""
        return self.status_cards
    
    def update_status_card(self, card_name, value):
        """Update a specific status card."""
        if card_name in self.status_cards:
            self.status_cards[card_name].update_value(value)
    
    def update_containers_stats(self):
        """Update containers statistics."""
        if self.container_manager:
            total_containers = self.container_manager.get_total_containers_count()
            running_containers = self.container_manager.get_running_containers_count()
            stopped_containers = self.container_manager.get_stopped_containers_count()
            
            self.update_status_card("containers", str(total_containers))
            self.update_status_card("running", str(running_containers))
            self.update_status_card("stopped", str(stopped_containers))
    
    def update_images_stats(self):
        """Update images statistics."""
        if self.image_manager:
            total_images = self.image_manager.get_total_images_count()
            self.update_status_card("images", str(total_images))
    
    def update_networks_stats(self):
        """Update networks statistics."""
        if self.network_manager:
            total_networks = self.network_manager.get_total_networks_count()
            self.update_status_card("networks", str(total_networks))
    
    def update_volumes_stats(self):
        """Update volumes statistics."""
        if self.volume_manager:
            total_volumes = self.volume_manager.get_total_volumes_count()
            self.update_status_card("volumes", str(total_volumes))
