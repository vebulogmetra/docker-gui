import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod


class ResourceView(ABC):
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.view_mode = "list"  # "list" или "cards"
        self.search_bar = None
        self.filter_bar = None
        self.main_container = None
        self.list_view = None
        self.cards_view = None
        self.loading_spinner = None
        
        # Subscribe to events from the resource manager
        self.resource_manager.add_callback(self._on_resource_event)
        
    def create_view(self) -> Gtk.Widget:
        """
        Create the view.
        
        Returns:
            GTK widget of the view
        """
        # Create the main container
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Create the toolbar
        toolbar = self._create_toolbar()
        self.main_container.append(toolbar)
        
        # Create the search and filter panel
        search_filter_panel = self._create_search_filter_panel()
        self.main_container.append(search_filter_panel)
        
        # Create the loading spinner
        self.loading_spinner = Gtk.Spinner()
        self.loading_spinner.set_visible(False)
        self.main_container.append(self.loading_spinner)
        
        # Create the container for the views
        view_container = Gtk.Stack()
        view_container.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        
        # Create the views
        self.list_view = self._create_list_view()
        self.cards_view = self._create_cards_view()
        
        view_container.add_titled(self.list_view, "list", "Список")
        view_container.add_titled(self.cards_view, "cards", "Карточки")
        
        self.main_container.append(view_container)
        
        # Set the initial view mode
        self.switch_view_mode(self.view_mode)
        
        return self.main_container
    
    def _create_toolbar(self) -> Gtk.Widget:
        """
        Create the toolbar.
        
        Returns:
            GTK widget of the toolbar
        """
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        # Refresh button
        refresh_button = Gtk.Button()
        refresh_button.set_icon_name("view-refresh-symbolic")
        refresh_button.set_tooltip_text("Обновить")
        refresh_button.connect("clicked", self._on_refresh_clicked)
        toolbar.append(refresh_button)
        
        # View mode switcher
        view_mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        list_button = Gtk.ToggleButton()
        list_button.set_icon_name("view-list-symbolic")
        list_button.set_tooltip_text("Список")
        list_button.connect("toggled", self._on_list_mode_toggled)
        
        cards_button = Gtk.ToggleButton()
        cards_button.set_icon_name("view-grid-symbolic")
        cards_button.set_tooltip_text("Карточки")
        cards_button.connect("toggled", self._on_cards_mode_toggled)
        
        view_mode_box.append(list_button)
        view_mode_box.append(cards_button)
        
        # Group the view mode buttons
        view_mode_group = Gtk.ButtonGroup()
        view_mode_group.add(list_button)
        view_mode_group.add(cards_button)
        
        toolbar.append(view_mode_box)
        
        # Add a spacer
        toolbar.append(Gtk.Box())  # Spacer
        
        # Action buttons
        actions_box = self._create_action_buttons()
        toolbar.append(actions_box)
        
        return toolbar
    
    def _create_search_filter_panel(self) -> Gtk.Widget:
        """
        Create the search and filter panel.
        
        Returns:
            GTK widget of the search and filter panel
        """
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # Search panel
        search_panel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        search_label = Gtk.Label(label="Поиск:")
        search_panel.append(search_label)
        
        self.search_bar = self._create_search_bar()
        search_panel.append(self.search_bar)
        
        panel.append(search_panel)
        
        # Filter panel
        filter_panel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        filter_label = Gtk.Label(label="Фильтры:")
        filter_panel.append(filter_label)
        
        self.filter_bar = self._create_filter_bar()
        filter_panel.append(self.filter_bar)
        
        panel.append(filter_panel)
        
        return panel
    
    def _create_search_bar(self) -> Gtk.Widget:
        """
        Create the search panel.
        
        Returns:
            GTK widget of the search panel
        """
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        search_entry = Gtk.SearchEntry()
        search_entry.set_placeholder_text("Введите текст для поиска...")
        search_entry.connect("search-changed", self._on_search_changed)
        search_box.append(search_entry)
        
        clear_button = Gtk.Button()
        clear_button.set_icon_name("edit-clear-symbolic")
        clear_button.set_tooltip_text("Очистить поиск")
        clear_button.connect("clicked", self._on_clear_search_clicked)
        clear_button.set_visible(False)
        search_box.append(clear_button)
        
        return search_box
    
    def _create_filter_bar(self) -> Gtk.Widget:
        """
        Create the filter panel.
        
        Returns:
            GTK widget of the filter panel
        """
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        # Base filters (will be overridden in subclasses)
        filter_box.append(Gtk.Label(label="Фильтры не реализованы"))
        
        clear_filters_button = Gtk.Button()
        clear_filters_button.set_icon_name("edit-clear-symbolic")
        clear_filters_button.set_tooltip_text("Очистить фильтры")
        clear_filters_button.connect("clicked", self._on_clear_filters_clicked)
        filter_box.append(clear_filters_button)
        
        return filter_box
    
    @abstractmethod
    def _create_action_buttons(self) -> Gtk.Widget:
        """
        Create the action buttons.
        
        Returns:
            GTK widget with action buttons
        """
        pass
    
    @abstractmethod
    def _create_list_view(self) -> Gtk.Widget:
        """
        Create the list view.
        
        Returns:
            GTK widget of the list view
        """
        pass
    
    @abstractmethod
    def _create_cards_view(self) -> Gtk.Widget:
        """
        Create the cards view.
        
        Returns:
            GTK widget of the cards view
        """
        pass
    
    def switch_view_mode(self, mode: str):
        """
        Switch the view mode.
        
        Args:
            mode: View mode ("list" or "cards")
        """
        if mode not in ["list", "cards"]:
            return
            
        self.view_mode = mode
        
        # Update the visibility of the views
        if self.list_view and self.cards_view:
            if mode == "list":
                self.list_view.set_visible(True)
                self.cards_view.set_visible(False)
            else:
                self.list_view.set_visible(False)
                self.cards_view.set_visible(True)
    
    def update_view(self):
        """
        Update the view.
        """
        if self.view_mode == "list":
            self._update_list_view()
        else:
            self._update_cards_view()
    
    @abstractmethod
    def _update_list_view(self):
        """
        Update the list view.
        """
        pass
    
    @abstractmethod
    def _update_cards_view(self):
        """
        Update the cards view.
        """
        pass
    
    def _on_resource_event(self, event_type: str, data: Any):
        """
        Handler for events from the resource manager.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        if event_type == 'loading_started':
            self._show_loading()
        elif event_type == 'loading_completed':
            self._hide_loading()
            self.update_view()
        elif event_type == 'loading_error':
            self._hide_loading()
            self._show_error(data)
        elif event_type in ['search_changed', 'filters_changed', 'search_cleared', 'filters_cleared']:
            self.update_view()
        elif event_type == 'resource_deleted':
            self.update_view()
    
    def _show_loading(self):
        """
        Show the loading spinner.
        """
        if self.loading_spinner:
            self.loading_spinner.set_visible(True)
            self.loading_spinner.start()
    
    def _hide_loading(self):
        """
        Hide the loading spinner.
        """
        if self.loading_spinner:
            self.loading_spinner.stop()
            self.loading_spinner.set_visible(False)
    
    def _show_error(self, error_message: str):
        """
        Show the error.
        
        Args:
            error_message: Error message
        """
        # Here you can implement showing the error through notifications
        print(f"Error: {error_message}")
    
    def _on_refresh_clicked(self, button):
        """
        Handler for the click on the refresh button.
        
        Args:
            button: Refresh button
        """
        self.resource_manager.refresh()
    
    def _on_list_mode_toggled(self, button):
        """
        Handler for switching to the list mode.
        
        Args:
            button: List mode button
        """
        if button.get_active():
            self.switch_view_mode("list")
    
    def _on_cards_mode_toggled(self, button):
        """
        Handler for switching to the cards mode.
        
        Args:
            button: Cards mode button
        """
        if button.get_active():
            self.switch_view_mode("cards")
    
    def _on_search_changed(self, entry):
        """
        Handler for the change of the search.
        
        Args:
            entry: Search entry
        """
        query = entry.get_text()
        self.resource_manager.search(query)
    
    def _on_clear_search_clicked(self, button):
        """
        Handler for the click on the clear search button.
        
        Args:
            button: Clear button
        """
        self.resource_manager.clear_search()
        # Clear the search entry
        if self.search_bar:
            search_entry = self.search_bar.get_first_child()
            if isinstance(search_entry, Gtk.SearchEntry):
                search_entry.set_text("")
    
    def _on_clear_filters_clicked(self, button):
        """
        Handler for the click on the clear filters button.
        
        Args:
            button: Clear filters button
        """
        self.resource_manager.clear_filters()
    
    def get_selected_resources(self) -> List[Any]:
        """
        Get the selected resources.
        
        Returns:
            List of selected resources
        """
        if self.view_mode == "list":
            return self._get_selected_from_list()
        else:
            return self._get_selected_from_cards()
    
    @abstractmethod
    def _get_selected_from_list(self) -> List[Any]:
        """
        Get the selected resources from the list.
        
        Returns:
            List of selected resources
        """
        pass
    
    @abstractmethod
    def _get_selected_from_cards(self) -> List[Any]:
        """
        Get the selected resources from the cards.
        
        Returns:
            List of selected resources
        """
        pass
