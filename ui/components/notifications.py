import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib


class NotificationManager:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.notifications = []
        self.notification_box = None
        self._create_notification_area()
    
    def _create_notification_area(self):
        """Create the notification display area."""
        self.notification_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.notification_box.add_css_class("notification-area")
        self.notification_box.set_margin_start(16)
        self.notification_box.set_margin_end(16)
        self.notification_box.set_margin_top(16)
        self.notification_box.set_margin_bottom(16)
        
        # Add to parent window
        if hasattr(self.parent_window, 'notification_overlay'):
            self.parent_window.notification_overlay.add_overlay(self.notification_box)
        else:
            # Create overlay if it doesn't exist
            self.parent_window.notification_overlay = Gtk.Overlay()
            self.parent_window.notification_overlay.add_overlay(self.notification_box)
            
            # Replace the main child with overlay
            main_child = self.parent_window.get_child()
            self.parent_window.notification_overlay.set_child(main_child)
            self.parent_window.set_child(self.parent_window.notification_overlay)
    
    def show_notification(self, message, notification_type="info", duration=3000):
        """
        Show a notification.
        
        Args:
            message (str): The notification message
            notification_type (str): Type of notification (info, success, warning, error)
            duration (int): Duration in milliseconds (0 for persistent)
        """
        notification = NotificationToast(message, notification_type, duration)
        
        # Add to notification area
        self.notification_box.append(notification)
        self.notifications.append(notification)
        
        # Show the notification
        notification.show()
        
        # Auto-remove after duration
        if duration > 0:
            GLib.timeout_add(duration, self._remove_notification, notification)
        
        return notification
    
    def show_info(self, message, duration=3000):
        """Show an info notification."""
        return self.show_notification(message, "info", duration)
    
    def show_success(self, message, duration=3000):
        """Show a success notification."""
        return self.show_notification(message, "success", duration)
    
    def show_warning(self, message, duration=5000):
        """Show a warning notification."""
        return self.show_notification(message, "warning", duration)
    
    def show_error(self, message, duration=0):
        """Show an error notification (persistent by default)."""
        return self.show_notification(message, "error", duration)
    
    def _remove_notification(self, notification):
        """Remove a notification from the display."""
        if notification in self.notifications:
            self.notifications.remove(notification)
            self.notification_box.remove(notification)
        return False  # Stop the timeout
    
    def clear_all(self):
        """Clear all notifications."""
        for notification in self.notifications[:]:
            self._remove_notification(notification)


class NotificationToast(Gtk.Revealer):
    """
    A toast notification component.
    """
    
    def __init__(self, message, notification_type="info", duration=3000):
        super().__init__()
        
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        
        # Apply styling
        self.add_css_class("notification-toast")
        self.add_css_class(f"notification-{notification_type}")
        
        # Set reveal properties
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        self.set_reveal_child(True)
        
        self._build_toast()
    
    def _build_toast(self):
        """Build the toast notification content."""
        
        # Main container
        toast_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        toast_box.add_css_class("toast-content")
        toast_box.set_margin_start(16)
        toast_box.set_margin_end(16)
        toast_box.set_margin_top(12)
        toast_box.set_margin_bottom(12)
        
        # Icon
        icon_name = self._get_icon_name()
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(20)
        icon.add_css_class("toast-icon")
        toast_box.append(icon)
        
        # Message
        message_label = Gtk.Label(label=self.message)
        message_label.add_css_class("toast-message")
        message_label.set_hexpand(True)
        message_label.set_halign(Gtk.Align.START)
        message_label.set_wrap(True)
        message_label.set_max_width_chars(50)
        toast_box.append(message_label)
        
        # Close button
        close_button = Gtk.Button()
        close_button.add_css_class("toast-close")
        close_button.set_icon_name("window-close-symbolic")
        close_button.connect("clicked", self._on_close_clicked)
        toast_box.append(close_button)
        
        self.set_child(toast_box)
    
    def _get_icon_name(self):
        """Get the appropriate icon name for the notification type."""
        icons = {
            "info": "dialog-information-symbolic",
            "success": "emblem-ok-symbolic",
            "warning": "dialog-warning-symbolic",
            "error": "dialog-error-symbolic"
        }
        return icons.get(self.notification_type, "dialog-information-symbolic")
    
    def _on_close_clicked(self, button):
        """Handle close button click."""
        self.close()
    
    def close(self):
        """Close the notification with animation."""
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        self.set_reveal_child(False)
        
        # Remove after animation
        GLib.timeout_add(300, self._remove_self)
    
    def _remove_self(self):
        """Remove self from parent."""
        parent = self.get_parent()
        if parent:
            parent.remove(self)
        return False


class AlertDialog:
    def __init__(self, parent_window, title, message, dialog_type="info"):
        self.parent_window = parent_window
        self.title = title
        self.message = message
        self.dialog_type = dialog_type
        self.dialog = None
    
    def show(self):
        """Show the alert dialog."""
        self.dialog = Gtk.Dialog(
            title=self.title,
            transient_for=self.parent_window,
            modal=True
        )
        
        # Add buttons
        self.dialog.add_button("OK", Gtk.ResponseType.OK)
        
        # Create content
        content_area = self.dialog.get_content_area()
        content_area.set_spacing(12)
        content_area.set_margin_start(16)
        content_area.set_margin_end(16)
        content_area.set_margin_top(16)
        content_area.set_margin_bottom(16)
        
        # Icon and message
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        # Icon
        icon_name = self._get_icon_name()
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(48)
        box.append(icon)
        
        # Message
        message_label = Gtk.Label(label=self.message)
        message_label.set_wrap(True)
        message_label.set_hexpand(True)
        message_label.set_halign(Gtk.Align.START)
        box.append(message_label)
        
        content_area.append(box)
        
        # Show dialog
        self.dialog.present()
        
        # Connect response signal
        self.dialog.connect("response", self._on_response)
    
    def _get_icon_name(self):
        """Get the appropriate icon name for the dialog type."""
        icons = {
            "info": "dialog-information",
            "success": "emblem-ok",
            "warning": "dialog-warning",
            "error": "dialog-error",
            "question": "dialog-question"
        }
        return icons.get(self.dialog_type, "dialog-information")
    
    def _on_response(self, dialog, response_id):
        """Handle dialog response."""
        dialog.destroy()
    
    @staticmethod
    def show_info(parent_window, title, message):
        """Show an info dialog."""
        alert = AlertDialog(parent_window, title, message, "info")
        alert.show()
    
    @staticmethod
    def show_warning(parent_window, title, message):
        """Show a warning dialog."""
        alert = AlertDialog(parent_window, title, message, "warning")
        alert.show()
    
    @staticmethod
    def show_error(parent_window, title, message):
        """Show an error dialog."""
        alert = AlertDialog(parent_window, title, message, "error")
        alert.show()
    
    @staticmethod
    def show_question(parent_window, title, message):
        """Show a question dialog."""
        alert = AlertDialog(parent_window, title, message, "question")
        alert.show()
