from flask import Flask, render_template, request, json

from database.db import initialize_db
from database.models import ClusterBalancesAtTimePoint
from datastore.service import cluster_balances_to_cluster_at_time_point
from utils.utils import group_cluster_monitor, get_cluster_balance_mean, get_timepoint_mean_silhouette, \
    get_timepoint_number_cluster, get_timepoint_clustering_spent_time, sort_dict_by_key, rmse

from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.arima_model import ARMA
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

from random import random

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost/clustering'
}
initialize_db(app)

algorithm_mapping = {
    'algorithm1': {
        'clustering_type': 'random',
        'new_mean_method': 'furthest_in_cluster',
    },
    'algorithm2': {
        'clustering_type': 'history',
        'new_mean_method': 'random',
    },
    'algorithm3': {
        'clustering_type': 'history',
        'new_mean_method': 'furthest',
    },
    'algorithm4': {
        'clustering_type': 'history',
        'new_mean_method': 'furthest_in_cluster',
    }
}


@app.route('/')
def get_clustering_result():
    cluster_results_history = ClusterBalancesAtTimePoint.objects(clustering_type="history", new_mean_method="furthest")
    cluster_results_random = ClusterBalancesAtTimePoint.objects(clustering_type="random",
                                                                new_mean_method="random")
    cluster_results_sil_history = get_timepoint_mean_silhouette(cluster_results_history)
    cluster_results_number_cluster_history = get_timepoint_number_cluster(cluster_results_history)
    cluster_results_spent_time_history = get_timepoint_clustering_spent_time(cluster_results_history)

    cluster_results_sil_random = get_timepoint_mean_silhouette(cluster_results_random)
    cluster_results_number_cluster_random = get_timepoint_number_cluster(cluster_results_random)
    cluster_results_spent_time_random = get_timepoint_clustering_spent_time(cluster_results_random)

    return render_template("base.html",
                           cluster_results_sil_history=cluster_results_sil_history,
                           cluster_resultes_number_cluster_history=cluster_results_number_cluster_history,
                           cluster_results_spent_time_history=cluster_results_spent_time_history,
                           cluster_results_sil_random=cluster_results_sil_random,
                           cluster_results_number_cluster_random=cluster_results_number_cluster_random,
                           cluster_results_spent_time_random=cluster_results_spent_time_random)


@app.route('/<month>')
def get_specific_clustering_result(month):
    algorithm = request.args['algorithm']
    clustering_type = algorithm_mapping[algorithm]['clustering_type']
    new_mean_method = algorithm_mapping[algorithm]['new_mean_method']

    return json.dumps(
        ClusterBalancesAtTimePoint.objects(clustering_type=clustering_type, new_mean_method=new_mean_method,
                                           time_point=int(month))[0])


@app.route('/cluster_balance/<month>')
def get_cluster_balance(month):
    algorithm = request.args['algorithm']
    clustering_type = algorithm_mapping[algorithm]['clustering_type']
    new_mean_method = algorithm_mapping[algorithm]['new_mean_method']

    result = ClusterBalancesAtTimePoint.objects(clustering_type=clustering_type, new_mean_method=new_mean_method,
                                                time_point=int(month))[0]

    cluster_mean_balance = get_cluster_balance_mean(result)

    return json.dumps(cluster_mean_balance)


@app.route('/cluster_monitor/<month>')
def get_cluster_monitor(month):
    algorithm = request.args['algorithm']
    clustering_type = algorithm_mapping[algorithm]['clustering_type']
    new_mean_method = algorithm_mapping[algorithm]['new_mean_method']

    result = ClusterBalancesAtTimePoint.objects(clustering_type=clustering_type, new_mean_method=new_mean_method,
                                                time_point=int(month))[0]

    cluster_monitors = group_cluster_monitor(result.cluster_monitors)

    return json.dumps(cluster_monitors)


@app.route('/clustering_analytic/<month>')
def clustering_analytic(month):
    algorithms = request.args['algorithms'].split(',')
    compare_dict = {}
    for algorithm in algorithms:
        clustering_type = algorithm_mapping[algorithm]['clustering_type']
        new_mean_method = algorithm_mapping[algorithm]['new_mean_method']
        result = ClusterBalancesAtTimePoint.objects(clustering_type=clustering_type, new_mean_method=new_mean_method,
                                                    time_point=int(month))[0]
        sils = [x.cluster_silhouette for x in result.clusters]
        compare_dict[algorithm] = {
            'spent_time': result.spent_time,
            'number_clusters': len(result.clusters),
            'mean_silhouette': sum(sils) / len(sils)
        }

    return compare_dict


@app.route("/forecast/<month>")
def forecast(month):
    algorithm = request.args['algorithm']
    forecast_method = request.args['forecast']

    clustering_type = algorithm_mapping[algorithm]['clustering_type']
    new_mean_method = algorithm_mapping[algorithm]['new_mean_method']

    result = ClusterBalancesAtTimePoint.objects(clustering_type=clustering_type, new_mean_method=new_mean_method,
                                                time_point=int(month))[0]
    dict = {}
    for cluster in result.clusters:
        if forecast == 'AR':
            dict[cluster.cluster_id] = {
                'forecast': cluster.cluster_forecast_ar,
                'history': cluster.cluster_balances,
                'actual': cluster.cluster_balances_actual
            }
        elif forecast_method == 'MA':
            dict[cluster.cluster_id] = {
                'forecast': cluster.cluster_forecast_ma,
                'history': cluster.cluster_balances,
                'actual': cluster.cluster_balances_actual
            }
        else:
            dict[cluster.cluster_id] = {
                'forecast': cluster.cluster_forecast_ses,
                'history': cluster.cluster_balances,
                'actual': cluster.cluster_balances_actual
            }

    return json.dumps(sort_dict_by_key(dict))


@app.route("/forecast_all/<month>")
def forecast_all(month):
    algorithm = request.args['algorithm']

    clustering_type = algorithm_mapping[algorithm]['clustering_type']
    new_mean_method = algorithm_mapping[algorithm]['new_mean_method']

    result = ClusterBalancesAtTimePoint.objects(clustering_type=clustering_type, new_mean_method=new_mean_method,
                                                time_point=int(month))[0]
    dict = {}
    for cluster in result.clusters:
        dict[cluster.cluster_id] = {
            'ar': cluster.cluster_forecast_ar,
            'ma': cluster.cluster_forecast_ma,
            'ets': cluster.cluster_forecast_ses,
            'history': cluster.cluster_balances,
            'actual': cluster.cluster_balances_actual
        }

    return json.dumps(sort_dict_by_key(dict))


@app.route('/forecast_analytic/<month>')
def forecast_analytic(month):
    algorithm = request.args['algorithm']
    clustering_type = algorithm_mapping[algorithm]['clustering_type']
    new_mean_method = algorithm_mapping[algorithm]['new_mean_method']
    result = ClusterBalancesAtTimePoint.objects(clustering_type=clustering_type, new_mean_method=new_mean_method,
                                                time_point=int(month))[0]

    dict = {}
    for cluster in result.clusters:
        dict[cluster.cluster_id] = {
            "AR": rmse(cluster.cluster_balances_actual, cluster.cluster_forecast_ar),
            "MA": rmse(cluster.cluster_balances_actual, cluster.cluster_forecast_ma),
            "ETS": rmse(cluster.cluster_balances_actual, cluster.cluster_forecast_ses)
        }

    return json.dumps(dict)


if __name__ == '__main__':
    app.run()
