<?php
?>
<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Load CSS Libraries -->
    <link rel="stylesheet" href="/css/bootstrap.css">
    <link rel="stylesheet" href="/css/all.min.css">
    <link rel="stylesheet" href="/css/chart.min.css">
    <link rel="stylesheet" href="/css/style.css">

    <title>Network Automation UI - Dev</title>
  </head>
  <body>
    <div id="sites" class="container">
      <div id ="navigation" class="row pt-2 pb-2">
        <button type="button" class="btn btn-primary mr-2"><i class="far fa-edit"></i></button>
        <button type="button" class="btn btn-secondary mr-2"><i class="fas fa-file-export"></i>Export to CSV</button>
      </div>
      <div class="row">
        <table id="sites-table" class="table table-striped">
          <thead class="thead-light">
            <tr>
              <th scope="col">Site Name</th>
              <th scope="col">Address</th>
              <th scope="col">Management Subnet(s)</th>
            </tr>
          </thead>
          <tbody>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Javascript Libraries -->
    <script src="/js/jquery.min.js"></script>
    <script src="/js/bootstrap.bundle.min.js"></script>
    <script src="/js/chart.min.js"></script>
    <script src="/js/index.js"></script>

  </body>
</html>
