import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib


class StatusBar(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, **kwargs)
        
        # Apply styling
        self.add_css_class("status-bar")
        self.set_margin_start(8)
        self.set_margin_end(8)
        self.set_margin_top(4)
        self.set_margin_bottom(4)
        
        # Status indicators
        self.docker_status = None
        self.progress_bar = None
        self.status_label = None
        self.action_buttons = {}
        
        self._build_status_bar()
    
    def _build_status_bar(self):
        """Build the status bar components."""
        
        # Docker connection status
        self.docker_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.docker_status.add_css_class("status-indicator")
        
        # Status icon
        self.status_icon = Gtk.Image.new_from_icon_name("network-server")
        self.status_icon.set_pixel_size(16)
        self.docker_status.append(self.status_icon)
        
        # Status text
        self.status_text = Gtk.Label(label="Connecting...")
        self.status_text.add_css_class("status-text")
        self.docker_status.append(self.status_text)
        
        self.append(self.docker_status)
        
        # Separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.append(separator)
        
        # Progress bar (hidden by default)
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.add_css_class("status-progress")
        self.progress_bar.set_visible(False)
        self.append(self.progress_bar)
        
        # Main status label
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.add_css_class("status-message")
        self.status_label.set_hexpand(True)
        self.status_label.set_halign(Gtk.Align.START)
        self.append(self.status_label)
        
        # Action buttons area
        self.action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.append(self.action_box)
    
    def set_docker_status(self, connected, message=None):
        """Set the Docker connection status."""
        if connected:
            self.status_icon.set_from_icon_name("network-server-symbolic")
            self.status_text.set_label("Connected")
            self.docker_status.add_css_class("connected")
            self.docker_status.remove_css_class("disconnected")
        else:
            self.status_icon.set_from_icon_name("network-error-symbolic")
            self.status_text.set_label("Disconnected")
            self.docker_status.add_css_class("disconnected")
            self.docker_status.remove_css_class("connected")
        
        if message:
            self.set_status_message(message)
    
    def set_status_message(self, message):
        """Set the main status message."""
        self.status_label.set_label(message)
    
    def show_progress(self, show=True):
        """Show or hide the progress bar."""
        self.progress_bar.set_visible(show)
    
    def set_progress(self, fraction):
        """Set the progress bar fraction (0.0 to 1.0)."""
        self.progress_bar.set_fraction(fraction)
    
    def set_progress_text(self, text):
        """Set the progress bar text."""
        self.progress_bar.set_text(text)
    
    def add_action_button(self, name, label, callback=None, css_class=None):
        """Add an action button to the status bar."""
        button = Gtk.Button(label=label)
        if css_class:
            button.add_css_class(css_class)
        if callback:
            button.connect("clicked", callback)
        
        self.action_buttons[name] = button
        self.action_box.append(button)
        return button
    
    def remove_action_button(self, name):
        """Remove an action button from the status bar."""
        if name in self.action_buttons:
            button = self.action_buttons[name]
            self.action_box.remove(button)
            del self.action_buttons[name]
    
    def clear_action_buttons(self):
        """Clear all action buttons."""
        for button in self.action_buttons.values():
            self.action_box.remove(button)
        self.action_buttons.clear()
    
    def show_loading(self, message="Loading..."):
        """Show loading state."""
        self.set_status_message(message)
        self.show_progress(True)
        self.set_progress(0.0)
    
    def hide_loading(self, message="Ready"):
        """Hide loading state."""
        self.set_status_message(message)
        self.show_progress(False)
    
    def show_error(self, message):
        """Show error state."""
        self.set_status_message(f"Error: {message}")
        self.show_progress(False)
    
    def show_success(self, message):
        """Show success state."""
        self.set_status_message(message)
        self.show_progress(False)
    
    def update_status(self, message):
        """Update the status message (alias for set_status_message)."""
        self.set_status_message(message)
    
    def update_state(self, connected, message=None):
        """Update the Docker connection state (alias for set_docker_status)."""
        self.set_docker_status(connected, message)
