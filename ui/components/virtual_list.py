import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, GObject
from typing import List, Any, Callable, Optional


class VirtualList(Gtk.Box):
    __gtype_name__ = 'VirtualList'
    def __init__(self, item_height: int = 60, buffer_size: int = 10):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        self.item_height = item_height
        self.buffer_size = buffer_size
        self.items = []
        self.visible_range = (0, 0)
        self.visible_widgets = {}
        self.item_factory = None
        self.on_item_clicked = None
        
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_hexpand(True)
        
        self.list_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        self.size_widget = Gtk.Box()
        self.size_widget.set_size_request(-1, 0)
        
        self.list_container.append(self.size_widget)
        self.scrolled_window.set_child(self.list_container)
        self.append(self.scrolled_window)
        
        self.scrolled_window.get_vadjustment().connect('value-changed', self._on_scroll)
        
    def set_items(self, items: List[Any]):
        """
        Set the list items.

        Args:
            items: List of items to display
        """
        self.items = items
        self._update_size()
        self._update_visible_items()
        
    def set_item_factory(self, factory: Callable[[Any], Gtk.Widget]):
        """
        Set the item factory.

        Args:
            factory: Function that creates a widget for an item
        """
        self.item_factory = factory
        
    def set_on_item_clicked(self, callback: Callable[[Any], None]):
        """
        Set the callback for item click.

        Args:
            callback: Callback function
        """
        self.on_item_clicked = callback
        
    def _update_size(self):
        """Update the size of the list container."""
        total_height = len(self.items) * self.item_height
        self.size_widget.set_size_request(-1, total_height)
        
    def _update_visible_items(self):
        """Update the visible items in the list."""
        if not self.items or not self.item_factory:
            return
            
        adjustment = self.scrolled_window.get_vadjustment()
        scroll_value = adjustment.get_value()
        viewport_height = adjustment.get_page_size()
        
        start_index = max(0, int(scroll_value / self.item_height) - self.buffer_size)
        end_index = min(
            len(self.items),
            int((scroll_value + viewport_height) / self.item_height) + self.buffer_size
        )
        
        if self.visible_range == (start_index, end_index):
            return
            
        self.visible_range = (start_index, end_index)
        
        widgets_to_remove = []
        for index, widget in self.visible_widgets.items():
            if index < start_index or index >= end_index:
                widgets_to_remove.append(index)
                
        for index in widgets_to_remove:
            widget = self.visible_widgets.pop(index)
            self.list_container.remove(widget)
            
        for index in range(start_index, end_index):
            if index not in self.visible_widgets:
                item = self.items[index]
                widget = self._create_item_widget(item, index)
                self.visible_widgets[index] = widget
                
                self._insert_widget_at_position(widget, index)
                
    def _create_item_widget(self, item: Any, index: int) -> Gtk.Widget:
        """
        Create a widget for an item.

        Args:
            item: Item data
            index: Item index
            
        Returns:
            Item widget
        """
        widget = self.item_factory(item)
        widget.set_size_request(-1, self.item_height)
        
        if self.on_item_clicked:
            click_controller = Gtk.GestureClick()
            click_controller.connect('pressed', lambda controller, n_press, x, y: self._on_item_click(item))
            widget.add_controller(click_controller)
            
        return widget
        
    def _insert_widget_at_position(self, widget: Gtk.Widget, index: int):
        """
        Insert a widget at the correct position.

        Args:
            widget: Widget to insert
            index: Position index
        """
        insert_position = 1
        
        for i in range(len(self.items)):
            if i == index:
                break
            if i in self.visible_widgets:
                insert_position += 1
                
        self.list_container.insert_child_after(widget, self.size_widget)
        
    def _on_scroll(self, adjustment):
        """Handler for scroll event."""
        GLib.idle_add(self._update_visible_items)
        
    def _on_item_click(self, item: Any):
        """Handler for item click."""
        if self.on_item_clicked:
            self.on_item_clicked(item)
            
    def scroll_to_item(self, index: int):
        """
        Scroll to an item by index.

        Args:
            index: Item index
        """
        if 0 <= index < len(self.items):
            adjustment = self.scrolled_window.get_vadjustment()
            target_value = index * self.item_height
            adjustment.set_value(target_value)
            
    def get_visible_items(self) -> List[Any]:
        """
        Get the list of visible items.

        Returns:
            List of visible items
        """
        start, end = self.visible_range
        return self.items[start:end]
        
    def refresh(self):
        """Update the list display."""
        self._update_visible_items()


class OptimizedTreeView(Gtk.TreeView):
    def __init__(self):
        super().__init__()
        
        self.set_enable_tree_lines(False)
        self.set_show_expanders(False)
        self.set_headers_visible(True)
        
        self.set_fixed_height_mode(True)
        
        self.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        
    def set_model(self, model: Gtk.TreeModel):
        """
        Set the model with optimization.
        
        Args:
            model: Data model
        """
        super().set_model(model)
        
        for column in self.get_columns():
            column.set_resizable(True)
            column.set_expand(False)
            
    def add_column(self, title: str, cell_renderer: Gtk.CellRenderer, 
                   data_column: int, expand: bool = False):
        """
        Add a column with optimization.
        
        Args:
            title: Column title
            cell_renderer: Cell renderer
            data_column: Data column index
            expand: Expand the column
        """
        column = Gtk.TreeViewColumn(title, cell_renderer)
        column.add_attribute(cell_renderer, "text", data_column)
        column.set_resizable(True)
        column.set_expand(expand)
        column.set_sort_column_id(data_column)
        
        self.append_column(column)
        return column
        
    def get_selected_items(self) -> List[Any]:
        """
        Get the selected items.
        
        Returns:
            List of selected items
        """
        selection = self.get_selection()
        model, paths = selection.get_selected_rows()
        
        items = []
        for path in paths:
            iter = model.get_iter(path)
            if iter:
                items.append(model.get_value(iter, 0))
                
        return items
        
    def select_all(self):
        """Select all items."""
        model = self.get_model()
        if model:
            selection = self.get_selection()
            selection.select_all()
            
    def unselect_all(self):
        """Unselect all items."""
        selection = self.get_selection()
        selection.unselect_all()
        
    def refresh(self):
        """Update the display."""
        model = self.get_model()
        if model:
            model.emit('row-changed', Gtk.TreePath.new_first(), model.get_iter_first())


class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
        
    def start_timer(self, name: str):
        """
        Start a timer for a metric.
        
        Args:
            name: Metric name
        """
        self.start_times[name] = GLib.get_monotonic_time()
        
    def end_timer(self, name: str) -> float:
        """
        Stop the timer and get the execution time.
        
        Args:
            name: Metric name
            
        Returns:
            Execution time in milliseconds
        """
        if name not in self.start_times:
            return 0.0
            
        end_time = GLib.get_monotonic_time()
        start_time = self.start_times[name]
        duration = (end_time - start_time) / 1000.0
        
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(duration)
        
        del self.start_times[name]
        return duration
        
    def get_average_time(self, name: str) -> float:
        """
        Get the average execution time of a metric.
        
        Args:
            name: Metric name
            
        Returns:
            Average execution time in milliseconds
        """
        if name not in self.metrics or not self.metrics[name]:
            return 0.0
            
        return sum(self.metrics[name]) / len(self.metrics[name])
        
    def get_metrics(self) -> dict:
        """
        Get all metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        result = {}
        for name, times in self.metrics.items():
            result[name] = {
                'average': sum(times) / len(times) if times else 0.0,
                'min': min(times) if times else 0.0,
                'max': max(times) if times else 0.0,
                'count': len(times)
            }
        return result
        
    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.start_times.clear()


# Global instance of the performance monitor
performance_monitor = PerformanceMonitor()
