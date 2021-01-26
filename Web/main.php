<?php
session_start();

if(isset($_SESSION['login']) && $_SESSION['login']) {
    include 'header.php';
    include 'importmodal.php';
    include 'nav.php';
    include 'sites.php';
    include 'footer.php';
} else {
    session_destroy();
    die('<script type="text/javascript">window.location.replace("/index.php");</script>');
}
?>