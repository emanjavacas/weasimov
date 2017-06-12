var Delta = Quill.import('delta');
var quill = new Quill('#editor', {
    scrollingContainer: '#scrolling-container',
    theme: 'snow',
    placeholder: 'Bieb, Bieb!'
});

// Store accumulated changes
var change = new Delta();
quill.on('text-change', function(delta) {
    change = change.compose(delta);
});

// Save periodically
setInterval(function() {
    if (change.length() > 0) {
        console.log('Saving changes', change);
        // Send partial changes
        $.ajax({
            contentType: 'application/json;charset=UTF-8',
            url: 'savechange',
            data: JSON.stringify(change),
            type: 'POST',
            dataType: 'json',
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
        change = new Delta();
    }
}, 5*1000);

setInterval(function() {
    console.log('Saving document');
    $.ajax({
        contentType: 'application/json;charset=UTF-8',
        url: 'savedoc',
        data: JSON.stringify(quill.getContents()),
        type: 'POST',
        dataType: 'json',
        success: function(response) {
            console.log(response);
        },
        error: function(error) {
            console.log(error);
        }
    });
}, 50*1000);

// API
// models
var selectedModel;

function models() {
    $('#models-dropdown').empty();
    
    function createDropdownItem(model) {
	$a = $(document.createElement('a'))
	    .attr('href', '#')
	    .text(model.path);
	$li = $(document.createElement('li'))
	    .addClass('dropdown-item')
	    .attr('data-loaded', model.loaded).attr('data-path', model.path)
	    .click(function() {
		if (!model.loaded) {
		    console.log("loading model", model.path);
		    loadModel(model.path);
		}
		selectModel(model.path);
	    });
	$li.append($a);
	return $li;
    }

    $.ajax({
        contentType: 'application/json;charset=UTF-8',
        url: 'models',
        type: 'GET',
        dataType: 'json',
        success: function(response) {
	    for (i=0; i<response.models.length; i++) {
		if (i === 0); selectModel(response.models[0].path);
		$('#models-dropdown').append(createDropdownItem(response.models[i]));
	    }
        },
        error: function(error) {
            console.log(error);
        }
    });
}
models();

function selectModel(model_name) {
    selectedModel = model_name;
    console.log($('#model-name'));
    $('#model-name').text(model_name);
}

function loadModel(model_name) {
    $.ajax({
        contentType: 'application/json;charset=UTF-8',
        url: 'load_model',
        type: 'GET',
	data: JSON.stringify({'model_name': model_name}),
        dataType: 'json',
        success: function(response) {
	    $('*[data-path=' + model_name + ']').attr('data-loaded', 'true');
	    selectModel(model_name);
        },
        error: function(error) {
            console.log(error);
        }
    });
}

// generate
function generate() {
    emptySuggestions();
    var range = quill.getSelection();
    if (range) {
        if (range.length === 0) {
            console.log('User cursor is at index', range.index);
            t = quill.getText(0, range.index);
            var start = range.index;
            for (var i = start; i > -1; i--) {
                if (t[i] === "." && (start - i) > 10) {
                    start = i;
                    break;
                }
                if (i === 0) {
                    start = -2;
                    break;
                }
            }
            var text = quill.getText(start + 2, range.index);
            $.ajax({
                contentType: 'application/json;charset=UTF-8',
                url: 'generate',
                data: JSON.stringify({'selection': text, 'model_name': selectedModel}),
                type: 'POST',
                dataType: 'json',
                success: function(response) {
		    console.log(response.hyps);
		    handleSuggestions(response.hyps, range);
                },
                error: function(error) {
                    console.log(error);
                }
            });
        } else {
            var text = quill.getText(range.index, range.length);
            console.log('User has highlighted: ', text);
        }
    } else {
        console.log('User cursor is not in editor');
    }
}

function emptySuggestions() {
    $('#hyps-panel').empty();
}

function handleSuggestions(hyps, range) {
    function createSuggestionItem(hyp) {
	text = hyp.text.replace(/[\r\n]/g, " ");
	$label = $(document.createElement('span'))
	    .addClass("label").addClass("label-default").addClass("pull-right")
	    .text(hyp.score);
	$li = $(document.createElement('li'))
	    .addClass('list-group-item')
	    .text(text)
	    .click(function(e){
		insertText(text, range);
		emptySuggestions();
		$('#hyps-toolbar').css('visibility', 'hidden');
	    });
	$li.append($label);
	return $li;
    }
    
    if (hyps) {
	$('#hyps-toolbar').css('visibility', 'visible');
	for (i=0; i<hyps.length; i++) {
	    console.log(hyps[i]);
	    $('#hyps-panel').append(createSuggestionItem(hyps[i]));
	}
    }
}

function insertText(text, range) {
    if (range.index > 0) {
        text = " " + text;
    }
    quill.insertText(range.index, text, 'underline', true, 'api');
    quill.format('underline', false, 'api');
}


// temperature
function temperature() {
    var temp = document.getElementById('temperature').value;
    $.ajax({
        contentType: 'application/json;charset=UTF-8',
        url: 'temperature',
        data: JSON.stringify({data: temp}),
        type: 'POST',
        dataType: 'json',
        success: function(response) {
            console.log(response);
        },
        error: function(error) {
            console.log(error);
        }
    });
}

window.onbeforeunload = function() {
    if (change.length() > 0) {
        return 'There are unsaved changes. Are you sure you want to leave?';
    } 
    return null;
};
