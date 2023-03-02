/*! Bootstrap integration for DataTables' SearchPanes
 * © SpryMedia Ltd - datatables.net/license
 */

(function( factory ){
	if ( typeof define === 'function' && define.amd ) {
		// AMD
		define( ['jquery', 'datatables.net-zf', 'datatables.net-searchpanes'], function ( $ ) {
			return factory( $, window, document );
		} );
	}
	else if ( typeof exports === 'object' ) {
		// CommonJS
		module.exports = function (root, $) {
			if ( ! root ) {
				// CommonJS environments without a window global must pass a
				// root. This will give an error otherwise
				root = window;
			}

			if ( ! $ ) {
				$ = typeof window !== 'undefined' ? // jQuery's factory checks for a global window
					require('jquery') :
					require('jquery')( root );
			}

			if ( ! $.fn.dataTable ) {
				require('datatables.net-zf')(root, $);
			}

			if ( ! $.fn.dataTable.SearchPanes ) {
				require('datatables.net-searchpanes')(root, $);
			}

			return factory( $, root, root.document );
		};
	}
	else {
		// Browser
		factory( jQuery, window, document );
	}
}(function( $, window, document, undefined ) {
'use strict';
var DataTable = $.fn.dataTable;


$.extend(true, DataTable.SearchPane.classes, {
    buttonGroup: 'secondary button-group',
    disabledButton: 'disabled',
    narrow: 'dtsp-narrow',
    narrowButton: 'dtsp-narrowButton',
    narrowSearch: 'dtsp-narrowSearch',
    paneButton: 'secondary button',
    pill: 'badge secondary',
    search: 'search',
    searchLabelCont: 'searchCont',
    show: 'col',
    table: 'unstriped'
});
$.extend(true, DataTable.SearchPanes.classes, {
    clearAll: 'dtsp-clearAll button secondary',
    collapseAll: 'dtsp-collapseAll button secondary',
    disabledButton: 'disabled',
    panes: 'panes dtsp-panesContainer',
    showAll: 'dtsp-showAll button secondary',
    title: 'dtsp-title'
});


return DataTable;
}));
