self.importScripts('https://cdn.jsdelivr.net/npm/papaparse@5/papaparse.min.js');

self.onmessage = function(e) {
    const { lines, chunkSize } = e.data;
    
    // Process in chunks to avoid blocking
    const results = Papa.parse(lines, {
        header: true,
        skipEmptyLines: true,
        dynamicTyping: true,
        chunk: function(results, parser) {
            self.postMessage({
                type: 'chunk',
                data: results.data
            });
        },
        complete: function() {
            self.postMessage({ type: 'complete' });
        },
        error: function(error) {
            self.postMessage({
                type: 'error',
                error: error.message
            });
        }
    });
};
