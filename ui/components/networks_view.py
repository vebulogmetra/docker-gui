import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

from ui.components.search import SearchBar
from ui.components.card import ResourceCard


class NetworksView(Gtk.Box):
    def __init__(self, network_manager, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10, **kwargs)
        
        self.network_manager = network_manager
        self.networks = []
        self.filtered_networks = []
        self.current_search_text = ""
        self.current_filters = {}
        
        self.search_bar = None
        self.filter_bar = None
        self.networks_list = None
        self.networks_grid = None
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
        
        self.search_bar = SearchBar(placeholder="Поиск сетей...")
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
        
        create_btn = Gtk.Button(label="Создать сеть")
        create_btn.connect("clicked", self._on_create_network)
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
        self.list_store = Gtk.ListStore(str, str, str, str)
        
        self.tree_view = Gtk.TreeView(model=self.list_store)
        self.tree_view.set_headers_visible(True)
        
        selection = self.tree_view.get_selection()
        selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        
        columns = [
            ("Имя", 0, 200),
            ("Драйвер", 1, 100),
            ("Область", 2, 100),
            ("Подсеть", 3, 150)
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
        self.networks_grid = Gtk.FlowBox()
        self.networks_grid.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.networks_grid.set_max_children_per_line(4)
        self.networks_grid.set_min_children_per_line(2)
        self.networks_grid.add_css_class("networks-grid")
        
        grid_container = Gtk.ScrolledWindow()
        grid_container.set_vexpand(True)
        grid_container.set_child(self.networks_grid)
        
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
        self.network_manager.add_callback(self._on_network_manager_event)
    
    def _load_data(self):
        """Load the data."""
        self.networks = self.network_manager.get_resources()
        self.filtered_networks = self.networks.copy()
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
        
        for network in self.filtered_networks:
            self.list_store.append([
                network.get('Name', ''),
                network.get('Driver', ''),
                network.get('Scope', ''),
                network.get('Subnet', '')
            ])
    
    def _update_cards_view(self):
        """Update the cards view."""
        for child in self.networks_grid:
            self.networks_grid.remove(child)
        
        for network in self.filtered_networks:
            card = self._create_network_card(network)
            self.networks_grid.append(card)
    
    def _create_network_card(self, network):
        """Create the network card."""
        card = ResourceCard(
            resource_type="network",
            resource_data=network
        )
        
        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self._on_card_clicked, network)
        card.add_controller(gesture)
        
        return card
    
    def _on_search_changed(self, search_bar, query):
        """Handler for search change."""
        self.current_search_text = query
        self.network_manager.search(query)
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply the filters."""
        self.network_manager.filter(self.current_filters)
    
    def _on_refresh(self, button):
        """Handler for refresh."""
        self.network_manager.refresh(self._on_data_updated)
    
    def _on_toggle_view(self, button):
        """Handler for toggle view."""
        if self.view_mode == "list":
            self._show_cards_view()
        else:
            self._show_list_view()
    
    def _on_create_network(self, button):
        """Handler for create network."""
        # TODO: Implement create network dialog
        print("Создание сети - не реализовано")
    
    def _on_card_clicked(self, gesture, n_press, x, y, network):
        """Handler for card click."""
        button = gesture.get_current_button()
        if button == 3:  # Right click
            # Create event for context menu
            event = type('Event', (), {'button': button})()
            self._show_context_menu(gesture.get_widget(), event, network)
    
    def _show_context_menu(self, card, event, network):
        """Show the context menu."""
        menu = Gtk.PopoverMenu()
        menu.set_pointing_to(card)
        menu.set_position(Gtk.PositionType.BOTTOM)
        
        inspect_item = Gtk.MenuItem(label="Инспектировать")
        inspect_item.connect("activate", self._on_inspect_network, network)
        menu.append(inspect_item)
        
        delete_item = Gtk.MenuItem(label="Удалить")
        delete_item.connect("activate", self._on_delete_network, network)
        menu.append(delete_item)
        
        menu.show_all()
    
    def _on_inspect_network(self, menu_item, network):
        """Handler for inspect network."""
        # TODO: Implement inspect network
        print(f"Инспектирование сети {network.get('Name', '')} - не реализовано")
    
    def _on_delete_network(self, menu_item, network):
        """Handler for delete network."""
        # TODO: Implement delete network
        print(f"Удаление сети {network.get('Name', '')} - не реализовано")
    
    def _on_select_all(self, button):
        """Select all networks."""
        if self.view_mode == "list":
            self.tree_view.get_selection().select_all()
        else:
            self.networks_grid.select_all()
    
    def _on_deselect_all(self, button):
        """Deselect all networks."""
        if self.view_mode == "list":
            self.tree_view.get_selection().unselect_all()
        else:
            self.networks_grid.unselect_all()
    
    def _on_delete_selected(self, button):
        """Delete selected networks."""
        if self.view_mode == "list":
            selection = self.tree_view.get_selection()
            model, paths = selection.get_selected_rows()
            selected_networks = []
            for path in paths:
                iter = model.get_iter(path)
                network_name = model.get_value(iter, 0)
                selected_networks.append(network_name)
        else:
            selected_networks = []
            for child in self.networks_grid.get_selected_children():
                card = child.get_child()
                if hasattr(card, 'resource_data'):
                    selected_networks.append(card.resource_data.get('Name', ''))
        
        if selected_networks:
            print(f"Удаление выбранных сетей: {selected_networks} - не реализовано")
        else:
            print("Нет выбранных сетей для удаления")
    
    def _on_network_manager_event(self, event_type, data):
        """Handler for network manager events."""
        if event_type == 'loading_complete':
            GLib.idle_add(self._on_data_updated)
        elif event_type == 'ui_update':
            GLib.idle_add(self._on_data_updated)
    
    def _on_data_updated(self):
        """Handler for data update."""
        self.networks = self.network_manager.get_resources()
        self.filtered_networks = self.network_manager.get_filtered_resources()
        self._update_view()
        return False
