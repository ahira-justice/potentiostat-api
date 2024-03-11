from app.common.data.models import Experiment
from app.modules.experiment.experiment_dtos import ExperimentResponse


def experiment_to_experiment_response(experiment: Experiment) -> ExperimentResponse:
    result = ExperimentResponse(
        id=experiment.id,
        experiment_status=experiment.experiment_status,
        username=experiment.user.username,
        client_id=experiment.client.identifier
    )

    return result
