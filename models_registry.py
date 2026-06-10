from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.ensemble import (
    AdaBoostClassifier,
    BaggingClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

RANDOM_STATE = 42


class LabelEncodeWrapper(BaseEstimator, ClassifierMixin):
    """Wrap estimators that need numeric class labels (e.g. XGBoost, LightGBM)."""

    def __init__(self, estimator):
        self.estimator = estimator
        self.label_encoder_ = LabelEncoder()

    def fit(self, X, y):
        y_encoded = self.label_encoder_.fit_transform(y)
        self.estimator.fit(X, y_encoded)
        self.classes_ = self.label_encoder_.classes_
        return self

    def predict(self, X):
        encoded = self.estimator.predict(X)
        return self.label_encoder_.inverse_transform(encoded)

    def predict_proba(self, X):
        return self.estimator.predict_proba(X)


def _scaled_pipeline(estimator):
    return Pipeline([("scaler", StandardScaler()), ("clf", estimator)])


def get_models():
    models = {
        "decision_tree": DecisionTreeClassifier(
            max_depth=5, random_state=RANDOM_STATE
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100, max_depth=5, random_state=RANDOM_STATE
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=200, max_depth=5, random_state=RANDOM_STATE
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=100, max_depth=3, random_state=RANDOM_STATE
        ),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            max_depth=5, max_iter=200, random_state=RANDOM_STATE
        ),
        "adaboost": AdaBoostClassifier(
            estimator=DecisionTreeClassifier(max_depth=3, random_state=RANDOM_STATE),
            n_estimators=100,
            random_state=RANDOM_STATE,
        ),
        "bagging": BaggingClassifier(
            estimator=DecisionTreeClassifier(max_depth=5, random_state=RANDOM_STATE),
            n_estimators=100,
            random_state=RANDOM_STATE,
        ),
        "logistic_regression": _scaled_pipeline(
            LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
        ),
        "knn": _scaled_pipeline(KNeighborsClassifier(n_neighbors=5)),
        "svm": _scaled_pipeline(
            SVC(kernel="rbf", probability=True, random_state=RANDOM_STATE)
        ),
        "mlp": _scaled_pipeline(
            MLPClassifier(
                hidden_layer_sizes=(64, 32),
                max_iter=1000,
                random_state=RANDOM_STATE,
            )
        ),
    }

    try:
        from xgboost import XGBClassifier

        models["xgboost"] = LabelEncodeWrapper(
            XGBClassifier(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.1,
                eval_metric="mlogloss",
                random_state=RANDOM_STATE,
            )
        )
    except ImportError:
        pass

    try:
        from lightgbm import LGBMClassifier

        models["lightgbm"] = LabelEncodeWrapper(
            LGBMClassifier(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.1,
                random_state=RANDOM_STATE,
                verbose=-1,
            )
        )
    except ImportError:
        pass

    return models
