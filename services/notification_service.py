import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from typing import Dict, Any, Optional, Callable
import time


class NotificationService:
    TYPE_SUCCESS = "success"
    TYPE_WARNING = "warning"
    TYPE_ERROR = "error"
    TYPE_INFO = "info"
    
    def __init__(self, parent_window: Optional[Gtk.Window] = None):
        self.parent_window = parent_window
        self.notifications = []
        self.notification_container = None
        self._callbacks = []
        
        # Default settings
        self.auto_dismiss_timeout = 5000  # 5 seconds
        self.max_notifications = 5
        self.enable_sounds = True
        
    def add_callback(self, callback: Callable):
        """
        Add a callback for notifications.
        
        Args:
            callback: Callback function
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """
        Remove a callback.
        
        Args:
            callback: Callback function to remove
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _notify_callbacks(self, event_type: str, data: Any = None):
        """
        Notify all registered callbacks.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        for callback in self._callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                print(f"Error in notification callback: {e}")
    
    def create_notification_container(self) -> Gtk.Widget:
        """
        Create a container for notifications.
        
        Returns:
            GTK widget for the notification container
        """
        self.notification_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.notification_container.set_margin_start(16)
        self.notification_container.set_margin_end(16)
        self.notification_container.set_margin_top(16)
        self.notification_container.set_margin_bottom(16)
        
        # Set position in the top right corner
        self.notification_container.set_halign(Gtk.Align.END)
        self.notification_container.set_valign(Gtk.Align.START)
        
        return self.notification_container
    
    def show_notification(self, message: str, notification_type: str = TYPE_INFO, 
                         title: str = None, timeout: int = None, 
                         actions: Dict[str, Callable] = None, 
                         dismissible: bool = True) -> str:
        """
        Show a notification.
        
        Args:
            message: Notification message
            notification_type: Notification type
            title: Notification title
            timeout: Time to automatically dismiss (ms)
            actions: Dictionary of actions {text: function}
            dismissible: Can the notification be dismissed
            
        Returns:
            Notification ID
        """
        notification_id = f"notification_{int(time.time() * 1000)}"
        
        # Create notification widget
        notification_widget = self._create_notification_widget(
            notification_id, message, notification_type, title, actions, dismissible
        )
        
        # Add to container
        if self.notification_container:
            self.notification_container.append(notification_widget)
            
            # Limit the number of notifications
            if len(self.notifications) >= self.max_notifications:
                self._remove_oldest_notification()
        
        # Save notification information
        notification_info = {
            'id': notification_id,
            'widget': notification_widget,
            'type': notification_type,
            'message': message,
            'created_at': time.time()
        }
        self.notifications.append(notification_info)
        
        # Set automatic dismissal
        if timeout is None:
            timeout = self.auto_dismiss_timeout
        
        if timeout > 0:
            GLib.timeout_add(timeout, self._auto_dismiss_notification, notification_id)
        
        # Notify callbacks
        self._notify_callbacks('notification_shown', notification_info)
        
        return notification_id
    
    def _create_notification_widget(self, notification_id: str, message: str, 
                                   notification_type: str, title: str = None,
                                   actions: Dict[str, Callable] = None,
                                   dismissible: bool = True) -> Gtk.Widget:
        """
        Create a notification widget.
        
        Args:
            notification_id: Notification ID
            message: Notification message
            notification_type: Notification type
            title: Notification title
            actions: Actions
            dismissible: Can the notification be dismissed
            
        Returns:
            GTK widget for the notification
        """
        # Main container
        notification_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        notification_box.set_css_classes(['notification', f'notification-{notification_type}'])
        notification_box.set_margin_start(8)
        notification_box.set_margin_end(8)
        notification_box.set_margin_top(4)
        notification_box.set_margin_bottom(4)
        
        # Header and close button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        # Notification type icon
        icon_name = self._get_notification_icon(notification_type)
        icon = Gtk.Image()
        icon.set_from_icon_name(icon_name)
        icon.set_pixel_size(16)
        header_box.append(icon)
        
        # Title
        if title:
            title_label = Gtk.Label(label=title)
            title_label.set_css_classes(['heading'])
            title_label.set_xalign(0)
            title_label.set_hexpand(True)
            header_box.append(title_label)
        
        # Close button
        if dismissible:
            close_button = Gtk.Button()
            close_button.set_icon_name("window-close-symbolic")
            close_button.set_tooltip_text("Закрыть")
            close_button.set_css_classes(['flat'])
            close_button.connect("clicked", self._on_close_notification, notification_id)
            header_box.append(close_button)
        
        notification_box.append(header_box)
        
        # Message
        message_label = Gtk.Label(label=message)
        message_label.set_xalign(0)
        message_label.set_wrap(True)
        message_label.set_hexpand(True)
        notification_box.append(message_label)
        
        # Actions
        if actions:
            actions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            actions_box.set_halign(Gtk.Align.END)
            
            for action_text, action_func in actions.items():
                action_button = Gtk.Button(label=action_text)
                action_button.set_css_classes(['flat'])
                action_button.connect("clicked", self._on_action_clicked, 
                                    notification_id, action_func)
                actions_box.append(action_button)
            
            notification_box.append(actions_box)
        
        return notification_box
    
    def _get_notification_icon(self, notification_type: str) -> str:
        """
        Get the icon for the notification type.
        
        Args:
            notification_type: Notification type
            
        Returns:
            Icon name
        """
        icons = {
            self.TYPE_SUCCESS: "emblem-ok-symbolic",
            self.TYPE_WARNING: "dialog-warning-symbolic",
            self.TYPE_ERROR: "dialog-error-symbolic",
            self.TYPE_INFO: "dialog-information-symbolic"
        }
        return icons.get(notification_type, icons[self.TYPE_INFO])
    
    def _on_close_notification(self, button, notification_id: str):
        """
        Handler for closing the notification.
        
        Args:
            button: Close button
            notification_id: Notification ID
        """
        self.dismiss_notification(notification_id)
    
    def _on_action_clicked(self, button, notification_id: str, action_func: Callable):
        """
        Handler for clicking an action.
        
        Args:
            button: Action button
            notification_id: Notification ID
            action_func: Action function
        """
        try:
            action_func()
            self.dismiss_notification(notification_id)
        except Exception as e:
            print(f"Error executing notification action: {e}")
    
    def _auto_dismiss_notification(self, notification_id: str) -> bool:
        """
        Automatically dismiss the notification.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            False to stop the timer
        """
        self.dismiss_notification(notification_id)
        return False
    
    def dismiss_notification(self, notification_id: str):
        """
        Hide the notification.
        
        Args:
            notification_id: Notification ID
        """
        notification_info = self._find_notification(notification_id)
        if not notification_info:
            return
        
        # Remove the widget
        if self.notification_container and notification_info['widget']:
            self.notification_container.remove(notification_info['widget'])
        
        # Remove from the list
        self.notifications.remove(notification_info)
        
        # Notify callbacks
        self._notify_callbacks('notification_dismissed', notification_info)
    
    def _find_notification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a notification by ID.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            Notification information or None
        """
        for notification in self.notifications:
            if notification['id'] == notification_id:
                return notification
        return None
    
    def _remove_oldest_notification(self):
        """
        Remove the oldest notification.
        """
        if self.notifications:
            oldest = self.notifications[0]
            self.dismiss_notification(oldest['id'])
    
    def clear_all_notifications(self):
        """
        Clear all notifications.
        """
        notification_ids = [n['id'] for n in self.notifications.copy()]
        for notification_id in notification_ids:
            self.dismiss_notification(notification_id)
    
    def show_success(self, message: str, title: str = "Успешно", **kwargs) -> str:
        """
        Show a success notification.
        
        Args:
            message: Message
            title: Title
            **kwargs: Additional parameters
            
        Returns:
            Notification ID
        """
        return self.show_notification(message, self.TYPE_SUCCESS, title, **kwargs)
    
    def show_warning(self, message: str, title: str = "Предупреждение", **kwargs) -> str:
        """
        Show a warning notification.
        
        Args:
            message: Message
            title: Title
            **kwargs: Additional parameters
            
        Returns:
            Notification ID
        """
        return self.show_notification(message, self.TYPE_WARNING, title, **kwargs)
    
    def show_error(self, message: str, title: str = "Ошибка", **kwargs) -> str:
        """
        Show an error notification.
        
        Args:
            message: Message
            title: Title
            **kwargs: Additional parameters
            
        Returns:
            Notification ID
        """
        return self.show_notification(message, self.TYPE_ERROR, title, **kwargs)
    
    def show_info(self, message: str, title: str = "Информация", **kwargs) -> str:
        """
        Show an info notification.
        
        Args:
            message: Message
            title: Title
            **kwargs: Additional parameters
            
        Returns:
            Notification ID
        """
        return self.show_notification(message, self.TYPE_INFO, title, **kwargs)
    
    def show_confirm_dialog(self, message: str, title: str = "Подтверждение",
                           confirm_text: str = "Да", cancel_text: str = "Отмена") -> bool:
        """
        Show a confirmation dialog.
        
        Args:
            message: Message
            title: Title
            confirm_text: Text for the confirm button
            cancel_text: Text for the cancel button
            
        Returns:
            True if confirmed
        """
        dialog = Gtk.Dialog(title=title, transient_for=self.parent_window)
        dialog.set_modal(True)
        dialog.add_button(cancel_text, Gtk.ResponseType.CANCEL)
        dialog.add_button(confirm_text, Gtk.ResponseType.OK)
        
        # Dialog content
        content_area = dialog.get_content_area()
        content_area.set_margin_start(16)
        content_area.set_margin_end(16)
        content_area.set_margin_top(16)
        content_area.set_margin_bottom(16)
        
        message_label = Gtk.Label(label=message)
        message_label.set_wrap(True)
        content_area.append(message_label)
        
        dialog.show()
        response = dialog.run()
        dialog.destroy()
        
        return response == Gtk.ResponseType.OK
    
    def set_auto_dismiss_timeout(self, timeout: int):
        """
        Set the time to automatically dismiss.
        
        Args:
            timeout: Time in milliseconds
        """
        self.auto_dismiss_timeout = timeout
    
    def set_max_notifications(self, max_count: int):
        """
        Set the maximum number of notifications.
        
        Args:
            max_count: Maximum number
        """
        self.max_notifications = max_count
    
    def get_active_notifications(self) -> list:
        """
        Get active notifications.
        
        Returns:
            List of active notifications
        """
        return self.notifications.copy()
