$.event.special.inputchange = {
    setup: function () {
        var self = this,
            val;
        $.data(this, 'timer', window.setInterval(function () {
            val = self.value;
            if ($.data(self, 'cache') != val) {
                $.data(self, 'cache', val);
                $(self).trigger('inputchange');
            }
        }, 20));
    },
    teardown: function () {
        window.clearInterval($.data(this, 'timer'));
    },
    add: function () {
        $.data(this, 'cache', this.value);
    }
};


function show(id, makeVisible = true) {
    if (makeVisible && $('#' + id).is(":hidden")) {
        $('#' + id).hide();
        $('#' + id).removeClass("hide-on-load");
        $('#' + id).show(300);
    }
    if (!makeVisible && $('#' + id).is(":visible")) {
        $('#' + id).hide("fast", "swing");
    }
}

function enableTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
}