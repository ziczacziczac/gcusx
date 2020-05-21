# # -*- coding: utf-8 -*-
# """
# Created on Thu Apr  9 21:31:30 2020
#
# @author: ADMIN
# """
#
# # Imports the Google Cloud client library
from flask import Flask
from gcloud import datastore
import os

from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.arima_model import ARMA
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, ExponentialSmoothing

from database.db import initialize_db
from database.models import ClusterBalancesAtTimePoint, Cluster, ClusterMonitor, ClusterSample

HISTORY_CLUSTERED_RESULT = 'history_clustered_result'
HISTORY_CLUSTER_BALANCES = 'history_cluster_balances'
HISTORY_CLUSTER_MONITOR = 'history_cluster_monitor'
HISTORY_CLUSTER_STATISTIC = 'history_cluster_statistic'
HISTORY_CLUSTER_DISTANCE = 'history_cluster_distance'
HISTORY_CLUSTER_MEMBER_COUNT = 'history_cluster_member_count'
HISTORY_CLUSTER_SAMPLES = 'history_cluster_samples'
HISTORY_CLUSTER_MEMBERS = 'history_cluster_members'

RANDOM_CLUSTERED_RESULT = 'random_clustered_result'
RANDOM_CLUSTER_BALANCES = 'random_cluster_balances'
RANDOM_CLUSTER_MONITOR = 'random_cluster_monitor'
RANDOM_CLUSTER_STATISTIC = 'random_cluster_statistic'
RANDOM_CLUSTER_DISTANCE = 'random_cluster_distance'
RANDOM_CLUSTER_MEMBER_COUNT = 'random_cluster_member_count'
RANDOM_CLUSTER_SAMPLES = 'random_cluster_samples'
RANDOM_CLUSTER_MEMBERS = 'random_cluster_members'

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost/clustering'
}

def clear_datastore(client, smt):

    while True:
        query = client.query(kind = smt)
        count = 0
        query_iter = query.fetch()
        keys = []
        try:
            for entity in query_iter:
                print(str(count) + "\n")
                count = count + 1
                keys.append(client.key(smt, entity.key.id))
                if count == 200:
                    client.delete_multi(keys=keys)
                    count = -1
                    break
            if count != -1 and count != 0:
                client.delete_multi(keys=keys)
            elif count == 0: break
        except StopIteration:
            break


def clustered_result_to_cluster_at_time_point(entity, clustering_type):
    means = []
    for i in range(int(entity['balance_length'])):
        means.append(entity['mean' + str(i)])
    cluster = Cluster(cluster_id=entity['cluster_id'], cluster_silhouette=entity['silhouette'], cluster_means=means)
    result = ClusterBalancesAtTimePoint(time_point=entity['time_point'],
                                        balance_length=entity['balance_length'],
                                        new_mean_method=entity['new_mean_method'],
                                        spent_time=entity['spent_time'],
                                        clusters=[cluster],
                                        clustering_type=clustering_type)
    return result

def cluster_balances_to_cluster_at_time_point(entity, clustering_type):
    total = []
    for i in range(int(entity['balance_length']) + 3):
        total.append(round(entity['total' + str(i)], 2))
    cluster = Cluster(cluster_id=entity['cluster_id'], cluster_balances=total)
    result = ClusterBalancesAtTimePoint(time_point=entity['time_point'],
                                        balance_length=entity['balance_length'],
                                        new_mean_method=entity['new_mean_method'],
                                        clusters=[cluster],
                                        clustering_type=clustering_type)
    return result


def cluster_statistic_to_cluster_at_time_point(entity, clustering_type):
    cluster = Cluster(cluster_id=entity['cluster_id'], cluster_mean=round(entity['mean'], 2), cluster_variance=round(entity['variance'], 2))
    result = ClusterBalancesAtTimePoint(time_point=entity['time_point'],
                                        balance_length=entity['balance_length'],
                                        new_mean_method=entity['new_mean_method'],
                                        clusters=[cluster],
                                        clustering_type=clustering_type)
    return result


def cluster_mean_distance_to_cluster_at_time_point(entity, clustering_type):
    cluster = Cluster(cluster_id=entity['cluster_id'], cluster_mean_distance=entity['mean_distance'])
    result = ClusterBalancesAtTimePoint(time_point=entity['time_point'],
                                        balance_length=entity['balance_length'],
                                        new_mean_method=entity['new_mean_method'],
                                        clusters=[cluster],
                                        clustering_type=clustering_type)
    return result


def cluster_samples_to_cluster_at_time_point(entity, clustering_type):
    samples = []
    for i in range(int(entity['balance_length'])):
        samples.append(entity['mean' + str(i)])
    pca2 = [entity['p20'], entity['p21']]
    pca3 = [entity['p30'], entity['p31'], entity['p32']]

    cluster_sample = ClusterSample(dist=entity['dist'], samples=samples, pca2=pca2, pca3=pca3)
    cluster = Cluster(cluster_id=entity['cluster_id'], cluster_samples=[cluster_sample])
    result = ClusterBalancesAtTimePoint(time_point=entity['time_point'],
                                        balance_length=entity['balance_length'],
                                        new_mean_method=entity['new_mean_method'],
                                        clusters=[cluster],
                                        clustering_type=clustering_type)
    return result


def cluster_members_to_cluster_at_time_point(entity, clustering_type):
    cluster = Cluster(cluster_id=entity['cluster_id'], cluster_members=entity['cluster_members'])
    result = ClusterBalancesAtTimePoint(time_point=entity['time_point'],
                                        balance_length=entity['balance_length'],
                                        new_mean_method=entity['new_mean_method'],
                                        clusters=[cluster],
                                        clustering_type=clustering_type)
    return result


def cluster_monitor_to_cluster_at_time_point(entity, clustering_type):
    cluster_monitor = ClusterMonitor(from_cluster=entity['cluster_previous'], to_cluster=entity['cluster_current'],
                                     change_proportion=entity['change_proportion'], change_number=entity['number_cus'])
    result = ClusterBalancesAtTimePoint(time_point=entity['time_point'],
                                        balance_length=entity['balance_length'],
                                        new_mean_method=entity['new_mean_method'],
                                        cluster_monitors=[cluster_monitor],
                                        clustering_type=clustering_type)
    return result


def cluster_count_to_cluster_at_time_point(entity, clustering_type):
    cluster_count = Cluster(cluster_id=entity['cluster_id'], cluster_count=entity['cluster_count'])
    result = ClusterBalancesAtTimePoint(time_point=entity['time_point'],
                                        balance_length=entity['balance_length'],
                                        new_mean_method=entity['new_mean_method'],
                                        clusters=[cluster_count],
                                        clustering_type=clustering_type)
    return result


def clone_clustered_result(client, kind):
    d = {}
    query_iter = client.query(kind=kind).fetch()
    result = None
    for entity in query_iter:
        if 'history' in kind:
            result = clustered_result_to_cluster_at_time_point(entity, 'history')
        else :
            result = clustered_result_to_cluster_at_time_point(entity, 'random')
        key = str(result.time_point) + "_" + str(result.balance_length) + "_" + result.new_mean_method
        if key not in d:
            d[key] = result
        else :
            old_result = d[key]
            old_result.clusters.append(result.clusters[0])
    return d


def clone_cluster_balances(client, kind):
    d = {}
    query_iter = client.query(kind=kind).fetch()
    result = None
    for entity in query_iter:
        if 'history' in kind:
            result = cluster_balances_to_cluster_at_time_point(entity, 'history')
        else:
            result = cluster_balances_to_cluster_at_time_point(entity, 'random')

        key = str(result.time_point) + "_" + str(result.balance_length) + "_" + result.new_mean_method
        if key not in d:
            d[key] = result
        else:
            old_result = d[key]
            old_result.clusters.append(result.clusters[0])
    return d


def clone_cluster_monitor(client, kind):
    d = {}
    query_iter = client.query(kind=kind).fetch()
    result = None
    for entity in query_iter:
        if 'history' in kind:
            result = cluster_monitor_to_cluster_at_time_point(entity, 'history')
        else:
            result = cluster_monitor_to_cluster_at_time_point(entity, 'random')

        key = str(result.time_point) + "_" + str(result.balance_length) + "_" + result.new_mean_method
        if key not in d:
            d[key] = result
        else:
            old_result = d[key]
            old_result.cluster_monitors.append(result.cluster_monitors[0])
    return d

def clone_cluster_count(client, kind):
    d = {}
    query_iter = client.query(kind=kind).fetch()
    result = None
    for entity in query_iter:
        if 'history' in kind:
            result = cluster_count_to_cluster_at_time_point(entity, 'history')
        else:
            result = cluster_count_to_cluster_at_time_point(entity, 'random')

        key = str(result.time_point) + "_" + str(result.balance_length) + "_" + result.new_mean_method
        if key not in d:
            d[key] = result
        else:
            old_result = d[key]
            old_result.clusters.append(result.clusters[0])
    return d


def clone_cluster_statistic(client, kind):
    d = {}
    query_iter = client.query(kind=kind).fetch()
    result = None
    for entity in query_iter:
        if 'history' in kind:
            result = cluster_statistic_to_cluster_at_time_point(entity, 'history')
        else:
            result = cluster_statistic_to_cluster_at_time_point(entity, 'random')

        key = str(result.time_point) + "_" + str(result.balance_length) + "_" + result.new_mean_method
        if key not in d:
            d[key] = result
        else:
            old_result = d[key]
            old_result.clusters.append(result.clusters[0])
    return d


def clone_cluster_mean_distance(client, kind):
    d = {}
    query_iter = client.query(kind=kind).fetch()
    result = None
    for entity in query_iter:
        if 'history' in kind:
            result = cluster_mean_distance_to_cluster_at_time_point(entity, 'history')
        else:
            result = cluster_mean_distance_to_cluster_at_time_point(entity, 'random')

        key = str(result.time_point) + "_" + str(result.balance_length) + "_" + result.new_mean_method
        if key not in d:
            d[key] = result
        else:
            old_result = d[key]
            old_result.clusters.append(result.clusters[0])
    return d


def clone_cluster_samples(client, kind):
    d = {}
    query_iter = client.query(kind=kind).fetch()
    result = None
    for entity in query_iter:
        if 'history' in kind:
            result = cluster_samples_to_cluster_at_time_point(entity, 'history')
        else:
            result = cluster_samples_to_cluster_at_time_point(entity, 'random')

        key = str(result.time_point) + "_" + str(result.balance_length) + "_" + result.new_mean_method
        if key not in d:
            d[key] = result
        else:
            old_result = d[key]
            old_result.clusters.append(result.clusters[0])
    return d


def clone_cluster_members(client, kind):
    d = {}
    query_iter = client.query(kind=kind).fetch()
    result = None
    for entity in query_iter:
        if 'history' in kind:
            result = cluster_members_to_cluster_at_time_point(entity, 'history')
        else:
            result = cluster_members_to_cluster_at_time_point(entity, 'random')

        key = str(result.time_point) + "_" + str(result.balance_length) + "_" + result.new_mean_method
        if key not in d:
            d[key] = result
        else:
            old_result = d[key]
            old_result.clusters.append(result.clusters[0])
    return d


def ndarray2array(ndarray):
    arr = []
    for elem in ndarray:
        arr.append(elem)
    return arr


def forecast(balances, method):
    if method == 'AR':
        model = AutoReg(balances, lags=1)
        model_fit = model.fit()
        return ndarray2array(model_fit.predict(len(balances), len(balances) + 2))
    elif method == 'MA':
        model = ARMA(balances, order=(0, 1))
        model_fit = model.fit(disp=False)
        return ndarray2array(model_fit.predict(len(balances), len(balances) + 2))
    else:
        model = ExponentialSmoothing(balances)
        model_fit = model.fit()
        return ndarray2array(model_fit.predict(len(balances), len(balances) + 2))


def merge_cluster_info(result, balances, statistic, count, mean_distance, samples, members):
    for cluster in result:
        cluster_balances = [b for b in balances if cluster.cluster_id == b.cluster_id]
        cluster_statistic = [s for s in statistic if cluster.cluster_id == s.cluster_id]
        cluster_count = [c for c in count if cluster.cluster_id == c.cluster_id]
        cluster_mean_distance = [d for d in mean_distance if cluster.cluster_id == d.cluster_id]
        cluster_samples = [s.cluster_samples[0] for s in samples if cluster.cluster_id == s.cluster_id]
        cluster_members = [m for m in members if cluster.cluster_id == m.cluster_id]

        cluster.cluster_balances = cluster_balances[0].cluster_balances[0:12]
        cluster.cluster_forecast_ar = forecast(cluster.cluster_balances, 'AR')
        cluster.cluster_forecast_ma = forecast(cluster.cluster_balances, 'MA')
        cluster.cluster_forecast_ses = forecast(cluster.cluster_balances, 'SES')
        cluster.cluster_balances_actual = cluster_balances[0].cluster_balances[12:15]
        cluster.cluster_mean = cluster_statistic[0].cluster_mean
        cluster.cluster_variance = cluster_statistic[0].cluster_variance
        cluster.cluster_count = cluster_count[0].cluster_count
        cluster.mean_distance = cluster_mean_distance[0].cluster_mean_distance
        cluster.cluster_samples = cluster_samples
        cluster.cluster_members = cluster_members[0].cluster_members




def merge(dict_result, dict_balances, dict_statistic, dict_monitor, dict_count, dict_mean_distance, dict_sample, dict_members):
    for key in dict_result:
        result = dict_result[key]
        balances = dict_balances[key]
        statistic = dict_statistic[key]
        count = dict_count[key]
        mean_distance = dict_mean_distance[key]
        samples = dict_sample[key]
        members = dict_members[key]

        if key in dict_monitor:
            monitor = dict_monitor[key]
            result.cluster_monitors = monitor.cluster_monitors
        merge_cluster_info(result.clusters, balances.clusters, statistic.clusters,
                           count.clusters, mean_distance.clusters, samples.clusters, members.clusters)
        result.clusters.sort(key=lambda x: x.cluster_id, reverse=False)
        for cluster in result.clusters:
            cluster.cluster_samples.sort(key=lambda x: x.dist, reverse=False)

    return dict_result


def clone_history_result(client):
    dict_result = clone_clustered_result(client, HISTORY_CLUSTERED_RESULT)
    dict_balances = clone_cluster_balances(client, HISTORY_CLUSTER_BALANCES)
    dict_statistic = clone_cluster_statistic(client, HISTORY_CLUSTER_STATISTIC)
    dict_monitor = clone_cluster_monitor(client, HISTORY_CLUSTER_MONITOR)
    dict_count = clone_cluster_count(client, HISTORY_CLUSTER_MEMBER_COUNT)
    dict_mean_distance = clone_cluster_mean_distance(client, HISTORY_CLUSTER_DISTANCE)
    dict_samples = clone_cluster_samples(client, HISTORY_CLUSTER_SAMPLES)
    dict_members = clone_cluster_members(client, HISTORY_CLUSTER_MEMBERS)

    return merge(dict_result, dict_balances, dict_statistic, dict_monitor, dict_count, dict_mean_distance, dict_samples, dict_members)
    

def clone_random_result(client):
    dict_result = clone_clustered_result(client, RANDOM_CLUSTERED_RESULT)
    dict_balances = clone_cluster_balances(client, RANDOM_CLUSTER_BALANCES)
    dict_statistic = clone_cluster_statistic(client, RANDOM_CLUSTER_STATISTIC)
    dict_monitor = clone_cluster_monitor(client, RANDOM_CLUSTER_MONITOR)
    dict_count = clone_cluster_count(client, RANDOM_CLUSTER_MEMBER_COUNT)
    dict_mean_distance = clone_cluster_mean_distance(client, RANDOM_CLUSTER_DISTANCE)
    dict_samples = clone_cluster_samples(client, RANDOM_CLUSTER_SAMPLES)
    dict_members = clone_cluster_members(client, RANDOM_CLUSTER_MEMBERS)

    return merge(dict_result, dict_balances, dict_statistic, dict_monitor, dict_count, dict_mean_distance, dict_samples, dict_members)

def save(dict_result):
    for time_point in dict_result:
        tmp_result = dict_result[time_point]
        # dict_result[time_point].save()
        ClusterBalancesAtTimePoint(time_point=tmp_result.time_point,
                                   clustering_type=tmp_result.clustering_type,
                                   spent_time=tmp_result.spent_time,
                                   clusters=tmp_result.clusters,
                                   cluster_monitors=tmp_result.cluster_monitors,
                                   balance_length=tmp_result.balance_length,
                                   new_mean_method=tmp_result.new_mean_method).save()


def clone_datastore(client):
    dict_history = clone_history_result(client)
    save(dict_history)

    dict_random = clone_random_result(client)
    save(dict_random)
    return None


def clear_all_datastore(client):
    clear_datastore(client, HISTORY_CLUSTER_MONITOR)
    clear_datastore(client, HISTORY_CLUSTER_STATISTIC)
    clear_datastore(client, HISTORY_CLUSTERED_RESULT)
    clear_datastore(client, HISTORY_CLUSTER_BALANCES)
    clear_datastore(client, HISTORY_CLUSTER_DISTANCE)
    clear_datastore(client, HISTORY_CLUSTER_SAMPLES)
    clear_datastore(client, HISTORY_CLUSTER_MEMBER_COUNT)
    clear_datastore(client, HISTORY_CLUSTER_MEMBERS)

    clear_datastore(client, RANDOM_CLUSTER_MONITOR)
    clear_datastore(client, RANDOM_CLUSTER_STATISTIC)
    clear_datastore(client, RANDOM_CLUSTERED_RESULT)
    clear_datastore(client, RANDOM_CLUSTER_BALANCES)
    clear_datastore(client, RANDOM_CLUSTER_DISTANCE)
    clear_datastore(client, RANDOM_CLUSTER_SAMPLES)
    clear_datastore(client, RANDOM_CLUSTER_MEMBER_COUNT)
    clear_datastore(client, RANDOM_CLUSTER_MEMBERS)


def clear_all_database():
    ClusterBalancesAtTimePoint.delete()

if __name__ == '__main__':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/ADMIN/Downloads/real-time-clustering-1427b0be1a2c.json"
    initialize_db(app)
    # app.run()
    datastore_client = datastore.Client()
    clone_datastore(datastore_client)
    # clear_all_datastore(datastore_client)

# # clear_datastore(datastore_client, "clustered_result")
#
# import os
#
# from gcloud import datastore
#
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/ADMIN/Downloads/real-time-clustering-1427b0be1a2c.json"
# client = datastore.Client()
#
# query = client.query(kind='cluster_balances')
# # query.add_filter('time_point', '=', '0')
# query_iter = query.fetch()
# for entity in query_iter:
#     print(entity["time_point"])

