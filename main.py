import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QTextEdit, QListWidget, QListWidgetItem, QFormLayout, QGroupBox,
    QMessageBox, QDialog, QFrame, QSizePolicy, QDateTimeEdit, QComboBox,
    QCalendarWidget, QDateEdit, QScrollArea, QHeaderView, QTableWidget, QTableWidgetItem,
    QSplitter, QCompleter
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QDate, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
from datetime import datetime


class TransactionItem(QWidget):
    """Custom widget for displaying transaction items with styled edit and remove buttons."""
    def __init__(self, transaction, index, parent=None):
        super().__init__(parent)
        self.transaction = transaction
        self.index = index  # Store the index of the transaction
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(15)

        info_layout = QVBoxLayout()

        # Name label
        name_label = QLabel(self.transaction['name'])
        name_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #212121;")
        info_layout.addWidget(name_label)

        # Amount label
        amount_text = f"₹{self.transaction['amount']:.2f}"
        amount_label = QLabel(amount_text)
        if self.transaction['type'] == 'receive':
            amount_label.setStyleSheet("font-size: 16px; color: #4CAF50; font-weight: bold;")
        else:
            amount_label.setStyleSheet("font-size: 16px; color: #d32f2f; font-weight: bold;")
        info_layout.addWidget(amount_label)

        # Description label
        self.desc_label = QLabel(self.transaction['description'])
        self.desc_label.setStyleSheet("color: #666666; margin-top: 2px;")
        self.desc_label.setWordWrap(True)
        self.desc_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum) # Make it wrap and take minimum vertical space
        info_layout.addWidget(self.desc_label)

        # Date label
        date_label = QLabel(self.transaction['datetime'])
        date_label.setStyleSheet("font-size: 11px; color: #9e9e9e; margin-top: 2px;")
        info_layout.addWidget(date_label)

        layout.addLayout(info_layout, 1)

        # Edit and Remove Buttons (Styled)
        controls_layout = QVBoxLayout() # Arrange buttons vertically
        controls_layout.setSpacing(8)

        self.edit_button = QPushButton("Edit")
        self.edit_button.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; border: none; border-radius: 5px; padding: 6px 12px; font-size: 11px; }"
            "QPushButton:hover { background-color: #1976D2; }"
        )
        self.edit_button.setCursor(Qt.PointingHandCursor)

        self.remove_button = QPushButton("Remove")
        self.remove_button.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; border: none; border-radius: 5px; padding: 6px 12px; font-size: 11px; }"
            "QPushButton:hover { background-color: #d32f2f; }"
        )
        self.remove_button.setCursor(Qt.PointingHandCursor)

        controls_layout.addWidget(self.edit_button)
        controls_layout.addWidget(self.remove_button)
        layout.addLayout(controls_layout)

        # Add a line to separate items
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #e0e0e0;")
        layout.addWidget(line)

        self.setLayout(layout)


class FinanceApp(QWidget):
    """
    A finance tracking application using PyQt5 for the GUI and a JSON file for data storage with edit and remove features.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Finance Tracker")
        self.setGeometry(100, 100, 1200, 700)  # Increased default size for better UI

        self.balance = 0.0
        self.transactions = []
        self.filtered_transactions = []  # For search functionality
        self.data_file = "transactions.json"  # Name of the JSON file
        self.editing_index = None  # To keep track of the transaction being edited

        # Form input fields as instance attributes
        self.name_input = None
        self.amount_input = None
        self.desc_input = None
        self.date_input = None
        self.submit_btn = None
        self.form_popup = None
        self.form_type = None

        # Set application font
        font = QFont("Segoe UI", 10)
        QApplication.setFont(font)

        self.setup_ui()  # Initialize the UI FIRST
        self._load_and_display_transactions() # THEN load and display
        self.update_balance_ui() # Ensure initial balance is displayed

        # Start timer to periodically reload transactions (simulating real-time)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._load_and_display_transactions) # Reload data
        self.timer.start(5000)  # Reload every 5 seconds

    def setup_ui(self):
        """
        Sets up the user interface of the application.
        """
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Sidebar
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(20)

        # App Logo/Title
        app_title = QLabel("Finance Tracker")
        app_title.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin-bottom: 15px;")
        app_title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(app_title)

        # Balance Section
        balance_widget = QWidget()
        balance_widget.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;")
        balance_layout = QVBoxLayout(balance_widget)

        balance_title = QLabel("Current Balance")
        balance_title.setStyleSheet("color: #b3e5fc; font-size: 14px;")
        balance_layout.addWidget(balance_title)

        self.balance_label = QLabel("₹0.00")
        self.balance_label.setStyleSheet("font-weight: bold; font-size: 26px; color: white;")
        balance_layout.addWidget(self.balance_label)

        sidebar_layout.addWidget(balance_widget)

        # Transaction Buttons
        self.receive_button = QPushButton("Receive Money")
        self.receive_button.clicked.connect(lambda: self.show_form("receive"))
        self.receive_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border: none; border-radius: 8px; padding: 12px; font-size: 14px; }"
            "QPushButton:hover { background-color: #367c39; }"
        )
        self.receive_button.setCursor(Qt.PointingHandCursor)
        sidebar_layout.addWidget(self.receive_button)

        self.send_button = QPushButton("Send Money")
        self.send_button.clicked.connect(lambda: self.show_form("send"))
        self.send_button.setStyleSheet(
            "QPushButton { background-color: #F44336; color: white; border: none; border-radius: 8px; padding: 12px; font-size: 14px; }"
            "QPushButton:hover { background-color: #d32f2f; }"
        )
        self.send_button.setCursor(Qt.PointingHandCursor)
        sidebar_layout.addWidget(self.send_button)

        # Credits
        credits = QLabel("© 2025 Finance App")
        credits.setStyleSheet("color: #78909c; font-size: 10px; margin-top: 10px;")
        credits.setAlignment(Qt.AlignCenter)

        sidebar_layout.addStretch()
        sidebar_layout.addWidget(credits)
        sidebar_widget.setStyleSheet("background-color: #263238; border-radius: 15px;")
        sidebar_widget.setFixedWidth(250)  # Fixed width for sidebar
        main_layout.addWidget(sidebar_widget)

        # Main Content Area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Search bar (NEW FEATURE)
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, description or amount...")
        self.search_input.setStyleSheet(
            "QLineEdit { border: 2px solid #dcedc8; border-radius: 8px; padding: 10px; font-size: 14px; }"
            "QLineEdit:focus { border-color: #8bc34a; }"
        )
        self.search_input.textChanged.connect(self.search_transactions)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)

        # Clear search button
        self.clear_search_button = QPushButton("Clear")
        self.clear_search_button.setStyleSheet(
            "QPushButton { background-color: #9e9e9e; color: white; border: none; border-radius: 8px; padding: 8px 15px; }"
            "QPushButton:hover { background-color: #757575; }"
        )
        self.clear_search_button.clicked.connect(self.clear_search)
        self.clear_search_button.setCursor(Qt.PointingHandCursor)
        search_layout.addWidget(self.clear_search_button)

        content_layout.addLayout(search_layout)

        # Transaction Lists - Using a splitter for responsiveness
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)
        splitter.setChildrenCollapsible(False)

        # Received Section
        received_widget = QWidget()
        received_layout = QVBoxLayout(received_widget)
        received_layout.setContentsMargins(10, 10, 10, 10)

        received_header = QLabel("Money Received")
        received_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #00897b; margin-bottom: 10px;")
        received_layout.addWidget(received_header)

        self.received_list = QListWidget()
        self.received_list.setStyleSheet(
            "QListWidget { background-color: #e0f7fa; border-radius: 12px; padding: 10px; }"
            "QListWidget::item { border-bottom: 1px solid #b2ebf2; padding: 5px; }"
            "QListWidget::item:selected { background-color: #b2ebf2; }"
        )
        self.received_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        received_layout.addWidget(self.received_list)

        splitter.addWidget(received_widget)

        # Sent Section
        sent_widget = QWidget()
        sent_layout = QVBoxLayout(sent_widget)
        sent_layout.setContentsMargins(10, 10, 10, 10)

        sent_header = QLabel("Money Sent")
        sent_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #d32f2f; margin-bottom: 10px;")
        sent_layout.addWidget(sent_header)

        self.sent_list = QListWidget()
        self.sent_list.setStyleSheet(
            "QListWidget { background-color: #f3e5f5; border-radius: 12px; padding: 10px; }"
            "QListWidget::item { border-bottom: 1px solid #e1bee7; padding: 5px; }"
            "QListWidget::item:selected { background-color: #e1bee7; }"
        )
        self.sent_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sent_layout.addWidget(self.sent_list)

        splitter.addWidget(sent_widget)

        # Make the splitter sections equal width initially
        splitter.setSizes([500, 500])

        content_layout.addWidget(splitter)
        content_widget.setStyleSheet("background-color: #f5f5f5; border-radius: 15px;")
        main_layout.addWidget(content_widget, 1)  # Content area takes most space

        # Form Popup
        self.form_popup = self.create_form_popup()
        self.form_popup.hide()

        # Set overall app style
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #90a4ae;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def create_form_popup(self):
        """
        Creates the popup form for entering/editing transaction details.
        Now includes date selection functionality.

        Returns:
            QWidget: The form widget.
        """
        self.form_popup = QDialog(self, Qt.Window)  # Use QDialog and assign to self.form_popup
        self.form_popup.setWindowTitle("Transaction Form")
        self.form_popup.setGeometry(300, 200, 500, 450)  # Larger for more content
        self.form_popup.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        self.form_type = None

        form_group = QGroupBox("Transaction Details")
        form_group.setStyleSheet(
            "QGroupBox { border: 1px solid #90caf9; border-radius: 8px; margin-top: 20px; padding: 15px; font-weight: bold; }"
            "QGroupBox::title { color: #1976d2; }"
        )
        form_group_layout = QFormLayout()
        form_group_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
        form_group_layout.setVerticalSpacing(15)

        # Name input
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(
            "QLineEdit { border: 2px solid #bbdefb; border-radius: 8px; padding: 10px; font-size: 14px; }"
            "QLineEdit:focus { border-color: #42a5f5; }"
        )
        self.name_input.setPlaceholderText("Enter Name")
        form_group_layout.addRow("Name:", self.name_input)

        # Amount input
        self.amount_input = QLineEdit()
        self.amount_input.setStyleSheet(
            "QLineEdit { border: 2px solid #bbdefb; border-radius: 8px; padding: 10px; font-size: 14px; }"
            "QLineEdit:focus { border-color: #42a5f5; }"
        )
        self.amount_input.setPlaceholderText("Enter Amount (₹)")
        form_group_layout.addRow("Amount:", self.amount_input)

        # Description input
        self.desc_input = QTextEdit()
        self.desc_input.setFixedHeight(80)
        self.desc_input.setStyleSheet(
            "QTextEdit { border: 2px solid #bbdefb; border-radius: 8px; padding: 10px; font-size: 14px; }"
            "QTextEdit:focus { border-color: #42a5f5; }"
        )
        self.desc_input.setPlaceholderText("Enter Description")
        form_group_layout.addRow("Description:", self.desc_input)

        # Date and time selection (NEW FEATURE)
        self.date_input = QDateTimeEdit()
        self.date_input.setDateTime(QDateTime.currentDateTime())
        self.date_input.setCalendarPopup(True)
        self.date_input.setStyleSheet(
            "QDateTimeEdit { border: 2px solid #bbdefb; border-radius: 8px; padding: 10px; font-size: 14px; }"
            "QDateTimeEdit:focus { border-color: #42a5f5; }"
            "QCalendarWidget { selection-background-color: #1976d2; selection-color: white; }"
        )
        form_group_layout.addRow("Date & Time:", self.date_input)

        form_group.setLayout(form_group_layout)
        form_layout.addWidget(form_group)

        # Buttons layout
        buttons_layout = QHBoxLayout()

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(
            "QPushButton { background-color: #9e9e9e; color: white; border: none; border-radius: 8px; padding: 12px; font-size: 14px; }"
            "QPushButton:hover { background-color: #757575; }"
        )
        cancel_btn.clicked.connect(self.form_popup.hide)
        buttons_layout.addWidget(cancel_btn)
        self.cancel_btn = cancel_btn  # Make it an instance attribute

        # Submit button
        submit_btn = QPushButton("Submit")
        submit_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border: none; border-radius: 8px; padding: 12px; font-size: 14px; }"
            "QPushButton:hover { background-color: #367c39; }"
        )
        submit_btn.clicked.connect(self.submit_transaction)
        buttons_layout.addWidget(submit_btn)
        self.submit_btn = submit_btn  # Make it an instance attribute

        form_layout.addLayout(buttons_layout)
        self.form_popup.setLayout(form_layout)  # Set layout for the form_popup

        return self.form_popup  # Return the created form_popup

    def show_form(self, transaction_type=None, index_to_edit=None):
        """
        Displays the transaction input form for adding or editing.

        Args:
            transaction_type (str, optional): The type of transaction ("receive" or "send"). Defaults to None for editing.
            index_to_edit (int, optional): The index of the transaction to edit. Defaults to None for adding.
        """
        self.form_type = transaction_type
        self.editing_index = index_to_edit
        if self.name_input:
            self.name_input.clear()
        if self.amount_input:
            self.amount_input.clear()
        if self.desc_input:
            self.desc_input.clear()
        if self.date_input:
            self.date_input.setDateTime(QDateTime.currentDateTime())  # Reset to current date/time

        # Set form title based on action
        if self.form_popup:
            if transaction_type == "receive" and index_to_edit is None:
                self.form_popup.setWindowTitle("Receive Money")
            elif transaction_type == "send" and index_to_edit is None:
                self.form_popup.setWindowTitle("Send Money")
            else:
                self.form_popup.setWindowTitle("Edit Transaction")

            if index_to_edit is not None:
                # Determine if we're using filtered or all transactions
                if self.search_input.text().strip():
                    original_index = self._get_original_index(index_to_edit)
                    if 0 <= original_index < len(self.transactions):
                        transaction_to_edit = self.transactions[original_index]
                        if self.name_input:
                            self.name_input.setText(transaction_to_edit['name'])
                        if self.amount_input:
                            self.amount_input.setText(str(transaction_to_edit['amount']))
                        if self.desc_input:
                            self.desc_input.setText(transaction_to_edit['description'])
                        if self.date_input:
                            try:
                                date_time = QDateTime.fromString(transaction_to_edit['datetime'], "dd-MM-yyyy HH:mm:ss")
                                if date_time.isValid():
                                    self.date_input.setDateTime(date_time)
                                else:
                                    self.date_input.setDateTime(QDateTime.currentDateTime())
                            except:
                                self.date_input.setDateTime(QDateTime.currentDateTime())
                        if self.submit_btn:
                            self.submit_btn.setText("Save Changes")
                else:
                    if 0 <= index_to_edit < len(self.transactions):
                        transaction_to_edit = self.transactions[index_to_edit]
                        if self.name_input:
                            self.name_input.setText(transaction_to_edit['name'])
                        if self.amount_input:
                            self.amount_input.setText(str(transaction_to_edit['amount']))
                        if self.desc_input:
                            self.desc_input.setText(transaction_to_edit['description'])
                        if self.date_input:
                            try:
                                date_time = QDateTime.fromString(transaction_to_edit['datetime'], "dd-MM-yyyy HH:mm:ss")
                                if date_time.isValid():
                                    self.date_input.setDateTime(date_time)
                                else:
                                    self.date_input.setDateTime(QDateTime.currentDateTime())
                            except:
                                self.date_input.setDateTime(QDateTime.currentDateTime())
                        if self.submit_btn:
                            self.submit_btn.setText("Save Changes")
            else:
                if self.submit_btn:
                    self.submit_btn.setText("Submit")

            self.form_popup.show()

    def submit_transaction(self):
        """
        Submits a new transaction or saves an edited transaction.
        Now uses the selected date from date picker instead of current time.
        """
        if not self.name_input or not self.amount_input:
            return  # Should not happen if form is created correctly

        name = self.name_input.text().strip()
        amount_text = self.amount_input.text().strip()
        desc = self.desc_input.toPlainText().strip() if self.desc_input else ""
        selected_datetime = self.date_input.dateTime().toString("dd-MM-yyyy HH:mm:ss") if self.date_input else datetime.now().strftime("dd-MM-yyyy HH:mm:ss")

        # Validate inputs
        if not name:
            QMessageBox.warning(self.form_popup, "Input Error", "Name cannot be empty.")
            return
        if not amount_text:
            QMessageBox.warning(self.form_popup, "Input Error", "Amount cannot be empty.")
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                QMessageBox.warning(self.form_popup, "Input Error", "Amount must be positive.")
                return
        except ValueError:
            QMessageBox.warning(self.form_popup, "Input Error", "Invalid amount format.")
            return

        transaction_data = {
            "name": name,
            "amount": amount,
            "description": desc,
            "type": self.form_type if self.form_type else (
                self.transactions[self._get_original_index(self.editing_index)]['type']
                if self.search_input.text().strip() and self.editing_index is not None and 0 <= self._get_original_index(self.editing_index) < len(self.transactions) else
                self.transactions[self.editing_index]['type'] if self.editing_index is not None and 0 <= self.editing_index < len(self.transactions) else "receive" # Default to receive if type can't be determined
            ),
            "datetime": selected_datetime
        }

        if self.editing_index is not None:
            # Get original index if using filtered results
            if self.search_input.text().strip():
                original_index = self._get_original_index(self.editing_index)
                if 0 <= original_index < len(self.transactions):
                    self.transactions[original_index] = transaction_data
            else:
                if 0 <= self.editing_index < len(self.transactions):
                    self.transactions[self.editing_index] = transaction_data
            self.editing_index = None
            if self.form_popup:
                QMessageBox.information(self.form_popup, "Success", "Transaction updated successfully!")
        else:
            self.transactions.append(transaction_data)
            if self.form_popup:
                QMessageBox.information(self.form_popup, "Success", "Transaction added successfully!")

        self.save_transactions()
        self._load_and_display_transactions()  # Reload and update UI
        if self.form_popup:
            self.form_popup.hide()

    def remove_transaction(self, index_to_remove):
        """
        Removes a transaction at the given index.

        Args:
            index_to_remove (int): The index of the transaction to remove.
        """
        reply = QMessageBox.question(
            self,
            "Remove Transaction",
            "Are you sure you want to remove this transaction?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Get the original index if using filtered results
            if self.search_input.text().strip():
                original_index = self._get_original_index(index_to_remove)
                if 0 <= original_index < len(self.transactions):
                    del self.transactions[original_index]
            else:
                if 0 <= index_to_remove < len(self.transactions):
                    del self.transactions[index_to_remove]

            self.save_transactions()
            self._load_and_display_transactions()  # Reload and update UI

    def _load_and_display_transactions(self):
        """
        Loads transactions from the JSON file and updates the UI.
        """
        self.load_transactions()
        self.display_transactions(self.transactions if not self.search_input.text().strip() else self.filtered_transactions)

    def display_transactions(self, transactions_to_display):
        """
        Updates the UI with the given transactions.

        Args:
            transactions_to_display (list): List of transactions to display.
        """
        self.received_list.clear()
        self.sent_list.clear()

        for index, tx in enumerate(transactions_to_display):
            self._add_transaction_to_ui(tx, index)

        self.update_balance_ui()

        # Update lists with placeholder when empty
        if self.received_list.count() == 0:
            empty_item = QListWidgetItem()
            empty_widget = QLabel("No received transactions found")
            empty_widget.setStyleSheet("color: #9e9e9e; padding: 20px; font-style: italic;")
            empty_widget.setAlignment(Qt.AlignCenter)
            empty_item.setSizeHint(QSize(0, 50))
            self.received_list.addItem(empty_item)
            self.received_list.setItemWidget(empty_item, empty_widget)

        if self.sent_list.count() == 0:
            empty_item = QListWidgetItem()
            empty_widget = QLabel("No sent transactions found")
            empty_widget.setStyleSheet("color: #9e9e9e; padding: 20px; font-style: italic;")
            empty_widget.setAlignment(Qt.AlignCenter)
            empty_item.setSizeHint(QSize(0, 50))
            self.sent_list.addItem(empty_item)
            self.sent_list.setItemWidget(empty_item, empty_widget)

    def search_transactions(self):
        """
        Filters transactions based on search query.
        NEW FEATURE: Search functionality
        """
        search_query = self.search_input.text().strip().lower()

        if not search_query:
            self.display_transactions(self.transactions)
            return

        self.filtered_transactions = []

        for tx in self.transactions:
            if (search_query in tx['name'].lower() or
                    search_query in tx['description'].lower() or
                    search_query in str(tx['amount']).lower() or
                    search_query in tx['datetime'].lower()):
                self.filtered_transactions.append(tx)

        self.display_transactions(self.filtered_transactions)

    def clear_search(self):
        """Clears the search input and shows all transactions."""
        self.search_input.clear()
        self.display_transactions(self.transactions)

    def _get_original_index(self, filtered_index):
        """
        Converts an index from filtered results to the original transactions list.

        Args:
            filtered_index (int): Index in the filtered list

        Returns:
            int: Index in the original transactions list
        """
        if filtered_index < 0 or filtered_index >= len(self.filtered_transactions):
            return -1

        filtered_tx = self.filtered_transactions[filtered_index]

        # Find the same transaction in the original list
        for i, tx in enumerate(self.transactions):
            if (tx['name'] == filtered_tx['name'] and
                    tx['amount'] == filtered_tx['amount'] and
                    tx['datetime'] == filtered_tx['datetime']):
                return i

        return -1

    def load_transactions(self):
        """
        Loads transactions from the JSON file into the self.transactions list.
        """
        try:
            with open(self.data_file, 'r') as f:
                self.transactions = json.load(f)
        except FileNotFoundError:
            self.transactions = []
        except json.JSONDecodeError:
            self.transactions = []
            QMessageBox.critical(self, "Error", "Could not decode the transactions file. Starting with an empty list.")

    def save_transactions(self):
        """
        Saves the current list of transactions to the JSON file.
        """
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.transactions, f, indent=4)
        except IOError:
            QMessageBox.critical(self, "Error", "Could not save transactions to the file.")

    def _add_transaction_to_ui(self, tx, index):
        """
        Adds a transaction to the appropriate list in the UI using a custom widget with edit and remove buttons.

        Args:
            tx (dict): The transaction data.
            index (int): The index of the transaction in the list being displayed.
        """
        # Create custom widget for this transaction
        transaction_widget = TransactionItem(tx, index)
        transaction_widget.edit_button.clicked.connect(lambda idx=index: self.show_form(index_to_edit=idx))
        transaction_widget.remove_button.clicked.connect(lambda idx=index: self.remove_transaction(idx))

        # Create list item and set its size
        item = QListWidgetItem()
        item.setSizeHint(transaction_widget.sizeHint())

        # Add to appropriate list
        if tx["type"] == "receive":
            self.received_list.addItem(item)
            self.received_list.setItemWidget(item, transaction_widget)
        else:
            self.sent_list.addItem(item)
            self.sent_list.setItemWidget(item, transaction_widget)

    def update_balance_ui(self):
        self.balance = 0.0
        for tx in self.transactions:
            if tx["type"] == "receive":
                self.balance += float(tx["amount"])
            else:
                self.balance -= float(tx["amount"])

        # Format balance with commas for thousands separator and two decimal places
        formatted_balance = f"₹{abs(self.balance):,.2f}"

        # Change color based on balance status
        if self.balance >= 0:
            self.balance_label.setStyleSheet("font-weight: bold; font-size: 26px; color: #4CAF50;")
            self.balance_label.setText(formatted_balance)
        else:
            self.balance_label.setStyleSheet("font-weight: bold; font-size: 26px; color: #F44336;")
            self.balance_label.setText("-" + formatted_balance)

    def closeEvent(self, event):
        """
        Overrides the closeEvent to ensure transactions are saved and the timer is stopped.
        """
        self.save_transactions()
        self.timer.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinanceApp()
    window.show()
    sys.exit(app.exec_())