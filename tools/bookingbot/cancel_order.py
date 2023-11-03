import pyautogui
import time

def cancel(in_queue_step=0):

    # full screen and load password
    time.sleep(1)
    pyautogui.press('f11')
    pyautogui.press('tab')

    # Make sure to log out
    time.sleep(1)
    pyautogui.moveTo(1880, 50, duration=0.5)
    time.sleep(1)
    pyautogui.click()

    #click log in
    time.sleep(1)
    pyautogui.moveTo(1000, 330, duration=0.5)
    pyautogui.click()

    #click log in
    time.sleep(1)
    pyautogui.moveTo(1000, 520, duration=0.5)
    pyautogui.click()

    # go stocks etf crypto
    time.sleep(1)
    pyautogui.moveTo(1000, 480, duration=0.5)
    pyautogui.click()

    # go stocks etf crypto
    pyautogui.moveTo(1000, 480, duration=0.5)
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)

    # select activities
    pyautogui.moveTo(420, 40, duration=0.5)
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)

    # select order corresponding to the step input
    order_location = 320 + (90 * int(in_queue_step))
    pyautogui.moveTo(1000, 320 + (90 * int(in_queue_step)), duration=0.5)
    pyautogui.click()
    # cancel order button
    pyautogui.moveTo(800, 750 + (90 * int(in_queue_step)), duration=0.5)
    pyautogui.click()
    #Yes
    pyautogui.moveTo(950, 300, duration=0.5)


     # completes cancellation


if __name__=='__main__':
    cancel(
        in_queue_step=1
    )