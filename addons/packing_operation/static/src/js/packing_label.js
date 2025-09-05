odoo.define('packing_label_dialog', function(require) {
    "use strict";
    const { registry } = require("@web/core/registry");
    const { patch } = require("@web/core/utils/patch");
    const FormController = require("@web/views/form/form_controller");
    const Dialog = require("@web/core/dialog/dialog");

    patch(FormController.prototype, {
        async onClickActionButton(button) {
            // Ищем именно вашу кнопку по классу или названию!
            if (button.name === 'action_print_label_dummy') {
                const record = this.model.root;
                const name = record.data.name || '';
                const pk = record.data.id || '';
                const label_text = `packing.order: ${name}\nID: ${pk}`;
                Dialog.alert(this, label_text, { title: "Этикетка" });
                // не выполняем стандартное действие, прекращаем обработку
                return;
            }
            // иначе стандартно
            await super.onClickActionButton(...arguments);
        }
    });
});