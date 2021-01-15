<?php
session_start();
include header.php;?>
    <form id="login" action="" method="post" enctype="multipart/formdata">
        <div class="alert alert-danger">Authentication Failed</div>
        <label for="username">Username: </label>
        <input id="username" type="text" name="username" value="<?= $_POST['username'] ?>" />
        <label for="password">Password: </label>
        <input id="password" type="password" name="password" value="" />
        <input type="submit" name="submit" value="Sign in" class="btn btn-primary" />
    </form>
<?php include footer.php;?>
