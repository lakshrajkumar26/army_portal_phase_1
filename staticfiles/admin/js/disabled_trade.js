// // disable_trade.js
// // Place at: exam/questions/static/admin/js/disable_trade.js
// // Keeps your existing disable/enable logic and adds automatic population of the
// // QP assign select by calling the admin endpoint:
// //    /admin/questions/questionpaper/qp-for-trade/?trade_id=<trade_pk>&paper_type=<value>
// //
// // Response expected: { "ok": true, "qp": { "id": <pk>, "label": "..." } }

(function(window, $) {
    // jQuery safety
    $ = $ || window.jQuery;
    if (!$) {
        console.warn("[disable_trade] jQuery not found, aborting");
        return;
    }

    function findPaperSelectors() {
        // possible selectors for the paper-type field (try several fallbacks)
        return [
            '#id_question_paper',
            '[name="question_paper"]',
            '[name$="question_paper"]',
            '#id_paper_type',
            '[name="paper_type"]'
        ];
    }

    function findTradeSelectors() {
        return [
            '#id_trade',
            '[name="trade"]',
            '[name$="trade"]'
        ];
    }

    function findQpAssignSelectors() {
        // possible selectors for the QP assign select on your admin form
        return [
            '#id_qp_assign',
            '[name="qp_assign"]',
            '[name$="qp_assign"]',
            '#id_qpassign',
            '[name$="questionpaper_assign"]',
            'select[id^="id_"][name$="qp_assign"]'
        ];
    }

    function getFirstExistingSelector(list, root) {
        root = root || document;
        for (var i = 0; i < list.length; i++) {
            var sel = list[i];
            if ($(sel, root).length) return sel;
        }
        return null;
    }

    function toggleTradeFor(paperEl, tradeEl) {
        var val = $(paperEl).val();
        var $trade = $(tradeEl);

        if (!$trade.length) return;

        if (val === "Secondary" || val === "secondary" || val === "COMMON" || val === "common") {
            // disable trade
            $trade.prop("disabled", true);

            // clear value safely, trigger change for Select2 / Chosen
            try {
                if ($trade.is('select')) {
                    $trade.val("").trigger('change');
                } else {
                    $trade.val("");
                }
            } catch (e) {
                $trade.val("");
            }
        } else {
            // enable trade
            $trade.prop("disabled", false);
        }
    }

    /**
     * Populate or clear the QP assign select by calling the admin endpoint.
     * Uses an absolute admin endpoint: '/admin/questions/questionpaper/qp-for-trade/'
     */
    function updateQPAssign(tradeSel, paperSel, root) {
        root = root || document;

        var $trade = $(tradeSel, root);
        var qpSel = getFirstExistingSelector(findQpAssignSelectors(), root);
        var $qpAssign = qpSel ? $(qpSel, root) : $();

        if (!$qpAssign.length) {
            // nothing to populate
            return;
        }

        // If trade field not present -> clear
        if (!$trade.length) {
            $qpAssign.empty().append($('<option>').val('').text('---------')).trigger('change');
            return;
        }

        // If trade is disabled, clear qp_assign
        if ($trade.prop('disabled')) {
            $qpAssign.empty().append($('<option>').val('').text('---------')).trigger('change');
            return;
        }

        var tradeId = $trade.val();
        if (!tradeId) {
            $qpAssign.empty().append($('<option>').val('').text('---------')).trigger('change');
            return;
        }

        // Read paper type value if present
        var paperVal = '';
        if (paperSel) {
            var $paper = $(paperSel, root);
            if ($paper.length) paperVal = $paper.val();
        }

        // <-- CHANGED: absolute admin endpoint
        var endpoint = '/admin/questions/questionpaper/qp-for-trade/';


        $.ajax({
            url: endpoint,
            method: 'GET',
            data: { trade_id: tradeId, paper_type: paperVal },
            dataType: 'json',
            success: function(resp) {
                // expected resp: { "ok": true, "qp": { "id": <pk>, "label": "..." } }
                $qpAssign.empty();
                $qpAssign.append($('<option>').val('').text('---------'));

                if (resp && resp.ok && resp.qp) {
                    // If backend returns one qp (latest), populate and select it
                    var it = resp.qp;
                    $qpAssign.append($('<option>').val(it.id).text(it.label));
                    try {
                        $qpAssign.val(it.id).trigger('change');
                    } catch (e) {
                        // ignore
                    }
                } else if (resp && resp.results && resp.results.length) {
                    // support alternate shape: { results: [ {id,text}, ...] }
                    resp.results.forEach(function(it){
                        $qpAssign.append($('<option>').val(it.id).text(it.text));
                    });
                    try { $qpAssign.trigger('change'); } catch(e){}
                } else {
                    // nothing found -> leave blank option
                }
            },
            error: function(err) {
                console.error("[disable_trade] Failed to fetch question papers for trade:", tradeId, err);
            }
        });
    }

    function setupToggle(root) {
        root = root || document;
        var paperSel = getFirstExistingSelector(findPaperSelectors(), root);
        var tradeSel = getFirstExistingSelector(findTradeSelectors(), root);

        if (!paperSel || !tradeSel) {
            // nothing to do on this page / form
            return;
        }

        var $paper = $(paperSel, root);
        var $trade = $(tradeSel, root);

        // when paper type changes: toggle trade and update QP assign
        $paper.off('change.disableTrade').on('change.disableTrade', function() {
            toggleTradeFor(this, tradeSel);
            // update QP assign after toggle
            setTimeout(function() { updateQPAssign(tradeSel, paperSel, root); }, 0);
        });

        // when trade changes directly: update QP assign
        $trade.off('change.updateQP').on('change.updateQP', function() {
            updateQPAssign(tradeSel, paperSel, root);
        });

        // initialize: apply toggle and populate QP assign if needed
        $paper.each(function() {
            toggleTradeFor(this, tradeSel);
        });
        updateQPAssign(tradeSel, paperSel, root);
    }

    // On document ready, set up for the main form
    $(function() {
        setupToggle(document);

        // handle Django admin dynamic formsets insertion
        $(document).on('formset:added', function(e, $row, formsetName) {
            var root = $row && $row.length ? $row[0] : document;
            setupToggle(root);
        });

        // also handle common "add row" clicks
        $(document).on('click', '.add-row a, .add-row, .grp-add-handler', function() {
            setTimeout(function() { setupToggle(document); }, 200);
        });
    });

})(window, window.jQuery);