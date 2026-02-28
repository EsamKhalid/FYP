using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.Rendering;
using static UnityEngine.GraphicsBuffer;

public class CameraScript : MonoBehaviour
{
    [SerializeField] private Transform centerTransform;
    [SerializeField] private float sensitivity = 5f;
    [SerializeField] private float zoomSmoothValue = 10f;
    [SerializeField] private float maxOrbitDistance = 10f;
    [SerializeField] private float minOrbitDistance = 2f;

    private bool isOrbit = false;

    private float currentDistance;
    private float targetDistance;
    private float currentPitch;
    private float currentYaw;

    private float mouseX;
    private float mouseY;
    
    private void Start()
    {
        Vector3 offset = transform.position - centerTransform.position;
        currentDistance = offset.magnitude;
        targetDistance = currentDistance;
        currentYaw = Mathf.Atan2(offset.x, offset.z) * Mathf.Rad2Deg;
        currentPitch = Mathf.Asin(offset.y / currentDistance) * Mathf.Rad2Deg;
    }


    void Update()
    {
        if (Keyboard.current != null && Keyboard.current.cKey.wasPressedThisFrame) 
        {
            isOrbit = !isOrbit;
            if(!isOrbit)
            {
                transform.SetLocalPositionAndRotation(Vector3.zero, Quaternion.identity);
                transform.rotation = Quaternion.identity;
            }
            else
            {
                currentDistance = 5f;
            }
        }

        handleZoom();

        if (isOrbit)
        {
            handleOrbit();
        }

        ApplyCameraTransform();
    }

    private void handleOrbit()
    {
        if (Mouse.current == null) { return; }
        if (!Mouse.current.rightButton.isPressed) { return; }

        Debug.Log("moving");

        transform.LookAt(centerTransform);

        Vector2 mouseDelta = Mouse.current.delta.ReadValue();


        transform.eulerAngles += new Vector3(-mouseDelta.y * sensitivity, mouseDelta.x * sensitivity, 0);
        currentYaw += mouseDelta.x * sensitivity;
        currentPitch -= mouseDelta.y * sensitivity;
        currentPitch = Mathf.Clamp(currentPitch, -80f, 80f);
    }

    private void handleZoom()
    {
        if (Mouse.current == null) { return; }

        float scroll = Mouse.current.scroll.ReadValue().y;

        if (Mathf.Abs(scroll) > 0.01f)
        {
            targetDistance -= scroll * sensitivity * Time.deltaTime * 100f;
            targetDistance = Mathf.Clamp(targetDistance, minOrbitDistance, maxOrbitDistance);
        }

        currentDistance = Mathf.Lerp(currentDistance, targetDistance, zoomSmoothValue * Time.deltaTime);
    }   

    private void ApplyCameraTransform()
    {
        Quaternion rotation = Quaternion.Euler(currentPitch, currentYaw, 0f);
        Vector3 offset = rotation * new Vector3(0f, 0f, -currentDistance);

        transform.position = centerTransform.position + offset;
        transform.LookAt(centerTransform.position);
    }
}
