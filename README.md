# Module 2025-sensor-detector 

Parses object detection output from a vision service, outputs person_detection as 1 if True and 0 if False based on confidence_value.

### Configuration

People-Detector is tested on the configuation below
- add a camera from the Viam Registry (https://docs.viam.com/operate/reference/components/camera/webcam)
- add a ml model & vision service from the Viam Registry (https://docs.viam.com/tutorials/projects/send-security-photo/)

```json
{
"camera_name": <string>,
"vision_service": <string>
}
```

#### Attributes

The following attributes are available for this model:

| Name          | Type   | Inclusion | Description                |
|---------------|--------|-----------|----------------------------|
| `camera_name` | string  | Required  | Name of camera component |
| `vision_service` | string | Required  | Name of vision service |
| `confidence_value` | float | Optional  | Value between 0 and 1, limitor for person detection |

#### Example Configuration

```json
{
  "camera_name": "FaceTimeHDCameraDisplay",
  "vision_service": "vision-1",
  "confidence_value": 0.8
}
```
