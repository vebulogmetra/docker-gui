import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

from ui.components.search import SearchBar
from ui.components.card import ResourceCard
from core.base_operations import BaseOperations


class VolumesView(Gtk.Box):
    def __init__(self, volume_manager, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10, **kwargs)
        
        self.volume_manager = volume_manager
        self.volumes = []
        self.filtered_volumes = []
        self.current_search_text = ""
        self.current_filters = {}
        
        self.search_bar = None
        self.filter_bar = None
        self.volumes_list = None
        self.volumes_grid = None
        self.view_mode = "list"  # "list" или "cards"
        
        self._build_ui()
        self._setup_callbacks()
        self._load_data()
    
    def _build_ui(self):
        """Build the user interface."""
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        toolbar.set_margin_start(10)
        toolbar.set_margin_end(10)
        toolbar.set_margin_top(10)
        self.append(toolbar)
        
        self.search_bar = SearchBar(placeholder="Поиск томов...")
        self.search_bar.connect("search-changed", self._on_search_changed)
        toolbar.append(self.search_bar)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        toolbar.append(button_box)
        
        refresh_btn = Gtk.Button(label="Обновить")
        refresh_btn.connect("clicked", self._on_refresh)
        button_box.append(refresh_btn)
        
        self.view_btn = Gtk.Button(label="Карточки")
        self.view_btn.connect("clicked", self._on_toggle_view)
        button_box.append(self.view_btn)
        
        create_btn = Gtk.Button(label="Создать том")
        create_btn.connect("clicked", self._on_create_volume)
        button_box.append(create_btn)
        
        self.select_all_btn = Gtk.Button(label="Выбрать все")
        self.select_all_btn.connect("clicked", self._on_select_all)
        button_box.append(self.select_all_btn)
        
        self.deselect_all_btn = Gtk.Button(label="Снять выбор")
        self.deselect_all_btn.connect("clicked", self._on_deselect_all)
        button_box.append(self.deselect_all_btn)
        
        self.delete_selected_btn = Gtk.Button(label="Удалить выбранные")
        self.delete_selected_btn.connect("clicked", self._on_delete_selected)
        button_box.append(self.delete_selected_btn)
        
        self.content_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.content_area.set_vexpand(True)
        self.append(self.content_area)
        
        self._create_list_view()
        self._create_cards_view()
        
        self._show_list_view()
    
    def _create_list_view(self):
        """Create the list view."""
        self.volumes_list = Gtk.ListBox()
        self.volumes_list.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.volumes_list.add_css_class("volumes-list")
        
        self.list_store = Gtk.ListStore(str, str, str, str, str)  # Name, Driver, Mountpoint, Size, Status
        
        self.tree_view = Gtk.TreeView(model=self.list_store)
        self.tree_view.set_headers_visible(True)
        
        selection = self.tree_view.get_selection()
        selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        
        columns = [
            ("Имя", 0, 200),
            ("Драйвер", 1, 100),
            ("Точка монтирования", 2, 300),
            ("Размер", 3, 100),
            ("Статус", 4, 100)
        ]
        
        for title, column_id, width in columns:
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=column_id)
            column.set_min_width(width)
            column.set_resizable(True)
            self.tree_view.append_column(column)
        
        list_container = Gtk.ScrolledWindow()
        list_container.set_vexpand(True)
        list_container.set_child(self.tree_view)
        
        self.list_container = list_container
    
    def _create_cards_view(self):
        """Create the cards view."""
        self.volumes_grid = Gtk.FlowBox()
        self.volumes_grid.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.volumes_grid.set_max_children_per_line(4)
        self.volumes_grid.set_min_children_per_line(2)
        self.volumes_grid.add_css_class("volumes-grid")
        
        grid_container = Gtk.ScrolledWindow()
        grid_container.set_vexpand(True)
        grid_container.set_child(self.volumes_grid)
        
        self.grid_container = grid_container
    
    def _show_list_view(self):
        """Show the list view."""
        while self.content_area.get_first_child():
            self.content_area.remove(self.content_area.get_first_child())
        self.content_area.append(self.list_container)
        self.view_mode = "list"
        self.view_btn.set_label("Карточки")
        self._update_view()
    
    def _show_cards_view(self):
        """Show the cards view."""
        while self.content_area.get_first_child():
            self.content_area.remove(self.content_area.get_first_child())
        self.content_area.append(self.grid_container)
        self.view_mode = "cards"
        self.view_btn.set_label("Список")
        self._update_view()
    
    def _setup_callbacks(self):
        """Setup the callbacks."""
        self.volume_manager.add_callback(self._on_volume_manager_event)
    
    def _load_data(self):
        """Load the data."""
        self.volumes = self.volume_manager.get_all_volumes_formatted()
        self.filtered_volumes = self.volumes.copy()
        self._update_view()
    
    def _update_view(self):
        """Update the view."""
        if self.view_mode == "list":
            self._update_list_view()
        else:
            self._update_cards_view()
    
    def _update_list_view(self):
        """Update the list view."""
        self.list_store.clear()
        
        for volume in self.filtered_volumes:
            self.list_store.append([
                volume.get('Name', ''),
                volume.get('Driver', ''),
                volume.get('Mountpoint', ''),
                volume.get('Size', ''),
                volume.get('Status', '')
            ])
    
    def _update_cards_view(self):
        """Update the cards view."""
        for child in self.volumes_grid:
            self.volumes_grid.remove(child)
        
        for volume in self.filtered_volumes:
            card = self._create_volume_card(volume)
            self.volumes_grid.append(card)
    
    def _create_volume_card(self, volume):
        """Create the volume card."""
        card = ResourceCard(
            resource_type="volume",
            resource_data=volume
        )
        
        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self._on_card_clicked, volume)
        card.add_controller(gesture)
        
        return card
    
    def _on_search_changed(self, search_bar, query):
        """Handler for search change."""
        self.current_search_text = query
        self.volume_manager.search(query)
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply the filters."""
        self.volume_manager.filter(self.current_filters)
    
    def _on_refresh(self, button):
        """Handler for refresh."""
        self.volume_manager.refresh(self._on_data_updated)
    
    def _on_toggle_view(self, button):
        """Handler for toggle view."""
        if self.view_mode == "list":
            self._show_cards_view()
        else:
            self._show_list_view()
    
    def _on_create_volume(self, button):
        """Handler for create volume."""
        # TODO: Implement the volume creation dialog
        print("Volume creation - not implemented")
    
    def _on_card_clicked(self, gesture, n_press, x, y, volume):
        """Handler for card click."""
        button = gesture.get_current_button()
        if button == 3:  # Right click
            # Create an event to pass to the context menu
            event = type('Event', (), {'button': button})()
            self._show_context_menu(gesture.get_widget(), event, volume)
    
    def _show_context_menu(self, card, event, volume):
        """Show the context menu."""
        menu = Gtk.PopoverMenu()
        menu.set_pointing_to(card)
        menu.set_position(Gtk.PositionType.BOTTOM)
        
        inspect_item = Gtk.MenuItem(label="Inspect")
        inspect_item.connect("activate", self._on_inspect_volume, volume)
        menu.append(inspect_item)
        
        delete_item = Gtk.MenuItem(label="Удалить")
        delete_item.connect("activate", self._on_delete_volume, volume)
        menu.append(delete_item)
        
        menu.show_all()
    
    def _on_inspect_volume(self, menu_item, volume):
        """Handler for inspect volume."""
        # TODO: Implement the volume inspection
        print(f"Inspect volume {volume.get('Name', '')} - not implemented")
    
    def _on_delete_volume(self, menu_item, volume):
        """Handler for delete volume."""
        # TODO: Implement the volume deletion
        print(f"Delete volume {volume.get('Name', '')} - not implemented")
    
    def _on_select_all(self, button):
        """Select all volumes."""
        if self.view_mode == "list":
            self.tree_view.get_selection().select_all()
        else:
            self.volumes_grid.select_all()
    
    def _on_deselect_all(self, button):
        """Unselect all volumes."""
        if self.view_mode == "list":
            self.tree_view.get_selection().unselect_all()
        else:
            self.volumes_grid.unselect_all()
    
    def _on_delete_selected(self, button):
        """Delete selected volumes."""
        if self.view_mode == "list":
            selection = self.tree_view.get_selection()
            model, paths = selection.get_selected_rows()
            selected_volumes = []
            for path in paths:
                iter = model.get_iter(path)
                volume_name = model.get_value(iter, 0)  # First column - name
                selected_volumes.append(volume_name)
        else:
            selected_volumes = []
            for child in self.volumes_grid.get_selected_children():
                # Get the volume data from the card
                card = child.get_child()
                if hasattr(card, 'resource_data'):
                    selected_volumes.append(card.resource_data.get('Name', ''))
        
        if selected_volumes:
            print(f"Удаление выбранных томов: {selected_volumes} - не реализовано")
        else:
            print("Нет выбранных томов для удаления")
    
    def _on_volume_manager_event(self, event_type, data):
        """Handler for volume manager events."""
        if event_type == 'loading_complete':
            GLib.idle_add(self._on_data_updated)
        elif event_type == 'ui_update':
            GLib.idle_add(self._on_data_updated)
    
    def _on_data_updated(self):
        """Handler for data update."""
        self.volumes = self.volume_manager.get_all_volumes_formatted()
        self.filtered_volumes = self.volume_manager.get_filtered_resources()
        self._update_view()
        return False  # Stop the idle callback
