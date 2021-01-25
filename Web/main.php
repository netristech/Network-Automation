<?php
session_start();
$_SESSION['login'] = $_POST['login'];
if($_SESSION['login']) {
    include 'header.php';
    include 'importmodal.php';
    include 'nav.php';
    include 'sites.php';
    include 'footer.php';
}
?>