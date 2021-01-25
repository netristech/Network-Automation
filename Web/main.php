<?php
session_start();

if($_SESSION['login']) {
    include 'header.php';
    include 'importmodal.php';
    include 'nav.php';
    include 'sites.php';
    include 'footer.php';

} else {
    header("Location: $_SERVER['HTTP_HOST']");
    die();
}
?>