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
    $server = $_POST['server'];
    $username = $_POST['username'];
    $password = $_POST['password'];
    $output = null;
    $return_var = null;
    //$command = escapeshellcmd("/usr/bin/python3 ./auth.py " . $username . " " . $password);
    //$command = escapeshellcmd("sshpass -p " . $password . " ssh " . $username . "@" . $server . " 'exit'");
    $command = escapeshellcmd('ls -lah');
    //$output = shell_exec($command);
    exec($command, $output, $return_var);
    print_r($output);
}