/**
 * The API should be the following:
 *
 * * Request initialization;
 *  send({'type': 'initialize'})
 *
 *
 *
 */
if (!window.hasOwnProperty('Chart')) {
    alert('Chart.js library missing, nothing will work');
} else {
    Chart.defaults.global.animation = false;
    Chart.defaults.global.scaleIntegersOnly = false;
    Chart.defaults.global.scaleBeginAtZero = true;
    Chart.defaults.global.responsive = true;
    Chart.defaults.global.scaleOverride = true;
    Chart.defaults.global.scaleSteps = 5;
    Chart.defaults.global.scaleStepWidth = 20;
    Chart.defaults.global.scaleStartValue = 0;
}

var application = new function () {
    this.charts = {};

    this.colors = [
        {
            fillColor: "rgba(151,187,205,0.2)",
            strokeColor: "rgba(151,187,205,1)",
            pointColor: "rgba(151,187,205,1)",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(151,187,205,1)",
        },
        {

            fillColor: "rgba(220,220,220,0.2)",
            strokeColor: "rgba(220,220,220,1)",
            pointColor: "rgba(220,220,220,1)",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(220,220,220,1)",
        },
    ];


    this.get_container = function () {
        var conts = document.getElementsByTagName('div');
        var container;
        for (i in conts) {
            container = conts[i];
            if (container.id == 'container')
                break;
        }
        if (!container || container.id != 'container') {
            container = document.createElement('div');
            container.id = 'container';
            var body = document.getElementsByTagName('body')[0];
            body.appendChild(container);
        }
        return container;
    };

    this.get_display = function (display_id) {
        var container = this.get_container();
        var display = document.getElementById(display_id);
        if (!display) {
            if (document.getElementById(display_id + '-canvas')) {
                console.error('Canvas for ' + display_id + '-canvas is already' +
                    ' defined, but no display area!');
            }
            var display = document.createElement("section");
            display.id = display_id;
            container.appendChild(display);
        }
        return display;
    };

    this.update_display_elements = function (display, data) {
        var canvas = display.getElementsByTagName('canvas').item(0);
        if (!canvas) {
            display.innerHTML = '<canvas id="' + display['id'] + '-canvas"></canvas>';
            canvas = display.getElementsByTagName('canvas').item(0);
        }
        var chart = new Chart(canvas.getContext('2d'));
        var chart_data = {
            labels: [],
            datasets: [],
        };
        for (var i in data['signals']) {
            signal = data['signals'][i];
            var signal_data = {
                label: signal['name'],
                data: []
            };
            for (var a in this.colors[signal['id']]) {
                signal_data[a] = this.colors[signal['id']][a];
            }
            chart_data['datasets'].push(signal_data);
        }
        var line_chart = chart.Line(chart_data);
        this.charts[display['id']] = line_chart;

        if ('controls' in data) {
            for (control in data['controls']) {
                /* No controls for the moment! */
            }
        }
    };

    this.update_display = function (data) {
        var display = this.get_display(data['id']);
        this.update_display_elements(display, data);
    };

    this.handle_initialize = function (msg) {
        console.log("Handling initialization");
        for (var i in msg['displays']) {
            this.update_display(msg['displays'][i]);
        }
    };

    this.get_chart = function (display) {
        if (display['id'] in this.charts)
            return this.charts[display['id']];
    };

    this.update_signal_data = function (display, data) {
        var chart = this.get_chart(display);
        if (!chart)
            return;
        var chart_data = [];
        for (var i in data['signals']) {
            if ( i ==0){
                timestamp = data['signals'][0][0];
            } else {
            var d = data['signals'][i];
            chart_data.push(d['data'][0]);
            }
        }
        chart.addData(chart_data, timestamp);
        while (chart.datasets[0].points.length > 150) {
            chart.removeData();
        }
    };

    this.handle_data = function (msg) {
        for (var i in msg) {
            data = msg[i];
            var display = this.get_display(data['id']);
            this.update_signal_data(display, data);
            /* this.update_controls(display, data); */
            console.log("Handling data");
        }
    };

    this.onmessage = function (e) {
        try {
            var o = JSON.parse(e.data);
        } catch (err) {
            console.error("Data unable to parse:" + e.data);
            return;
        }
        if (o['type'] == 'error') {
            console.log('Error ocurred in backend: ' + o['message']);
        }
        else if (o['type'] == 'initialize') {
            this.handle_initialize(o['message']);
        } else if (o['type'] == 'data') {
            this.handle_data(o['message']);
        }
        else {
            console.log('No idea on what to do with type ' + o['type']);
        }
    };

};

ws = new WebSocket("ws://" + location.host + '/ws');

ws.onopen = function (e) {
    console.log("Opened ws " + e);
    this.send('{"type": "initialize"}');
};

ws.onerror = function (e) {
    console.log("Error on the WS" + e);
};

ws.onclose = function (e) {
    console.log("WS closed!");
};

ws.onmessage = function (e) {
    application.onmessage(e);
};
