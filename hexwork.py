import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QFileDialog, QDesktopWidget, \
    QWidget, QHBoxLayout, QTextEdit, QDialog, QLabel, QInputDialog, QLineEdit
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont, QTextCursor, QTextCharFormat
from PyQt5.QtCore import Qt


# Returns palette settings
def get_palette():
    dark = QPalette()
    # Works only with Adwaita Dark theme
    # tested on Gnome 40.1
    '''dark.setColor(QPalette.Window, QColor(53, 53, 53))
    dark.setColor(QPalette.WindowText, Qt.white)
    dark.setColor(QPalette.Base, QColor(25, 25, 25))
    dark.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark.setColor(QPalette.ToolTipBase, Qt.white)
    dark.setColor(QPalette.ToolTipText, Qt.white)
    dark.setColor(QPalette.Text, Qt.white)
    dark.setColor(QPalette.Button, QColor(53, 53, 53))
    dark.setColor(QPalette.ButtonText, Qt.white)
    dark.setColor(QPalette.BrightText, Qt.white)
    dark.setColor(QPalette.Link, QColor(42, 130, 218))
    dark.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark.setColor(QPalette.HighlightedText, Qt.black)
    dark.setColor(QPalette.Background, QColor(53, 53, 53))'''
    return dark


class UserMessage(QDialog):
    def __init__(self, parent, window_title):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.label = QLabel(self)
        self.label.move(10, 5)
        self.setPalette(get_palette())

    def act(self, text):
        text = str(text)
        self.label.setText(text)
        self.setFixedSize(self.label.width() * 3 + 20, 30)
        print(self.windowTitle().title(), ': ', text, sep='')
        self.open()


class FileSelector(QFileDialog):
    def __init__(self):
        super().__init__()
        self.file_name = self.file_name()
        self.show()

    def file_name(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Directory View", "", "All Files (*)")

        return file_name


class FileSaver(QFileDialog):
    def __init__(self):
        super().__init__()

        self.file_name = self.file_name()

        self.show()

    def file_name(self):
        file_name, _ = QFileDialog.getSaveFileName(self)

        return file_name


class InputDialogue(QInputDialog):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.setPalette(get_palette())

    def act(self, text):
        response, complete = QInputDialog.getText(self, self.title, text, QLineEdit.Normal, '')

        if complete and response:
            print('InputDialogue(complete):', complete)
            return response
        else:
            print('InputDialogue(incomplete): ' + str(response if response else complete))
            return


class RealTimeTextEdit(QTextEdit):
    def __init__(self, app):
        super(RealTimeTextEdit, self).__init__()
        self.app = app

    def keyPressEvent(self, e) -> None:
        super(RealTimeTextEdit, self).keyPressEvent(e)
        '''if not self.app.exit_flag:
            self.app.data += bytes(chr(e.key()))
            self.app.print_data_app()'''


class App(QMainWindow):
    def __init__(self):
        self.exit_flag = True

        super().__init__()

        self.dig_per_col = 2

        self.encode = 'ASCII'

        self.main_text = RealTimeTextEdit(self)
        self.decoded_text = RealTimeTextEdit(self)
        self.offset_text = QTextEdit()

        self.setPalette(get_palette())

        self.init_ui()

        self.col_per_row = 1

        self.data = b''
        if len(sys.argv) > 1:
            self.read_data(sys.argv[1])

    def read_data(self, file_name):

        with open(file_name, 'rb') as file:
            self.data = hex(int.from_bytes(file.read(), 'big'))
            self.exit_flag = False

        self.print_data_app()

    def save_data(self, file_name):
        error_dialogue = UserMessage(self, 'Error')
        try:
            with open(file_name, 'wb') as file:
                file.write(self.data)
                print('File was saved as', file_name)
        except PermissionError as err:
            error_dialogue.act(err)

    def open_file(self):
        selector = FileSelector()
        file_name = selector.file_name

        if file_name:
            print('File was selected: ', file_name)
            self.read_data(file_name)
        else:
            print('No file was selected')

    def save_file(self):
        saver = FileSaver()
        file_name = saver.file_name

        if file_name:
            self.save_data(file_name)
        else:
            print('No file was saved')

    # Exit from app by Ctrl+Q
    def close(self):
        if not self.exit_flag:
            self.exit_flag = True
            self.close()

    def settings_menu(self):
        pass

    # Highlights hexadecimal text (middle column)
    def highlight_main_text(self):
        # Acceptation
        highlight_cursor = QTextCursor(self.decoded_text.document())
        cursor = self.main_text.textCursor()

        # Resetting
        highlight_cursor.select(QTextCursor.Document)
        highlight_cursor.setCharFormat(QTextCharFormat())
        highlight_cursor.clearSelection()

        # Getting info
        selection_start = cursor.selectionStart()
        selection_end = cursor.selectionEnd()

        main_text = self.main_text.toPlainText()
        decoded_text = self.decoded_text.toPlainText()

        decoded_start = len(main_text[:selection_start].split())
        decoded_start_offset = decoded_text[:decoded_start].count('\n')
        decoded_start_offset += decoded_start_offset // self.col_per_row

        decoded_end = len(main_text[:selection_end].split())
        decoded_end_offset = decoded_text[:decoded_end].count('\n')
        decoded_end_offset += decoded_end_offset // self.col_per_row

        # Select and highlight
        highlight_cursor.setPosition(decoded_start + decoded_start_offset, QTextCursor.MoveAnchor)
        highlight_cursor.setPosition(decoded_end + decoded_end_offset, QTextCursor.KeepAnchor)

        highlight = QTextCharFormat()
        highlight.setBackground(Qt.red)
        highlight_cursor.setCharFormat(highlight)
        highlight_cursor.clearSelection()

    # Highlights decoded text (right column)
    def highlight_decoded_text(self):
        # Acceptation
        highlight_cursor = QTextCursor(self.main_text.document())
        cursor = self.decoded_text.textCursor()

        # Resetting
        highlight_cursor.select(QTextCursor.Document)
        highlight_cursor.setCharFormat(QTextCharFormat())
        highlight_cursor.clearSelection()

        # Getting info
        selected_text = cursor.selectedText()
        selection_start = cursor.selectionStart()
        selection_end = cursor.selectionEnd()

        main_text = self.main_text.toPlainText()
        decoded_text = self.decoded_text.toPlainText()

        main_start = len(decoded_text[:selection_start].replace('\n', '')) * self.dig_per_col + \
                     decoded_text[:selection_start].count('\n') + \
                     len(decoded_text[:selection_start].replace('\n', '')) * 2

        main_end = len(decoded_text[:selection_end].replace('\n', '')) * self.dig_per_col + \
                   decoded_text[:selection_end].count('\n') + \
                   len(decoded_text[:selection_end].replace('\n', '')) * 2

        # Select and highlight
        highlight_cursor.setPosition(main_start, QTextCursor.MoveAnchor)
        highlight_cursor.setPosition(main_end - 2 if main_end > 0 else 0, QTextCursor.KeepAnchor)

        highlight = QTextCharFormat()
        highlight.setBackground(Qt.red)
        highlight_cursor.setCharFormat(highlight)
        highlight_cursor.clearSelection()

    # Calculates user input in dialogue by Ctrl+K
    def calc(self):
        dialogue = InputDialogue('Calculate')
        user_message = UserMessage(self, 'Answer')
        try:
            dial = dialogue.act('Expression:')
            if dial is not None:
                ans = eval(dial)
            else:
                return
        except Exception as err:
            ans = err
            user_message.setWindowTitle('Error')
        user_message.act(ans)

    def change_read_write_mode(self):
        self.main_text.setReadOnly(False if self.main_text.isReadOnly() else True)
        self.decoded_text.setReadOnly(False if self.decoded_text.isReadOnly() else True)

    # Prints file data in the app
    def print_data_app(self):
        if not self.exit_flag:
            data_str_tmp = str(self.data)[2:]
        else:
            data_str_tmp = ''.join(self.main_text.toPlainText().split())

        self.col_per_row = self.main_text.width() // self.main_text.fontMetrics().boundingRect(('0' * self.dig_per_col)
                                                                                               + '   ').width()

        main_text = ''
        decoded_text = ''
        offset_text = ''

        offset = 0

        for data_cur_str in [data_str_tmp[i:i + self.dig_per_col * self.col_per_row] for i in range(0, len(data_str_tmp), self.dig_per_col * self.col_per_row)]:
            offset_text += ((len(str(hex((self.dig_per_col * self.col_per_row // 2) *
                                         (len(data_str_tmp) // (self.dig_per_col * self.col_per_row // 2)))))) -
                            len(str(hex(offset))[2:]) - 2) * '0' + str(hex(offset))[2:] + '\n'
            for data_cur_col in [data_cur_str[i:i + self.dig_per_col] for i in range(0, len(data_cur_str), self.dig_per_col)]:

                # Hexadecimal data (middle column)
                main_text += data_cur_col + '  '

                # Encoded data (right column)
                if self.encode == 'ASCII':
                    char_int = int(data_cur_col, 16)
                    decoded_text += chr(char_int) if 0x7f > char_int > 0x20 else '.'

            main_text += '\n'
            decoded_text += '\n'

            # Offset from the beginning of a file (left column)
            offset += self.dig_per_col * self.col_per_row // 2

        del data_str_tmp

        self.main_text.setText(main_text)
        self.decoded_text.setText(decoded_text)
        self.offset_text.setText(offset_text)

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if not self.exit_flag:
            self.print_data_app()

    # Settings up app view
    def create_main_view(self):
        qh_box = QHBoxLayout()

        self.main_text.setReadOnly(True)
        self.decoded_text.setReadOnly(True)
        self.offset_text.setReadOnly(True)

        font = QFont("DejaVu Sans Mono", 12, QFont.Normal, True)

        self.main_text.setFont(font)
        self.decoded_text.setFont(font)
        self.offset_text.setFont(font)

        self.offset_text.setTextColor(Qt.darkGray)

        # Syncing scrolls.
        self.main_text.verticalScrollBar().valueChanged.connect(self.decoded_text.verticalScrollBar().setValue)
        self.main_text.verticalScrollBar().valueChanged.connect(self.offset_text.verticalScrollBar().setValue)
        self.decoded_text.verticalScrollBar().valueChanged.connect(self.main_text.verticalScrollBar().setValue)
        self.decoded_text.verticalScrollBar().valueChanged.connect(self.offset_text.verticalScrollBar().setValue)
        self.offset_text.verticalScrollBar().valueChanged.connect(self.decoded_text.verticalScrollBar().setValue)
        self.offset_text.verticalScrollBar().valueChanged.connect(self.main_text.verticalScrollBar().setValue)

        self.main_text.selectionChanged.connect(self.highlight_main_text)
        self.decoded_text.selectionChanged.connect(self.highlight_decoded_text)

        qh_box.addWidget(self.offset_text, 1)
        qh_box.addWidget(self.main_text, 6)
        qh_box.addWidget(self.decoded_text, 2)

        return qh_box

    # Initialized user interface
    def init_ui(self):
        self.setWindowTitle('hexwork')
        self.setGeometry(0, 0, 1080, 720)

        rect = self.frameGeometry()
        point_mid = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(point_mid)
        self.move(rect.topLeft())

        menu_bar = self.menuBar()

        menu_bar.setPalette(get_palette())

        file_menu = menu_bar.addMenu('File')
        edit_menu = menu_bar.addMenu('Edit')
        view_menu = menu_bar.addMenu('View')

        open_action = QAction(QIcon(), 'Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open file')
        open_action.triggered.connect(self.open_file)

        save_action = QAction(QIcon(), 'Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Open file')
        save_action.triggered.connect(self.save_file)

        exit_action = QAction(QIcon(), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)

        file_menu.addActions((open_action, save_action, exit_action))

        settings_action = QAction(QIcon(), 'Settings', self)
        settings_action.setShortcut('Ctrl+Shift+S')
        settings_action.setStatusTip('Open settings menu')
        settings_action.triggered.connect(self.close)

        eval_action = QAction(QIcon(), 'Calculate', self)
        eval_action.setShortcut('Ctrl+K')
        eval_action.setStatusTip('Calculate with eval()')
        eval_action.triggered.connect(self.calc)

        insert_action = QAction(QIcon(), 'Insert', self)
        insert_action.setShortcut('Insert')
        insert_action.setStatusTip('Set write/read only mode')
        insert_action.triggered.connect(self.change_read_write_mode)

        edit_menu.addActions((settings_action, eval_action, insert_action))

        widget_mid = QWidget()
        widget_mid.setLayout(self.create_main_view())

        self.setCentralWidget(widget_mid)

        self.show()


def main():

    app = QApplication(sys.argv)

    hex_aarch = App()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
