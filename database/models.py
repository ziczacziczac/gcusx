from .db import db


class ClusterSample(db.EmbeddedDocument):
    dist = db.FloatField(required=True, unique=False)
    pca2 = db.ListField(db.FloatField(), unique=False)
    pca3 = db.ListField(db.FloatField(), unique=False)
    samples = db.ListField(db.FloatField(), unique=False)


class Cluster(db.EmbeddedDocument):
    cluster_id = db.IntField(required=True, unique=False)
    cluster_members = db.StringField(required=False, unique=False)
    cluster_balances = db.ListField(db.FloatField(), unique=False)
    cluster_forecast_ar = db.ListField(db.FloatField(), unique=False)
    cluster_forecast_ma = db.ListField(db.FloatField(), unique=False)
    cluster_forecast_ses = db.ListField(db.FloatField(), unique=False)
    cluster_balances_actual = db.ListField(db.FloatField(), unique=False)
    cluster_mean = db.FloatField(required=False, unique=False)
    cluster_variance = db.FloatField(required=False, unique=False)
    cluster_silhouette = db.FloatField(required=False, unique=False)
    cluster_means = db.ListField(db.FloatField(), unique=False)
    cluster_count = db.IntField(required=False, unique=False)
    cluster_mean_distance = db.FloatField(required=False, unique=False)
    cluster_samples = db.EmbeddedDocumentListField(ClusterSample)


class ClusterMonitor(db.EmbeddedDocument):
    from_cluster = db.IntField(required=True, unique=False)
    to_cluster = db.IntField(required=True, unique=False)
    change_proportion = db.FloatField(required=True, unique=False)
    change_number = db.IntField(required=True, unique=False)


class ClusterBalancesAtTimePoint(db.Document):
    time_point = db.IntField(required=True, unique=False)
    clustering_type = db.StringField(required=True, unique=False)
    spent_time = db.IntField(required=True, unique=False)
    clusters = db.EmbeddedDocumentListField(Cluster)
    cluster_monitors = db.EmbeddedDocumentListField(ClusterMonitor)
    balance_length = db.IntField(required=True, unique=False)
    new_mean_method = db.StringField(required=True, unique=False)
