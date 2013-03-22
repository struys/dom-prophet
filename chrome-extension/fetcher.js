(function () {
    'use strict';

    var poster,
        logBackLog = [],
        yConfig = null,
        isYConfig = false;

    function prepareLogLine(logLine) {
        logLine.uniqueRequestId = yConfig.uniqueRequestId || yConfig.uniqueRequestID;
    }

    window.addEventListener('message', function(event) {
        var logLine;

        if (event.data.yConfig) {
            yConfig = event.data.yConfig;
            isYConfig = event.data.isYConfig;

            while (logBackLog.length) {
                logLine = logBackLog.pop();
                prepareLogLine(logLine);
                poster.log.push(logLine);
            }
        }
    }, false);

    (function() {
        var script = document.createElement('script');
        script.appendChild(document.createTextNode([
            '(function () {',
            '    \'use strict\';',
            '',
            '    if (window.yConfig) {',
            '        window.postMessage({ yConfig: window.yConfig, isYConfig: true }, \'*\');',
            '    } else {',
            '        window.postMessage({ yConfig: window.yelp.config, isYConfig: false }, \'*\');',
            '    }',
            '} ());'
        ].join('')));
        document.body.appendChild(script);
    } ());

    jQuery('*').on('mouseenter click', function(e) {
        var next = e.target;
        var path = [];

        var logLine = {
            eventType: e.type,
            elements: [],
            url: document.location.href,
            cookie: document.cookie,
            pathName: window.location.pathname
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

        if (yConfig) {
            prepareLogLine(logLine);
            poster.log.push(logLine);
        } else {
            logBackLog.push(logLine);
        }
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
} ());

