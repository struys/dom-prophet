
jQuery('*').on('mouseenter click', function(e) {
    var next = e.target;
    var path = [];

    var logLine = {
        eventType: e.type,
        elements: [],
        url: document.location.href,
        cookie: document.cookie
    };

    while (next != null) {
        var attributes = [];
        var obj = {
            'tagName': next.tagName,
            'attributes': attributes
        };
        for (var i = 0; i < next.attributes.length; i++) {
            attributes.push([next.attributes[i].name, next.attributes[i].value]);
        }
        next = next.parentElement;
        logLine.elements.push(obj);
    }

    poster.log.push(logLine);
});


var Poster = function() {
    this.log = [];
    $(window).unload(this.handleUnload.bind(this));
    this.handleLoad();

    setInterval(this.postLog.bind(this), 5000);
};

/**
 * Handle module loading at page load.
 */
Poster.prototype.handleLoad = function() {
    this.log = this.getLogFromDB();
};

/**
 * Handle page unload.
 */
Poster.prototype.handleUnload = function() {
    this.saveLogToDB();
};


/**
 * Save this item's log data to localStorage.
 */
Poster.prototype.saveLogToDB = function() {
    if (window.localStorage) {
        window.localStorage.setItem('click-tracker-log', JSON.stringify(this.log));
    }
};

/**
 * Save this item's log data to localStorage.
 * @return {Array} Array of logged items.
 */
Poster.prototype.getLogFromDB = function() {
    if (window.localStorage) {
        return JSON.parse(window.localStorage.getItem('click-tracker-log'));
    }
    return [];
};

/**
 * Post logs in module to server.
 */
Poster.prototype.postLog = function() {
    if (this.log.length === 0) {
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
