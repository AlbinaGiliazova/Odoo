odoo.define('barcode_scanner_widget', function(require) {
    "use strict";
    var fieldRegistry = require('web.field_registry');
    var basicFields = require('web.basic_fields');

    var BarcodeScannerWidget = basicFields.FieldChar.extend({
        events: _.extend({}, basicFields.FieldChar.prototype.events, {
            'keydown': '_onKeyDown',
        }),

        _onKeyDown: function(ev) {
            if (ev.which === 13) {
                ev.preventDefault();
                var value = this.$input.val();
                if (!/^\d+$/.test(value)) {
                    this.displayNotification({ type: 'danger', message: 'Введите корректный ID детали' });
                    return;
                }
                var self = this;
                this.trigger_up('field_changed', {
                    dataPointID: this.record.id,
                    changes: { barcode_scanner: value },
                    viewType: this.viewType,
                });
                // RPC на сервер
                this._rpc({
                    model: 'packing.order',
                    method: 'process_barcode_scan',
                    args: [ [this.record.data.id], parseInt(value) ],
                }).then(function() {
                    self.$input.val(''); // Очищаем поле
                }).catch(function(error){
                    self.displayNotification({ 
                        type: 'danger', 
                        message: error.data && error.data.message || "Ошибка при обработке сканирования" 
                    });
                });
            }
        },
    });

    fieldRegistry.add('barcode_scanner_widget', BarcodeScannerWidget);
});
