/*
bootstrap-ckeditor-modal-fix.js
hack to fix ckeditor/bootstrap compatiability bug when ckeditor appears in a bootstrap modal dialog
Include this AFTER both bootstrap and ckeditor are loaded.

See: https://ckeditor.com/old/forums/CKEditor/CKEditor-dialog-forms-not-accessible-when-in-a-modal-dialog
See: https://stackoverflow.com/questions/14420300/bootstrap-with-ckeditor-equals-problems/18554395#18554395
*/
$.fn.modal.Constructor.prototype.enforceFocus = function() {
  modal_this = this
  $(document).on('focusin.modal', function (e) {
    if (modal_this.$element[0] !== e.target && !modal_this.$element.has(e.target).length
    && !$(e.target.parentNode).hasClass('cke_dialog_ui_input_select')
    && !$(e.target.parentNode).hasClass('cke_dialog_ui_input_text')) {
      modal_this.$element.focus()
    }
  })
};
