import threading
import os


def read_urls(urls):
    for url in urls:
        print(url)


if __name__ == '__main__':
    if not os.path.exists('test.txt'):
        file = open('test.txt', 'w', encoding="utf-8")
        for index in range(20):
            file.write(str(index) + '\n')
        file.close()
    file = open('test.txt', 'r', encoding="utf-8")
    urls = file.readlines()
    t1 = threading.Thread(target=read_urls, args=(urls[0:10],))
    t2 = threading.Thread(target=read_urls, args=(urls[10:20],))
    t1.start()
    t2.start()
