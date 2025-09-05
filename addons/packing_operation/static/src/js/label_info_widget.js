odoo.define('label_info_widget', function(require) {
    "use strict";
    const { Component } = require('@odoo/owl');
    const registry = require('@web/core/registry');

    class LabelInfoWidget extends Component {}
    LabelInfoWidget.template = 'PackingOperation.LabelInfoWidget';

    registry.category('fields').add('label_info_widget', LabelInfoWidget);

    return LabelInfoWidget;
});