// inspired by the original python program

// targetCollector as an object
var targetCollector = {
  requests: 0,
  collectedData: {
    liveDomains: [],
    redirections: [],
    processedDomains: [],
  },
  getStatus: function(subdomain) {
    var req = new XMLHttpRequest();
    var url = 'https://' + subdomain;
    req.open('get', url, true);
    req.timeout = 3000;
    req.ontimeout = function() {
      req.abort();
    };
    req.onreadystatechange = function() {
      if (req.responseURL && req.readyState == 4) {
        targetCollector.collectedData.redirections.push(url + ' ==> ' + req.responseURL);
      } else if (req.readyState == 4) {
        targetCollector.collectedData.liveDomains.push(url);
      }
    };
    targetCollector.requests++;
    req.send();
  },
  processFile: function() {
    var processor = new XMLHttpRequest();
    processor.open('get', '/subdomains.txt', true);
    processor.onreadystatechange = function() {
      if (processor.readyState == 4 && processor.status == 200) {
        var text = processor.responseText;
        var lines = text.split('\n');
        lines.forEach(function(processed) {
          if (processed.charAt(processed.length - 1) == '\r') {
            processed = processed.slice(0, -1);
          }
          targetCollector.collectedData.processedDomains.push(processed);
        });
      }
    };
    processor.send();
  }
};
