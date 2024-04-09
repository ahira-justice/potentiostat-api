from app.common.data.models import Experiment
from app.modules.experiment.experiment_dtos import ExperimentResponse


def experiment_to_experiment_response(experiment: Experiment) -> ExperimentResponse:
    result = ExperimentResponse(
        id=experiment.id,
        experiment_status=experiment.experiment_status,
        start_voltage=experiment.start_voltage,
        end_voltage=experiment.end_voltage,
        voltage_step=experiment.voltage_step,
        username=experiment.user.username,
        client_id=experiment.client.identifier
    )

    return result
