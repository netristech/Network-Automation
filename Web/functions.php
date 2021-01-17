<?php

include('phpseclib/Net/SSH2.php');

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
    $ssh = new SSH2($server, '22');
    if(!$ssh->login($username, $password)) {
        echo 1;
    } else {
        $ssh->exec('exit');
        echo 0;
    }
    /*$command = escapeshellcmd("/usr/bin/python3 ./auth.py " . $username . " " . $password);
    $command = escapeshellcmd("sshpass -p " . $password . " ssh " . $username . "@" . $server . " 'exit'");
    $command = escapeshellcmd('sshpass --help');
    $output = shell_exec($command);
    exec($command, $output, $return_var);
    print_r($output);*/
}