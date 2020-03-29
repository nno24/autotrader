import pyautogui

cnt=5

buy_now=pyautogui.confirm("some text", "some title",timeout=cnt*1000)
print(buy_now)