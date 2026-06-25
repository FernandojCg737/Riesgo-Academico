from sklearn.model_selection import GroupShuffleSplit, GroupKFold, cross_val_score
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix, roc_auc_score
from sqlalchemy import delete, select

from src.infrastructure.config import settings
from src.infrastructure.repositories.academic_repository import AcademicRepository
from src.infrastructure.repositories.model_repository import ModelRepository
from src.infrastructure.db.session import SessionLocal
from src.infrastructure.db.models.trained_model_model import ModeloEntrenado
from src.infrastructure.db.models.model_evaluation_model import EvaluacionModelo
from src.application.services.preprocessing_service import PreprocessingService

NOMBRES_MODELOS = [
    "logistic_regression", "decision_tree", "random_forest",
    "logistic_regression_alt", "decision_tree_alt", "random_forest_alt"
]


class EvaluateModels:
    def __init__(
        self,
        dataset_id: int,
        academic_repo: AcademicRepository = None,
        model_repo: ModelRepository = None,
        preproc_service: PreprocessingService = None,
    ):
        self.dataset_id = dataset_id
        self.academic_repo = academic_repo or AcademicRepository()
        self.model_repo = model_repo or ModelRepository(dataset_id=dataset_id)
        self.preproc_service = preproc_service or PreprocessingService()

    def ejecutar(self) -> dict:
        print(f"Ejecutando caso de uso: Evaluar Modelos (dataset_id={self.dataset_id})...")

        df = self.academic_repo.cargar_modelo_dataset(self.dataset_id)
        X, y, groups = self.preproc_service.separar_predictores_y_objetivo(df)

        gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=settings.RANDOM_STATE)
        train_idx, test_idx = next(gss.split(df, y, groups=groups))

        X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        groups_train = groups.iloc[train_idx]
        X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]

        resultados = {}

        with SessionLocal() as session:
            for nombre in NOMBRES_MODELOS:
                print(f"  Evaluando modelo: {nombre}...")
                pipeline = self.model_repo.cargar_modelo(nombre)

                y_pred = pipeline.predict(X_test)
                y_prob = pipeline.predict_proba(X_test)[:, 1] if hasattr(pipeline, "predict_proba") else None

                accuracy_test = accuracy_score(y_test, y_pred)
                precision_test, recall_test, f1_test, _ = precision_recall_fscore_support(y_test, y_pred, average="binary", pos_label=1)
                roc_auc_test = roc_auc_score(y_test, y_prob) if y_prob is not None else 0.5
                cm_test = confusion_matrix(y_test, y_pred)
                report_test = classification_report(y_test, y_pred, target_names=["Sin Riesgo", "Riesgo"])

                falsos_negativos = int(cm_test[1][0])

                y_pred_train = pipeline.predict(X_train)
                y_prob_train = pipeline.predict_proba(X_train)[:, 1] if hasattr(pipeline, "predict_proba") else None

                accuracy_train = accuracy_score(y_train, y_pred_train)
                _, recall_train, f1_train, _ = precision_recall_fscore_support(y_train, y_pred_train, average="binary", pos_label=1)
                roc_auc_train = roc_auc_score(y_train, y_prob_train) if y_prob_train is not None else 0.5

                gkf = GroupKFold(n_splits=5)
                cv_scores = cross_val_score(pipeline, X_train, y_train, groups=groups_train, cv=gkf, scoring="recall")
                cv_mean = cv_scores.mean()
                cv_std = cv_scores.std()

                resultados[nombre] = {
                    "modelo": nombre,
                    "accuracy": accuracy_test,
                    "precision_clase_1": precision_test,
                    "recall_clase_1": recall_test,
                    "f1_clase_1": f1_test,
                    "roc_auc_test": roc_auc_test,
                    "matriz_confusion": cm_test,
                    "classification_report": report_test,
                    "falsos_negativos": falsos_negativos,
                    "accuracy_train": accuracy_train,
                    "recall_train": recall_train,
                    "f1_train": f1_train,
                    "roc_auc_train": roc_auc_train,
                    "cv_recall_mean": cv_mean,
                    "cv_recall_std": cv_std,
                }

                modelo_id = session.execute(
                    select(ModeloEntrenado.id).where(
                        ModeloEntrenado.nombre_interno == nombre,
                        ModeloEntrenado.dataset_id == self.dataset_id,
                    )
                ).scalar_one()

                session.execute(delete(EvaluacionModelo).where(EvaluacionModelo.modelo_id == modelo_id))
                session.add(EvaluacionModelo(
                    modelo_id=modelo_id,
                    accuracy_test=float(accuracy_test),
                    accuracy_train=float(accuracy_train),
                    precision_clase_1=float(precision_test),
                    recall_clase_1=float(recall_test),
                    recall_train=float(recall_train),
                    f1_clase_1=float(f1_test),
                    f1_train=float(f1_train),
                    roc_auc_test=float(roc_auc_test),
                    roc_auc_train=float(roc_auc_train),
                    falsos_negativos=falsos_negativos,
                    matriz_confusion=cm_test.tolist(),
                    cv_recall_mean=float(cv_mean),
                    cv_recall_std=float(cv_std),
                    classification_report=report_test,
                ))
            session.commit()

        print("Evaluación de todos los modelos finalizada con éxito.")
        return resultados
