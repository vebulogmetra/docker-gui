import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib


class LoadingIndicator(Gtk.Box):
    def __init__(self, message: str = "Loading..."):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.set_hexpand(True)
        self.set_vexpand(True)
        
        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(48, 48)
        
        self.message_label = Gtk.Label(label=message)
        self.message_label.set_css_classes(['title-3'])
        
        self.info_label = Gtk.Label(label="")
        self.info_label.set_css_classes(['caption'])
        self.info_label.set_visible(False)
        
        self.append(self.spinner)
        self.append(self.message_label)
        self.append(self.info_label)
        
        self.spinner.start()
        
        self.set_visible(False)
    
    def show_loading(self, message: str = None, info: str = None):
        """
        Show the loading indicator.
        
        Args:
            message: Main message
            info: Additional information
        """
        if message:
            self.message_label.set_label(message)
        
        if info:
            self.info_label.set_label(info)
            self.info_label.set_visible(True)
        else:
            self.info_label.set_visible(False)
        
        self.set_visible(True)
        self.spinner.start()
    
    def hide_loading(self):
        """Hide the loading indicator."""
        self.set_visible(False)
        self.spinner.stop()
    
    def update_message(self, message: str):
        """
        Update the message.
        
        Args:
            message: New message
        """
        self.message_label.set_label(message)
    
    def update_info(self, info: str):
        """
        Update the additional information.
        
        Args:
            info: New information
        """
        if info:
            self.info_label.set_label(info)
            self.info_label.set_visible(True)
        else:
            self.info_label.set_visible(False)


class ProgressIndicator(Gtk.Box):
    def __init__(self, message: str = "Processing..."):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.set_hexpand(True)
        self.set_vexpand(True)
        
        self.message_label = Gtk.Label(label=message)
        self.message_label.set_css_classes(['title-4'])
        
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_size_request(300, 20)
        self.progress_bar.set_show_text(True)
        
        self.info_label = Gtk.Label(label="")
        self.info_label.set_css_classes(['caption'])
        self.info_label.set_visible(False)
        
        self.append(self.message_label)
        self.append(self.progress_bar)
        self.append(self.info_label)
        
        self.set_visible(False)
    
    def show_progress(self, message: str = None, fraction: float = 0.0, info: str = None):
        """
        Show the progress indicator.
        
        Args:
            message: Main message
            fraction: Fraction of completion (0.0 - 1.0)
            info: Additional information
        """
        if message:
            self.message_label.set_label(message)
        
        self.progress_bar.set_fraction(fraction)
        
        if info:
            self.info_label.set_label(info)
            self.info_label.set_visible(True)
        else:
            self.info_label.set_visible(False)
        
        self.set_visible(True)
    
    def hide_progress(self):
        """Hide the progress indicator."""
        self.set_visible(False)
        self.progress_bar.set_fraction(0.0)
    
    def update_progress(self, fraction: float, message: str = None, info: str = None):
        """
        Update the progress.
        
        Args:
            fraction: Fraction of completion (0.0 - 1.0)
            message: New message
            info: New information
        """
        self.progress_bar.set_fraction(fraction)
        
        if message:
            self.message_label.set_label(message)
        
        if info:
            self.info_label.set_label(info)
            self.info_label.set_visible(True)
        else:
            self.info_label.set_visible(False)


class StatusIndicator(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.CENTER)
        
        self.status_icon = Gtk.Image()
        self.status_icon.set_size_request(16, 16)
        
        self.status_label = Gtk.Label(label="")
        self.status_label.set_css_classes(['caption'])
        
        self.append(self.status_icon)
        self.append(self.status_label)
        
        self.set_visible(False)
    
    def show_success(self, message: str):
        """
        Show the success status.
        
        Args:
            message: Success message
        """
        self.status_icon.set_from_icon_name("emblem-ok-symbolic")
        self.status_label.set_label(message)
        self.status_label.set_css_classes(['caption', 'success'])
        self.set_visible(True)
        
        GLib.timeout_add(3000, self.hide_status)
    
    def show_error(self, message: str):
        """
        Show the error status.
        
        Args:
            message: Error message
        """
        self.status_icon.set_from_icon_name("dialog-error-symbolic")
        self.status_label.set_label(message)
        self.status_label.set_css_classes(['caption', 'error'])
        self.set_visible(True)
        
        GLib.timeout_add(5000, self.hide_status)
    
    def show_warning(self, message: str):
        """
        Show the warning status.
        
        Args:
            message: Warning message
        """
        self.status_icon.set_from_icon_name("dialog-warning-symbolic")
        self.status_label.set_label(message)
        self.status_label.set_css_classes(['caption', 'warning'])
        self.set_visible(True)
        
        GLib.timeout_add(4000, self.hide_status)
    
    def show_info(self, message: str):
        """
        Show the informational status.
        
        Args:
            message: Informational message
        """
        self.status_icon.set_from_icon_name("dialog-information-symbolic")
        self.status_label.set_label(message)
        self.status_label.set_css_classes(['caption', 'info'])
        self.set_visible(True)
        
        GLib.timeout_add(3000, self.hide_status)
    
    def hide_status(self):
        """Hide the status indicator."""
        self.set_visible(False)
        return False
