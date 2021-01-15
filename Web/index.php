<?php
//session_start();
include 'header.php';
?>
    <div id="login" class="container">
        <form id="login-form" action="" method="post" enctype="multipart/formdata">
            <div class="alert alert-danger">Authentication Failed</div>
            <label for="username">Username: </label>
            <input id="username" type="text" name="username" value="" /><br />
            <label for="password">Password:  </label>
            <input id="password" type="password" name="password" value="" /><br />
            <input type="submit" name="submit" value="Sign in" class="btn btn-primary" />
        </form>
    </div>
<?php include 'footer.php'; ?>
