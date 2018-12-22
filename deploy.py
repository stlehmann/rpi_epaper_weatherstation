"""
:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2018-12-22 10:46:16
:last modified by:   Stefan Lehmann
:last modified time: 2018-12-22 11:39:58

"""
import subprocess
from fabric import Connection, task

subprocess.call(["git", "add", "-i"])
subprocess.call(["git", "commit"])
subprocess.call(["git", "push"])

c = Connection("rpizw-camera", user="pi")
c.run("cd /home/pi/python/epaper_display && git pull")
c.run("sudo supervisorctl restart epaper")
