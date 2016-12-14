# Getting Stared On Windows

## System Requirements

Only Windows 10 is supported.

At this time(2016/12/5) windows server 2016 doesn't support running linux containers yet. We'll add the support for windows server 2016 once it supports running linux containers.

## Install the Requirements

### Install Docker for Windows

Follow the instructions on https://docs.docker.com/docker-for-windows/ to install docker on windows.

You need to turn on the Hyper-V feature in your system:

- Open "program and features" from windows start menu
- Click "turn on/off windows features", you'll see a settings window
- If Hyper-V is not checked, check it. You may be asked to reboot your system after that.

Make sure docker daemon is running before continuing.

### Install Git

Download the installer from https://git-scm.com/download/win and install it.

**Important**: During the installation, you must choose "Checkout as is, Commit as is".

### Install Notepad++

Seafile configuration files are using linux-style line-ending, which can't be hanlded by the notepad.exe program. So we need to install notepad++, an lightweight text editor that works better in this case.

Download the installer from https://notepad-plus-plus.org/download/v7.2.2.html and install it. During the installation, you can uncheck all the optional components.

## Getting Started with Seafile Docker

### Decide Which Drive to Store Seafile Data

Choose the larges drive on your system. Assume it's the `C:` Drive. Now right-click on the tray icon of the docker app, and click the "settings" menu item.

You should see a settings dialog now. Click the "Shared Drives" tab, and check the `C:` drive. Then click "**apply**" on the settings dialog.

### Run Seafile Docker

First open a powershell window **as administrator** , and run the following command to set the execution policy to "RemoteSigned":

```sh
Set-ExecutionPolicy RemoteSigned
```

Close the powershell window, and open a new one **as the normal user**.

Now run the following commands:

(Note that if you're using another drive than "C:", say "D:" ,you should change the "/c/seafile" in the following commands to "/d/seafile" instead.)

```sh
git clone https://github.com/haiwen/seafile-docker.git /c/seafile/
cd /c/seafile/

Copy-Item samples/server.conf bootstrap/bootstrap.conf
# Edit the options according to your use case
start notepad++ bootstrap/bootstrap.conf

./launcher.ps1 bootstrap
./launcher.ps1 start
```
