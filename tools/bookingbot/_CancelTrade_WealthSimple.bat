@ECHO OFF
start chrome --start-fullscreen --app=https://my.wealthsimple.com/app/login?locale=en-ca
"C:\Users\hyacinthe\Desktop\Investment\venv\Scripts\python.exe" C:\Users\hyacinthe\Desktop\Investment\tools\bookingbot\cancel_order.py
pause