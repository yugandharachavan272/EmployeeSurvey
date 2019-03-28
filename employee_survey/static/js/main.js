$(document).ready(function() {
    var table = $('#example').DataTable({
        "pageLength": 5,
        "info": false,
        "lengthChange":false
    });

    // Handle form submission event
   $('#frm-example').on('submit', function(e){
      var form = this;
      // Encode a set of form elements from all pages as an array of names and values
      var params = table.$('input,select,textarea').serializeArray();

      // Iterate over all form elements
      $.each(params, function(){
         // If element doesn't exist in DOM
         if(!$.contains(document, form[this.name])){
            // Create a hidden element
            $(form).append(
               $('<input>')
                  .attr('type', 'hidden')
                  .attr('name', this.name)
                  .val(this.value)
            );
         }
      });
   });

    $('#survey_status').on('change', function() {
        var selected_value = this.value;
        console.log(" selected_value ", selected_value)
        if( selected_value == "Select Status" || selected_value == "All"){
            $('.data-row tr').each(function(){
                $(this).show();
            });
        }
        else{
            $('.status_cell label').each(function()
            {
                if( $(this).html() != selected_value)
                {
                      $(this).parent().parent().hide();
                }
                else{
                     $(this).parent().parent().show();
                }
            });
        }
    });
} );