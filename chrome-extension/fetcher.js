(function() {
    'use strict';

    var poster,
        logBackLog = [],
        yConfig = null,
        isYConfig = false;

    // XXX: this is jacked from quirksmode.org and I don't really like it
    function readCookie(name) {
        var nameEQ = name + '=';
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i += 1) {
            var c = ca[i];
            while (c.charAt(0) === ' ') {
                c = c.substring(1, c.length);
            }
            if (c.indexOf(nameEQ) === 0) {
                return c.substring(nameEQ.length, c.length);
            }
        }
        return null;
    }

    function prepareLogLine(logLine) {
        logLine.uniqueRequestId = (
            yConfig.uniqueRequestId || yConfig.uniqueRequestID);
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

    // Recognize Query Click requesting DOM Elt Details.
    jQuery('*').on('click', function(e) {
      if (!e.shiftKey) {
          return;
      }
      // Process Shift-Click for Target Element Details.
      var pathToTarget = getPathToElement(e.target);
      $.ajax('http://127.0.0.1:5000/path_stats', {
          method: 'GET',
          data: {
              'pathElements': JSON.stringify(pathToTarget)
          },
          success: handleResponse(e)
      });

      return false;
    });

    /**
     * Handle successful response for data about target element.
     * @param {Object} e The event object.
     */
    function handleResponse(e) {
        var targetElement = e.target;
        return function(response) {
            // Handle the path_stats response for the target element.
            response = JSON.parse(response);

            createStatCardForElement(
                targetElement, e.clientX, e.clientY, response.clickCount, response.mouseoverCount);
        };
    };

    /**
     * Creates a stat-card and places it nearby
     * where the user clicked at (offsetX, offsetY).
     * This function is super ugly, don't look at it too closely or you may go blind.
     * @param {domNode} targetElement The clicked element.
     * @param {number} offsetX The offsetX of the click event.
     * @param {number} offsetY The offsetY of the click event.
     * @param {number} clickCount Number of times the element was clicked.
     * @param {number} mouseoverCount Number of times element was moused over.
     */
    function createStatCardForElement(targetElement, offsetX, offsetY, clickCount, mouseoverCount) {
        // Remove ugly selection of part of element text on shift-click.
        targetElement.style['-webkit-user-select'] = 'none';
        // Create stats card.
        var card = document.createElement('div');
        card.className = 'stat-card-for-element';
        card.innerHTML = '<div>Interaction Data:</div><div>Clicks: ' + clickCount + '</div><div>Mouseovers: ' + mouseoverCount + '</div>';
        $(card).css({
          'color': '#FFF',
          'position': 'absolute',
          'top': offsetY + 'px',
          'left': offsetX + 10 + 'px',
          'fontSize': '16px',
          'lineHeight': '140%',
          'backgroundColor': 'rgba(255, 0, 0, .7)',
          'zIndex': 9001,
          'padding': '5px',
          'border-radius': '5px'
        });

        // Remove old cards, add new card.
        $('.stat-card-for-element').remove();
        targetElement.appendChild(card);
        document.getElementsByTagName('body')[0].appendChild(card);
    };

    /**
     * Get the path from the HTML root to the element.
     * @param {Object} element The dom element.
     * @return {Array} pathElements The path from HTML node to target node.
     */
    function getPathToElement(element) {
        var pathElements = [];
        while (element != null) {
            var attributes = [];
            var obj = {
                tagName: element.tagName,
                attributes: attributes
            };
            for (var i = 0; i < element.attributes.length; i++) {
                attributes.push([element.attributes[i].name, element.attributes[i].value]);
            }
            element = element.parentElement;
            pathElements.push(obj);
        }
        return pathElements;
    }

    jQuery('*').on('mouseenter click', function(e) {
        var logLine = {
            eventType: e.type,
            timeStamp: Date.now(),
            elements: getPathToElement(e.target),
            url: document.location.href,
            cookie: document.cookie,
            pathName: window.location.pathname,
            yuv: readCookie('yuv')
        };

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

