from typing import (Any, ClassVar, Dict, List, Mapping, Optional,
                    Sequence)

from typing_extensions import Self
from viam.components.sensor import Sensor
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import Geometry, ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.utils import SensorReading, ValueTypes
from viam.services.vision import Vision
from viam.components.camera import Camera


class PeopleDetector(Sensor, EasyResource):
    # To enable debug-level logging, either run viam-server with the --debug option,
    # or configure your resource/machine to display debug logs.
    MODEL: ClassVar[Model] = Model(
        ModelFamily("mta", "2025-sensor-detector"), "people-detector"
    )
    
    camera_name: str
    vision_service: str
    confidence_value: float = 0.8

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Sensor component.
        The default implementation sets the name from the `config` parameter and then calls `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both implicit and explicit)

        Returns:
            Self: The resource
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any implicit dependencies based on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Sequence[str]: A list of implicit dependencies
        """
        fields = config.attributes.fields
        deps = []

        if "camera_name" not in fields:
            raise ValueError("missing required camera_name attribute")
        if not fields["camera_name"].HasField("string_value"):
            raise ValueError("camera_name must be a string")
        camera_name = fields["camera_name"].string_value

        if "vision_service" not in fields:
            raise ValueError("missing required vision_service attribute") 
        if not fields["vision_service"].HasField("string_value"):
            raise ValueError("vision_service must be a string")
        vision_service = fields["vision_service"].string_value

        if "confidence_value" in fields:
            if not fields["confidence_value"].HasField("number_value"):
                raise ValueError("confidence_value must be a float")
            confidence_value = fields["confidence_value"].number_value
            if not 0 <= confidence_value <= 1:
                raise ValueError("confidence_value must be between 0 and 1")

        # Add dependencies as strings
        deps.extend([vision_service, camera_name])

        return deps

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both implicit and explicit)
        """
        fields = config.attributes.fields

        self.camera_name = fields["camera_name"].string_value
        self.vision_service = fields["vision_service"].string_value

        # Handle optional confidence_value
        confidence_field = fields.get("confidence_value")
        self.confidence_value = confidence_field.number_value if confidence_field else 0.8

        # Store the vision service instance using Vision
        self.vision_service_instance = dependencies[Vision.get_resource_name(self.vision_service)]
        
        # Store the camera instance
        self.camera_instance = dependencies[Camera.get_resource_name(self.camera_name)]

        return super().reconfigure(config, dependencies)

    async def get_readings(self, *, extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None, **kwargs
    ) -> Mapping[str, SensorReading]:
        
        # Get image from camera
        img = await self.camera_instance.get_image()
        
        # Use the Vision instance to get detections from the image, matching tutorial logic
        detections = await self.vision_service_instance.get_detections(img)
        
        person_detected = any(
            d.class_name.lower() == "person" and d.confidence >= self.confidence_value
            for d in detections)
        
        return {"person_detected": 1 if person_detected else 0}

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        self.logger.error("`do_command` is not implemented")
        raise NotImplementedError()

    async def get_geometries(
        self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None
    ) -> List[Geometry]:
        self.logger.error("`get_geometries` is not implemented")
        raise NotImplementedError()