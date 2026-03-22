odoo.define('project_custom.custom_attachment_image_widget', function (require) {
    "use strict";

    var registry = require('web.field_registry');
    var AttachmentImage = require('web.basic_fields').AttachmentImage;
    var CustomAttachmentImageWidget = AttachmentImage.extend({
        _render: function () {
            this._super.apply(this, arguments);
            this.$('img').attr('style', 'margin:0; max-height:100px; max-width:100px;');
        },
    });

    registry.add('custom_attachment_image', CustomAttachmentImageWidget);

    var KanbanRecord = require('web.KanbanRecord');

    KanbanRecord.include({
        _onKanbanActionClicked: function (event) {
            event.preventDefault();
    
            var $action = $(event.currentTarget);
            var type = $action.data('type') || 'button';
    
            switch (type) {
                case 'edit':
                    this.trigger_up('open_record', { id: this.db_id, mode: 'edit' });
                    break;
                case 'open':
                    this.trigger_up('open_record', { id: this.db_id });
                    break;
                case 'delete':
                    this.trigger_up('kanban_record_delete', { id: this.db_id, record: this });
                    break;
                case 'action':
                case 'object':
                    var attrs = $action.data();
                    attrs.confirm = $action.attr('confirm');
                    this.trigger_up('button_clicked', {
                        attrs: attrs,
                        record: this.state,
                    });
                    break;
                case 'set_cover':
                    var fieldName = $action.data('field');
                    var autoOpen = $action.data('auto-open');
                    if (this.fields[fieldName].type === 'many2one' &&
                        this.fields[fieldName].relation === 'ir.attachment' &&
                        this.fieldsInfo[fieldName].widget === 'custom_attachment_image') {
                        this._setCoverImage(fieldName, autoOpen);
                    } else {
                        var warning = _.str.sprintf(_t('Could not set the cover image: incorrect field ("%s") is provided in the view.'), fieldName);
                        this.displayNotification({ title: warning, type: 'danger' });
                    }
                    break;
                default:
                    this.displayNotification({ message: _t("Kanban: no action for type: ") + type, type: 'danger' });
            }
        },
    });
});
