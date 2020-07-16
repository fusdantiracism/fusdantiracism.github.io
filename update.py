import os
os.chdir("/home/ubuntu/fusdantiracism.github.io")
os.system("python3 getSignatures.py")
os.system("python3 htmlFromTemplate.py")
os.system("git add index.html")
os.system('git commit -m "updated signatures"')
os.system("git push")
