import socket
import random
import time


def step(u1, u2):
    u1.send('Твой ход'.encode('utf8'))
    u2.send('Ход противника'.encode('utf8'))

    res = []
    for _ in range(2):
        answer = u1.recv(32)
        i, j = answer.decode('utf8').split('_')
        res.append(nums[int(i) * 6 + int(j)])
        u2.send(answer)
    return res


sock = socket.socket()
sock.bind(('localhost', 50000))
sock.listen(2)

user1, _ = sock.accept()
user2, _ = sock.accept()

nums = [str(i//2+1) for i in range(36)]
random.shuffle(nums)
user1.send(('TABLE' + '_'.join(nums)).encode('utf8'))
user2.send(('TABLE' + '_'.join(nums)).encode('utf8'))
time.sleep(1)

while True:
    num1 = num2 = 0
    while num1 == num2:
        num1, num2 = step(user1, user2)
        time.sleep(0.1)

    user1, user2 = user2, user1
