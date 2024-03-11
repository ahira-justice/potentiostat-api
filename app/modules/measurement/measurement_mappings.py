from app.common.data.models import Measurement
from app.modules.measurement.measurement_dtos import MeasurementResponse


def measurement_to_measurement_response(measurement: Measurement) -> MeasurementResponse:
    result = MeasurementResponse(
        id=measurement.id,
        timestamp=measurement.timestamp,
        voltage=measurement.voltage,
        current=measurement.current,
        experiment_id=measurement.experiment.id
    )

    return result
