var current_algorithm = 'algorithm2'

function clear_canvas(parent_id, canvas_id) {
    var existed = document.getElementById(canvas_id)
    if (existed)
        document.getElementById(parent_id).removeChild(existed)
    var new_canvas = document.createElement("canvas")
    new_canvas.setAttribute("id", canvas_id)
    document.getElementById(parent_id).appendChild(new_canvas)
}

function generate_cluster_silhouette(clusters) {

    clear_canvas("silhouette", "cluster_silhouette")
    var labels = [];
    for (i = 0; i < clusters.length; i++) {
        labels[i] = clusters[i].cluster_id
    }

    var data = [];
    for (i = 0; i < clusters.length; i++) {
        data[i] = clusters[i].cluster_silhouette;
    }

    var cluster_silhouette = {
        labels: labels,
        datasets: [
            {
                label: "Silhouette",
                backgroundColor: colors[3],
                data: data
            },
        ]
    };

    var cluster_silhouette_config = {
        type: "bar",
        data: cluster_silhouette,
        options: {
            responsive: true
        }
    };

    var cluster_silhouette_chart = document.getElementById("cluster_silhouette").getContext("2d")

    new Chart(cluster_silhouette_chart, cluster_silhouette_config)
}

function generate_cluster_means(clusters) {
    var existed_row = document.getElementById("cluster_means_sample").getElementsByClassName("row")

    if (existed_row.length !== 0) {
        document.getElementById("cluster_means_sample")
            .removeChild(existed_row[0])
    }
    var newRows = document.createElement("div")
    newRows.setAttribute("class", "row")
    // newRows.setAttribute("style", "height: 600px")
    document.getElementById("cluster_means_sample").appendChild(newRows)
    for (i = 0; i < clusters.length; i++) {
        var cluster = clusters[i];

        var labels = [];

        for (kk = 0; kk < cluster.cluster_means.length; kk++) {
            labels[kk] = "Month " + kk
        }

        var datasets = []
        datasets[0] = {
            label: "centroid",
            fill: false,
            backgroundColor: colors[cluster.cluster_id],
            borderColor: colors[clusters[i].cluster_id],
            data: clusters[i].cluster_means
        };

        var length = 20
        if (cluster.cluster_samples.length < length) {
            length = cluster.cluster_samples.length
        }
        for (j = 0; j < length; j++) {
            datasets[j + 1] = {
                // label: "sample",
                fill: false,
                backgroundColor: colors[6],
                borderColor: colors[6],
                data: cluster.cluster_samples[j].samples
            };
        }

        var cluster_mean_data = {
            labels: labels,
            datasets: datasets
        };
        var cluster_means_chart_config = {
            type: 'line',
            data: cluster_mean_data,
            options: {
                legend: {
                    display: false
                },
                responsive: true,
                title: {
                    display: true,
                    text: "Cluster " + cluster.cluster_id
                }
            }
        }

        var canvas_id = "cluster_means_" + cluster.cluster_id
        var newCanvas = document.createElement("canvas")
        newCanvas.setAttribute("id", canvas_id)

        var newCols = document.createElement("div")
        newCols.setAttribute("class", "col-md-4")

        newCols.appendChild(newCanvas)

        document.getElementById("cluster_means_sample").getElementsByClassName("row")[0].appendChild(newCols)

        // get bar chart canvas
        var cluster_means_chart = document.getElementById(canvas_id).getContext("2d");

        // draw bar chart
        new Chart(cluster_means_chart, cluster_means_chart_config);
    }
}

function generate_cluster_forecast(forecast, container_id) {
    var existed_row = document.getElementById(container_id).getElementsByClassName("row")

    if (existed_row.length !== 0) {
        document.getElementById(container_id)
            .removeChild(existed_row[0])
    }
    var newRows = document.createElement("div")
    newRows.setAttribute("class", "row")
    // newRows.setAttribute("style", "height: 600px")
    document.getElementById(container_id).appendChild(newRows)
    for (var key in forecast) {
        var value = forecast[key]
        var history = value['history']
        var fc = value['forecast']
        var history_data = []
        var forecast_data = []
        var labels = []
        var total_length = history.length + fc.length
        for (i = 0; i < total_length; i++) {
            labels[i] = "Month " + i
            if (i < history.length) {
                history_data[i] = history[i]
                forecast_data[i] = null
            } else {
                history_data[i] = null
                forecast_data[i] = fc[i - history.length]
            }
        }

        var datasets = [
            {
                label: "History balances",
                data: history_data,
                borderColor: colors[0],
                backgroundColor: colors[0],
                fill: false
            },
            {
                label: "Forecast balances",
                data: forecast_data,
                borderColor: colors[1],
                backgroundColor: colors[1],
                fill: false
            }
        ]

        var balance_data = {
            labels: labels,
            datasets: datasets
        }

        var cluster_forecast_config = {
            type: 'line',
            data: balance_data,
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: "Cluster " + key
                }
            }
        }

        var canvas_id = container_id + key
        var newCanvas = document.createElement("canvas")
        newCanvas.setAttribute("id", canvas_id)

        var newCols = document.createElement("div")
        newCols.setAttribute("class", "col-md-4")

        newCols.appendChild(newCanvas)

        document.getElementById(container_id).getElementsByClassName("row")[0].appendChild(newCols)

        var cluster_forecast_chart = document.getElementById(canvas_id).getContext('2d')

        new Chart(cluster_forecast_chart, cluster_forecast_config)

    }
}

function generate_cluster_sample_pca2(clusters) {
    var datasets = []

    for (i = 0; i < clusters.length; i++) {
        var cluster = clusters[i];
        var data = [];
        for (j = 0; j < cluster.cluster_samples.length; j++) {
            var sample = cluster.cluster_samples[j]
            data[j] = {x: sample.pca2[0], y: sample.pca2[1]}
        }
        datasets[i] = {
            label: "Cluster " + clusters[i].cluster_id,
            borderColor: colors[clusters[i].cluster_id],
            backgroundColor: colors[clusters[i].cluster_id],
            data: data
        }
    }

    var sample_pca2_data = {
        datasets: datasets
    };

    var sample_pca2_chart = document.getElementById("cluster_sample_pca2").getContext("2d")
    new Chart(sample_pca2_chart, {
        type: 'scatter',
        data: sample_pca2_data,
        options: {
            title: {
                display: true,
                text: "Cluster sample PCA"
            }
        }
    })
}

function generate_cluster_balance(clusters) {
    clear_canvas("balance", "balance_chart")
    var labels = []
    var data = []
    for (i = 0; i < clusters.length; i++) {
        labels[i] = clusters[i].cluster_id
        data[i] = {
            label: 'Total balance of cluster ' + clusters[i].cluster_id,
            backgroundColor: colors[clusters[i].cluster_id],
            data: clusters[i].cluster_balances.slice(0, clusters[i].cluster_balances.length - 3)
        }
    }

    var cluster_balance_data = {
        labels: labels,
        datasets: data
    };

// get bar chart canvas
    var balance_bar_chart = document.getElementById("balance_chart").getContext("2d");
    new Chart(balance_bar_chart, {
        type: 'bar',
        data: cluster_balance_data,
        options: {
            title: {
                display: true,
                text: 'Total balances'
            },
            tooltips: {
                mode: 'index',
                intersect: false
            },
            responsive: true,
            scales: {
                xAxes: [{
                    stacked: true,
                }],
                yAxes: [{
                    stacked: true
                }]
            }
        }
    });


}

function generate_cluster_balance_proportion(clusters_mean_balances) {
    clear_canvas("proportion", "balance_proportion")
    var labels = []
    var data = []
    var background = []
    var i = 0
    for (var key in clusters_mean_balances) {
        var k = key;
        var v = clusters_mean_balances[k];
        labels[i] = k;
        data[i] = v;
        background[i] = colors[i];
        i++
    }

    var cluster_balance_proportion = {
        labels: labels,
        datasets: [{
            data: data,
            backgroundColor: background,
            label: "Cluster mean proportion"
        }]
    };

    var cluster_balance_mean_config = {
        type: 'pie',
        data: cluster_balance_proportion,
        options: {
            responsive: true
        }
    };

    var cluster_mean_balances_chart = document.getElementById('balance_proportion').getContext('2d')
    new Chart(cluster_mean_balances_chart, cluster_balance_mean_config)
}

function generate_cluster_statistic(clusters) {
    clear_canvas("statistic", "balance_statistic")
    var labels = [];
    var mean = [];
    var std = [];

    for (i = 0; i < clusters.length; i++) {
        labels[i] = clusters[i].cluster_id;
        mean[i] = clusters[i].cluster_mean;
        std[i] = clusters[i].cluster_variance
    }

    var cluster_statistic = {
        labels: labels,
        datasets: [
            {
                label: "Mean",
                backgroundColor: colors[0],
                data: mean
            },

            {
                label: "Std",
                backgroundColor: colors[1],
                data: std
            }
        ]
    };

    var cluster_statistic_config = {
        type: "bar",
        data: cluster_statistic,
        options: {
            responsive: true
        }
    };

    var balance_statistic_chart = document.getElementById("balance_statistic").getContext("2d")

    new Chart(balance_statistic_chart, cluster_statistic_config)
}

function generate_cluster_monitor(cluster_monitors) {

    var existed_row = document.getElementById("cluster_monitor_container").getElementsByClassName("row")

    if (existed_row.length !== 0) {
        document.getElementById("cluster_monitor_container")
            .removeChild(existed_row[0])
    }

    var newRows = document.createElement("div")
    newRows.setAttribute("class", "row")
    // newRows.setAttribute("style", "height: 600px")
    document.getElementById("cluster_monitor_container").appendChild(newRows)

    for (var key in cluster_monitors) {
        var value = cluster_monitors[key]

        var labels = []
        var data = []
        var background = []
        var i = 0

        for (var k in value) {
            for (var kk in value[k]) {
                labels[i] = kk
                data[i] = value[k][kk]
                background[i] = colors[kk]
            }
            i++
        }

        var cluster_monitor = {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: background,
                labels: "Cluster monitor"
            }]
        };

        var cluster_monitor_config = {
            type: 'doughnut',
            data: cluster_monitor,
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: "Cluster " + key
                }
            }
        };

        var canvas_id = "cluster_monitor" + key
        var newCanvas = document.createElement("canvas")
        newCanvas.setAttribute("id", canvas_id)

        var newCols = document.createElement("div")
        newCols.setAttribute("class", "col-md-4")

        newCols.appendChild(newCanvas)
        document.getElementById("cluster_monitor_container").getElementsByClassName("row")[0]
            .appendChild(newCols)

        var cluster_monitor_chart = document.getElementById(canvas_id).getContext('2d')
        new Chart(cluster_monitor_chart, cluster_monitor_config)
    }

}

function generate_all_time_silhouette(sils_random, sils_history) {
    var labels = [];
    var random_values = [];
    var history_values = [];
    var i = 0;

    for (var key in sils_random) {
        labels[i] = key;
        random_values[i] = sils_random[key];
        history_values[i] = sils_history[key];
        i++
    }

    var all_time_sils = {
        labels: labels,
        datasets: [
            {
                label: "Random",
                backgroundColor: colors[0],
                data: random_values
            },
            {
                label: "History",
                backgroundColor: colors[1],
                data: history_values
            }
        ]
    };

    var all_time_sil_config = {
        type: "bar",
        data: all_time_sils,
        options: {
            responsive: true,
            title: {
                display: true,
                text: "Silhouette values over time points"
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        max: 1,
                        min: 0,
                        stepSize: 0.2
                    }
                }]
            }
        }
    }

    var all_time_sil_chart = document.getElementById("all_time_silhouette").getContext("2d")
    new Chart(all_time_sil_chart, all_time_sil_config)
}

function generate_all_time_number_cluster(number_random, number_history) {
    var labels = [];
    var random_values = [];
    var history_values = [];
    var i = 0;

    for (var key in number_random) {
        labels[i] = key;
        random_values[i] = number_random[key];
        history_values[i] = number_history[key];
        i++
    }

    var all_time_number_cluster = {
        labels: labels,
        datasets: [
            {
                label: "Random",
                backgroundColor: colors[0],
                data: random_values
            },
            {
                label: "History",
                backgroundColor: colors[1],
                data: history_values
            }
        ]
    };

    var all_time_number_cluster_config = {
        type: "bar",
        data: all_time_number_cluster,
        options: {
            responsive: true,
            title: {
                display: true,
                text: "Number of cluster over time points"
            },
            scales: {
                yAxes: [{
                    display: true,
                    ticks: {
                        beginAtZero: true,
                        max: 1,
                        min: 10,
                        stepSize: 2
                    }
                }]
            }
        }
    }

    var all_time_number_cluster_chart = document.getElementById("all_time_number_cluster").getContext("2d")
    new Chart(all_time_number_cluster_chart, all_time_number_cluster_config)
}

function generate_all_time_spent_time(spent_time_random, spent_time_history) {
    var labels = [];
    var random_values = [];
    var history_values = [];
    var i = 0;

    for (var key in spent_time_random) {
        labels[i] = key;
        random_values[i] = spent_time_random[key];
        history_values[i] = spent_time_history[key];
        i++
    }

    var all_time_spent_time = {
        labels: labels,
        datasets: [
            {
                label: "Random",
                backgroundColor: colors[0],
                data: random_values
            },
            {
                label: "History",
                backgroundColor: colors[1],
                data: history_values
            }
        ]
    };

    var all_time_spent_time_config = {
        type: "bar",
        data: all_time_spent_time,
        options: {
            responsive: true,
            title: {
                display: true,
                text: "Clustering spent time over time points"
            },
            scales: {
                yAxes: [{
                    display: true,
                    ticks: {
                        beginAtZero: true,
                        // max: 1,
                        // min: 10,
                        // stepSize: 2
                    }
                }]
            }
        }
    }

    var all_time_number_spent_time_chart = document.getElementById("all_time_spent_time").getContext("2d")
    new Chart(all_time_number_spent_time_chart, all_time_spent_time_config)
}

function next_month() {
    var current_month = document.getElementById("current_month").innerText
    var next_month = parseInt(current_month, 10) + 1
    document.getElementById("current_month").innerText = next_month
    load(next_month, current_algorithm)
}

function previous_month() {
    var current_month = document.getElementById("current_month").innerText
    var prev_month = parseInt(current_month, 10) - 1
    document.getElementById("current_month").innerText = prev_month
    load(prev_month, current_algorithm)
}

function load(month, algorithm) {
    $.ajax({
        url: "http://localhost:5000/" + month + "?algorithm=" + algorithm,
        success: function (result) {
            var cluster = JSON.parse(result)
            console.log(cluster.clusters.length)
            generate_cluster_means(cluster.clusters);
            // generate_cluster_balance(cluster.clusters);
            // generate_cluster_statistic(cluster.clusters);
            // generate_cluster_silhouette(cluster.clusters);
        }
    });

    $.ajax({
        url: "http://localhost:5000/cluster_balance/" + month + "?algorithm=" + algorithm,
        success: function (result) {
            var cluster_balances = JSON.parse(result)
            // generate_cluster_balance_proportion(cluster_balances);
        }
    });

    $.ajax({
        url: "http://localhost:5000/cluster_monitor/" + month + "?algorithm=" + algorithm,
        success: function (result) {
            var cluster_monitors = JSON.parse(result)
            generate_cluster_monitor(cluster_monitors);
        }
    });

    $.ajax({
        url: "http://localhost:5000/forecast/" + month + "?algorithm=" + algorithm + "&forecast=AR",
        success: function (result) {
            var forecast = JSON.parse(result)
            generate_cluster_forecast(forecast, "cluster_balance_AR_forecast")
        }
    })

    $.ajax({
        url: "http://localhost:5000/forecast/" + month + "?algorithm=" + algorithm + "&forecast=MA",
        success: function (result) {
            var forecast = JSON.parse(result)
            generate_cluster_forecast(forecast, "cluster_balance_MA_forecast")
        }
    })

    $.ajax({
        url: "http://localhost:5000/forecast/" + month + "?algorithm=" + algorithm + "&forecast=ETS",
        success: function (result) {
            var forecast = JSON.parse(result)
            generate_cluster_forecast(forecast, "cluster_balance_ETS_forecast")
        }
    })
}

function change_algorithm(algorithm) {
    current_algorithm = algorithm
    var current_month = parseInt(document.getElementById("current_month").innerText, 10)
    load(current_month, algorithm)
}

function forecast_analytic() {
    var current_month = parseInt(document.getElementById("current_month").innerText, 10)

    $.ajax({
        url: "http://localhost:5000/forecast_all/" + current_month + "?algorithm=algorithm2",
        success: function (result) {
            var forecast = JSON.parse(result)
            generate_actual_and_predict("actual_and_predict_ar", forecast)
        }
    })

    $.ajax({
        url: "http://localhost:5000/forecast_analytic/" + current_month + "?algorithm=algorithm2",
        success: function (result) {
            var forecast_analytic = JSON.parse(result)
            generate_rmse("rmse_ar", forecast_analytic)
        }
    })

}

function clustering_analytic() {
    var current_month = parseInt(document.getElementById("current_month").innerText, 10)

    $.ajax({
        url: "http://localhost:5000/clustering_analytic/" + current_month + "?algorithms=algorithm1,algorithm2,algorithm3,algorithm4",
        success: function(result) {
            generate_compare_silhouette(result)
            generate_compare_number_cluster(result)
            generate_compare_spent_time(result)
        }
    })
}

function generate_compare_silhouette(clustering_analytic) {
    clear_canvas("compare_silhouette_parent", "compare_silhouette")
    var labels = ["Algorithm 1", "Algorithm 2", "Algorithm 3", "Algorithm 4"]
    var data = [clustering_analytic["algorithm1"]["mean_silhouette"],
        clustering_analytic["algorithm2"]["mean_silhouette"],
        clustering_analytic["algorithm3"]["mean_silhouette"],
        clustering_analytic["algorithm4"]["mean_silhouette"]]

    var compare_silhouette = {
        labels: labels,
        datasets: [{
            label: "Silhouette",
            backgroundColor: colors[2],
            data: data
        }]
    }

    var compare_sihouette_config = {
        type: "bar",
        data: compare_silhouette,
        options: {
            responsive: true,
            scales: {
                yAxes: [{
                    display:true,
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    }

    var compare_silhouette_chart = document.getElementById("compare_silhouette").getContext("2d")

    new Chart(compare_silhouette_chart, compare_sihouette_config)
}

function generate_compare_number_cluster(clustering_analytic) {
    clear_canvas("compare_number_cluster_parent", "compare_number_cluster")
    var labels = ["Algorithm 1", "Algorithm 2", "Algorithm 3", "Algorithm 4"]
    var data = [clustering_analytic["algorithm1"]["number_clusters"],
        clustering_analytic["algorithm2"]["number_clusters"],
        clustering_analytic["algorithm3"]["number_clusters"],
        clustering_analytic["algorithm4"]["number_clusters"]]

    var compare_silhouette = {
        labels: labels,
        datasets: [{
            label: "Number of clusters",
            backgroundColor: colors[2],
            data: data
        }]
    }

    var compare_sihouette_config = {
        type: "bar",
        data: compare_silhouette,
        options: {
            responsive: true,
            scales: {
                yAxes: [{
                    display:true,
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    }

    var compare_silhouette_chart = document.getElementById("compare_number_cluster").getContext("2d")

    new Chart(compare_silhouette_chart, compare_sihouette_config)
}

function generate_compare_spent_time(clustering_analytic) {
    clear_canvas("compare_spent_time_parent", "compare_spent_time")
    var labels = ["Algorithm 1", "Algorithm 2", "Algorithm 3", "Algorithm 4"]
    var data = [clustering_analytic["algorithm1"]["spent_time"],
        clustering_analytic["algorithm2"]["spent_time"],
        clustering_analytic["algorithm3"]["spent_time"],
        clustering_analytic["algorithm4"]["spent_time"]]

    var compare_silhouette = {
        labels: labels,
        datasets: [{
            label: "Clustering spent time",
            backgroundColor: colors[2],
            data: data
        }]
    }

    var compare_sihouette_config = {
        type: "bar",
        data: compare_silhouette,
        options: {
            responsive: true,
            scales: {
                yAxes: [{
                    display:true,
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    }

    var compare_silhouette_chart = document.getElementById("compare_spent_time").getContext("2d")

    new Chart(compare_silhouette_chart, compare_sihouette_config)
}

function generate_actual_and_predict(container_id, forecast) {
    var existed_row = document.getElementById(container_id).getElementsByClassName("row")

    if (existed_row.length !== 0) {
        document.getElementById(container_id)
            .removeChild(existed_row[0])
    }

    var newRows = document.createElement("div")
    newRows.setAttribute("class", "row")
    // newRows.setAttribute("style", "height: 600px")
    document.getElementById(container_id).appendChild(newRows)

    for (var key in forecast) {
        var value = forecast[key]
        var history = value['history']
        var fc_ar = value['ar']
        var fc_ma = value['ma']
        var fc_ets = value['ets']
        var actual = value['actual']
        var history_data = []
        var fc_ar_data = []
        var fc_ma_data = []
        var fc_ets_data = []
        var actual_data = []
        var labels = []
        var total_length = history.length + fc_ma.length
        for (i = 0; i < total_length; i++) {
            labels[i] = "Month " + i
            if (i < history.length) {
                history_data[i] = history[i]
                fc_ar_data[i] = null
                fc_ma_data[i] = null
                fc_ets_data[i] = null
                actual_data[i] = null
            } else {
                history_data[i] = null
                fc_ar_data[i] = fc_ar[i - history.length]
                fc_ma_data[i] = fc_ma[i - history.length]
                fc_ets_data[i] = fc_ets[i - history.length]
                actual_data[i] = actual[i - history.length]
            }
        }

        var datasets = [
            {
                label: "History balances",
                data: history_data,
                borderColor: colors[0],
                backgroundColor: colors[0],
                fill: false
            },
            {
                label: "AR Forecast balances",
                data: fc_ar_data,
                borderColor: colors[1],
                backgroundColor: colors[1],
                fill: false
            },
            {
                label: "MA Forecast balances",
                data: fc_ma_data,
                borderColor: colors[2],
                backgroundColor: colors[2],
                fill: false
            },
            {
                label: "ETS Forecast balances",
                data: fc_ets_data,
                borderColor: colors[3],
                backgroundColor: colors[3],
                fill: false
            },
            {
                label: "Actual balances",
                data: actual_data,
                borderColor: colors[4],
                backgroundColor: colors[4],
                fill: false
            },
        ]

        var balance_data = {
            labels: labels,
            datasets: datasets
        }

        var cluster_forecast_config = {
            type: 'line',
            data: balance_data,
            options: {
                legend: {
                    display: false
                },
                responsive: true,
                title: {
                    display: true,
                    text: "Cluster " + key
                }
            }
        }

        var canvas_id = container_id + "_analytic_" + key
        var newCanvas = document.createElement("canvas")
        newCanvas.setAttribute("id", canvas_id)

        var newCols = document.createElement("div")
        newCols.setAttribute("class", "col-md-4")

        newCols.appendChild(newCanvas)

        document.getElementById(container_id).getElementsByClassName("row")[0].appendChild(newCols)

        var cluster_forecast_chart = document.getElementById(canvas_id).getContext('2d')

        new Chart(cluster_forecast_chart, cluster_forecast_config)
    }

}

function generate_rmse(container_id, rmse_data) {
    var existed_row = document.getElementById(container_id).getElementsByClassName("row")

    if (existed_row.length !== 0) {
        document.getElementById(container_id)
            .removeChild(existed_row[0])
    }

    var newRows = document.createElement("div")
    newRows.setAttribute("class", "row")
    newRows.setAttribute("style", "height: 400px")
    // newRows.setAttribute("style", "height: 600px")
    document.getElementById(container_id).appendChild(newRows)

    for (var key in rmse_data) {
        var value = rmse_data[key]
        var labels = ["AR", "MA", "ETS"]
        var data = [value["AR"], value["MA"], value["ETS"]]
        var rmse = {
            labels: labels,
            datasets: [
                {
                    label: "RMSE",
                    backgroundColor: colors[0],
                    data: data
                }
            ]
        }
        var rmse_config = {
            type: "bar",
            data: rmse,
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: "Cluster " + key
                }
            }
        }

        var canvas_id = container_id + key
        var newCanvas = document.createElement("canvas")
        newCanvas.setAttribute("id", canvas_id)

        var newCols = document.createElement("div")
        newCols.setAttribute("class", "col-md-4")

        newCols.appendChild(newCanvas)

        document.getElementById(container_id).getElementsByClassName("row")[0].appendChild(newCols)

        var rmse_chart = document.getElementById(canvas_id).getContext("2d")

        new Chart(rmse_chart, rmse_config)
    }
}