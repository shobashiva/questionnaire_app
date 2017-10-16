(function($) {
	$(document).ready(function($){
		$(".object-tools > li").hide();
		$(".object-tools").append('<li><a href="/siteadmin/base/freeresponsequestion/add/" class="addlink">Add free response question</a></li>');
		$(".object-tools").append('<li><a href="/siteadmin/base/singleanswerquestion/add/" class="addlink">Add single answer question</a></li>');
		$(".object-tools").append('<li><a href="/siteadmin/base/multiplechoicequestion/add/" class="addlink">Add multiple choice question</a></li>');
		$(".object-tools").append('<li><a href="/siteadmin/base/gridquestion/add/" class="addlink">Add grid question</a></li>');
	});

})(django.jQuery);