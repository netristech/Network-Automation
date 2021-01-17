<?php

if(isset($_POST['action']) && !empty($_POST['action'])) {
    $action = $_POST['action'];
    switch($action) {
        case 'login':
            processLogin();
            break;
    }
}

function processLogin() {
    $username = $_POST['username'];
    $password = $_POST['password'];
    $server = $POST['server'];
    //$command = escapeshellcmd("/usr/bin/python3 ./auth.py " . $username . " " . $password);
    $command = escapeshellcmd("sshpass -p " . $password . " ssh " . $username . "@" . $server . " 'exit'");
    //$output = shell_exec($command);
    echo $command;
}