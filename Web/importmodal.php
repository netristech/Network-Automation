<?php
?>
    
    <div id="import-modal" class="modal fade" tabindex="-1" role="dialog">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <i class="fas fa-times" aria-hidden="true"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <form id="import-form" method="post" action="" enctype="multipart/form-data">
                        <div class="alert alert-danger" style="display: none;">Error uploading file, please check file type and size are correct.</div>
                        <div class="alert alert-secondary">Select a CSV file to import</div>
                        <input type="file" id="import-file" name="file" />
                        <!--<input type="submit" name="submit" value="Import" />-->
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" id="import-btn" class="btn btn-primary">
                        <i class="fas fa-file-import"></i>&nbsp;Import
                    </button>
                </div>
            </div>
        </div>
    </div>