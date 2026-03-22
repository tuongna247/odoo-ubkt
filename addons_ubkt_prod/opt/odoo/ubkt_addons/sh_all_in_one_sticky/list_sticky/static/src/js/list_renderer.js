odoo.define('sh_dynamic_list_view.ListController', function (require) {
	"use strict";

	var ListRenderer = require('web.ListRenderer');

	ListRenderer.include({
		 _renderView: function () {
		        var self = this;
		        var oldPagers = this.pagers;
		        this.pagers = [];

		        // display the no content helper if there is no data to display
		        var displayNoContentHelper = !this._hasContent() && !!this.noContentHelp;
		        this.$el.toggleClass('o_list_view', !displayNoContentHelper);
		        if (displayNoContentHelper) {
		            // destroy the previously instantiated pagers, if any
		            _.invoke(oldPagers, 'destroy');

		            this.$el.removeClass('table-responsive');
		            this.$el.html(this._renderNoContentHelper());
		            return this._super.apply(this, arguments);
		        }

		        var orderedBy = this.state.orderedBy;
		        this.hasHandle = orderedBy.length === 0 || orderedBy[0].name === this.handleField;
		        this._computeAggregates();

		        var $table = $('<table>').addClass('o_list_table table table-sm table-hover table-striped');
		        $table.toggleClass('o_list_table_grouped', this.isGrouped);
		        $table.toggleClass('o_list_table_ungrouped', !this.isGrouped);
		        var defs = [];
		        this.defs = defs;
		        if (this.isGrouped) {
		            $table.append(this._renderHeader());
		            $table.append(this._renderGroups(this.state.data));
		            $table.append(this._renderFooter());

		        } else {
		            $table.append(this._renderHeader());
		            $table.append(this._renderBody());
		            $table.append(this._renderFooter());
		        }
		        delete this.defs;

		        var prom = Promise.all(defs).then(function () {
		            // destroy the previously instantiated pagers, if any
		            _.invoke(oldPagers, 'destroy');

		            self.$el.html($('<div>', {
		                class: 'table-responsive',
		                html: $table
		            }));

		            if (self.optionalColumns.length) {
		                self.$el.addClass('o_list_optional_columns');
		                self.$('thead').append($('<i class="o_optional_columns_dropdown_toggle fa fa-ellipsis-v"/>'));
		                self.$el.append(self._renderOptionalColumnsDropdown());
		            }

		            if (self.selection.length) {
		                var $checked_rows = self.$('tr').filter(function (index, el) {
		                    return _.contains(self.selection, $(el).data('id'));
		                });
		                $checked_rows.find('.o_list_record_selector input').prop('checked', true);
		            }
		            self.currentRow = null;
		            const table = self.el.getElementsByTagName('table')[0];
		            if (table) {
		                table.classList.toggle('o_empty_list', !self._hasVisibleRecords(self.state));
		                self._freezeColumnWidths();
		            }
		        });
		        return prom;
		    },
		    
	});

});