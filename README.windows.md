# Getting Stared On Windows

## System Requirements

Tested on Windows 10 & Server 2016

Refer to the system requirements for Docker Desktop. If you look over the docker desktop release notes at https://docs.docker.com/desktop/windows/release-notes/ you will see a Deprecation section for some updates. As new versions release the Docker team has chosen to no longer support older builds of Windows. Make sure to download a docker desktop version compatible with your Host OS (ex. Docker Desktop 2.4.0.0 is the last to support Server 2016). You can determine your Windows OS build by using the "**winver**" command on the host.

## Install the Requirements

### Install Docker for Windows

Follow the instructions on https://docs.docker.com/docker-for-windows/ to install docker on windows.

You need to turn on the Hyper-V feature in your system. This may give trouble if you intended to run docker within a VM:

- Open the start menu
- Search for "Turn Windows features on or off"
- If Hyper-V is not checked, check it. You may be asked to reboot your system after that.

Make sure docker desktop has started before continuing.

### Install Notepad++ (Not Required)

(Optional if you wish to edit config files after deployment)
Seafile configuration files are using linux-style line-ending, which can't be handled by the notepad.exe program. So we need to install notepad++, a lightweight text editor that works better in this case.

Download the installer from https://notepad-plus-plus.org/downloads/ and install it. During the installation, you can uncheck all the optional components.

## Getting Started with Seafile Docker

### Decide Which Drive to Store Seafile Data

Open Settings by using the Docker Desktop try icon. You should see a settings dialog now. Click the "Shared Drives" tab, and check the drive letter (ex. `D:` drive) in which you wish to store Seafile's database and configuration. Click "**apply**" afterwards to save changes. Keep in mind that this is the drive where the seafile containers will store their **Data**, **NOT** where the containers themselves will be stored. Those will be placed according to your docker desktop settings.

### Configure the seafile compose YAML

Download the [official seafile docker yaml](https://download.seafile.com/d/320e8adf90fa43ad8fee/files/?p=/docker/docker-compose.yml) document and open it up in Notepad++ or some other tool as an administrator.

This is a basic configuration file which you will need to tweak to suit your needs. The version number on top can be used to control under which version of docker compose the file should be built. You may need to change this if you leverage a feature in a newer version or a deprecated feature in an older version.

The latest seafile-mc builds have switched from using port 8000 for SeaHub http to port 80. Below the seafile image section within the yaml you can specify which ports you want to use and expose from Host to Docker image. Perhaps you have a conflicting service running on the host's port 80. If you specify "**8000:80**" in the yaml underneath the **ports** section, then all traffic to the host's port 8000 will be routed to port 80 within the docker container. Depending on your setup you may also want to open port **8082:8082** which is the fileserver port for seafile. Be careful if exposing these ports outside the local network. It is not recommended to do so as it's a security risk. Instead most seem to deploy behind something such as Nginx/Apache. You only need to set ports for the **seafile** image as **db** and **memcached** should not need to communicate across host and container.

You will also need to specify the directory in which data is to be stored underneath the **volume** sections of the images within the yaml. You can use the below format as a starting point. My drive letter was 'D' but you will need to change yours to whichever drive you planned to use. The path to the left of the colon is the host's path, and to the right is the path within the container. You can find seafile data & config files by navigating to the host directory specified within the yaml in windows explorer once the containers are up and running. Make sure the folder structure exists on the host before running docker compose. Be sure to configure this for both the db and seafile services.
  - "- /D/seafile/opt/seafile-data:/shared "

Set the **SEAFILE_ADMIN_EMAIL** and **SEAFILE_ADMIN_PASSWORD** for the administrator account so that you can login to SeaHub once it's up. You can also set the **TIME_ZONE** to your locale though be sure to look up the proper formatting or the seafile container will fail to start. For me it was **America/New_York** for the US east coast. **SEAFILE_SERVER_HOSTNAME** should be set too if you plan to use https.

The rest of the included options should be fine to get you started. If you want to use a specific version of seafile you can change the image tag seafileltd/seafile-mc:latest to something like seafileltd/seafile-mc:9.0.4

If you wish to run seafile on boot or when docker desktop starts, you may want to specify the restart policy in the yaml for reach image so that the seafile containers are started when docker starts. I set mine to the value **always** but additional flags can be found here: https://docs.docker.com/config/containers/start-containers-automatically/

One thing to note is that while the initial container start after the docker compose will respect the **depends_on** setting in the yaml, thus delaying the start of the seafile container until after the db & memcached containers have started, from my experience, if your restart policy is set to always then docker will simply try to start all of the containers at the same time and omit the delay. This can lead to seafile not starting properly and the inability to access SeaHub if db & memcached are not up first. Manually stopping and starting the seafile container again with the db & memcached containers up should fix this, however...

A better solution to the above is to implement healthchecks into the yaml. These are individual tests performed by docker each time the containers start to report a health status (starting, healthy, unhealthy, etc.). If deploying these containers within a **docker swarm**, the swarm can automatically monitor these status' and restart any unhealthy containers. This can also be done outside of a swarm by leveraging a tool such as [**autoheal**](https://hub.docker.com/r/willfarrell/autoheal/) to do the same. This solves the issue of the seafile container starting before db & memcached are ready as the swarm or autoheal can auto-restart the seafile container should the healthcheck fail. Below are examples of healthchecks for each image.

- db
```
healthcheck:
      test: ["CMD", "mysqladmin", "ping", "--silent"]
      interval: 20s
      timeout: 10s
      retries: 1
      start_period: 45s   
```
- memcached
```
healthcheck:
      test: ["CMD", "echo", "stats", "|", "nc", "127.0.0.1", "11211"]
      interval: 20s
      timeout: 10s
      retries: 1
      start_period: 45s  
```   
- seafile
```
healthcheck:
      test: ["CMD", "curl", "-f", "127.0.0.1:80"]
      interval: 30s
      timeout: 30s
      retries: 1
      start_period: 60s        
```
### Compose and Run Seafile Docker

First open a powershell window **as administrator** , and run the following command to set the execution policy to "RemoteSigned":

```sh
Set-ExecutionPolicy RemoteSigned
```

Close the powershell window, and open a new one **as the normal user**.

Now run the following commands:

Navigate to the location of your modified yaml, I placed mine on the root of the D drive
```sh
cd d:\
```

With docker desktop started, run the below commands to build and start the seafile containers:
```sh
docker-compose up -d
```

To verify the containers have started you can use the following command:
```sh
docker container ls
```

Optionally you can also deploy via swarm instead by using:
```sh
docker swarm init
docker stack deploy -c docker-compose.yml seafile
```

If all went well Seafile will be up and running and you should be able to login to seahub by using the following on the host machine. You will need to open up ports on the host's firewall before you can access from another machine on your network if not using Nginx/Apache.
 - 127.0.0.1:8000 (fill in proper port used). 

### Managing Seafile & Docker

If for any reason you want to stop and delete your seafile containers (perhaps while testing a configuration) you can use the commands below. I also recommend deleting at least the config files used by the containers on your local drive before composing again.
```sh
docker kill $(docker ps -q)
docker container prune
```

You can also stop an individual container by using:
```sh
docker stop seafile
```

If you are not familiar with docker commands, refer to [docker documentation](https://docs.docker.com/engine/reference/commandline/cli/).

If you want Seafile to start without the need to log into the host machine, such as on a headless server, you can configure docker desktop to start as a task on boot. Information can be found [here](https://stackoverflow.com/questions/51252181/how-to-start-docker-daemon-windows-service-at-startup-without-the-need-to-log). Make sure to un-check the Docker Desktop General "Start Docker Desktop when you log in" setting or docker will try to start twice and present an error any time you log into the host.
