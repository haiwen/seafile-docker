# -*- buffer-file-coding-system: utf-8-unix -*-
<#

This is the powershell version of the launcher script to be used on windows.
you should use it instead of the linux 'launcher' script.

#>

$ErrorActionPreference = "Stop"

$version = "6.0.5"
$image = "seafileorg/server:$version"
$local_image = "local_seafile/server:latest"

$dockerdir = $PSScriptRoot.Replace("\", "/")
$sharedir = "$dockerdir/shared"
$installdir = "/opt/seafile/seafile-server-$version"

$bootstrap_conf="$dockerdir/bootstrap/bootstrap.conf"
$version_stamp_file="$sharedir/seafile/seafile-data/current_version"
$bash_history="$sharedir/.bash_history"

function usage() {
    Write-Host "Usage: launcher.ps1 COMMAND [-skipPrereqs]"
    Write-Host "Commands:"
    Write-Host "    start:      Start/initialize the container"
    Write-Host "    stop:       Stop a running container"
    Write-Host "    restart:    Restart the container"
    Write-Host "    destroy:    Stop and remove the container"
    Write-Host "    enter:      Open a shell to run commands inside the container"
    Write-Host "    logs:       View the Docker container logs"
    Write-Host "    bootstrap:  Bootstrap the container based on a template"
    Write-Host "    rebuild:    Rebuild the container (destroy old, bootstrap, start new)"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "    -skipPrereqs             Don't check launcher prerequisites"
    exit 1
}

function main() {
    Param(
        [Parameter(Position=1)]
        [string]$action,

        [switch]$skipPrereqs,

        [switch]$v
    )

    $script:action = $action
    $script:skipPrereqs = $skipPrereqs
    # Always verbose before we reach a stable release.
    $script:v = $true
    $script:verbose = $script:v

    check_is_system_supported

    if (!$action) {
        usage
    }

    # loginfo "action = $action"
    if (!$skipPrereqs) {
        check_prereqs
    }

    switch ($action) {
        "bootstrap"         { do_bootstrap }
        "start"             { do_start }
        "stop"              { do_stop }
        "restart"           { do_restart }
        "enter"             { do_enter }
        "destroy"           { do_destroy }
        "logs"              { do_logs }
        "rebuild"           { do_rebuild }
        "manual-upgrade"    { do_manual_upgrade }
        default             { usage }
    }
}

<# A Powershell version of the following bash code:

[[ $a == "1" ]] || {
    # do something else when a != 1
}

Use it like:

do_if_not { where.exe docker } { loginfo "docker program doesn't exist"}

Currently the first branch must be a subprocess call.

#>
function do_if_not([scriptblock]$block_1, [scriptblock]$block_2) {
    $failed = $false
    $global:LASTEXITCODE = $null
    try {
        & $block_1
    } catch [System.Management.Automation.RemoteException] {
        $failed = $true
    }
    if ($failed -or !($global:LASTEXITCODE -eq 0)) {
        & $block_2
    }
}

function do_if([scriptblock]$block_1, [scriptblock]$block_2) {
    $failed = $false
    $global:LASTEXITCODE = $null
    try {
        & $block_1
    } catch [System.Management.Automation.RemoteException] {
        $failed = $true
    }
    if (!($failed) -and ($global:LASTEXITCODE -eq 0)) {
        & $block_2
    }
}

<#
Mimics python's `subproess.check_output`: Run the given command, capture the
output, and terminate the script if the command fails. For example:

check_output docker run ...

Code borrowed from http://stackoverflow.com/a/11549817/1467959
#>
function check_output($cmd) {
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = $cmd
    $pinfo.RedirectStandardError = $false
    $pinfo.RedirectStandardOutput = $true
    $pinfo.UseShellExecute = $false
    $pinfo.WorkingDirectory = $PSScriptRoot
    if ($args) {
        $pinfo.Arguments = $args
    }
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $pinfo
    $p.Start() | Out-Null
    $stdout = $p.StandardOutput.ReadToEnd()
    $p.WaitForExit()
    echo "$stdout"
    if (!($p.ExitCode -eq 0)) {
        err_and_quit "The command $cmd $args failed"
    }
}

<#

Mimics python's `subprocess.check_call`: Run the given command, capture the
output, and terminate the script if the command fails. For example:

check_call docker run ...

#>
function check_call($cmd) {
    if ($args) {
        $process = Start-Process -NoNewWindow -Wait -FilePath "$cmd" -ArgumentList $args -PassThru
    } else {
        $process = Start-Process -NoNewWindow -Wait -FilePath "$cmd" -PassThru
    }
    if (!($process.ExitCode -eq 0)) {
        if ($script:on_call_error) {
            err_and_quit $script:on_call_error
            $script:on_call_error = $null
        } else {
            err_and_quit "The command $cmd $args failed with code $LASTEXITCODE"
        }
    }
}

function get_date_str() {
    Get-Date -format "yyyy-MM-dd hh:mm:ss"
}

function err_and_quit($msg) {
    Write-Host -BackgroundColor Black -ForegroundColor Yellow -Object "[$(get_date_str)] Error: $msg"
    exit 1
}

function logdbg($msg) {
    if ($script:verbose) {
        loginfo "[debug] $msg"
    }
}

function loginfo($msg) {
    Write-Host -ForegroundColor Green -Object "[$(get_date_str)] $msg"
}

function program_exists($exe) {
    try {
        Get-Command "$exe" -CommandType Application 2>&1>$null
    } catch [CommandNotFoundException] {
    }
    return $?
}

function to_unix_path($path) {
    $path -replace '^|\\+','/' -replace ':'
}

$sharedir_u = $(to_unix_path $sharedir)
$dockerdir_u = $(to_unix_path $dockerdir)

function check_prereqs() {
    if (!(program_exists "git.exe")) {
        err_and_quit "You need to install git first. Check https://git-scm.com/download/win".
    }

    if (!(program_exists "docker.exe")) {
        err_and_quit "You need to install docker first. Check https://docs.docker.com/docker-for-windows/."
    }
}

function check_is_system_supported() {
    $ver = [Environment]::OSVersion
    if (!($ver.Version.Major -eq 10)) {
        err_and_quit "Only Windows 10 is supported."
    }
}

function set_envs() {
    $script:envs = @()
    if ($script:v) {
        $script:envs += "-e"
        $script:envs += "SEAFILE_DOCKER_VERBOSE=true"
    }
}

# Call powershell mkdir, but only create the directory when it doesn't exist
function makedir($path) {
    if (!(Test-Path $path)) {
        New-Item -ItemType "Directory" -Force -Path $path 2>&1>$null
    }
}

function touch($path) {
    if (!(Test-Path $path)) {
        New-Item -ItemType "file" -Path $path 2>&1>$null
    }
}


function init_shared() {
    makedir "$sharedir/seafile"
    makedir "$sharedir/db"
    makedir "$sharedir/logs/seafile"
    makedir "$sharedir/logs/var-log"

    makedir "$sharedir/logs/var-log/nginx"
    touch "$sharedir/logs/var-log/syslog"
    touch $bash_history
}

function set_bootstrap_volumes() {
    init_shared

    $mounts = @(
        "${sharedir_u}:/shared",
        "${sharedir_u}/logs/var-log:/var/log",
        "${sharedir_u}/db:/var/lib/mysql",
        "${dockerdir_u}/bootstrap:/bootstrap",
        "${dockerdir_u}/scripts:/scripts:ro",
        "${dockerdir_u}/templates:/templates:ro",
        "${dockerdir_u}/scripts/tmp/check_init_admin.py:$installdir/check_init_admin.py:ro",
        "${sharedir_u}/.bash_history:/root/.bash_history"
    )
    $script:volumes = @()
    foreach($m in $mounts) {
        $script:volumes += "-v"
        $script:volumes += "$m"
    }
}

function set_volumes() {
    init_shared

    $mounts = @(
        "${sharedir_u}:/shared",
        "${sharedir_u}/logs/var-log:/var/log",
        "${sharedir_u}/db:/var/lib/mysql",
        "${sharedir_u}/.bash_history:/root/.bash_history"
    )
    $script:volumes=@()
    foreach($m in $mounts) {
        $script:volumes += "-v"
        $script:volumes += "$m"
    }
}

function set_ports() {
    $ports = $(check_output "docker" "run" "--rm" "-it" `
      "-v" "${dockerdir_u}/scripts:/scripts" `
      "-v" "${dockerdir_u}/bootstrap:/bootstrap:ro" `
      $image `
      "/scripts/bootstrap.py" "--parse-ports")

    # The output is like "-p 80:80 -p 443:443", we need to split it into an array
    $script:ports = $(-split $ports)
}

function set_my_init() {
    $script:my_init = @("/sbin/my_init")
    if (!($script:v)) {
        $script:my_init += "--quiet"
    }
}

function parse_seafile_container([array]$lines) {
    foreach($line in $lines) {
        $fields = $(-split $line)
        if ("seafile".Equals($fields[-1])) {
            echo $fields[0]
            break
        }
    }

    ## We can write it using more elegant "ForEach-Object" using the following
    ## code, but someone says that "break" works like "continue" in the
    ## ForEach-Object's script block.
    ##
    ## See ## http://stackoverflow.com/a/7763698/1467959
    ##
    ## Anway, we use a foreach loop to keep the code
    ## simple.
    ##
    # $lines | ForEach-Object {
    #     $fields =$(-split $_)
    #     if ("seafile".Equals($fields[-1])) {
    #         echo $fields[0]
    #         break
    #     }
    # }
}

# Equivalent of `docker ps | awk '{ print $1, $(NF) }' | grep " seafile$" | awk '{ print $1 }' || true`
function set_running_container() {
    try {
        $script:existing = $(parse_seafile_container $(check_output docker ps))
    } catch [System.Management.Automation.RemoteException] {
        $script:existing = ""
    }
}

# Equivalent of `docker ps -a |awk '{ print $1, $(NF) }' | grep " seafile$" | awk '{ print $1 }' || true`
function set_existing_container() {
    try {
        $script:existing = $(parse_seafile_container $(docker ps -a))
    } catch [System.Management.Automation.RemoteException] {
        $script:existing = ""
    }
}

function ensure_container_running() {
    set_existing_container
    if (!($script:existing)) {
        err_and_quit "seafile was not started !"
    }
}

function ignore_error($cmd) {
    if ($args) {
        Start-Process -NoNewWindow -Wait -FilePath "$cmd" -ArgumentList $args
    } else {
        Start-Process -NoNewWindow -Wait -FilePath "$cmd"
    }
}

function remove_container($container) {
    do_if { docker inspect $container 2>&1>$null } {
        docker rm -f $container 2>&1>$null
    }
}

function do_bootstrap() {
    if (!(Test-Path $bootstrap_conf)) {
        err_and_quit "The file $bootstrap_conf doesn't exist. Have you run seafile-server-setup?"
    }

    do_if_not { docker history $image 2>&1>$null } {
        loginfo "Pulling Seafile server image $version, this may take a while."
        check_call docker pull $image
        loginfo "Seafile server image $version pulled. Now bootstrapping the server ..."
    }

    set_envs
    set_bootstrap_volumes
    set_ports
    set_my_init

    # loginfo "ports is $script:ports"
    remove_container "seafile-bootstrap"

    check_call "docker" "run" "--rm" "-it" "--name" "seafile-bootstrap" `
      "-e" "SEAFILE_BOOTSRAP=1" `
      @script:envs `
      @script:volumes `
      @script:ports `
      $image `
      @script:my_init "--" "/scripts/bootstrap.py"
      # @script:my_init "--" "/bin/bash"

    loginfo "Now building the local docker image."
    check_call "docker" "build" "-f" "bootstrap/generated/Dockerfile" "-t" "local_seafile/server:latest" "." 2>$null
    loginfo "Image built."
}

function do_start() {
    set_running_container
    if ($script:running) {
        loginfo "Nothing to do, your container has already started!"
        exit 0
    }

    check_version_match

    set_existing_container
    if ($script:existing) {
        loginfo "starting up existing container"
        check_call docker start seafile
        exit 0
    }

    set_envs
    set_volumes
    set_ports

    $attach_on_run = @()
    $restart_policy = @()
    if ("true".Equals($SUPERVISED)) {
        $restart_policy = @("--restart=no")
        $attach_on_run = @("-a", "stdout", "-a", "stderr")
    } else {
        $attach_on_run = @("-d")
    }

    loginfo "Starting up new seafile server container"
    remove_container "seafile"
    docker run @attach_on_run @restart_policy --name seafile -h seafile @envs @volumes @ports $local_image
}

function do_rebuild() {
    $branch=(check_output git symbolic-ref --short HEAD).Trim()
    if ("master".Equals($branch)) {
        loginfo "Ensuring launcher is up to date"

        check_call git remote update

        $LOCAL=(check_output git rev-parse "@").Trim()
        $REMOTE=(check_output git rev-parse "@{u}").Trim()
        $BASE=(check_output git merge-base "@" "@{u}").Trim()

        if ($LOCAL.Equals($REMOTE)) {
            loginfo "Launcher is up-to-date"

        } elseif ($LOCAL.Equals($BASE)) {
            loginfo "Updating Launcher"
            do_if_not { git pull } {
                err_and_quit "failed to update"
            }

            $myself = Join-Path $PSScriptRoot $script:MyInvocation.MyCommand
            $newargs = @($myself) + $script:args
            # logdbg "Running: Start-Process -NoNewWindow -FilePath powershell.exe -ArgumentList $($newargs)"
            Start-Process -NoNewWindow -FilePath powershell.exe -ArgumentList $newargs -Wait
            exit 0

        } elseif ($REMOTE.Equals($BASE)) {
            loginfo "Your version of Launcher is ahead of origin"

        } else {
            loginfo "Launcher has diverged source, this is only expected in Dev mode"
        }
    }

    set_existing_container

    if ($script:existing) {
        loginfo "Stopping old container"
        check_call docker stop -t 10 seafile
    }

    do_bootstrap
    loginfo "Rebuilt successfully."

    if ($script:existing) {
        loginfo "Removing old container"
        check_call docker rm seafile
    }

    check_upgrade

    do_start

    loginfo "Your seafile server is now running."
}

function get_major_version($ver) {
    echo "$($ver.Split(".")[0..1] -join ".")"
}

function check_version_match() {
    $last_version=(Get-Content $version_stamp_file).Trim()
    $last_major_version=$(get_major_version $last_version)
    $current_major_version=$(get_major_version $version)

    logdbg "Your version: ${last_version}, latest version: ${version}"

    if (!($last_major_version.Equals($current_major_version))) {
        loginfo "******* Major upgrade detected *******"
        loginfo "You have $last_version, latest is $version"
        loginfo "Please run './launcher.ps1 rebuild' to upgrade"
        exit 1
    }
}

function check_upgrade() {
    loginfo "Checking if there is major version upgrade"

    $last_version=(Get-Content $version_stamp_file).Trim()
    $last_major_version=$(get_major_version $last_version)
    $current_major_version=$(get_major_version $version)

    if ($last_major_version.Equals($current_major_version)) {
        return
    } else {
        loginfo "********************************"
        loginfo "Major upgrade detected: You have $last_version, latest is $version"
        loginfo "********************************"

        # $use_manual_upgrade="true"
        if ("true".Equals($use_manual_upgrade)) {
            loginfo "Now you can run './launcher.ps1 manual-upgrade' to do manual upgrade."
            exit 0
        } else {
            loginfo "Going to launch the docker container for manual upgrade"
            _launch_for_upgrade -auto
        }
    }
}

function _launch_for_upgrade([switch]$auto) {
    if ($auto) {
        $script:on_call_error = 'Failed to upgrade to latest version. You can try run it manually by "./launcher.ps1 manual-upgrade"'
        $cmd="/scripts/upgrade.py"
    } else {
        $script:on_call_error = "Upgrade failed"
        $cmd="/bin/bash"
    }

    set_envs
    set_volumes

    remove_container seafile-upgrade

    check_call docker run `
      -it -rm --name seafile-upgrade -h seafile `
      @script:envs @script:volumes $local_image `
      @script:my_init -- $cmd
}

function do_manual_upgrade() {
    _launch_for_upgrade

    loginfo "If you have manually upgraded the server, please update the version stamp by:"
    loginfo
    loginfo "       Set-Content -Path ""$version_stamp_file"" -Value $version"
    loginfo "       ./launcher.ps1 start"
    loginfo
}

function do_stop() {
    ensure_container_running
    loginfo "Stopping seafile container"
    check_call docker stop -t 10 seafile
}

function do_restart() {
    do_stop
    do_start
}

function do_enter() {
    ensure_container_running
    loginfo "Launching a linux bash shell in the seafile container"
    docker exec -it seafile /bin/bash
}

function do_destroy() {
    loginfo "Stopping seafile container"
    ignore_error docker stop -t 10 seafile
    ignore_error docker rm seafile
}

function do_logs() {
    ensure_container_running
    docker logs --tail=20 -f seafile
}

main @args
