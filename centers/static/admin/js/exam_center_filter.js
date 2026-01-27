// exam_center_filter.js
(function() {
    // Exam center choices data
    const EXAM_CENTER_CHOICES = {
        "SC": [
            ["Secunderabad", "Secunderabad"],
            ["Jhansi", "Jhansi"],
            ["Ahmedabad", "Ahmedabad"],
            ["Jodhpur", "Jodhpur"],
            ["Saugor", "Saugor"],
            ["Bhopal", "Bhopal"],
            ["Pune", "Pune"],
        ],
        "EC": [
            ["Binaguri", "Binaguri"],
            ["Kolkata", "Kolkata"],
            ["Missamari", "Missamari"],
            ["Rangapahar", "Rangapahar"],
            ["Dinjan", "Dinjan"],
            ["Gangtok", "Gangtok"],
            ["Leimakhong", "Leimakhong"],
            ["Tenga", "Tenga"],
            ["Panagarh", "Panagarh"],
            ["Ranchi", "Ranchi"],
            ["Likabali", "Likabali"],
            ["Tejpur", "Tejpur"],
            ["Kalimpong", "Kalimpong"],
        ],
        "WC": [
            ["Jalandhar", "Jalandhar"],
            ["Ambala", "Ambala"],
            ["Delhi", "Delhi"],
            ["Amritsar", "Amritsar"],
            ["Ferozepur", "Ferozepur"],
            ["Patiala", "Patiala"],
            ["Jammu", "Jammu"],
            ["Pathankot", "Pathankot"],
            ["Chandimandir", "Chandimandir"],
            ["Meerut", "Meerut"],
        ],
        "CC": [
            ["Agra", "Agra"],
            ["Bareilly", "Bareilly"],
            ["Jabalpur", "Jabalpur"],
            ["Lucknow", "Lucknow"],
            ["Ranikhet", "Ranikhet"],
            ["Dehradun", "Dehradun"],
            
        ],
        "NC": [
            ["Udhampur", "Udhampur"],
            ["Baramula", "Baramula"],
            ["Kargil", "Kargil"],
            ["Leh", "Leh"],
            ["Srinagar", "Srinagar"],
            ["Kupwara", "Kupwara"],
            ["Allahabad", "Allahabad"],
            ["Rajouri", "Rajouri"],
            ["Akhnoor", "Akhnoor"],
            ["Nagrota", "Nagrota"],
            ["Palampur", "Palampur"],
            ["Mathura", "Mathura"],
            ["Karu", "Karu"],
        ],
        "SWC": [
            ["Jaipur", "Jaipur"],
            ["Hissar", "Hissar"],
            ["Bathinda", "Bathinda"],
            ["Sriganganagar", "Sriganganagar"],
            ["Bikaner", "Bikaner"],
            ["Suratgarh", "Suratgarh"],
            ["Kota", "Kota"],
        ],
        "ANC": [
            ["Port Blair", "Port Blair"],
        ],
        "ARTRAC": [
            ["Ahmednagar", "Ahmednagar"],
            ["Bangalore", "Bangalore"],
            ["Chennai", "Chennai"],
            ["Pune MINTSD", "Pune MINTSD"],
            ["MCTE Mhow", "MCTE Mhow"],
        ],
    };

    function updateExamCenters(comdValue) {
        const examCenterSelect = document.querySelector('#id_exam_Center');
        
        if (!examCenterSelect) {
            console.error('Exam center select element not found');
            return;
        }

        // Clear existing options
        examCenterSelect.innerHTML = '';

        if (!comdValue || !EXAM_CENTER_CHOICES[comdValue]) {
            // Add default option when no command is selected
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Select Command first';
            examCenterSelect.appendChild(defaultOption);
            return;
        }

        // Add default "Select" option
        const selectOption = document.createElement('option');
        selectOption.value = '';
        selectOption.textContent = 'Select Exam Center';
        examCenterSelect.appendChild(selectOption);

        // Add options for the selected command
        const centers = EXAM_CENTER_CHOICES[comdValue];
        centers.forEach(function(center) {
            const option = document.createElement('option');
            option.value = center[0];
            option.textContent = center[1];
            examCenterSelect.appendChild(option);
        });
    }

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        const comdSelect = document.querySelector('#id_comd');
        
        if (comdSelect) {
            // Add event listener for command change
            comdSelect.addEventListener('change', function() {
                updateExamCenters(this.value);
            });

            // Initialize on page load if command is already selected
            if (comdSelect.value) {
                updateExamCenters(comdSelect.value);
            }
        }
    });

    // Make function globally available
    window.updateExamCenters = updateExamCenters;
})();