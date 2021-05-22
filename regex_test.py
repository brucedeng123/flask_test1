import re

mobile="15830600956"
if not re.match("1[35789][0-9]{9}", mobile):
    print("ok")
print("skip")