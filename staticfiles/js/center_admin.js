// static/js/center_admin.js
django.jQuery(document).ready(function($) {
    console.log("Center admin JavaScript loaded!");
    
    // Get the select elements
    var comdSelect = $('#id_comd');
    var examCenterSelect = $('#id_exam_Center');
    
    console.log("comdSelect found:", comdSelect.length);
    console.log("examCenterSelect found:", examCenterSelect.length);
    
    // Function to update exam center options
    function updateExamCenterOptions() {
        console.log("comd changed to:", comdSelect.val());
        var selectedComd = comdSelect.val();
        
        // Clear current options
        examCenterSelect.empty();
        
        // If no command selected, show default message
        if (!selectedComd) {
            examCenterSelect.append($('<option>', {
                value: '',
                text: 'Select Command first'
            }));
            return;
        }
        
        // Make AJAX request to get centers for the selected command
        console.log("Making AJAX request for comd:", selectedComd);
        $.ajax({
            url: 'get_exam_centers/',
            data: {
                'comd': selectedComd
            },
            success: function(data) {
                console.log("AJAX response:", data);
                examCenterSelect.empty();
                if (data.centers && data.centers.length > 0) {
                    $.each(data.centers, function(index, option) {
                        examCenterSelect.append($('<option>', {
                            value: option[0],
                            text: option[1]
                        }));
                    });
                    
                    // If we're editing an existing record, select the saved value
                    var currentValue = examCenterSelect.data('initial-value');
                    if (currentValue) {
                        examCenterSelect.val(currentValue);
                    }
                } else {
                    examCenterSelect.append($('<option>', {
                        value: '',
                        text: 'No centers available for this command'
                    }));
                }
            },
            error: function(xhr, status, error) {
                console.error("AJAX error:", status, error);
            }
        });
    }
    
    // Store initial value if editing an existing record
    if (examCenterSelect.val()) {
        examCenterSelect.data('initial-value', examCenterSelect.val());
        console.log("Initial exam center value:", examCenterSelect.val());
    }
    
    // Initial update based on current comd value
    if (comdSelect.val()) {
        console.log("Initial comd value:", comdSelect.val());
        updateExamCenterOptions();
    } else {
        examCenterSelect.append($('<option>', {
            value: '',
            text: 'Select Command first'
        }));
    }
    
    // Update exam center options when comd changes
    comdSelect.change(updateExamCenterOptions);
    
    console.log("Event listener attached to comd select");
});
