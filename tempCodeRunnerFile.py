import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit,
    QPushButton, QHBoxLayout, QStatusBar, QProgressBar, QTabWidget, QMenu, QComboBox, QDialog, QListWidget, QMessageBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyQt5.QtGui import QIcon, QColor
from PyQt6.QtWebEngineCore import QWebEngineProfile


class CustomWebEnginePage(QWebEnginePage):
    def __init__(self):
        super().__init__()

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        print(f"JS Console: {msg} at {line} in {sourceID}")

    def acceptNavigationRequest(self, url, _type, is_main_frame):
        # Intercept navigation and allow all URLs
        print(f"Navigating to: {url.toString()}")
        return super().acceptNavigationRequest(url, _type, is_main_frame)
    def permissionRequest(self, request):
        """Handle Permission for location, Camera etc."""
        if request.permission() == QWebEnginePage.Geolocation:
            self.handle_geolocation_permission(request)
        elif request.permission() == QWebEnginePage.MediaAudioCapture:
            self.handle_media_permission(request)
        elif request.permission() == QWebEnginePage.MediaVideoCapture:
            self.handle_media_permission(request)
        else:
            request.ignore()  #Ignore all other permissions
        
    def handle_geolocation_permission(self, request):
        response = QMessageBox.question(None, "Geolocation Request", 
                                        "Do you allow this site to access your location?", 
                                        QMessageBox.Yes | QMessageBox.No)
        if response == QMessageBox.Yes:
            request.accept()
        else:
            request.reject()

    def handle_media_permission(self, request):
        response = QMessageBox.question(None, "Media Permission Request", 
                                        "Do you allow this site to access your camera and microphone?", 
                                        QMessageBox.Yes | QMessageBox.No)
        if response == QMessageBox.Yes:
            request.accept()
        else:
            request.reject()

    def userAgentForUrl(self, url):
        # Set a modern user agent like Chrome
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        return user_agent
    
    def enable_web_features(self):
        settings = self.page().settings()
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("My Browser")
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QIcon('mybrowser.png'))


        # Create the main layout
        self.browser_layout = QVBoxLayout()

        # Create the top navigation bar
        self.nav_layout = QHBoxLayout()

        # Add the Back button
        self.back_button = QPushButton("< Back")
        self.back_button.clicked.connect(self.back)
        self.nav_layout.addWidget(self.back_button)

        # Add the Forward button
        self.forward_button = QPushButton("Forward >")
        self.forward_button.clicked.connect(self.forward)
        self.nav_layout.addWidget(self.forward_button)

        # Add the Reload button
        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.reload)
        self.nav_layout.addWidget(self.reload_button)

        # Add the Home button
        self.home_button = QPushButton("Home")
        self.home_button.clicked.connect(self.go_home)
        self.nav_layout.addWidget(self.home_button)

        # Add the New Tab Button
        self.new_tab_button = QPushButton("+ New Tab")
        self.new_tab_button.clicked.connect(self.open_new_tab)
        self.nav_layout.addWidget(self.new_tab_button)

        # Add the address bar
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter URL and press Enter...")
        self.address_bar.returnPressed.connect(self.load_url)
        self.nav_layout.addWidget(self.address_bar)

        # Add bookmarks dropdown
        self.bookmarks_menu = QComboBox()
        self.bookmarks_menu.addItem("Bookmarks")
        self.bookmarks_menu.activated[str].connect(self.load_bookmark)
        self.nav_layout.addWidget(self.bookmarks_menu)

        # Add the Add Bookmark button
        self.add_bookmark_button = QPushButton("Add Bookmark")
        self.add_bookmark_button.clicked.connect(self.add_bookmark)
        self.nav_layout.addWidget(self.add_bookmark_button)

        # Add history button
        self.history_button = QPushButton("View History")
        self.history_button.clicked.connect(self.show_history)
        self.nav_layout.addWidget(self.history_button)

        # Add the Dark Mode toggle button
        self.dark_mode_button = QPushButton("Toggle Dark Mode")
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        self.nav_layout.addWidget(self.dark_mode_button)

        # Add the Clear History button
        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.clicked.connect(self.clear_history)
        self.nav_layout.addWidget(self.clear_history_button)

        # Add the navigation bar to the main layout
        self.browser_layout.addLayout(self.nav_layout)

        # Create a QTabWidget to manage multiple tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        self.browser_layout.addWidget(self.tab_widget)

        # Add tab context menu
        self.tab_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.show_tab_context_menu)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.statusBar().addPermanentWidget(self.progress_bar)
        self.progress_bar.setVisible(False)

        # Set up the central widget
        container = QWidget()
        container.setLayout(self.browser_layout)
        self.setCentralWidget(container)

        # Track history and bookmarks
        self.history = []
        self.bookmarks = []
        self.dark_mode = False  # Track dark mode state

        #  Add the Search Engine Selection dropDown
        self.search_engine_combo = QComboBox()
        self.search_engine_combo.addItem("Google", "https://www.google.com/search?q=")
        self.search_engine_combo.addItem("Bing", "https://www.bing.com/search?q=")
        self.search_engine_combo.addItem("DuckDuckGo", "https://www.duckduckgo.com/?q=")
        self.search_engine_combo.addItem("Yahoo!", "https://www.search.yahoo.com/search?p=")
        self.search_engine_combo.setCurrentIndex(0) #default to Google
        self.nav_layout.addWidget(self.search_engine_combo)

        # Create the setting Menu
        self.settings_button = QPushButton("...")
        self.settings_button.clicked.connect(self.show_setting_menu)
        self.nav_layout.addWidget(self.settings_button)

        # Open a default tab
        self.open_new_tab()

    def change_search_engine(self):
        # Open a dialog to let the user select a search engine
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Search Engine")

        layout = QVBoxLayout()
        combo = QComboBox(dialog)
        combo.addItems(["Google", "Bing", "DuckDuckGo", "Yahoo!"])

        # Set the current search engine as the selected item in the dropdown
        current_engine = self.search_engine_combo.currentText()
        combo.setCurrentText(current_engine)

        ok_button = QPushButton("OK", dialog)
        ok_button.clicked.connect(lambda: self.set_search_engine(combo.currentText()))
        ok_button.clicked.connect(dialog.accept)  # Close dialog on OK

        layout.addWidget(combo)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        dialog.exec_()
        

    def set_search_engine(self, engine):
        # Map search engines to their homepage URLs
        engines = {
            "Google": "https://www.google.com/",
            "Bing": "https://www.bing.com/",
            "DuckDuckGo": "https://www.duckduckgo.com/",
            "Yahoo!": "https://www.search.yahoo.com/",
        }

        # Update the search engine combo box with the selected engine
        if engine in engines:
            self.search_engine_combo.setCurrentText(engine)
            self.search_engine_combo.setItemData(self.search_engine_combo.currentIndex(), engines[engine])

            # Reload the current tab with the search engine's homepage
            self.load_url(engines[engine])


    def show_setting_menu(self):
        setting_menu = QMenu()

        # Add search engine selection
        search_engine_action = setting_menu.addAction("Choose Search Engine")
        search_engine_action.triggered.connect(self.change_search_engine)

        # Add history button 
        history_action = setting_menu.addAction("View History")
        history_action.triggered.connect(self.show_history)

        # Add bookmark button
        bookmark_action = setting_menu.addAction("View BookMarks")
        bookmark_action.triggered.connect(self.show_bookmark)

        setting_menu.exec_(self.settings_button.mapToGlobal(setting_menu.pos()))


    def open_new_tab(self, url="https://www.google.com"):
        if not isinstance(url, str):
            url = "https://www.google.com"
        
        # Create a webview and a loading page
        new_webview = QWebEngineView()

        # Use custom page for JavaScript handling
        new_webview.setPage(CustomWebEnginePage())

        # Enable JavaScript and additional settings
        settings = new_webview.page().settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)

        # Set URL to load
        new_webview.setUrl(QUrl(url))

        # Connect Title and icon updates
        new_webview.titleChanged.connect(self.update_tab_title)
        new_webview.iconChanged.connect(self.update_tab_icon)

        # Load progress and page finished signal
        new_webview.loadProgress.connect(self.update_progress_bar)
        new_webview.loadFinished.connect(self.page_loaded)

        # Add the new web view to a tab
        tab_index = self.tab_widget.addTab(new_webview, "New Tab")
        self.tab_widget.setCurrentIndex(tab_index)

        # Update the address bar when the tab's URL changes
        new_webview.urlChanged.connect(self.update_address_bar)

    def change_search_engine(self):
        # Open a dialog or logic to allow the user to change search engine
        pass

    def show_bookmarks(self):
        bookmark_dialog = QDialog(self)
        bookmark_dialog.setWindowTitle("Bookmarks")
        bookmark_layout = QVBoxLayout()

        bookmark_list = QListWidget()
        bookmark_list.addItems(self.bookmarks)
        bookmark_layout.addWidget(bookmark_list)

        bookmark_dialog.setLayout(bookmark_layout)
        bookmark_dialog.resize(300, 400)
        bookmark_dialog.exec_()

    def close_tab(self, index):
        current_webview = self.tab_widget.widget(index)
        if isinstance(current_webview, QWebEngineView):
            current_webview.page().triggerAction(QWebEnginePage.Stop)
        self.tab_widget.removeTab(index)

        if self.tab_widget.count() == 0:
            self.open_new_tab()
        # self.tab_widget.removeTab(index)
        # if self.tab_widget.count() == 0:
        #     self.open_new_tab()  # Open a new tab if all are closed

    def update_tab_title(self, title):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            self.tab_widget.setTabText(current_index, title)

    def update_tab_icon(self, icon):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            self.tab_widget.setTabIcon(current_index, icon)

    def tab_changed(self, index):
        if index != -1:
            current_webview = self.tab_widget.widget(index)
            if isinstance(current_webview, QWebEngineView):
                self.update_address_bar(current_webview.url())
                self.update_tab_title(current_webview.page().title())
                self.update_tab_icon(current_webview.page().icon())

    def show_tab_context_menu(self, position):
        menu = QMenu()
        duplicate_action = menu.addAction("Duplicate Tab")
        close_others_action = menu.addAction("Close Other Tabs")
        mute_action = menu.addAction("Mute/Unmute Tab") 
        action = menu.exec_(self.tab_widget.mapToGlobal(position))


        if action == duplicate_action:
            self.duplicate_tab()
        elif action == close_others_action:
            self.close_other_tabs()
        elif action == mute_action:
            self.toggle_tab_mute()

    def duplicate_tab(self):
        current_index = self.tab_widget.currentIndex()
        current_webview = self.tab_widget.widget(current_index)
        if isinstance(current_webview, QWebEngineView):
            self.open_new_tab(current_webview.url().toString())

    def close_other_tabs(self):
        current_index = self.tab_widget.currentIndex()
        for i in range(self.tab_widget.count() - 1, -1, -1):
            if i != current_index:
                self.tab_widget.removeTab(i)

    def load_url(self, url=None):
        if url is None:
            query = self.address_bar.text()
            if query:
                # Use Selected Search engine
                search_url = self.search_engine_combo.currentData() +  query
                self.load_url(search_url)
                return
            else:
                return # No url or search query entered
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        current_webview = self.tab_widget.currentWidget()
        if isinstance(current_webview, QWebEngineView):
            current_webview.setUrl(QUrl(url))

        if url not in self.history:
            self.history.append(url)
            self.history.sort()
        # if url is None:
        #     url = self.address_bar.text()
        # if not url.startswith("http://") and not url.startswith("https://"):
        #     url = "https://" + url

        # current_webview = self.tab_widget.currentWidget()
        # if isinstance(current_webview, QWebEngineView):
        #     current_webview.setUrl(QUrl(url))

        # Add to history
        if url not in self.history:
            self.history.append(url)
            self.history.sort()  # Sort history in alphabetical order

    def update_address_bar(self, url):
        self.address_bar.setText(url.toString())

    def update_progress_bar(self, progress):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(progress)

    def page_loaded(self):
        self.status_bar.showMessage("Page Loaded", 2000)
        self.progress_bar.setVisible(False)

    def go_home(self):
        self.load_url("https://www.google.com")

    def back(self):
        current_webview = self.tab_widget.currentWidget()
        if isinstance(current_webview, QWebEngineView):
            current_webview.back()

    def forward(self):
        current_webview = self.tab_widget.currentWidget()
        if isinstance(current_webview, QWebEngineView):
            current_webview.forward()

    def reload(self):
        current_webview = self.tab_widget.currentWidget()
        if isinstance(current_webview, QWebEngineView):
            current_webview.reload()

    def add_bookmark(self):
        current_webview = self.tab_widget.currentWidget()
        if isinstance(current_webview, QWebEngineView):
            url = current_webview.url().toString()
            if url not in self.bookmarks:
                self.bookmarks.append(url)
                self.bookmarks_menu.addItem(url)

    def load_bookmark(self, url):
        if url != "Bookmarks":
            self.load_url(url)

    def show_bookmark(self):
        bookmark_dialog = QDialog(self)
        bookmark_dialog.setWindowTitle("BookMark")
        bookmark_layout = QVBoxLayout()

        bookmark_list = QListWidget()
        bookmark_list.addItems(self.bookmarks)
        bookmark_list.itemClicked.connect(self.bookmark_item_clicked)
        bookmark_layout.addWidget(bookmark_list)
        
        bookmark_dialog.setLayout(bookmark_layout)
        bookmark_dialog.resize(300, 400)
        bookmark_dialog.exec_()

    def show_history(self):
        # Create and show history dialog
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle("History")
        history_layout = QVBoxLayout()

        history_list = QListWidget()
        history_list.addItems(self.history)  # Show history items
        history_list.itemClicked.connect(self.history_item_clicked)
        history_layout.addWidget(history_list)

        history_dialog.setLayout(history_layout)
        history_dialog.resize(300, 400)
        history_dialog.exec_()
    def bookmark_item_clicked(self, item):
        # When a Bookmark item is clicked load the corresponding url
        self.load_url(item.text())

    def history_item_clicked(self, item):
        # When a history item is clicked, load the corresponding URL
        self.load_url(item.text())

    def toggle_dark_mode(self):
        """Toggle between light and dark modes."""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2e2e2e;
                    color: white;
                }
                QLineEdit, QComboBox, QPushButton {
                    background-color: #4a4a4a;
                    color: white;
                }
                QStatusBar {
                    background-color: #2e2e2e;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("")

    def toggle_tab_mute(self):
        current_webview = self.tab_widget.currentWidget()
        if isinstance(current_webview, QWebEngineView):
            page = current_webview.page()
            is_muted = page.isAudioMuted()  # Check if the tab is currently muted
            page.setAudioMuted(not is_muted)  # Toggle mute
            self.status_bar.showMessage(f"Tab {'muted' if not is_muted else 'unmuted'}", 2000)

    def clear_history(self):
        """Clear the browsing history."""
        self.history.clear()
        self.show_history()  # Open history dialog again to show it's empty
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())
