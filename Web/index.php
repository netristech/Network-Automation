<?php include 'header.php';?>
    <div id="sites" class="container">
      <div id ="navigation" class="row pt-2 pb-2">
        <button type="button" class="btn btn-primary mr-2"><i class="far fa-edit"></i></button>
        <button type="button" class="btn btn-secondary mr-2"><i class="fas fa-file-export"></i>&nbsp;Export to CSV</button>
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
<?php include 'footer.php';?>
