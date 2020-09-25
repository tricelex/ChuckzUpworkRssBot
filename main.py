import feedparser
import os


# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files,
# tool windows, actions, and settings.
def feed():
    # url = "https://feedforall.com/sample.xml"
    # nnn_rss = 'https://www.upwork.com/ab/feed/topics/rss?securityToken' \
    #       '=10ea21d4249c994df0dfaa7321b14d04e370c0c8e8590ed6b14d4538a4a41012373a90200ba211ea434f85a1a62c41710a3cdc9f5220efe7f104bbe3ce55a6fe&userUid=1162176695087697920&orgUid=1162176695087697922&topic=4870392 '
    #
    # nnn_atom ='https://www.upwork.com/ab/feed/topics/atom?securityToken' \
    #           '=10ea21d4249c994df0dfaa7321b14d04e370c0c8e8590ed6b14d4538a4a41012373a90200ba211ea434f85a1a62c41710a3cdc9f5220efe7f104bbe3ce55a6fe&userUid=1162176695087697920&orgUid=1162176695087697922&topic=4870392 '
    #
    # parsed = feedparser.parse(nnn_atom)
    # print(parsed.keys())
    # print(parsed.entries[0].content)

    # for item in parsed.entries:
    #     print("title " + item.title)
    #     # print("description " + item.description)
    #     # print("guid " + item.guid)

    print(os.environ)


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f"Hi, {name}")  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    feed()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
