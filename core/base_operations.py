import datetime
from typing import Any, Dict, List
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


class BaseOperations:
    # Status colors
    STATUS_COLORS = {
        'running': '#10b981',      # Green
        'stopped': '#ef4444',      # Red
        'paused': '#f59e0b',       # Yellow
        'created': '#3b82f6',      # Blue
        'exited': '#6b7280',       # Gray
        'dead': '#dc2626',         # Dark Red
        'removing': '#f97316',     # Orange
        'default': '#6b7280'       # Gray
    }
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Format the size in bytes to a readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted string of the size
        """
        if size_bytes is None or size_bytes == 0:
            return "0 B"
        
        # Define the units of measurement
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        unit_index = 0
        
        # Convert to the corresponding unit
        size = float(size_bytes)
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1
        
        # Format with one decimal place
        if unit_index == 0:  # Bytes - no decimal places
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"
    
    @staticmethod
    def format_date(date_string: str, format_type: str = "relative") -> str:
        """
        Format the date to a readable format.
        
        Args:
            date_string: String with the date
            format_type: Format type ("relative", "short", "full")
            
        Returns:
            Formatted string of the date
        """
        if not date_string:
            return "Неизвестно"
        
        try:
            # Parse the date (assuming ISO format)
            if 'T' in date_string:
                # ISO format with time
                dt = datetime.datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            else:
                # Only the date
                dt = datetime.datetime.fromisoformat(date_string)
            
            now = datetime.datetime.now(dt.tzinfo) if dt.tzinfo else datetime.datetime.now()
            
            if format_type == "relative":
                return BaseOperations._format_relative_date(dt, now)
            elif format_type == "short":
                return dt.strftime("%d.%m.%Y %H:%M")
            elif format_type == "full":
                return dt.strftime("%d.%m.%Y %H:%M:%S")
            else:
                return dt.strftime("%d.%m.%Y %H:%M")
                
        except (ValueError, TypeError):
            return "Неизвестно"
    
    @staticmethod
    def _format_relative_date(dt: datetime.datetime, now: datetime.datetime) -> str:
        """
        Format the relative date.
        
        Args:
            dt: Date to format
            now: Current date
            
        Returns:
            Relative date as a string
        """
        diff = now - dt
        
        if diff.days == 0:
            if diff.seconds < 60:
                return "Только что"
            elif diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"{minutes} мин. назад"
            else:
                hours = diff.seconds // 3600
                return f"{hours} ч. назад"
        elif diff.days == 1:
            return "Вчера"
        elif diff.days < 7:
            return f"{diff.days} дн. назад"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} нед. назад"
        elif diff.days < 365:
            months = diff.days // 30
            return f"{months} мес. назад"
        else:
            years = diff.days // 365
            return f"{years} лет назад"
    
    @staticmethod
    def get_status_color(status: str) -> str:
        """
        Get the color for the status.
        
        Args:
            status: Status of the resource
            
        Returns:
            HEX code of the color
        """
        status_lower = status.lower() if status else 'default'
        return BaseOperations.STATUS_COLORS.get(status_lower, BaseOperations.STATUS_COLORS['default'])
    
    @staticmethod
    def get_status_icon(status: str) -> str:
        """
        Get the icon for the status.
        
        Args:
            status: Status of the resource
            
        Returns:
            Name of the icon
        """
        status_icons = {
            'running': 'media-playback-start-symbolic',
            'stopped': 'media-playback-stop-symbolic',
            'paused': 'media-playback-pause-symbolic',
            'created': 'document-new-symbolic',
            'exited': 'application-exit-symbolic',
            'dead': 'process-stop-symbolic',
            'removing': 'edit-delete-symbolic',
            'default': 'help-about-symbolic'
        }
        
        status_lower = status.lower() if status else 'default'
        return status_icons.get(status_lower, status_icons['default'])
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 50) -> str:
        """
        Truncate the text to the specified length.
        
        Args:
            text: Original text
            max_length: Maximum length
            
        Returns:
            Truncated text
        """
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length-3] + "..."
    
    @staticmethod
    def create_property_list(properties: Dict[str, Any]) -> Gtk.Widget:
        """
        Create a list of properties for display.
        
        Args:
            properties: Dictionary of properties
            
        Returns:
            GTK widget with the list of properties
        """
        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        
        for key, value in properties.items():
            row = Gtk.ListBoxRow()
            
            # Create a container for the row
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            box.set_margin_start(12)
            box.set_margin_end(12)
            box.set_margin_top(8)
            box.set_margin_bottom(8)
            
            # Key
            key_label = Gtk.Label(label=f"{key}:")
            key_label.set_xalign(0)
            key_label.set_hexpand(False)
            key_label.set_css_classes(['dim-label'])
            box.append(key_label)
            
            # Value
            value_str = str(value) if value is not None else "Не указано"
            value_label = Gtk.Label(label=value_str)
            value_label.set_xalign(0)
            value_label.set_hexpand(True)
            value_label.set_wrap(True)
            box.append(value_label)
            
            row.set_child(box)
            list_box.append(row)
        
        return list_box
    
    @staticmethod
    def create_action_button(label: str, icon_name: str, action: str, 
                           tooltip: str = None) -> Gtk.Button:
        """
        Create an action button.
        
        Args:
            label: Text of the button
            icon_name: Name of the icon
            action: Action of the button
            tooltip: Tooltip
            
        Returns:
            GTK button
        """
        button = Gtk.Button()
        button.set_label(label)
        button.set_icon_name(icon_name)
        
        if tooltip:
            button.set_tooltip_text(tooltip)
        
        # Add CSS class for styling
        button.set_css_classes(['action-button'])
        
        return button
    
    @staticmethod
    def create_info_card(title: str, content: str, icon_name: str = None) -> Gtk.Widget:
        """
        Create an information card.
        
        Args:
            title: Title of the card
            content: Content of the card
            icon_name: Name of the icon
            
        Returns:
            GTK card
        """
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.set_css_classes(['card', 'info-card'])
        card.set_margin_start(8)
        card.set_margin_end(8)
        card.set_margin_top(8)
        card.set_margin_bottom(8)
        
        # Title
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        if icon_name:
            icon = Gtk.Image()
            icon.set_from_icon_name(icon_name)
            title_box.append(icon)
        
        title_label = Gtk.Label(label=title)
        title_label.set_css_classes(['heading'])
        title_label.set_xalign(0)
        title_box.append(title_label)
        
        card.append(title_box)
        
        # Content
        content_label = Gtk.Label(label=content)
        content_label.set_xalign(0)
        content_label.set_wrap(True)
        card.append(content_label)
        
        return card
    
    @staticmethod
    def create_loading_spinner() -> Gtk.Widget:
        """
        Create a loading spinner.
        
        Returns:
            GTK spinner
        """
        spinner = Gtk.Spinner()
        spinner.set_visible(True)
        spinner.start()
        
        # Center the spinner
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_vexpand(True)
        box.set_hexpand(True)
        box.append(spinner)
        
        return box
    
    @staticmethod
    def create_empty_state(message: str, icon_name: str = "dialog-information-symbolic") -> Gtk.Widget:
        """
        Create an empty state.
        
        Args:
            message: Message
            icon_name: Name of the icon
            
        Returns:
            GTK widget of the empty state
        """
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_vexpand(True)
        box.set_hexpand(True)
        
        # Icon
        icon = Gtk.Image()
        icon.set_from_icon_name(icon_name)
        icon.set_pixel_size(64)
        icon.set_css_classes(['dim-label'])
        box.append(icon)
        
        # Message
        message_label = Gtk.Label(label=message)
        message_label.set_css_classes(['dim-label', 'heading'])
        message_label.set_wrap(True)
        box.append(message_label)
        
        return box
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """
        Format the duration in seconds.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted string of the duration
        """
        if seconds is None or seconds < 0:
            return "Неизвестно"
        
        if seconds < 60:
            return f"{seconds} сек"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes} мин {remaining_seconds} сек"
        elif seconds < 86400:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            return f"{hours} ч {remaining_minutes} мин"
        else:
            days = seconds // 86400
            remaining_hours = (seconds % 86400) // 3600
            return f"{days} дн {remaining_hours} ч"
    
    @staticmethod
    def format_port_mapping(ports: List[Dict[str, Any]]) -> str:
        """
        Format the port mapping.
        
        Args:
            ports: List of ports
            
        Returns:
            Formatted string of the ports
        """
        if not ports:
            return "Нет"
        
        formatted_ports = []
        for port in ports:
            if isinstance(port, dict):
                host_port = port.get('HostPort', '')
                container_port = port.get('ContainerPort', '')
                if host_port and container_port:
                    formatted_ports.append(f"{host_port}:{container_port}")
                elif container_port:
                    formatted_ports.append(container_port)
            else:
                formatted_ports.append(str(port))
        
        return ", ".join(formatted_ports)
    
    @staticmethod
    def format_environment_variables(env_vars: List[str]) -> str:
        """
        Format the environment variables.
        
        Args:
            env_vars: List of environment variables
            
        Returns:
            Formatted string of the environment variables
        """
        if not env_vars:
            return "Нет"
        
        # Show only the first few variables
        if len(env_vars) <= 3:
            return ", ".join(env_vars)
        else:
            return f"{', '.join(env_vars[:3])} и еще {len(env_vars) - 3}"
