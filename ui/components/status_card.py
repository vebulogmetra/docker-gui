import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk


class StatusCard(Gtk.Box):
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
        # Update the label
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
        
        # Add gesture for click handling
        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self._on_status_card_clicked)
        self.add_controller(gesture)
        
        # Add key controller for keyboard navigation
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
