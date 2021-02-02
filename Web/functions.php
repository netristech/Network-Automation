<?php
session_start();
set_include_path(get_include_path() . PATH_SEPARATOR . 'phpseclib');
include('Net/SSH2.php');

if(isset($_POST['action']) && !empty($_POST['action'])) {
    $action = $_POST['action'];
    switch($action) {
        case 'login':
            processLogin();
            break;       
        case 'logout':
            processLogout();
            break;
        case 'test':
            test();
            break;
    }
}

function processLogin() {
    //$server = $_POST['server'];
    $username = $_POST['username'];
    $password = $_POST['password'];
    //$ssh = new Net_SSH2($server, '22');
    $ssh = new Net_SSH2('172.30.191.45', '22');
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
    die("<script type='text/javascript'>window.replace('/index.html');</script>");
}

function test() {
    $output = shell_exec("curl -k -s --user admin:Ans1bl3 -X GET -H 'Content-Type: application/json' http://172.31.104.28/api/v2/job_templates/12/launch/");
    echo $output;
}