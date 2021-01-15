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
    $output = shell_exec("sudo ./auth.py $username $password");
    echo "<pre>" . $output . "</pre>";
}