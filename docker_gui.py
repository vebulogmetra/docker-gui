#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib
import threading

from docker_api import DockerAPI


class DockerGuiApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.vebulogmetra.docker-gui")
        self.connect("activate", self.on_activate)
        self.docker_api = DockerAPI()

    def on_activate(self, app):
        # Создаем главное окно
        self.win = Gtk.ApplicationWindow(application=app, title="Docker GUI")
        self.win.set_default_size(800, 600)

        # Создаем основную структуру
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)

        # Кнопка для очистки всей системы
        system_prune_button = Gtk.Button(label="Docker System Prune (Все)")
        system_prune_button.connect("clicked", self.on_system_prune)
        system_prune_button.set_margin_bottom(10)
        main_box.append(system_prune_button)

        # Создаем блокнот с вкладками
        notebook = Gtk.Notebook()

        # Добавляем вкладки
        notebook.append_page(self.create_images_tab(), Gtk.Label(label="Images"))
        notebook.append_page(self.create_containers_tab(), Gtk.Label(label="Containers"))
        notebook.append_page(self.create_networks_tab(), Gtk.Label(label="Networks"))
        notebook.append_page(self.create_volumes_tab(), Gtk.Label(label="Volumes"))

        main_box.append(notebook)

        # Устанавливаем главный бокс как дочерний элемент окна
        self.win.set_child(main_box)

        # Показываем все виджеты
        self.win.present()


    def create_images_tab(self):
        # Контейнер для вкладки Images
        tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Создаем модель данных для списка
        self.images_store = Gtk.ListStore(str, str, str, str, bool)  # Добавляем столбец для выбора

        # Создаем представление списка
        images_view = Gtk.TreeView(model=self.images_store)

        # Добавляем колонку с чекбоксами для выбора
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_image_toggled)
        column = Gtk.TreeViewColumn("Select", renderer_toggle, active=4)
        images_view.insert_column(column, 0)

        # Добавляем другие колонки
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("ID", renderer, text=0)
        images_view.insert_column(column, 1)

        column = Gtk.TreeViewColumn("Repository", renderer, text=1)
        images_view.insert_column(column, 2)

        column = Gtk.TreeViewColumn("Tag", renderer, text=2)
        images_view.insert_column(column, 3)

        column = Gtk.TreeViewColumn("Size", renderer, text=3)
        images_view.insert_column(column, 4)

        # Настраиваем режим выбора
        images_view.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.images_selection = images_view.get_selection()

        # Создаем прокрутку
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(images_view)
        tab.append(scrolled)

        # Создаем бокс с кнопками
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        # Кнопка обновления
        refresh_button = Gtk.Button(label="Обновить")
        refresh_button.connect("clicked", self.on_refresh_images)
        button_box.append(refresh_button)

        # Кнопка удаления выбранных
        delete_selected_button = Gtk.Button(label="Удалить выбранные")
        delete_selected_button.connect("clicked", self.on_delete_selected_images)
        button_box.append(delete_selected_button)

        # Кнопка очистки (prune)
        prune_button = Gtk.Button(label="Очистить неиспользуемые")
        prune_button.connect("clicked", self.on_prune_images)
        button_box.append(prune_button)

        tab.append(button_box)

        # Загружаем данные
        self.load_images()
        return tab


    def create_containers_tab(self):
        # Контейнер для вкладки Containers
        tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Создаем модель для хранения данных
        self.containers_store = Gtk.ListStore(str, str, str, str, str, bool)  # Добавляем столбец для выбора

        # Создаем представление списка
        containers_view = Gtk.TreeView(model=self.containers_store)

        # Добавляем колонку с чекбоксами для выбора
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_container_toggled)
        column = Gtk.TreeViewColumn("Select", renderer_toggle, active=5)
        containers_view.insert_column(column, 0)

        # Добавляем другие колонки
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("ID", renderer, text=0)
        containers_view.insert_column(column, 1)

        column = Gtk.TreeViewColumn("Name", renderer, text=1)
        containers_view.insert_column(column, 2)

        column = Gtk.TreeViewColumn("Image", renderer, text=2)
        containers_view.insert_column(column, 3)

        column = Gtk.TreeViewColumn("Status", renderer, text=3)
        containers_view.insert_column(column, 4)

        column = Gtk.TreeViewColumn("Ports", renderer, text=4)
        containers_view.insert_column(column, 5)

        # Настраиваем режим выбора
        containers_view.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.containers_selection = containers_view.get_selection()

        # Создаем прокрутку
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(containers_view)
        tab.append(scrolled)

        # Создаем бокс с кнопками
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        # Кнопка обновления
        refresh_button = Gtk.Button(label="Обновить")
        refresh_button.connect("clicked", self.on_refresh_containers)
        button_box.append(refresh_button)

        # Кнопка остановки выбранных
        stop_selected_button = Gtk.Button(label="Остановить выбранные")
        stop_selected_button.connect("clicked", self.on_stop_selected_containers)
        button_box.append(stop_selected_button)

        # Кнопка удаления выбранных
        delete_selected_button = Gtk.Button(label="Удалить выбранные")
        delete_selected_button.connect("clicked", self.on_delete_selected_containers)
        button_box.append(delete_selected_button)

        # Кнопка очистки (prune)
        prune_button = Gtk.Button(label="Очистить неиспользуемые")
        prune_button.connect("clicked", self.on_prune_containers)
        button_box.append(prune_button)

        tab.append(button_box)

        # Загружаем данные
        self.load_containers()
        return tab


    def create_networks_tab(self):
        # Контейнер для вкладки Networks
        tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Создаем модель для хранения данных
        self.networks_store = Gtk.ListStore(str, str, str, bool)  # Добавляем столбец для выбора

        # Создаем представление списка
        networks_view = Gtk.TreeView(model=self.networks_store)

        # Добавляем колонку с чекбоксами для выбора
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_network_toggled)
        column = Gtk.TreeViewColumn("Select", renderer_toggle, active=3)
        networks_view.insert_column(column, 0)

        # Добавляем другие колонки
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("ID", renderer, text=0)
        networks_view.insert_column(column, 1)

        column = Gtk.TreeViewColumn("Name", renderer, text=1)
        networks_view.insert_column(column, 2)

        column = Gtk.TreeViewColumn("Driver", renderer, text=2)
        networks_view.insert_column(column, 3)

        # Настраиваем режим выбора
        networks_view.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.networks_selection = networks_view.get_selection()

        # Создаем прокрутку
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(networks_view)
        tab.append(scrolled)

        # Создаем бокс с кнопками
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        # Кнопка обновления
        refresh_button = Gtk.Button(label="Обновить")
        refresh_button.connect("clicked", self.on_refresh_networks)
        button_box.append(refresh_button)

        # Кнопка удаления выбранных
        delete_selected_button = Gtk.Button(label="Удалить выбранные")
        delete_selected_button.connect("clicked", self.on_delete_selected_networks)
        button_box.append(delete_selected_button)

        # Кнопка очистки (prune)
        prune_button = Gtk.Button(label="Очистить неиспользуемые")
        prune_button.connect("clicked", self.on_prune_networks)
        button_box.append(prune_button)

        tab.append(button_box)

        # Загружаем данные
        self.load_networks()
        return tab


    def create_volumes_tab(self):
        # Контейнер для вкладки Volumes
        tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Создаем модель для хранения данных
        self.volumes_store = Gtk.ListStore(str, str, bool)  # Добавляем столбец для выбора

        # Создаем представление списка
        volumes_view = Gtk.TreeView(model=self.volumes_store)

        # Добавляем колонку с чекбоксами для выбора
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_volume_toggled)
        column = Gtk.TreeViewColumn("Select", renderer_toggle, active=2)
        volumes_view.insert_column(column, 0)

        # Добавляем другие колонки
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Name", renderer, text=0)
        volumes_view.insert_column(column, 1)

        column = Gtk.TreeViewColumn("Driver", renderer, text=1)
        volumes_view.insert_column(column, 2)

        # Настраиваем режим выбора
        volumes_view.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.volumes_selection = volumes_view.get_selection()

        # Создаем прокрутку
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(volumes_view)
        tab.append(scrolled)

        # Создаем бокс с кнопками
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        # Кнопка обновления
        refresh_button = Gtk.Button(label="Обновить")
        refresh_button.connect("clicked", self.on_refresh_volumes)
        button_box.append(refresh_button)

        # Кнопка удаления выбранных
        delete_selected_button = Gtk.Button(label="Удалить выбранные")
        delete_selected_button.connect("clicked", self.on_delete_selected_volumes)
        button_box.append(delete_selected_button)

        # Кнопка очистки (prune)
        prune_button = Gtk.Button(label="Очистить неиспользуемые")
        prune_button.connect("clicked", self.on_prune_volumes)
        button_box.append(prune_button)

        tab.append(button_box)

        # Загружаем данные
        self.load_volumes()
        return tab


    # Методы загрузки данных
    def load_images(self):
        def _load():
            try:
                images = self.docker_api.get_images()

                def update_ui():
                    # Очищаем модель перед обновлением данных
                    while len(self.images_store) > 0:
                        self.images_store.remove(self.images_store.get_iter_first())
                    
                    for image in images:
                        size = self.docker_api.format_size(image["size"])
                        self.images_store.append([
                            image["id"], 
                            image["repository"], 
                            image["tag"], 
                            size,
                            False  # По умолчанию чекбокс не выбран
                        ])
                GLib.idle_add(update_ui)
            except Exception as e:
                print(f"Error loading images: {e}")
        threading.Thread(target=_load).start()


    def load_containers(self):
        def _load():
            try:
                containers = self.docker_api.get_containers()

                def update_ui():
                    # Очищаем модель перед обновлением данных
                    while len(self.containers_store) > 0:
                        self.containers_store.remove(self.containers_store.get_iter_first())
                    for container in containers:
                        self.containers_store.append([
                            container["id"],
                            container["name"],
                            container["image"],
                            container["status"],
                            container["ports"],
                            False  # По умолчанию чекбокс не выбран
                        ])

                GLib.idle_add(update_ui)
            except Exception as e:
                print(f"Error loading containers: {e}")
        threading.Thread(target=_load).start()


    def load_networks(self):
        def _load():
            try:
                networks = self.docker_api.get_networks()

                def update_ui():
                    # Очищаем модель перед обновлением данных
                    while len(self.networks_store) > 0:
                        self.networks_store.remove(self.networks_store.get_iter_first())
                    for network in networks:
                        self.networks_store.append([
                            network["id"],
                            network["name"],
                            network["driver"],
                            False  # По умолчанию чекбокс не выбран
                        ])
                GLib.idle_add(update_ui)
            except Exception as e:
                print(f"Error loading networks: {e}")
        threading.Thread(target=_load).start()


    def load_volumes(self):
        def _load():
            try:
                volumes = self.docker_api.get_volumes()

                def update_ui():
                    # Очищаем модель перед обновлением данных
                    while len(self.volumes_store) > 0:
                        self.volumes_store.remove(self.volumes_store.get_iter_first())
                    for volume in volumes:
                        self.volumes_store.append([
                            volume["name"],
                            volume["driver"],
                            False  # По умолчанию чекбокс не выбран
                        ])
                GLib.idle_add(update_ui)
            except Exception as e:
                print(f"Error loading volumes: {e}")
        threading.Thread(target=_load).start()


    # Обработчики переключения чекбоксов
    def on_image_toggled(self, cell, path):
        self.images_store[path][4] = not self.images_store[path][4]

    def on_container_toggled(self, cell, path):
        self.containers_store[path][5] = not self.containers_store[path][5]

    def on_network_toggled(self, cell, path):
        self.networks_store[path][3] = not self.networks_store[path][3]

    def on_volume_toggled(self, cell, path):
        self.volumes_store[path][2] = not self.volumes_store[path][2]

    # Обработчики событий кнопок
    def on_refresh_images(self, button):
        self.load_images()

    def on_delete_image(self, button):
        # Получаем выбранную строку
        model, treeiter = self.images_selection.get_selected()

        if treeiter is not None:
            image_id = model[treeiter][0]
            # Создаем диалог подтверждения
            dialog = Gtk.MessageDialog(
                transient_for=self.win,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=f"Вы уверены, что хотите удалить образ {image_id}?"
            )

            def on_response(dialog, response_id):
                dialog.destroy()
                if response_id == Gtk.ResponseType.YES:
                    # Удаляем образ в отдельном потоке
                    def remove_image():
                        try:
                            if self.docker_api.delete_image(image_id):
                                GLib.idle_add(self.load_images)
                            else:
                                GLib.idle_add(lambda: self.show_error("Не удалось удалить образ"))
                        except Exception as e:
                            GLib.idle_add(lambda: self.show_error(f"Ошибка при удалении образа: {e}"))
                    threading.Thread(target=remove_image).start()

            dialog.connect("response", on_response)
            dialog.present()


    def on_delete_selected_images(self, button):
        # Получаем список выбранных образов
        selected_image_ids = []
        for row in self.images_store:
            if row[4]:  # Если чекбокс выбран (5-й столбец)
                selected_image_ids.append(row[0])  # Добавляем ID образа (1-й столбец)

        if not selected_image_ids:
            self.show_error("Не выбрано ни одного образа")
            return

        # Создаем диалог подтверждения
        dialog = Gtk.MessageDialog(
            transient_for=self.win,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Вы уверены, что хотите удалить {len(selected_image_ids)} выбранных образов?"
        )

        def on_response(dialog, response_id):
            dialog.destroy()
            if response_id == Gtk.ResponseType.YES:
                # Удаляем образы в отдельном потоке
                def remove_images():
                    try:
                        results = self.docker_api.delete_images(selected_image_ids)

                        # Подсчитываем статистику
                        success_count = sum(1 for success in results.values() if success)
                        fail_count = len(results) - success_count

                        def update_ui():
                            self.load_images()
                            self.show_info(f"Удалено {success_count} образов. Не удалось удалить {fail_count} образов.")

                        GLib.idle_add(update_ui)
                    except Exception as e:
                        GLib.idle_add(lambda: self.show_error(f"Ошибка при удалении образов: {e}"))
                threading.Thread(target=remove_images).start()

        dialog.connect("response", on_response)
        dialog.present()


    def on_prune_images(self, button):
        # Создаем диалог подтверждения
        dialog = Gtk.MessageDialog(
            transient_for=self.win,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Вы уверены, что хотите очистить неиспользуемые образы Docker?"
        )

        def on_response(dialog, response_id):
            dialog.destroy()
            if response_id == Gtk.ResponseType.YES:
                # Выполняем очистку в отдельном потоке
                def prune_task():
                    try:
                        result = self.docker_api.prune_images()
                        def update_ui():
                            self.load_images()
                            if result["success"]:
                                deleted_count = len(result.get("deleted", []))
                                space_reclaimed = self.docker_api.format_size(result.get("space_reclaimed", 0))
                                self.show_info(f"Удалено {deleted_count} образов. Освобождено {space_reclaimed} дискового пространства.")
                            else:
                                self.show_error(f"Ошибка при очистке образов: {result.get('error', 'Неизвестная ошибка')}")
                        GLib.idle_add(update_ui)
                    except Exception as e:
                        GLib.idle_add(lambda: self.show_error(f"Ошибка при очистке образов: {e}"))
                threading.Thread(target=prune_task).start()

        dialog.connect("response", on_response)
        dialog.present()

    def on_refresh_containers(self, button):
        self.load_containers()

    def on_stop_container(self, button):
        # Получаем выбранную строку
        model, treeiter = self.containers_selection.get_selected()

        if treeiter is not None:
            container_id = model[treeiter][0]

            # Создаем диалог подтверждения
            dialog = Gtk.MessageDialog(
                transient_for=self.win,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=f"Вы уверены, что хотите остановить контейнер {container_id}?"
            )

            def on_response(dialog, response_id):
                dialog.destroy()
                if response_id == Gtk.ResponseType.YES:
                    # Останавливаем контейнер в отдельном потоке
                    def stop_container():
                        try:
                            if self.docker_api.stop_container(container_id):
                                GLib.idle_add(self.load_containers)
                            else:
                                GLib.idle_add(lambda: self.show_error("Не удалось остановить контейнер"))
                        except Exception as e:
                            GLib.idle_add(lambda: self.show_error(f"Ошибка при остановке контейнера: {e}"))
                    threading.Thread(target=stop_container).start()

            dialog.connect("response", on_response)
            dialog.present()


    def on_stop_selected_containers(self, button):
        # Получаем список выбранных контейнеров
        selected_container_ids = []
        for row in self.containers_store:
            if row[5]:  # Если чекбокс выбран
                selected_container_ids.append(row[0])  # Добавляем ID контейнера

        if not selected_container_ids:
            self.show_error("Не выбрано ни одного контейнера")
            return

        # Создаем диалог подтверждения
        dialog = Gtk.MessageDialog(
            transient_for=self.win,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Вы уверены, что хотите остановить {len(selected_container_ids)} выбранных контейнеров?"
        )

        def on_response(dialog, response_id):
            dialog.destroy()
            if response_id == Gtk.ResponseType.YES:
                # Останавливаем контейнеры в отдельном потоке
                def stop_containers():
                    try:
                        results = self.docker_api.stop_containers(selected_container_ids)
                        # Подсчитываем статистику
                        success_count = sum(1 for success in results.values() if success)
                        fail_count = len(results) - success_count

                        def update_ui():
                            self.load_containers()
                            self.show_info(f"Остановлено {success_count} контейнеров. Не удалось остановить {fail_count} контейнеров.")
                        GLib.idle_add(update_ui)
                    except Exception as e:
                        GLib.idle_add(lambda: self.show_error(f"Ошибка при остановке контейнеров: {e}"))
                threading.Thread(target=stop_containers).start()

        dialog.connect("response", on_response)
        dialog.present()


    def on_delete_container(self, button):
        # Получаем выбранную строку
        model, treeiter = self.containers_selection.get_selected()
        if treeiter is not None:
            container_id = model[treeiter][0]

            # Создаем диалог подтверждения
            dialog = Gtk.MessageDialog(
                transient_for=self.win,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=f"Вы уверены, что хотите удалить контейнер {container_id}?"
            )

            def on_response(dialog, response_id):
                dialog.destroy()
                if response_id == Gtk.ResponseType.YES:
                    # Удаляем контейнер в отдельном потоке
                    def remove_container():
                        try:
                            if self.docker_api.delete_container(container_id, force=True):
                                GLib.idle_add(self.load_containers)
                            else:
                                GLib.idle_add(lambda: self.show_error("Не удалось удалить контейнер"))
                        except Exception as e:
                            GLib.idle_add(lambda: self.show_error(f"Ошибка при удалении контейнера: {e}"))
                    threading.Thread(target=remove_container).start()

            dialog.connect("response", on_response)
            dialog.present()


    def on_delete_selected_containers(self, button):
        # Получаем список выбранных контейнеров
        selected_container_ids = []
        for row in self.containers_store:
            if row[5]:  # Если чекбокс выбран
                selected_container_ids.append(row[0])  # Добавляем ID контейнера

        if not selected_container_ids:
            self.show_error("Не выбрано ни одного контейнера")
            return

        # Создаем диалог подтверждения
        dialog = Gtk.MessageDialog(
            transient_for=self.win,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Вы уверены, что хотите удалить {len(selected_container_ids)} выбранных контейнеров?"
        )

        def on_response(dialog, response_id):
            dialog.destroy()
            if response_id == Gtk.ResponseType.YES:
                # Удаляем контейнеры в отдельном потоке
                def remove_containers():
                    try:
                        results = self.docker_api.delete_containers(selected_container_ids, force=True)
                        # Подсчитываем статистику
                        success_count = sum(1 for success in results.values() if success)
                        fail_count = len(results) - success_count

                        def update_ui():
                            self.load_containers()
                            self.show_info(f"Удалено {success_count} контейнеров. Не удалось удалить {fail_count} контейнеров.")
                        GLib.idle_add(update_ui)
                    except Exception as e:
                        GLib.idle_add(lambda: self.show_error(f"Ошибка при удалении контейнеров: {e}"))
                threading.Thread(target=remove_containers).start()

        dialog.connect("response", on_response)
        dialog.present()


    def on_prune_containers(self, button):
        # Создаем диалог подтверждения
        dialog = Gtk.MessageDialog(
            transient_for=self.win,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Вы уверены, что хотите очистить остановленные контейнеры Docker?"
        )

        def on_response(dialog, response_id):
            dialog.destroy()
            if response_id == Gtk.ResponseType.YES:
                # Выполняем очистку в отдельном потоке
                def prune_task():
                    try:
                        result = self.docker_api.prune_containers()
                        def update_ui():
                            self.load_containers()
                            if result["success"]:
                                deleted_count = len(result.get("deleted", []))
                                space_reclaimed = self.docker_api.format_size(result.get("space_reclaimed", 0))
                                self.show_info(f"Удалено {deleted_count} контейнеров. Освобождено {space_reclaimed} дискового пространства.")
                            else:
                                self.show_error(f"Ошибка при очистке контейнеров: {result.get('error', 'Неизвестная ошибка')}")
                        GLib.idle_add(update_ui)
                    except Exception as e:
                        GLib.idle_add(lambda: self.show_error(f"Ошибка при очистке контейнеров: {e}"))
                threading.Thread(target=prune_task).start()

        dialog.connect("response", on_response)
        dialog.present()

    def on_refresh_networks(self, button):
        self.load_networks()

    def on_delete_selected_networks(self, button):
        # Получаем список выбранных сетей
        selected_network_ids = []
        for row in self.networks_store:
            if row[3]:  # Если чекбокс выбран
                selected_network_ids.append(row[0])  # Добавляем ID сети
        if not selected_network_ids:
            self.show_error("Не выбрано ни одной сети")
            return

        # Создаем диалог подтверждения
        dialog = Gtk.MessageDialog(
            transient_for=self.win,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Вы уверены, что хотите удалить {len(selected_network_ids)} выбранных сетей?"
        )

        def on_response(dialog, response_id):
            dialog.destroy()
            if response_id == Gtk.ResponseType.YES:
                # Удаляем сети в отдельном потоке
                def remove_networks():
                    try:
                        results = self.docker_api.delete_networks(selected_network_ids)
                        # Подсчитываем статистику
                        success_count = sum(1 for success in results.values() if success)
                        fail_count = len(results) - success_count
                        def update_ui():
                            self.load_networks()
                            self.show_info(f"Удалено {success_count} сетей. Не удалось удалить {fail_count} сетей.")
                        GLib.idle_add(update_ui)
                    except Exception as e:
                        GLib.idle_add(lambda: self.show_error(f"Ошибка при удалении сетей: {e}"))
                threading.Thread(target=remove_networks).start()

        dialog.connect("response", on_response)
        dialog.present()


    def on_prune_networks(self, button):
        # Создаем диалог подтверждения
        dialog = Gtk.MessageDialog(
            transient_for=self.win,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Вы уверены, что хотите очистить неиспользуемые сети Docker?"
        )

        def on_response(dialog, response_id):
            dialog.destroy()
            if response_id == Gtk.ResponseType.YES:
                # Выполняем очистку в отдельном потоке
                def prune_task():
                    try:
                        result = self.docker_api.prune_networks()
                        def update_ui():
                            self.load_networks()
                            if result["success"]:
                                deleted_count = len(result.get("deleted", []))
                                self.show_info(f"Удалено {deleted_count} неиспользуемых сетей.")
                            else:
                                self.show_error(f"Ошибка при очистке сетей: {result.get('error', 'Неизвестная ошибка')}")
                        GLib.idle_add(update_ui)
                    except Exception as e:
                        GLib.idle_add(lambda: self.show_error(f"Ошибка при очистке сетей: {e}"))
                threading.Thread(target=prune_task).start()

        dialog.connect("response", on_response)
        dialog.present()


    def on_refresh_volumes(self, button):
        self.load_volumes()

    def on_delete_selected_volumes(self, button):
        # Получаем список выбранных томов
        selected_volume_names = []
        for row in self.volumes_store:
            if row[2]:  # Если чекбокс выбран
                selected_volume_names.append(row[0])  # Добавляем имя тома

        if not selected_volume_names:
            self.show_error("Не выбрано ни одного тома")
            return

        # Создаем диалог подтверждения
        dialog = Gtk.MessageDialog(
            transient_for=self.win,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Вы уверены, что хотите удалить {len(selected_volume_names)} выбранных томов?"
        )

        def on_response(dialog, response_id):
            dialog.destroy()
            if response_id == Gtk.ResponseType.YES:
                # Удаляем томы в отдельном потоке
                def remove_volumes():
                    try:
                        results = self.docker_api.delete_volumes(selected_volume_names)
                        # Подсчитываем статистику
                        success_count = sum(1 for success in results.values() if success)
                        fail_count = len(results) - success_count
                        def update_ui():
                            self.load_volumes()
                            self.show_info(f"Удалено {success_count} томов. Не удалось удалить {fail_count} томов.")
                        GLib.idle_add(update_ui)
                    except Exception as e:
                        GLib.idle_add(lambda: self.show_error(f"Ошибка при удалении томов: {e}"))
                threading.Thread(target=remove_volumes).start()

        dialog.connect("response", on_response)
        dialog.present()


    def on_prune_volumes(self, button):
        # Создаем диалог подтверждения
        dialog = Gtk.MessageDialog(
            transient_for=self.win,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Вы уверены, что хотите очистить неиспользуемые тома Docker?"
        )

        def on_response(dialog, response_id):
            dialog.destroy()
            if response_id == Gtk.ResponseType.YES:
                # Выполняем очистку в отдельном потоке
                def prune_task():
                    try:
                        result = self.docker_api.prune_volumes()
                        def update_ui():
                            self.load_volumes()
                            if result["success"]:
                                deleted_count = len(result.get("deleted", []))
                                space_reclaimed = self.docker_api.format_size(result.get("space_reclaimed", 0))
                                self.show_info(f"Удалено {deleted_count} томов. Освобождено {space_reclaimed} дискового пространства.")
                            else:
                                self.show_error(f"Ошибка при очистке томов: {result.get('error', 'Неизвестная ошибка')}")
                        GLib.idle_add(update_ui)
                    except Exception as e:
                        GLib.idle_add(lambda: self.show_error(f"Ошибка при очистке томов: {e}"))
                threading.Thread(target=prune_task).start()

        dialog.connect("response", on_response)
        dialog.present()


    def on_system_prune(self, button):
        # Создаем диалог подтверждения
        dialog = Gtk.MessageDialog(
            transient_for=self.win,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Вы уверены, что хотите очистить всю систему Docker?\n\nЭто удалит все неиспользуемые контейнеры, сети, образы и тома."
        )

        def on_response(dialog, response_id):
            dialog.destroy()
            if response_id == Gtk.ResponseType.YES:
                # Выполняем очистку в отдельном потоке
                def prune_task():
                    try:
                        result = self.docker_api.prune_system()
                        def update_ui():
                            # Обновляем все списки
                            self.load_images()
                            self.load_containers()
                            self.load_networks()
                            self.load_volumes()
                            if result["success"]:
                                space_reclaimed = self.docker_api.format_size(result.get("space_reclaimed", 0))
                                self.show_info(f"Система Docker успешно очищена. Освобождено {space_reclaimed} дискового пространства.")
                            else:
                                self.show_error(f"Ошибка при очистке системы: {result.get('error', 'Неизвестная ошибка')}")
                        GLib.idle_add(update_ui)
                    except Exception as e:
                        GLib.idle_add(lambda: self.show_error(f"Ошибка при очистке системы: {e}"))
                threading.Thread(target=prune_task).start()

        dialog.connect("response", on_response)
        dialog.present()


    # Вспомогательные методы
    def show_error(self, message):
        """Показывает диалоговое окно с сообщением об ошибке."""
        dialog = Gtk.MessageDialog(
            transient_for=self.win,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        def on_response(dialog, response_id):
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.present()


    def show_info(self, message):
        """Показывает диалоговое окно с информационным сообщением."""
        dialog = Gtk.MessageDialog(
            transient_for=self.win,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        def on_response(dialog, response_id):
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.present()

def main():
    app = DockerGuiApp()
    app.run(None)

if __name__ == "__main__":
    main()
