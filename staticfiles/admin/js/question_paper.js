(function($) {
    $(document).ready(function() {
        function toggleTradeField() {
            var paperType = $("#id_paper_type").val();
            var tradeField = $("#id_trade");

            if (!tradeField.length) {
                return;
            }

            if (paperType === "Secondary") {
                tradeField.prop("disabled", true);
                // clear value when disabled
                tradeField.val("");
                // if select2 or similar, trigger change
                tradeField.trigger("change");
            } else {
                tradeField.prop("disabled", false);
            }
        }

        $("#id_paper_type").change(toggleTradeField);
        // initialize on load
        toggleTradeField();
    });
})(django.jQuery);
