import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib

from .light_theme import LightTheme
from .dark_theme import DarkTheme


class ThemeManager:
    def __init__(self, application):
        self.application = application
        self.current_theme = "dark"
        self.themes = {
            "light": LightTheme(),
            "dark": DarkTheme()
        }
        self.css_provider = None
        
        # Initialize theme
        self._setup_theme()
    
    def _setup_theme(self):
        """Setup the initial theme."""
        self.css_provider = Gtk.CssProvider()
        self.apply_theme(self.current_theme)
    
    def apply_theme(self, theme_name):
        """
        Apply a theme to the application.
        
        Args:
            theme_name (str): Name of the theme to apply
        """
        if theme_name not in self.themes:
            print(f"Theme '{theme_name}' not found")
            return
        
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        
        # Get CSS content
        css_content = theme.get_css()
        
        # Load CSS
        self.css_provider.load_from_data(css_content.encode())
        
        # Apply to display
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display,
                self.css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        
        # Update application window styling
        self._update_window_styling()
    
    def _update_window_styling(self):
        """Update window styling based on current theme."""
        theme = self.themes[self.current_theme]
        
        # Update window background
        if hasattr(self.application, 'win'):
            window = self.application.win
            style_context = window.get_style_context()
            
            # Remove old theme classes
            for theme_name in self.themes.keys():
                style_context.remove_class(f"theme-{theme_name}")
            
            # Add current theme class
            style_context.add_class(f"theme-{self.current_theme}")
    
    def get_current_theme(self):
        """Get the name of the current theme."""
        return self.current_theme
    
    def is_dark(self):
        """Check if the current theme is dark."""
        return self.current_theme == "dark"
    
    def get_available_themes(self):
        """Get list of available theme names."""
        return list(self.themes.keys())
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        if self.current_theme == "light":
            self.apply_theme("dark")
        else:
            self.apply_theme("light")
    
    def get_theme_colors(self):
        """Get the colors of the current theme."""
        theme = self.themes[self.current_theme]
        return theme.get_colors()
    
    def get_theme_css(self):
        """Get the CSS of the current theme."""
        theme = self.themes[self.current_theme]
        return theme.get_css()
    
    def add_custom_theme(self, name, theme_instance):
        """
        Add a custom theme.
        
        Args:
            name (str): Theme name
            theme_instance: Theme instance implementing get_css() method
        """
        self.themes[name] = theme_instance
    
    def remove_theme(self, name):
        """
        Remove a theme.
        
        Args:
            name (str): Theme name to remove
        """
        if name in self.themes and name not in ["light", "dark"]:
            del self.themes[name]
            
            # If current theme was removed, switch to light theme
            if self.current_theme == name:
                self.apply_theme("light")
    
    def reload_theme(self):
        """Reload the current theme."""
        self.apply_theme(self.current_theme)
