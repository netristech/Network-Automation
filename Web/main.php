<?php
session_start();
if(isset($_POST['login'])) {
    $_SESSION['login'] = $_POST['login'];
    if($_SESSION['login'] == 'valid') {
        include 'header.php';
        include 'importmodal.php';
        include 'nav.php';
        include 'sites.php';
        include 'footer.php';
    }
} else {
    echo 'login not set';
}
?>