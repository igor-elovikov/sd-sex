import sys

from PySide2.QtCore import Qt, Signal, QRect, QSize
from PySide2.QtGui import QFont, QTextCursor, QTextOption, QColor, QPainter, QTextFormat
from PySide2.QtWidgets import (QApplication, QCompleter, QHBoxLayout,
                               QLineEdit, QPlainTextEdit, QWidget, QTextEdit, QAbstractItemView)

class QLineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):

    class Completer(QCompleter):
        insertText = Signal(str)

        def __init__(self, keywords=None, parent=None):
            QCompleter.__init__(self, keywords, parent)
            self.activated.connect(self.changeCompletion)

        def changeCompletion(self, completion):
            if completion.find("(") != -1:
                completion = completion[:completion.find("(")]
            #print("completion is " + str(completion))
            self.insertText.emit(completion)

    def __init__(self, parent=None):
        super(CodeEditor, self).__init__(parent)
        self.completer = None
        self.font_size = 0
        self.line_color = QColor("#7f848b")
        self.char_width = 0
        self.tab_spaces = 4

        self.lineNumberArea = QLineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.updateLineNumberArea)

        self.cursorPositionChanged.connect(self.highlightCurrentLine)

    def setup_editor(self, font, font_size):
        font = QFont(font)
        self.font_size = font_size
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(self.font_size)
        self.lineNumberArea.setFont(font)
        self.char_width = self.fontMetrics().boundingRectChar('9').width()        
        self.update_line_number_area_width(0)

    def line_number_area_width(self):
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        space = (5 + digits) * self.char_width
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            
            lineColor = QColor(Qt.darkGray).darker(300)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(self.line_color)
                painter.drawText(0, top, self.lineNumberArea.width() - 2 * self.char_width, height, Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1


    def init_code_completion(self, keywords):
        completer = CodeEditor.Completer(keywords)
        self.setCompleter(completer)
        self.keywords = keywords

    def setCompleter(self, completer):
        if self.completer:
            self.disconnect(self.completer)
        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseSensitive)
        self.completer = completer
        self.completer.insertText.connect(self.insertCompletion)

    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = (len(completion) -
            len(self.completer.completionPrefix()))
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])

    def get_current_line(self):
        text_cursor = self.textCursor()
        return text_cursor.block().text()

    def get_previous_line(self):
        text_cursor = self.textCursor()
        return text_cursor.block().previous().text()

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)

        selected_text = tc.selectedText()
        
        if selected_text == "(":
            cursor_pos = tc.position()
            if cursor_pos - 2 > 0:
                cursor_prev = QTextCursor(self.document())
                cursor_prev.setPosition(cursor_pos - 2)
                cursor_prev.select(QTextCursor.WordUnderCursor)
                selected_text = cursor_prev.selectedText()

        #print(selected_text)
        return selected_text

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self)
        QPlainTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        if self.completer and self.completer.popup() and self.completer.popup().isVisible():
            if event.key() in (
            Qt.Key_Enter,
            Qt.Key_Return,
            Qt.Key_Escape,
            Qt.Key_Tab,
            Qt.Key_Backtab
            ):
                event.ignore()
                #print("Event ignored")
                return

        text_cursor = self.textCursor()

        process_event = True
        if event.key() == Qt.Key_Tab:
            text_cursor.insertText(" " * self.tab_spaces)
            process_event = False          

        if process_event:
            QPlainTextEdit.keyPressEvent(self, event)

        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            prev_line = self.get_previous_line()
            prev_line_leading_spaces = len(prev_line) - len(prev_line.lstrip(" "))
            new_line_spaces = " " * prev_line_leading_spaces
            if prev_line.startswith(" "):
                text_cursor.insertText(new_line_spaces)

        arrow_pressed = event.key() in (Qt.Key_Right, Qt.Key_Left, Qt.Key_Up, Qt.Key_Down, Qt.Key_Shift, Qt.Key_Control)

        modifiers = QApplication.keyboardModifiers()
        if event.key() == Qt.Key_Space and modifiers == Qt.ControlModifier:
            arrow_pressed = False

        completionPrefix = self.textUnderCursor()
        #print(f"Completion prefix is [{completionPrefix}]")

        if len(completionPrefix) > 0 and not arrow_pressed:
            if not (completionPrefix in self.keywords and sum(k.startswith(completionPrefix) for k in self.keywords) == 1):
                self.completer.setCompletionPrefix(completionPrefix)
                popup = self.completer.popup()
                popup.setCurrentIndex(
                    self.completer.completionModel().index(0,0))
                cr = self.cursorRect()
                cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                    + self.completer.popup().verticalScrollBar().sizeHint().width())
                self.completer.complete(cr)
            elif self.completer.popup():
                self.completer.popup().hide()

        if not completionPrefix and self.completer.popup():
                self.completer.popup().hide()
