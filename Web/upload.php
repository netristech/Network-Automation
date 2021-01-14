
<?php

if(isset($_FILES["file"]["name"])) {
  $target_file = "upload/" . $_FILES["file"]["name"];
  $fileType = strtolower(pathinfo($target_file,PATHINFO_EXTENSION));
  
  // file validation
  if (
    !file_exists($target_file) &&
    $_FILES["file"]["size"] <= 100000 &&
    $fileType == "csv" &&
    move_uploaded_file($_FILES["file"]["tmp_name"], $target_file)
  ) {
    echo $target_file;
  } else {
    echo 0;
  }
} else {
  echo 0;
}

?>