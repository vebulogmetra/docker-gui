import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

from ui.components.search import SearchBar
from ui.components.card import ResourceCard


class ContainersView(Gtk.Box):
    def __init__(self, container_manager, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10, **kwargs)
        
        self.container_manager = container_manager
        self.containers = []
        self.filtered_containers = []
        self.current_search_text = ""
        self.current_filters = {}
        
        self.search_bar = None
        self.filter_bar = None
        self.containers_list = None
        self.containers_grid = None
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
        
        self.search_bar = SearchBar(placeholder="Поиск контейнеров...")
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
        
        create_btn = Gtk.Button(label="Создать контейнер")
        create_btn.connect("clicked", self._on_create_container)
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
        self.list_store = Gtk.ListStore(str, str, str, str, str)
        
        self.tree_view = Gtk.TreeView(model=self.list_store)
        self.tree_view.set_headers_visible(True)
        
        selection = self.tree_view.get_selection()
        selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        
        # Колонки
        columns = [
            ("Имя", 0, 200),
            ("Образ", 1, 200),
            ("Статус", 2, 100),
            ("Порты", 3, 150),
            ("Размер", 4, 100)
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
        self.containers_grid = Gtk.FlowBox()
        self.containers_grid.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.containers_grid.set_max_children_per_line(4)
        self.containers_grid.set_min_children_per_line(2)
        self.containers_grid.add_css_class("containers-grid")
        
        grid_container = Gtk.ScrolledWindow()
        grid_container.set_vexpand(True)
        grid_container.set_child(self.containers_grid)
        
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
        self.container_manager.add_callback(self._on_container_manager_event)
    
    def _load_data(self):
        """Load the data."""
        self.containers = self.container_manager.get_resources()
        self.filtered_containers = self.containers.copy()
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
        
        for container in self.filtered_containers:
            ports = container.get('Ports', [])
            ports_str = container.get('ports', '')
            if isinstance(ports, list):
                ports_display = ', '.join(ports) if ports else ''
            elif ports_str:
                ports_display = ports_str
            else:
                ports_display = ''
            
            self.list_store.append([
                container.get('Names', [''])[0] if container.get('Names') else '',
                container.get('Image', ''),
                container.get('Status', ''),
                ports_display,
                container.get('Size', '')
            ])
    
    def _update_cards_view(self):
        """Update the cards view."""
        for child in self.containers_grid:
            self.containers_grid.remove(child)
        
        for container in self.filtered_containers:
            card = self._create_container_card(container)
            self.containers_grid.append(card)
    
    def _create_container_card(self, container):
        """Create the container card."""
        card = ResourceCard(
            resource_type="container",
            resource_data=container
        )
        
        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self._on_card_clicked, container)
        card.add_controller(gesture)
        
        return card
    
    def _on_search_changed(self, search_bar, query):
        """Handler for search change."""
        self.current_search_text = query
        self.container_manager.search(query)
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply filters."""
        self.container_manager.filter(self.current_filters)
    
    def _on_refresh(self, button):
        """Handler for refresh."""
        self.container_manager.refresh(self._on_data_updated)
    
    def _on_toggle_view(self, button):
        """Handler for toggle view."""
        if self.view_mode == "list":
            self._show_cards_view()
        else:
            self._show_list_view()
    
    def _on_create_container(self, button):
        """Handler for create container."""
        # TODO: Implement create container dialog
        print("Создание контейнера - не реализовано")
    
    def _on_card_clicked(self, gesture, n_press, x, y, container):
        """Handler for card click."""
        button = gesture.get_current_button()
        if button == 3:  # Right click
            # Create event for context menu
            event = type('Event', (), {'button': button})()
            self._show_context_menu(gesture.get_widget(), event, container)
    
    def _show_context_menu(self, card, event, container):
        """Show the context menu."""
        menu = Gtk.PopoverMenu()
        menu.set_pointing_to(card)
        menu.set_position(Gtk.PositionType.BOTTOM)
        
        start_item = Gtk.MenuItem(label="Запустить")
        start_item.connect("activate", self._on_start_container, container)
        menu.append(start_item)
        
        stop_item = Gtk.MenuItem(label="Остановить")
        stop_item.connect("activate", self._on_stop_container, container)
        menu.append(stop_item)
        
        restart_item = Gtk.MenuItem(label="Перезапустить")
        restart_item.connect("activate", self._on_restart_container, container)
        menu.append(restart_item)
        
        delete_item = Gtk.MenuItem(label="Удалить")
        delete_item.connect("activate", self._on_delete_container, container)
        menu.append(delete_item)
        
        menu.show_all()
    
    def _on_start_container(self, menu_item, container):
        """Handler for start container."""
        # TODO: Implement start container
        print(f"Запуск контейнера {container.get('Names', [''])[0]} - не реализовано")
    
    def _on_stop_container(self, menu_item, container):
        """Handler for stop container."""
        # TODO: Implement stop container
        print(f"Остановка контейнера {container.get('Names', [''])[0]} - не реализовано")
    
    def _on_restart_container(self, menu_item, container):
        """Handler for restart container."""
        # TODO: Implement restart container
        print(f"Перезапуск контейнера {container.get('Names', [''])[0]} - не реализовано")
    
    def _on_delete_container(self, menu_item, container):
        """Handler for delete container."""
        # TODO: Implement delete container
        print(f"Удаление контейнера {container.get('Names', [''])[0]} - не реализовано")
    
    def _on_select_all(self, button):
        """Select all containers."""
        if self.view_mode == "list":
            self.tree_view.get_selection().select_all()
        else:
            self.containers_grid.select_all()
    
    def _on_deselect_all(self, button):
        """Deselect all containers."""
        if self.view_mode == "list":
            self.tree_view.get_selection().unselect_all()
        else:
            self.containers_grid.unselect_all()
    
    def _on_delete_selected(self, button):
        """Delete selected containers."""
        if self.view_mode == "list":
            selection = self.tree_view.get_selection()
            model, paths = selection.get_selected_rows()
            selected_containers = []
            for path in paths:
                iter = model.get_iter(path)
                container_name = model.get_value(iter, 0)
                selected_containers.append(container_name)
        else:
            selected_containers = []
            for child in self.containers_grid.get_selected_children():
                card = child.get_child()
                if hasattr(card, 'resource_data'):
                    selected_containers.append(card.resource_data.get('Names', [''])[0])
        
        if selected_containers:
            print(f"Удаление выбранных контейнеров: {selected_containers} - не реализовано")
        else:
            print("Нет выбранных контейнеров для удаления")
    
    def _on_container_manager_event(self, event_type, data):
        """Handler for container manager events."""
        if event_type == 'loading_complete':
            GLib.idle_add(self._on_data_updated)
        elif event_type == 'ui_update':
            GLib.idle_add(self._on_data_updated)
    
    def _on_data_updated(self):
        """Handler for data update."""
        self.containers = self.container_manager.get_resources()
        self.filtered_containers = self.container_manager.get_filtered_resources()
        self._update_view()
        return False
