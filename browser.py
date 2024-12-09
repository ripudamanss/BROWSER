import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout, QStatusBar, QProgressBar, QTabWidget, QTabBar
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtGui import QIcon

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("My Browser")
        self.setGeometry(100, 100, 1000, 600)

        # Set up the window icon
        self.setWindowIcon(QIcon('mybrowser.png'))

        # Create the main layout
        self.browser_layout = QVBoxLayout()

        # Create the top navigation bar (with buttons and address bar)
        self.nav_layout = QHBoxLayout()

        # Add the Back button
        self.back_button = QPushButton("< Back")
        self.back_button.clicked.connect(self.back)
        self.back_button.setFixedHeight(40)  # Set height to make button visible
        self.nav_layout.addWidget(self.back_button)

        # Add the Forward button
        self.forward_button = QPushButton("Forward >")
        self.forward_button.clicked.connect(self.forward)
        self.forward_button.setFixedHeight(40)  # Set height to make button visible
        self.nav_layout.addWidget(self.forward_button)

        # Add the Reload button
        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.reload)
        self.reload_button.setFixedHeight(40)  # Set height to make button visible
        self.nav_layout.addWidget(self.reload_button)

        # Add the Home button
        self.home_button = QPushButton("Home")
        # self.home_button.
        self.home_button.clicked.connect(self.go_home)
        self.nav_layout.addWidget(self.home_button)

        # Add the address bar
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter URL and press Enter...")
        self.address_bar.returnPressed.connect(self.load_url)
        self.nav_layout.addWidget(self.address_bar)

        # Add the navigation bar to the main layout
        self.browser_layout.addLayout(self.nav_layout)

        #Create a QTabwidget to manage multiple tabs
        self.tab_widget = QTabWidget()
        self.browser_layout.addWidget(self.tab_widget)

        # Add the browser view
        self.browser_view = QWebEngineView()
        self.browser_layout.addWidget(self.browser_view)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.browser_layout.addWidget(self.status_bar)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.statusBar().addWidget(self.progress_bar)
        
        # Connect to loading signals
        self.browser_view.loadStarted.connect(self.load_started)
        self.browser_view.loadFinished.connect(self.load_finished)

        # Set up the central widget
        container = QWidget()
        container.setLayout(self.browser_layout)
        self.setCentralWidget(container)

        #Open a default tab
        self.open_new_tab()
        # Load a default website
        self.browser_view.setUrl(QUrl("https://www.google.com"))
        # Update the address bar with the current url
        self.browser_view.urlChanged.connect(self.update_address_bar)

        # Apply styles using CSS
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 16px;  /* Adjust font size */
                border-radius: 4px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 4px;
                width: 600px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QWidget {
                background-color: white;
                border-radius: 4px;
            }
            QStatusBar {
                background-color: #ecf0f1}
            QTabWidget {
                background-color: #ecf0f1
            }
        """)
    
    def open_new_tab(self):
        new_tab = QWidget()
        new_tab_layout = QVBoxLayout()
        new_webview = QWebEngineView()
        new_webview.setUrl(QUrl("https://www.google.com"))
        new_tab_layout.addWidget(new_webview)
        new_tab.setLayout(new_tab_layout)

        #Add the new tab to the tab widget
        tab_index = self.tab_widget.addTab(new_tab, "New Tab")

        # Make the new tab the current tab
        self.tab_widget.setCurrentIndex(tab_index)

        # update the address bar when the current tab URL changes
        new_webview.urlChanged.connect(lambda url: self.update_address_bar(url))

        # add a close button to the tab
        self.tab_widget.tabBar().setTabButton(tab_index, QTabBar.RightSide, self.create_close_button(new_webview))
    
    def create_close_button(self, webview):
        close_button = QPushButton('X')
        close_button.clicked.connect(lambda: self.close_tab(webview))
        return close_button

    def close_tab(self, webview):
        tab_index = self.tab_widget.indexOf(webview.parent())
        if tab_index != -1:
            self.tab_widget.removeTab(tab_index)
    
    def load_url(self):
        url = self.address_bar.text()
        current_tab = self.tab_widget.currentWidget()
        webview = current_tab.findChild(QWebEngineView)

        if not url.startswith("https://") and not url.startswith("http://"):
            url = "https://" + url
        webview.setUrl(QUrl(url))


    def load_started(self):
        self.progress_bar.setValue(0)

    def load_finished(self):
        self.progress_bar.setValue(100)
        self.status_bar.showMessage("Page Loaded", 2000)

        # hide the progress bar after the page load
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False) #hide the progress bar after loading is completed

    def update_address_bar(self, url):
        self.address_bar.setText(url.toString())
        # self.browser_view.setUrl(oQUrl(url))

    # def load_url(self):
    #     url = self.address_bar.text()
    #     if not url.startswith("http"):
    #         url = "https://" + url

    def go_home(self):
        self.browser_view.setUrl(QUrl("https://www.google.com"))

    def page_loaded(self):
        self.progress_bar.setValue(100)
        self.status_bar.showMessgae("Page Loaded", 2000)
        # hide the progress bar after the page load
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False) #hide the progress bar after loading is completed

    def back(self):
        self.browser_view.back()
        # current_tab = self.tab_widget.currentWidget()
        # webview = current_tab.findChild(QWebEngineView)
        # if webview.history().canGoBack():
        #     webview.back()

    def forward(self):
        self.browser_view.forward()
        # current_tab = self.tab_widget.currentWidget()
        # webview = current_tab.findChild(QWebEngineView)
        # if webview.history().canGoForward():
        #     webview.forward()

    def reload(self):
        self.browser_view.reload()
        # current_tab = self.tab_widget.currentWidget()
        # webview = current_tab.findChild(QWebEngineView)
        # webview.reload()
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('mybrowser.png'))
    window = Browser()
    window.show()
    sys.exit(app.exec_())
