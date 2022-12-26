
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6 import QtCore
import threading
import socket, sys
import random
import time

colors = ['#fe0a00', '#f8ff01', '#ff7000', '#31ff01', "#10ffeb", '#a192fe',
          '#1400ff', '#b900ff',  '#ff00f8', '#006400', '#00FF7F', '#1FFFF4',
          '#F0FF55', '#FFD700', '#8470FF', '#32CD32', '#9370DB', '#EE3B3B']


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.nums = []
        self.clicked = []
        self.timers = []
        self.server_events = []
        self.setWindowTitle("Игра на память")
        self.score1 = self.score2 = 0
        self.my_step = False
        self.game_table = QGridLayout()
        self.game_table.rowMinimumHeight(7)
        self.game_table.columnMinimumWidth(6)

        self.score_label = QLabel()
        self.score_label.setText(str(self.score1) + ' : ' + str(self.score2))
        self.score_label.setFont(QFont('Times', 40))
        self.game_table.addWidget(self.score_label, 6, 0, 1, 2)

        self.alert_label = QLabel()
        self.alert_label.setFont(QFont('Times', 20))
        self.game_table.addWidget(self.alert_label, 6, 2, 1, 4)

        self.widgets = {}
        for i in range(6):
            for j in range(6):
                btn = QPushButton('')
                btn.setFont(QFont('Times', 20))
                btn.setStyleSheet('QPushButton {background-color: #FFFFFF;}')
                btn.setFixedSize(60, 60)
                btn.clicked.connect(lambda _, r=i, c=j: self.btn_click(r, c))
                self.game_table.addWidget(btn, i, j)
                self.widgets[(i, j)] = btn

        self.alert_label.setText('Ожидание игрока...')
        widget = QWidget()
        widget.setLayout(self.game_table)
        self.setCentralWidget(widget)

    def btn_click(self, i, j, from_server=False):
        global server, window, app
        if (i, j) in self.clicked or (not self.my_step and not from_server):
            return 0
        if not from_server:
            server.send((str(i) + '_' + str(j)).encode('utf8'))
        self.clicked.append((i, j))
        self.set_button(i, j)
        if len(self.clicked) > 1:
            if self.nums[self.clicked[0][0] * 6 + self.clicked[0][1]] == self.nums[i * 6 + j]:
                self.game_table.removeWidget(self.widgets[(self.clicked[0][0], self.clicked[0][1])])
                self.game_table.removeWidget(self.widgets[(self.clicked[1][0], self.clicked[1][1])])
                self.widgets.pop((self.clicked[0][0], self.clicked[0][1]))
                self.widgets.pop((self.clicked[1][0], self.clicked[1][1]))
                self.clicked = self.clicked[2:]
                s1, s2 = (self.score1, self.score2 + 1) if from_server else (self.score1 + 1, self.score2)
                self.score_label.setText(str(s1) + ' : ' + str(s2))
                self.score1, self.score2 = s1, s2
                if self.score1 == 10 or self.score2 == 10 or (self.score1 == 9 and self.score2 == 9):
                    self.alert_label.setStyleSheet('QLabel {color: #FF2222;}')
                    result = 'Победа' if self.score1 == 10 else 'Поражение' if self.score2 == 10 else 'Ничья'
                    self.alert_label.setText(result)
                    self.my_step = False
                    timer.stop()
                self.game_table.update()
                return 0
            self.timers.append(time.time() + 0.5)

    def set_button(self, i, j, text=None):
        if text is None:
            text = str(self.nums[i * 6 + j])
        self.widgets[(i, j)].setText(text)
        if text != '':
            self.widgets[(i, j)].setStyleSheet('QPushButton {background-color: ' + colors[self.nums[i * 6 + j]-1] + '}')
        else:
            self.widgets[(i, j)].setStyleSheet('QPushButton {background-color: #FFFFFF;}')
        self.widgets[(i, j)].clicked.connect(lambda _, r=i, c=j: self.btn_click(r, c))
        self.game_table.update()


def tick():
    if window.server_events:
        if window.server_events[0] == 'Ход противника':
            window.my_step = False
            window.alert_label.setText('Ход противника...')
        elif window.server_events[0] == 'Твой ход':
            window.my_step = True
            window.alert_label.setText('Твой ход')
        elif window.server_events[0].startswith('TABLE'):
            window.nums = [int(k) for k in window.server_events[0][5:].split('_')]
        else:
            i, j = window.server_events[0].split('_')
            window.btn_click(int(i), int(j), from_server=True)
        window.game_table.update()
        if window.server_events:
            window.server_events.pop(0)

    if window.timers and window.timers[0] < time.time():
        window.set_button(window.clicked[0][0], window.clicked[0][1], text='')
        window.set_button(window.clicked[1][0], window.clicked[1][1], text='')
        window.clicked = window.clicked[2:]
        window.timers.pop(0)


def server_listener():
    while True:
        try:
            data = server.recv(1024).decode('utf8')
            if data:
                window.server_events.append(data)
        except:
            pass


server = socket.socket()
server.connect(('62.217.177.130', 5500))

app = QApplication([])

timer = QtCore.QTimer()
timer.timeout.connect(tick)
timer.start(100)

window = MainWindow()
window.show()

threading.Thread(target=server_listener, daemon=True).start()
app.exec()
