<?php
session_start();
include 'header.php';
?>
    <div id="login" class="container text-center">
        <form id="login-form" class="align-middle mx-auto" action="" method="post" enctype="multipart/formdata">
            <img src="logo.png" /><br /><br />
            <div class="alert alert-danger" style="display: none;">Authentication Failed</div>
            <!--<label for="server" class="col col-4">Server: </label>
            <input id="server" class="col col-7" type="text" name="server" value="" /><br />-->
            <label for="username" class="col col-4">Username: </label>
            <input id="username" class="col col-7" type="text" name="username" value="" /><br />
            <label for="password" class="col col-4">Password: </label>
            <input id="password" class="col col-7" type="password" name="password" value="" /><br /><br />
            <button type="button" id="login-btn" class="btn btn-primary" style="width: 95%;">
                <span class="spinner-border hide" role="status" aria-hidden="true"></span>Sign In
            </button>
        </form>
    </div>
<?php include 'footer.php'; ?>
