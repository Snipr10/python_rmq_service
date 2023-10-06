import threading

from add_insta_keys import add_keys_while
from add_insta_session import add_sessions_while
from add_insta_tasks import add_tasks_while
from read_insta_keys import read_keys_while
from read_insta_results import read_reslut_while
from read_insta_sessions import read_sessions_while
from read_insta_tasks import read_tasks_while
# from sessions import update_session_id_while
from test_checker import update_while_session, update_new_while_session
from update_data import update_while
from test_utils import sessions_start


if __name__ == '__main__':
    print("update_while")
    threading.Thread(target=update_while, args=()).start()
    #
    print("add_keys")
    threading.Thread(target=add_keys_while, args=()).start()

    print("add_sessions")
    threading.Thread(target=add_sessions_while, args=()).start()

    print("add_tasks")
    threading.Thread(target=add_tasks_while, args=()).start()

    print("read_keys")
    threading.Thread(target=read_keys_while, args=()).start()

    print("read_sessions")
    threading.Thread(target=read_sessions_while, args=()).start()

    print("read_tasks")
    threading.Thread(target=read_tasks_while, args=()).start()

    print("read_reslut_while")
    threading.Thread(target=read_reslut_while, args=()).start()

    print("update_session_id_while")
    # threading.Thread(target=update_session_id_while, args=()).start()
    print("update_while_session")
    # threading.Thread(target=update_while_session, args=()).start()

    print("update_new_while_session")
    threading.Thread(target=update_new_while_session, args=()).start()

    sessions_start()
