import socket
import random
import time
import threading


def step(u1, u2, nums):
    u1.send('Твой ход'.encode('utf8'))
    u2.send('Ход противника'.encode('utf8'))

    res = []
    for _ in range(2):
        answer = u1.recv(32)
        i, j = answer.decode('utf8').split('_')
        res.append(nums[int(i) * 6 + int(j)])
        u2.send(answer)
    return res


def new_users():
    while True:
        user, _ = sock.accept()
        waiting_game.append(user)
        if len(waiting_game) >= 2:
            threading.Thread(target=game, args=(waiting_game[0], waiting_game[1])).start()


def game(user1, user2):
    try:
        nums = [str(i // 2 + 1) for i in range(36)]
        random.shuffle(nums)
        waiting_game.pop(0)
        user1.send(('TABLE' + '_'.join(nums)).encode('utf8'))
        waiting_game.pop(0)
        user2.send(('TABLE' + '_'.join(nums)).encode('utf8'))
        time.sleep(1)

        while True:
            num1 = num2 = 0
            while num1 == num2:
                num1, num2 = step(user1, user2, nums)
                time.sleep(0.1)

            user1, user2 = user2, user1
    except Exception as e:
        print('Game over')
        print(e)


sock = socket.socket()
sock.bind(('', 5500))
sock.listen()

waiting_game = []
threading.Thread(target=new_users).start()
