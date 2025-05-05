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

"""
People Detector Implementation
============================

This class implements a sensor component that detects people using computer vision.
It integrates with Viam's vision service and camera components to process images
and detect human presence.

Dependencies:
- Viam Vision Service: For object detection
- Viam Camera Component: For image capture
"""

class PeopleDetector(Sensor, EasyResource):

    """
    A sensor component that detects people using computer vision.
    
    Attributes:
        MODEL: Component model identifier
        camera_name: Name of the camera resource to use
        vision_service: Name of the vision service to use
        confidence_value: Minimum confidence threshold for detections (0-1)
        vision_service_instance: Instance of the vision service
        camera_instance: Instance of the camera component
    """

    MODEL: ClassVar[Model] = Model(
        ModelFamily("mta", "2025-sensor-detector"), "people-detector"
    )
    
    # Declare instance variables with type hints.
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

        """
        Validates the component configuration and returns implicit dependencies.
        
        Validates:
        - Required camera_name and vision_service attributes
        - Optional confidence_value (must be 0-1 if present)
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of implicit dependencies
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Extract the fields from the configuration object.
        # Fields is a mapping of attribute names to their protobuf values.
        fields = config.attributes.fields
        deps = []

        # Define the required configuration fields.
        # These must be present in the config and must be strings.
        required_fields = ["camera_name", "vision_service"]

        # Validates the presence and type of each required field.
        for field in required_fields:
            # Check if the field exists in the configuration.
            if field not in fields:
                raise ValueError(f"missing required {field} attribute")
            # Verify that the field is a string value in the protobuf structure.
            if not fields[field].HasField("string_value"):
                raise ValueError(f"{field} must be a string")
        
        # Validates the presence and type optional fields.
        if "confidence_value" in fields:
            # Ensure the confidence_value is a number in the protobuf structure.
            if not fields["confidence_value"].HasField("number_value"):
                raise ValueError("confidence_value must be a float")
            # Extract the confidence value.
            confidence_value = fields["confidence_value"].number_value
            # Validate that the confidence value is within the acceptable range.
            if not 0 <= confidence_value <= 1:
                raise ValueError("confidence_value must be between 0 and 1")

        # Add the vision_service and camera_name as dependencies.
        deps.extend([
            fields["vision_service"].string_value,
            fields["camera_name"].string_value
        ])
        return deps

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):

        """
        Reconfigures the component with new settings.
        
        Updates:
        - Camera name and instance
        - Vision service name and instance
        - Confidence threshold
        
        Args:
            config: New configuration parameters
            dependencies: Updated resource dependencies
        """

        # Extract the fields from the configuration object.
        fields = config.attributes.fields

        # Set the camera_name from the config.
        self.camera_name = fields["camera_name"].string_value
        
        # Set the vision_service name from the config.
        self.vision_service = fields["vision_service"].string_value

        # If present, use the configured value; otherwise, default to 0.8.
        confidence_field = fields.get("confidence_value")
        self.confidence_value = confidence_field.number_value if confidence_field else 0.8

        # Store the vision service instance.
        # Use Vision.get_resource_name to create a ResourceName object for lookup.
        self.vision_service_instance = dependencies[Vision.get_resource_name(self.vision_service)]
        
        # Store the camera instance.
        # Use Camera.get_resource_name to create a ResourceName object for lookup.
        self.camera_instance = dependencies[Camera.get_resource_name(self.camera_name)]

        return super().reconfigure(config, dependencies)

    async def get_readings(self, *, extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None, **kwargs
    ) -> Mapping[str, SensorReading]:
        
        """
        Gets current sensor readings by processing camera feed for person detection.
        
        Process:
        1. Gets detections from vision service using camera feed
        2. Filters for person detections above confidence threshold
        3. Returns binary sensor reading (1 if person detected, 0 if not)
        
        Args:
            extra: Additional parameters
            timeout: Operation timeout in seconds
            
        Returns:
            Dict with "person_detected" key and binary value
            
        Raises:
            Exception: If detection fails
        """

        try:
            # Log a debug message to indicate the start of detection.
            self.logger.debug("Getting detections from vision service...")
            
            # Use the vision service to get detections directly from the camera.
            # Pass the camera name and a 5-second timeout to ensure the operation doesn't hang.
            detections = await self.vision_service_instance.get_detections_from_camera(
                self.camera_name,
                timeout=5.0)
            
            # Process the detections to check for people.
            # Iterate over each detection and check if it's labeled as "person" with a confidence
            # above the threshold (self.confidence_value).
            person_detected = any(
                d.class_name.lower() == "person" and d.confidence >= self.confidence_value
                for d in detections)
            
            # Log the number of detections found for debugging purposes.
            self.logger.debug(f"Processed image with {len(detections)} detections")
            
            # Return the result as a dictionary with a single key "person_detected".
            # The value is 1 if a person was detected, 0 otherwise.
            return {"person_detected": 1 if person_detected else 0}
        
        except Exception as e:
            # Log any errors that occur during the process.
            self.logger.error(f"Error in get_readings: {str(e)}")
            # Re-raise the exception to propagate the error up the call stack.
            raise

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        
        """
        Not implemented - raises NotImplementedError.
        
        This method is required by the Sensor interface but not used
        by the PeopleDetector implementation.
        """

        self.logger.error("`do_command` is not implemented")
        raise NotImplementedError()

    async def get_geometries(
        self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None
    ) -> List[Geometry]:
        
        """
        Not implemented - raises NotImplementedError.
        
        This method is required by the Sensor interface but not used
        by the PeopleDetector implementation.
        """

        self.logger.error("`get_geometries` is not implemented")
        raise NotImplementedError()
    
    async def cleanup(self):

        """
        Releases resources when component is stopped.
        
        Cleans up:
        - Camera instance reference
        - Vision service instance reference
        """

        # Clear the camera instance reference to release the resource.
        self.camera_instance = None
        # Clear the vision service instance reference to release the resource.
        self.vision_service_instance = None
        # Call the parent class's cleanup method to perform any additional cleanup.
        await super().cleanup()