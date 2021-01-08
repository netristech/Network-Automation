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
                        <input type="file" name="file" />
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" id="import-btn" class="btn btn-primary">
                        <i class="fas fa-file-import"></i>
                    </button>
                    <button type="button" id="cancel-btn" class="btn btn-danger">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>