
$('*').on('mouseover', function(e) {
    var next = e.target;
    var path = [];
    
    while(next != null) {
        var attributes = [];
        var obj = {
            'tagName': next.tagName,
            'attributes': attributes
        };
        for(var i = 0; i < next.attributes.length; i++) {
            attributes.push(next.attributes[i].name, next.attributes[i].value);
        }
        next = next.parentElement;
        path.push(obj);
    }
    
	poster.log.push(path);
});


var Poster = function() {
	this.log = [];
	$(window).unload(this.handleUnload.bind(this));
	this.handleLoad();

	setInterval(this.postLog.bind(this), 5000);
};

Poster.prototype.handleLoad = function() {
	if(window.localStorage) {
		var stringLog = window.localStorage['click-tracker-log'];
		if(stringLog) {
			this.log = stringLog;
		}
	}
}

Poster.prototype.handleUnload = function() {
	if(window.localStorage) {
		window.localStorage['click-tracker-log'] = this.log;
	}
};

Poster.prototype.postLog = function() {
	if(this.log.length === 0) {
		return;
	}

	var log = this.log;
	this.log = [];
	$.ajax('http://127.0.0.1:5000/log', { 
		method: 'POST',
		data: {
			'log': JSON.stringify(log)
		}
	});
};

poster = new Poster();
