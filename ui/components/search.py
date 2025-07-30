import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject


class SearchBar(Gtk.Box):
    __gsignals__ = {
        "search-changed": (GObject.SignalFlags.RUN_LAST, None, (str,))
    }
    """
    A search bar component with filtering capabilities.
    """
    
    def __init__(self, placeholder="Search...", **kwargs):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, **kwargs)
        
        self.placeholder = placeholder
        self.search_text = ""
        self.filters = {}
        self.callbacks = []
        
        # Apply styling
        self.add_css_class("search-bar")
        self.set_margin_start(8)
        self.set_margin_end(8)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        
        self._build_search_bar()
    
    def _build_search_bar(self):
        """Build the search bar components."""
        
        # Search icon
        search_icon = Gtk.Image.new_from_icon_name("system-search-symbolic")
        search_icon.set_pixel_size(16)
        self.append(search_icon)
        
        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.add_css_class("search-entry")
        self.search_entry.set_placeholder_text(self.placeholder)
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.append(self.search_entry)
        
        # Clear button
        self.clear_button = Gtk.Button()
        self.clear_button.add_css_class("search-clear")
        self.clear_button.set_icon_name("edit-clear-symbolic")
        self.clear_button.connect("clicked", self._on_clear_clicked)
        self.clear_button.set_visible(False)
        self.append(self.clear_button)
    
    def _on_search_changed(self, entry):
        """Handle search text changes."""
        self.search_text = entry.get_text()
        
        # Show/hide clear button
        self.clear_button.set_visible(bool(self.search_text))
        
        # Notify callbacks
        self._notify_search_changed()
    
    def _on_clear_clicked(self, button):
        """Handle clear button click."""
        self.search_entry.set_text("")
        self.search_text = ""
        self.clear_button.set_visible(False)
        self._notify_search_changed()
    
    def _notify_search_changed(self):
        """Notify all registered callbacks of search changes."""
        self.emit("search-changed", self.search_text)
        for callback in self.callbacks:
            callback(self.search_text, self.filters)
    
    def add_search_callback(self, callback):
        """Add a callback function to be called when search changes."""
        self.callbacks.append(callback)
    
    def remove_search_callback(self, callback):
        """Remove a search callback function."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def get_search_text(self):
        """Get the current search text."""
        return self.search_text
    
    def set_search_text(self, text):
        """Set the search text."""
        self.search_entry.set_text(text)
    
    def clear_search(self):
        """Clear the search text."""
        self.search_entry.set_text("")
        self.search_text = ""
        self.clear_button.set_visible(False)
        self._notify_search_changed()


class FilterBar(Gtk.Box):
    __gsignals__ = {
        "filter-changed": (GObject.SignalFlags.RUN_LAST, None, (object,))
    }
    """
    A filter bar component for applying multiple filters.
    """
    
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, **kwargs)
        
        self.filters = {}
        self.callbacks = []
        
        # Apply styling
        self.add_css_class("filter-bar")
        self.set_margin_start(8)
        self.set_margin_end(8)
        self.set_margin_top(4)
        self.set_margin_bottom(4)
        
        self._build_filter_bar()
    
    def _build_filter_bar(self):
        """Build the filter bar components."""
        
        # Filter label
        filter_label = Gtk.Label(label="Filters:")
        filter_label.add_css_class("filter-label")
        self.append(filter_label)
        
        # Filter chips container
        self.chips_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.chips_box.set_hexpand(True)
        self.append(self.chips_box)
        
        # Clear filters button
        self.clear_button = Gtk.Button(label="Clear All")
        self.clear_button.add_css_class("filter-clear")
        self.clear_button.connect("clicked", self._on_clear_all_clicked)
        self.clear_button.set_visible(False)
        self.append(self.clear_button)
    
    def add_filter(self, filter_name, filter_value, display_name=None):
        """Add a filter chip."""
        if display_name is None:
            display_name = f"{filter_name}: {filter_value}"
        
        # Create filter chip
        chip = FilterChip(display_name, filter_name, filter_value)
        chip.connect("removed", self._on_filter_removed)
        
        self.chips_box.append(chip)
        self.filters[filter_name] = filter_value
        
        # Show clear button if we have filters
        self.clear_button.set_visible(True)
        
        # Notify callbacks
        self._notify_filters_changed()
    
    def remove_filter(self, filter_name):
        """Remove a specific filter."""
        if filter_name in self.filters:
            # Remove the chip
            for child in self.chips_box:
                if isinstance(child, FilterChip) and child.filter_name == filter_name:
                    self.chips_box.remove(child)
                    break
            
            # Remove from filters dict
            del self.filters[filter_name]
            
            # Hide clear button if no filters
            if not self.filters:
                self.clear_button.set_visible(False)
            
            # Notify callbacks
            self._notify_filters_changed()
    
    def clear_filters(self):
        """Clear all filters."""
        # Remove all chips
        for child in self.chips_box:
            if isinstance(child, FilterChip):
                self.chips_box.remove(child)
        
        # Clear filters dict
        self.filters.clear()
        
        # Hide clear button
        self.clear_button.set_visible(False)
        
        # Notify callbacks
        self._notify_filters_changed()
    
    def _on_filter_removed(self, chip, filter_name):
        """Handle filter chip removal."""
        self.remove_filter(filter_name)
    
    def _on_clear_all_clicked(self, button):
        """Handle clear all filters button click."""
        self.clear_filters()
    
    def _notify_filters_changed(self):
        """Notify all registered callbacks of filter changes."""
        self.emit("filter-changed", self.filters)
        for callback in self.callbacks:
            callback(self.filters)
    
    def add_filter_callback(self, callback):
        """Add a callback function to be called when filters change."""
        self.callbacks.append(callback)
    
    def remove_filter_callback(self, callback):
        """Remove a filter callback function."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def get_filters(self):
        """Get the current filters."""
        return self.filters.copy()


class FilterChip(Gtk.Box):
    """
    A chip component for displaying active filters.
    """
    
    __gsignals__ = {
        'removed': (GObject.SignalFlags.RUN_LAST, None, (str,))
    }
    
    def __init__(self, display_name, filter_name, filter_value):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        self.display_name = display_name
        self.filter_name = filter_name
        self.filter_value = filter_value
        
        # Apply styling
        self.add_css_class("filter-chip")
        self.set_margin_start(2)
        self.set_margin_end(2)
        self.set_margin_top(2)
        self.set_margin_bottom(2)
        
        self._build_chip()
    
    def _build_chip(self):
        """Build the filter chip content."""
        
        # Label
        label = Gtk.Label(label=self.display_name)
        label.add_css_class("filter-chip-label")
        self.append(label)
        
        # Remove button
        remove_button = Gtk.Button()
        remove_button.add_css_class("filter-chip-remove")
        remove_button.set_icon_name("window-close-symbolic")
        remove_button.set_pixel_size(12)
        remove_button.connect("clicked", self._on_remove_clicked)
        self.append(remove_button)
    
    def _on_remove_clicked(self, button):
        """Handle remove button click."""
        self.emit("removed", self.filter_name)


class ResourceFilter:
    """
    A utility class for filtering Docker resources.
    """
    
    @staticmethod
    def filter_resources(resources, search_text="", filters=None):
        """
        Filter a list of resources based on search text and filters.
        
        Args:
            resources (list): List of resource dictionaries
            search_text (str): Search text to match against
            filters (dict): Dictionary of filters to apply
            
        Returns:
            list: Filtered list of resources
        """
        if filters is None:
            filters = {}
        
        filtered_resources = resources
        
        # Apply search text filter
        if search_text:
            filtered_resources = ResourceFilter._apply_search_filter(
                filtered_resources, search_text
            )
        
        # Apply specific filters
        for filter_name, filter_value in filters.items():
            filtered_resources = ResourceFilter._apply_filter(
                filtered_resources, filter_name, filter_value
            )
        
        return filtered_resources
    
    @staticmethod
    def _apply_search_filter(resources, search_text):
        """Apply search text filter to resources."""
        search_lower = search_text.lower()
        filtered = []
        
        for resource in resources:
            # Search in common fields
            searchable_fields = [
                resource.get("Names", []),
                resource.get("Image", ""),
                resource.get("Repository", ""),
                resource.get("Tag", ""),
                resource.get("Id", ""),
                resource.get("Status", ""),
                resource.get("State", ""),
                resource.get("Driver", ""),
                resource.get("Scope", "")
            ]
            
            # Flatten lists and convert to strings
            searchable_text = []
            for field in searchable_fields:
                if isinstance(field, list):
                    searchable_text.extend(field)
                else:
                    searchable_text.append(str(field))
            
            # Check if any field contains the search text
            if any(search_lower in text.lower() for text in searchable_text):
                filtered.append(resource)
        
        return filtered
    
    @staticmethod
    def _apply_filter(resources, filter_name, filter_value):
        """Apply a specific filter to resources."""
        filtered = []
        
        for resource in resources:
            if ResourceFilter._matches_filter(resource, filter_name, filter_value):
                filtered.append(resource)
        
        return filtered
    
    @staticmethod
    def _matches_filter(resource, filter_name, filter_value):
        """Check if a resource matches a specific filter."""
        if filter_name == "status":
            return resource.get("State", "").lower() == filter_value.lower()
        elif filter_name == "driver":
            return resource.get("Driver", "").lower() == filter_value.lower()
        elif filter_name == "scope":
            return resource.get("Scope", "").lower() == filter_value.lower()
        elif filter_name == "running":
            return resource.get("State", "").lower() == "running"
        elif filter_name == "stopped":
            return resource.get("State", "").lower() in ["stopped", "exited"]
        return True
