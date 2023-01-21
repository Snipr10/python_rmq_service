import threading

from add_insta_keys import add_keys
from add_insta_session import add_sessions
from add_insta_tasks import add_tasks
from read_insta_keys import read_keys
from read_insta_sessions import read_sessions
from read_insta_tasks import read_tasks

if __name__ == '__main__':
    print("add_keys")
    threading.Thread(target=add_keys, args=()).start()

    print("add_sessions")
    threading.Thread(target=add_sessions, args=()).start()

    print("add_tasks")
    threading.Thread(target=add_tasks, args=()).start()

    print("read_keys")
    threading.Thread(target=read_keys, args=()).start()

    print("read_sessions")
    threading.Thread(target=read_sessions, args=()).start()

    print("read_tasks")
    threading.Thread(target=read_tasks, args=()).start()

    print("read_insta_results.py")
    threading.Thread(target=read_insta_results, args=()).start()
