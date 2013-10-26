function addPicToBook(thumb_url, full_url, username){
	$.ajax({
		url: '/add_pic_to_book',
		method: 'POST',
		dataType:'json',
		data:{
			thumb_url: thumb_url,
			full_url: full_url,
			username: username,
			book_id: 1
		},
		success: function(resp){
			console.log('done');
		}
	})
}
$(document).ready(function(){
	//init some drag and drop stuff for the book page; from http://www.html5rocks.com/en/tutorials/dnd/basics/
	var dragSrcEl = null;

	function handleDragStart(e) {
	  // Target (this) element is the source node.
	  this.style.opacity = '0.4';

	  dragSrcEl = this;

	  e.dataTransfer.effectAllowed = 'move';
	  e.dataTransfer.setData('text/html', this.innerHTML);
	}

	function handleDragOver(e) {
	  if (e.preventDefault) {
	    e.preventDefault(); // Necessary. Allows us to drop.
	  }

	  e.dataTransfer.dropEffect = 'move';  // See the section on the DataTransfer object.

	  return false;
	}

	function handleDragEnter(e) {
	  // this / e.target is the current hover target.
	  this.classList.add('over');
	}

	function handleDragLeave(e) {
	  this.classList.remove('over');  // this / e.target is previous target element.
	}
	function handleDrop(e) {
	  // this / e.target is current target element.

	  $('#current-book .pics').append(dragSrcEl);
	  dragSrcEl.style.opacity = '1.0';
	  this.classList.remove('over');
	  // See the section on the DataTransfer object.
	  addPicToBook($(dragSrcEl).attr('src'),$(dragSrcEl).data('full'), $(dragSrcEl).data('user'));	//needs to be written
	  return false;
	}

	function handleDragEnd(e) {
	  // this/e.target is the source node.

	  [].forEach.call(cols, function (col) {
	    col.classList.remove('over');
	  });
	}
	var cols = document.querySelectorAll('.instapic');
	[].forEach.call(cols, function(col) {
	  col.addEventListener('dragstart', handleDragStart, false);
	});
	var book = document.getElementById('current-book')
	// var $book = $('#current-book');
	// $book.on('dragenter', handleDragEnter);
	// $book.on('dragover', handleDragOver);
	// $book.on('dragleave', handleDragLeave);
	  book.addEventListener('dragenter', handleDragEnter, false);
	  book.addEventListener('dragover', handleDragOver, false);
	  book.addEventListener('dragleave', handleDragLeave, false);
	  book.addEventListener('drop', handleDrop, false);
	  book.addEventListener('dragend', handleDragEnd, false);

});