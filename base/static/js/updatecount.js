
$(document).ready(function($){
	$('input').keypress(function(e) {
		if(e.which == 13){
			e.preventDefault();
			var inputs = $(this).parents("form").eq(0).find(":input");
			var idx = inputs.index(this);
			inputs.eq(inputs.index(this)+1).focus();
		}
	});

	$('.dec').click(function(e) {
		var m_val = $(this).parent().parent().children("input").val();
		var numeric_val = Number(m_val);
		if(numeric_val > 0){
			numeric_val = Number(m_val) - 1;
		}
		$(this).parent().parent().children("input").val(numeric_val);
	});

	$('.inc').click(function(e) {
		e.stopPropagation();
		var m_val = $(this).parent().parent().children("input").val();
		var numeric_val = Number(m_val) + 1;
		$(this).parent().parent().children("input").val(numeric_val);
	});

	$.each($('input[id$=role],input[id$=name],input[id$=presbytery]'),function(){this.title=this.value;});

	var targets = $( 'input[id$=role], input[id$=name],input[id$=presbytery]' ),
	target  = false,
	tooltip = false,
	title   = false;

	targets.bind( 'mouseenter', function()
	{
		target  = $( this );
		tip     = target.attr( 'title' );
		tooltip = $( '<div id="tooltip"></div>' );

		if( !tip || tip == '' )
			return false;

		target.removeAttr( 'title' );

		tooltip.css( 'opacity', 0.9 )
		.html( tip )
		.appendTo( 'body' );

		var init_tooltip = function()
		{ console.log("in init");
		if( $( window ).width() < tooltip.outerWidth() * 1.5 )
			tooltip.css( 'max-width', $( window ).width() / 2 );
		else
			tooltip.css( 'max-width', 340 );

		var pos_left = target.offset().left + ( target.outerWidth() / 2 ) - ( tooltip.outerWidth() / 2 ),
		pos_top  = target.offset().top - tooltip.outerHeight() - 20;

		if( pos_left < 0 )
		{
			pos_left = target.offset().left + target.outerWidth() / 2 - 20;
			tooltip.addClass( 'left' );
		}
		else
			tooltip.removeClass( 'left' );

		if( pos_left + tooltip.outerWidth() > $( window ).width() )
		{
			pos_left = target.offset().left - tooltip.outerWidth() + target.outerWidth() / 2 + 20;
			tooltip.addClass( 'right' );
		}
		else
			tooltip.removeClass( 'right' );

		if( pos_top < 0 )
		{
			var pos_top  = target.offset().top + target.outerHeight();
			tooltip.addClass( 'top' );
		}
		else
			tooltip.removeClass( 'top' );

		tooltip.css( { left: pos_left, top: pos_top } )
		.animate( { top: '+=10', opacity: 0.9 }, 50 );
	};

	init_tooltip();
    //$( window ).resize( init_tooltip );

    var remove_tooltip = function()
    {
    	tooltip.animate( { top: '-=10', opacity: 0 }, 50, function()
    	{
    		$( this ).remove();
    	});

    	target.attr( 'title', tip );
    };

    target.bind( 'mouseleave', remove_tooltip );
    tooltip.bind( 'click', remove_tooltip );
});
});
