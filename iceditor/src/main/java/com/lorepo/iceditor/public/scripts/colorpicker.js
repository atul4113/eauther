
(function (window) {
    function ColorPicker () {}

    /**
     * @param configuration - object containing following properties:
	 * @param configuration.elementId - html id of element on which we display color picker
	 * @param configuration.okCallback - callback when user clicks OK, is being sent color in hex but without #, ie. 00ff11
     */
    ColorPicker.prototype.showColorPicker = function (configuration) {
		$.colorpicker.swatches.custom_array = [
			 { name: '#000000' , r: 0.0000, g: 0.0000, b: 0.0000},
			 { name: '#444444' , r: 0.2667, g: 0.2667, b: 0.2667},
			 { name: '#666666' , r: 0.4000, g: 0.4000, b: 0.4000},
			 { name: '#999999' , r: 0.6000, g: 0.6000, b: 0.6000},
			 { name: '#cccccc' , r: 0.8000, g: 0.8000, b: 0.8000},
			 { name: '#eeeeee' , r: 0.9333, g: 0.9333, b: 0.9333},
			 { name: '#f3f3f3' , r: 0.9529, g: 0.9529, b: 0.9529},
			 { name: '#ffffff' , r: 1.0000, g: 1.0000, b: 1.0000},
			 { name: '#ff0000' , r: 1.0000, g: 0.0000, b: 0.0000},
			 { name: '#ff9900' , r: 1.0000, g: 0.6000, b: 0.0000},
			 { name: '#ffff00' , r: 1.0000, g: 1.0000, b: 0.0000},
			 { name: '#00ff00' , r: 0.0000, g: 1.0000, b: 0.0000},
			 { name: '#00ffff' , r: 0.0000, g: 1.0000, b: 1.0000},
			 { name: '#0000ff' , r: 0.0000, g: 0.0000, b: 1.0000},
			 { name: '#9900ff' , r: 0.6000, g: 0.0000, b: 1.0000},
			 { name: '#ff00ff' , r: 1.0000, g: 0.0000, b: 1.0000},
			 { name: '#f4cccc' , r: 0.9569, g: 0.8000, b: 0.8000},
			 { name: '#fce5cd' , r: 0.9882, g: 0.8980, b: 0.8039},
			 { name: '#fff2cc' , r: 1.0000, g: 0.9490, b: 0.8000},
			 { name: '#d9ead3' , r: 0.8510, g: 0.9176, b: 0.8275},
			 { name: '#d0e0e3' , r: 0.8157, g: 0.8784, b: 0.8902},
			 { name: '#cfe2f3' , r: 0.8118, g: 0.8863, b: 0.9529},
			 { name: '#d9d2e9' , r: 0.8510, g: 0.8235, b: 0.9137},
			 { name: '#ead1dc' , r: 0.9176, g: 0.8196, b: 0.8627},
			 { name: '#ea9999' , r: 0.9176, g: 0.6000, b: 0.6000},
			 { name: '#f9cb9c' , r: 0.9765, g: 0.7961, b: 0.6118},
			 { name: '#ffe599' , r: 1.0000, g: 0.8980, b: 0.6000},
			 { name: '#b6d7a8' , r: 0.7137, g: 0.8431, b: 0.6588},
			 { name: '#a2c4c9' , r: 0.6353, g: 0.7686, b: 0.7882},
			 { name: '#9fc5e8' , r: 0.6235, g: 0.7725, b: 0.9098},
			 { name: '#b4a7d6' , r: 0.7059, g: 0.6549, b: 0.8392},
			 { name: '#d5a6bd' , r: 0.8353, g: 0.6510, b: 0.7412},
			 { name: '#e06666' , r: 0.8784, g: 0.4000, b: 0.4000},
			 { name: '#f6b26b' , r: 0.9647, g: 0.6980, b: 0.4196},
			 { name: '#ffd966' , r: 1.0000, g: 0.8510, b: 0.4000},
			 { name: '#93c47d' , r: 0.5765, g: 0.7686, b: 0.4902},
			 { name: '#76a5af' , r: 0.4627, g: 0.6471, b: 0.6863},
			 { name: '#6fa8dc' , r: 0.4353, g: 0.6588, b: 0.8627},
			 { name: '#8e7cc3' , r: 0.5569, g: 0.4863, b: 0.7647},
			 { name: '#c27ba0' , r: 0.7608, g: 0.4824, b: 0.6275},
			 { name: '#cc0000' , r: 0.8000, g: 0.0000, b: 0.0000},
			 { name: '#e69138' , r: 0.9020, g: 0.5686, b: 0.2196},
			 { name: '#f1c232' , r: 0.9451, g: 0.7608, b: 0.1961},
			 { name: '#6aa84f' , r: 0.4157, g: 0.6588, b: 0.3098},
			 { name: '#45818e' , r: 0.2706, g: 0.5059, b: 0.5569},
			 { name: '#3d85c6' , r: 0.2392, g: 0.5216, b: 0.7765},
			 { name: '#674ea7' , r: 0.4039, g: 0.3059, b: 0.6549},
			 { name: '#a64d79' , r: 0.6510, g: 0.3020, b: 0.4745},
			 { name: '#990000' , r: 0.6000, g: 0.0000, b: 0.0000},
			 { name: '#b45f06' , r: 0.7059, g: 0.3725, b: 0.0235},
			 { name: '#bf9000' , r: 0.7490, g: 0.5647, b: 0.0000},
			 { name: '#38761d' , r: 0.2196, g: 0.4627, b: 0.1137},
			 { name: '#134f5c' , r: 0.0745, g: 0.3098, b: 0.3608},
			 { name: '#0b5394' , r: 0.0431, g: 0.3255, b: 0.5804},
			 { name: '#351c75' , r: 0.2078, g: 0.1098, b: 0.4588},
			 { name: '#741b47' , r: 0.4549, g: 0.1059, b: 0.2784},
			 { name: '#660000' , r: 0.4000, g: 0.0000, b: 0.0000},
			 { name: '#783f04' , r: 0.4706, g: 0.2471, b: 0.0157},
			 { name: '#7f6000' , r: 0.4980, g: 0.3765, b: 0.0000},
			 { name: '#274e13' , r: 0.1529, g: 0.3059, b: 0.0745},
			 { name: '#0c343d' , r: 0.0471, g: 0.2039, b: 0.2392},
			 { name: '#073763' , r: 0.0275, g: 0.2157, b: 0.3882},
			 { name: '#20124d' , r: 0.1255, g: 0.0706, b: 0.3020},
			 { name: '#4C1130' , r: 0.2980, g: 0.0667, b: 0.1882}
		];

		$(configuration.elementId).colorpicker({
            closeOnOutside : true,
            colorFormat: 'HEX',
            inlineFrame: false, // do not show a border and background when inline.
            inline : false, // do not show any divs as inline by default

            showNoneButton: true,
            modal: true,

            parts:	[ 'map', 'bar', 'preview', 'hsv', 'rgb', 'alpha', 'hex', 'swatches', 'footer'],
            swatches: 'custom_array',
            swatchesWidth : 384,

            // coordinates correspond to cells in a table, so if you want to have a part at top-left and spanning two rows and three columns, the value would be [0, 0, 3, 2].
            layout: {
                map:        [0, 0, 1, 5],
                bar:        [1, 0, 1, 5],
                preview:    [2, 0, 1, 1],
                hsv:        [2, 1, 1, 1],
                rgb:        [2, 2, 1, 1],
                hex:        [2, 4, 1, 1],
                swatches:   [0, 5, 5, 1]
            },

            okOnEnter : true,

            // If enabled, closing the dialog through any means but the OK button will revert the color back to the previous state, as if pressing the Cancel button.
            // The revert option changes the behavior of the [X] button in the header, the Escape keyboard button and clicking outside the dialog, when any of these features are enabled.
            revert: true,

            // http://api.jqueryui.com/position/
            position : {
                my : "right bottom",
                at : "left center", // bottom would make it touch bottom of page, top is touching top of page
                of : "#" + configuration.positionAt,
                collision : "fit" // so that it will slide to the left of textEditorPage
            },
            ok : function(event, color) {
            	configuration.okCallback(color.formatted);
            }
        });
    };

	window.iceEditorApplication = window.iceEditorApplication || {};
    window.iceEditorApplication.ColorPicker = window.iceEditorApplication.ColorPicker || ColorPicker;

})(window);