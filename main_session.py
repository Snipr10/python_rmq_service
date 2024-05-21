import threading

from add_insta_session import add_sessions_while



if __name__ == '__main__':

    print("add_sessions")
    threading.Thread(target=add_sessions_while, args=()).start()


