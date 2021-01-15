<?php
//session_start();
include 'header.php';
?>
    <div id="login" class="container text-center">
        <form id="login-form" class="align-middle mx-auto" action="" method="post" enctype="multipart/formdata">
            <div class="alert alert-danger" style="display: none;">Authentication Failed</div>
            <label for="username" class="col col-4">Username: </label>
            <input id="username" class="col col-7" type="text" name="username" value="" /><br />
            <label for="password" class="col col-4">Password:  </label>
            <input id="password" class="col col-7" type="password" name="password" value="" /><br />
            <input type="submit" name="submit" value="Sign in" class="btn btn-primary" />
        </form>
    </div>
<?php include 'footer.php'; ?>
