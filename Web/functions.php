<?php
session_start();
set_include_path(get_include_path() . PATH_SEPARATOR . 'phpseclib');
include('Net/SSH2.php');
$server = '172.30.191.45';

if(isset($_POST['action']) && !empty($_POST['action'])) {
    $action = $_POST['action'];
    switch($action) {
        case 'login':
            processLogin();
            break;       
        case 'logout':
            processLogout();
            break;
    }
}

function processLogin() {
    //$server = $_POST['server'];
    $username = $_POST['username'];
    $password = $_POST['password'];
    $ssh = new Net_SSH2($server, '22');
    if(!$ssh->login($username, $password)) {
        echo 1;
    } else {
        $ssh->disconnect();
        $_SESSION['login'] = true;
        echo 0;
    }
}

function processLogout() {
    session_destroy();
}