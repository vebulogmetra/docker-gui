"""
Card Components

This module provides card-based UI components for displaying Docker resources.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject, Pango, Gdk


class ResourceCard(Gtk.Box):
    """
    A card component for displaying Docker resources (images, containers, networks, volumes).
    """
    
    def __init__(self, resource_type, resource_data, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, **kwargs)
        
        self.resource_type = resource_type
        self.resource_data = resource_data
        self.selected = False
        
        # Apply card styling
        self.add_css_class("resource-card")
        self.set_margin_start(8)
        self.set_margin_end(8)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        
        # Make card clickable
        self.set_can_focus(True)
        self.add_css_class("clickable")
        
        # Connect click events
        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self._on_card_clicked)
        self.add_controller(gesture)
        
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_card_key_pressed)
        self.add_controller(key_controller)
        
        self._build_card()
    
    def _build_card(self):
        """Build the card content based on resource type."""
        
        # Header with title and status
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        # Title
        title_label = Gtk.Label(label=self._get_title())
        title_label.add_css_class("card-title")
        title_label.set_halign(Gtk.Align.START)
        title_label.set_hexpand(True)
        header_box.append(title_label)
        
        # Status indicator
        status_box = self._create_status_indicator()
        header_box.append(status_box)
        
        self.append(header_box)
        
        # Content area
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        content_box.add_css_class("card-content")
        
        # Add resource-specific content
        self._add_content(content_box)
        
        self.append(content_box)
        
        # Footer with actions
        footer_box = self._create_footer()
        self.append(footer_box)
    
    def _get_title(self):
        """Get the title for the card based on resource type."""
        if self.resource_type == "image":
            repo = self.resource_data.get("Repository", "")
            tag = self.resource_data.get("Tag", "")
            return f"{repo}:{tag}" if tag else repo
        elif self.resource_type == "container":
            return self.resource_data.get("Names", [""])[0] if self.resource_data.get("Names") else "Unknown"
        elif self.resource_type == "network":
            return self.resource_data.get("Name", "Unknown")
        elif self.resource_type == "volume":
            return self.resource_data.get("Name", "Unknown")
        return "Unknown Resource"
    
    def _create_status_indicator(self):
        """Create status indicator based on resource type."""
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        if self.resource_type == "container":
            status = self.resource_data.get("State", "unknown")
            status_label = Gtk.Label(label=status.upper())
            
            if status == "running":
                status_label.add_css_class("status-running")
            elif status == "stopped":
                status_label.add_css_class("status-stopped")
            elif status == "exited":
                status_label.add_css_class("status-exited")
            else:
                status_label.add_css_class("status-unknown")
                
            status_box.append(status_label)
        
        return status_box
    
    def _add_content(self, content_box):
        """Add resource-specific content to the card."""
        if self.resource_type == "image":
            self._add_image_content(content_box)
        elif self.resource_type == "container":
            self._add_container_content(content_box)
        elif self.resource_type == "network":
            self._add_network_content(content_box)
        elif self.resource_type == "volume":
            self._add_volume_content(content_box)
    
    def _add_image_content(self, content_box):
        """Add content specific to Docker images."""
        image_id = self.resource_data.get("Id", self.resource_data.get("id", ""))[:12]
        id_label = Gtk.Label(label=f"ID: {image_id}")
        id_label.add_css_class("card-detail")
        content_box.append(id_label)
        
        size = self.resource_data.get("Size", self.resource_data.get("size", 0))
        size_str = self._format_size(size)
        size_label = Gtk.Label(label=f"Size: {size_str}")
        size_label.add_css_class("card-detail")
        content_box.append(size_label)
        
        created = self.resource_data.get("Created", "")
        if created:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                created_label = Gtk.Label(label=f"Created: {formatted_date}")
            except:
                created_label = Gtk.Label(label=f"Created: {created[:10]}")
            created_label.add_css_class("card-detail")
            content_box.append(created_label)
        
        repo = self.resource_data.get("Repository", self.resource_data.get("repository", ""))
        tag = self.resource_data.get("Tag", self.resource_data.get("tag", ""))
        if repo and repo != "<none>":
            repo_label = Gtk.Label(label=f"Repo: {repo}:{tag}")
            repo_label.add_css_class("card-detail")
            content_box.append(repo_label)
    
    def _add_container_content(self, content_box):
        """Add content specific to Docker containers."""
        image = self.resource_data.get("Image", self.resource_data.get("image", ""))
        image_label = Gtk.Label(label=f"Image: {image}")
        image_label.add_css_class("card-detail")
        content_box.append(image_label)
        
        status = self.resource_data.get("State", self.resource_data.get("Status", self.resource_data.get("status", "")))
        status_label = Gtk.Label(label=f"Status: {status}")
        status_label.add_css_class("card-detail")
        content_box.append(status_label)
        
        ports = self.resource_data.get("Ports", [])
        ports_str = self.resource_data.get("ports", "")
        if ports:
            if isinstance(ports, list):
                ports_str = ", ".join(ports)
            else:
                ports_str = str(ports)
        elif ports_str:
            pass
        else:
            ports_str = "No ports"
            
        ports_label = Gtk.Label(label=f"Ports: {ports_str}")
        ports_label.add_css_class("card-detail")
        content_box.append(ports_label)
    
    def _add_network_content(self, content_box):
        """Add content specific to Docker networks."""
        driver = self.resource_data.get("Driver", self.resource_data.get("driver", ""))
        driver_label = Gtk.Label(label=f"Driver: {driver}")
        driver_label.add_css_class("card-detail")
        content_box.append(driver_label)
        
        scope = self.resource_data.get("Scope", "")
        if scope:
            scope_label = Gtk.Label(label=f"Scope: {scope}")
            scope_label.add_css_class("card-detail")
            content_box.append(scope_label)
    
    def _add_volume_content(self, content_box):
        """Add content specific to Docker volumes."""
        driver = self.resource_data.get("Driver", self.resource_data.get("driver", ""))
        driver_label = Gtk.Label(label=f"Driver: {driver}")
        driver_label.add_css_class("card-detail")
        content_box.append(driver_label)
        
        mountpoint = self.resource_data.get("Mountpoint", "")
        if mountpoint:
            if len(mountpoint) > 50:
                mountpoint_display = mountpoint[:47] + "..."
            else:
                mountpoint_display = mountpoint
            mountpoint_label = Gtk.Label(label=f"Mount: {mountpoint_display}")
            mountpoint_label.add_css_class("card-detail")
            content_box.append(mountpoint_label)
    
    def _create_footer(self):
        """Create footer with action buttons."""
        footer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        footer_box.add_css_class("card-footer")
        
        if self.resource_type == "image":
            delete_btn = Gtk.Button(label="Delete")
            delete_btn.add_css_class("destructive-action")
            footer_box.append(delete_btn)
            
        elif self.resource_type == "container":
            if self.resource_data.get("State") == "running":
                stop_btn = Gtk.Button(label="Stop")
                stop_btn.add_css_class("warning-action")
                footer_box.append(stop_btn)
            else:
                start_btn = Gtk.Button(label="Start")
                start_btn.add_css_class("success-action")
                footer_box.append(start_btn)
            
            delete_btn = Gtk.Button(label="Delete")
            delete_btn.add_css_class("destructive-action")
            footer_box.append(delete_btn)
            
        elif self.resource_type in ["network", "volume"]:
            delete_btn = Gtk.Button(label="Delete")
            delete_btn.add_css_class("destructive-action")
            footer_box.append(delete_btn)
        
        return footer_box
    
    def _format_size(self, size_bytes):
        """Format size in bytes to human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def set_selected(self, selected):
        """Set the selection state of the card."""
        self.selected = selected
        if selected:
            self.add_css_class("selected")
        else:
            self.remove_css_class("selected")
    
    def get_resource_id(self):
        """Get the resource ID."""
        return self.resource_data.get("Id", "")
    
    def _on_card_clicked(self, gesture, n_press, x, y):
        """Handle card click events."""
        self.toggle_selection()
    
    def _on_card_key_pressed(self, controller, keyval, keycode, state):
        """Handle card key press events."""
        if keyval == 32:  # Space key
            self.toggle_selection()
            return True
        return False
    
    def toggle_selection(self):
        """Toggle the selection state of the card."""
        self.set_selected(not self.selected)


class StatusCard(Gtk.Box):
    """
    A card component for displaying system status and statistics.
    """
    
    def __init__(self, title, value, icon_name=None, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, **kwargs)
        
        self.title = title
        self.value = value
        self.icon_name = icon_name
        self.clickable = False
        self.click_callback = None
        
        # Apply card styling
        self.add_css_class("status-card")
        self.set_margin_start(8)
        self.set_margin_end(8)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        
        self._build_card()
    
    def _build_card(self):
        """Build the status card content."""
        
        # Icon and title
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        if self.icon_name:
            icon = Gtk.Image.new_from_icon_name(self.icon_name)
            icon.set_pixel_size(24)
            header_box.append(icon)
        
        title_label = Gtk.Label(label=self.title)
        title_label.add_css_class("status-card-title")
        title_label.set_halign(Gtk.Align.START)
        title_label.set_hexpand(True)
        header_box.append(title_label)
        
        self.append(header_box)
        
        # Value
        value_label = Gtk.Label(label=str(self.value))
        value_label.add_css_class("status-card-value")
        value_label.set_halign(Gtk.Align.START)
        self.append(value_label)
    
    def update_value(self, new_value):
        """Update the displayed value."""
        self.value = new_value
        for child in self:
            if isinstance(child, Gtk.Label) and child.has_css_class("status-card-value"):
                child.set_label(str(new_value))
                break
    
    def make_clickable(self, callback=None):
        """Make the status card clickable."""
        self.clickable = True
        self.click_callback = callback
        self.set_can_focus(True)
        self.add_css_class("clickable")
        
        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self._on_status_card_clicked)
        self.add_controller(gesture)
        
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_status_card_key_pressed)
        self.add_controller(key_controller)
    
    def _on_status_card_clicked(self, gesture, n_press, x, y):
        """Handle status card click events."""
        if self.clickable and self.click_callback:
            self.click_callback(self.title.lower())
    
    def _on_status_card_key_pressed(self, controller, keyval, keycode, state):
        """Handle status card key press events."""
        if keyval == 32 and self.clickable:  # Space key
            if self.click_callback:
                self.click_callback(self.title.lower())
            return True
        return False
