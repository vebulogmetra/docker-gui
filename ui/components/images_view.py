import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

from ui.components.search import SearchBar
from ui.components.card import ResourceCard


class ImagesView(Gtk.Box):
    def __init__(self, image_manager, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10, **kwargs)
        
        self.image_manager = image_manager
        self.images = []
        self.filtered_images = []
        self.current_search_text = ""
        self.current_filters = {}
        
        self.search_bar = None
        self.filter_bar = None
        self.images_list = None
        self.images_grid = None
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
        
        self.search_bar = SearchBar(placeholder="Поиск образов...")
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
        
        pull_btn = Gtk.Button(label="Загрузить образ")
        pull_btn.connect("clicked", self._on_pull_image)
        button_box.append(pull_btn)
        
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
        
        columns = [
            ("Репозиторий", 0, 200),
            ("Тег", 1, 100),
            ("ID", 2, 150),
            ("Размер", 3, 100),
            ("Создан", 4, 150)
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
        self.images_grid = Gtk.FlowBox()
        self.images_grid.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.images_grid.set_max_children_per_line(4)
        self.images_grid.set_min_children_per_line(2)
        self.images_grid.add_css_class("images-grid")
        
        grid_container = Gtk.ScrolledWindow()
        grid_container.set_vexpand(True)
        grid_container.set_child(self.images_grid)
        
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
        self.image_manager.add_callback(self._on_image_manager_event)
    
    def _load_data(self):
        """Load the data."""
        self.images = self.image_manager.get_resources()
        self.filtered_images = self.images.copy()
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
        
        for image in self.filtered_images:
            repo = image.get('Repository', '')
            tag = image.get('Tag', '')
            image_id = image.get('Id', '')
            size = str(image.get('Size', ''))
            created = image.get('Created', '')
            
            self.list_store.append([repo, tag, image_id, size, created])
    
    def _update_cards_view(self):
        """Update the cards view."""
        for child in self.images_grid:
            self.images_grid.remove(child)
        
        for image in self.filtered_images:
            card = self._create_image_card(image)
            self.images_grid.append(card)
    
    def _create_image_card(self, image):
        """Create the image card."""
        card = ResourceCard(
            resource_type="image",
            resource_data=image
        )
        
        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self._on_card_clicked, image)
        card.add_controller(gesture)
        
        return card
    
    def _on_search_changed(self, search_bar, query):
        """Handler for search change."""
        self.current_search_text = query
        self.image_manager.search(query)
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply filters."""
        self.image_manager.filter(self.current_filters)
    
    def _on_refresh(self, button):
        """Handler for refresh."""
        self.image_manager.refresh(self._on_data_updated)
    
    def _on_toggle_view(self, button):
        """Handler for toggle view."""
        if self.view_mode == "list":
            self._show_cards_view()
        else:
            self._show_list_view()
    
    def _on_pull_image(self, button):
        """Handler for pull image."""
        # TODO: Implement pull image dialog
        print("Загрузка образа - не реализовано")
    
    def _on_card_clicked(self, gesture, n_press, x, y, image):
        """Handler for card click."""
        button = gesture.get_current_button()
        if button == 3:  # Right click
            # Create event for context menu
            event = type('Event', (), {'button': button})()
            self._show_context_menu(gesture.get_widget(), event, image)
    
    def _show_context_menu(self, card, event, image):
        """Show the context menu."""
        menu = Gtk.PopoverMenu()
        menu.set_pointing_to(card)
        menu.set_position(Gtk.PositionType.BOTTOM)
        
        # Пункты меню
        run_item = Gtk.MenuItem(label="Запустить контейнер")
        run_item.connect("activate", self._on_run_container, image)
        menu.append(run_item)
        
        inspect_item = Gtk.MenuItem(label="Инспектировать")
        inspect_item.connect("activate", self._on_inspect_image, image)
        menu.append(inspect_item)
        
        delete_item = Gtk.MenuItem(label="Удалить")
        delete_item.connect("activate", self._on_delete_image, image)
        menu.append(delete_item)
        
        menu.show_all()
    
    def _on_run_container(self, menu_item, image):
        """Handler for run container from image."""
        # TODO: Implement run container from image
        print(f"Запуск контейнера из образа {image.get('Repository', '')} - не реализовано")
    
    def _on_inspect_image(self, menu_item, image):
        """Handler for inspect image."""
        # TODO: Implement inspect image
        print(f"Инспектирование образа {image.get('Repository', '')} - не реализовано")
    
    def _on_delete_image(self, menu_item, image):
        """Handler for delete image."""
        # TODO: Implement delete image
        print(f"Удаление образа {image.get('Repository', '')} - не реализовано")
    
    def _on_select_all(self, button):
        """Select all images."""
        if self.view_mode == "list":
            self.tree_view.get_selection().select_all()
        else:
            self.images_grid.select_all()
    
    def _on_deselect_all(self, button):
        """Deselect all images."""
        if self.view_mode == "list":
            self.tree_view.get_selection().unselect_all()
        else:
            self.images_grid.unselect_all()
    
    def _on_delete_selected(self, button):
        """Delete selected images."""
        if self.view_mode == "list":
            selection = self.tree_view.get_selection()
            model, paths = selection.get_selected_rows()
            selected_images = []
            for path in paths:
                iter = model.get_iter(path)
                image_repo = model.get_value(iter, 0)
                image_tag = model.get_value(iter, 1)
                selected_images.append(f"{image_repo}:{image_tag}")
        else:
            selected_images = []
            for child in self.images_grid.get_selected_children():
                card = child.get_child()
                if hasattr(card, 'resource_data'):
                    repo = card.resource_data.get('Repository', '')
                    tag = card.resource_data.get('Tag', '')
                    selected_images.append(f"{repo}:{tag}")
        
        if selected_images:
            print(f"Удаление выбранных образов: {selected_images} - не реализовано")
        else:
            print("Нет выбранных образов для удаления")
    
    def _on_image_manager_event(self, event_type, data):
        """Handler for image manager events."""
        if event_type == 'loading_complete':
            GLib.idle_add(self._on_data_updated)
        elif event_type == 'ui_update':
            GLib.idle_add(self._on_data_updated)
    
    def _on_data_updated(self):
        """Handler for data update."""
        self.images = self.image_manager.get_resources()
        self.filtered_images = self.image_manager.get_filtered_resources()
        self._update_view()
        return False
