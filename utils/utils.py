import math

from statsmodels.genmod.families.links import sqrt


def group_cluster_monitor(cluster_monitor):
    monitor_group = {}
    for monitor in cluster_monitor:
        if monitor.to_cluster not in monitor_group:
            monitor_group[monitor.to_cluster] = [{monitor.from_cluster: monitor.change_number}]
        else:
           monitor_group[monitor.to_cluster].append({monitor.from_cluster: monitor.change_number})

    return sort_dict_by_key(monitor_group)


def get_cluster_balance_mean(cluster_result):
    cluster_mean_balance = {}
    for cluster in cluster_result.clusters:
        cluster_mean_balance[cluster.cluster_id] = sum(cluster.cluster_balances[0:len(cluster.cluster_means)]) / len(
            cluster.cluster_means)
    return sort_dict_by_key(cluster_mean_balance)


def get_timepoint_mean_silhouette(cluster_results):
    timepoint_mean_silhouette = {}
    for cluster_result in cluster_results:
        sils = [cluster.cluster_silhouette for cluster in cluster_result.clusters]
        timepoint_mean_silhouette[cluster_result.time_point] = sum(sils) / len(sils)

    return sort_dict_by_key(timepoint_mean_silhouette)


def get_timepoint_number_cluster(cluster_results):
    timepoint_number_cluster = {}
    for cluster_result in cluster_results:
        timepoint_number_cluster[cluster_result.time_point] = len(cluster_result.clusters)

    return sort_dict_by_key(timepoint_number_cluster)


def get_timepoint_clustering_spent_time(cluster_results):
    spent_times = {}
    for cluster_result in cluster_results:
        spent_times[cluster_result.time_point] = cluster_result.spent_time

    return sort_dict_by_key(spent_times)


def sort_dict_by_key(dict):
    sorted_dict = {k: dict[k] for k in sorted(dict)}
    return sorted_dict


def rmse(actual, predict):
    a = 0
    for i in range(len(actual)):
        a = a + (actual[i] - predict[i]) ** 2
    return math.sqrt(a / len(actual))