using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.Rendering;
using static UnityEngine.GraphicsBuffer;

public class CameraScript : MonoBehaviour
{
    public Transform centerTransform;
    public Transform destinationObject;
    [SerializeField] private float sensitivity = 5f;
    [SerializeField] private float zoomSmoothValue = 10f;
    [SerializeField] private float maxOrbitDistance = 100000000f;
    [SerializeField] private float minOrbitDistance = 5f;

    private float freeCamSens = 0.1f;

    private bool isOrbit = true;

    private float currentDistance;
    private float targetDistance;
    private float currentPitch;
    private float currentYaw;

    private float mouseX;
    private float mouseY;

    private float moveSpeed = 10f;
    
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
            toggleLock();
        }

        handleZoom();

        if (isOrbit)
        {
            handleOrbit();
            ApplyCameraTransform();
        }
        else
        {
            HandleFreeLook();
            HandleFreeMovement();
            currentDistance = (maxOrbitDistance + minOrbitDistance) / 2;
        }
    }
    private void toggleLock()
    {
        isOrbit = !isOrbit;
        if (!isOrbit)
        {
            transitionCamera(centerTransform);
            //transform.LookAt(centerTransform);
            //transform.SetLocalPositionAndRotation(centerTransform.position + new Vector3(10, 10, 10), Quaternion.identity);
            //transform.rotation = Quaternion.identity;
        }
        else
        {
            currentDistance = (maxOrbitDistance + minOrbitDistance) / 2;
        }
    }

    private void handleOrbit()
    {
        if (Mouse.current == null) { return; }
        if (!Mouse.current.rightButton.isPressed) { return; }

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
            targetDistance -= scroll * (sensitivity * 2.5f) * Time.deltaTime * 100f;
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

    public void transitionCamera(Transform destinationTransform)
    {
        transform.position = Vector3.MoveTowards(transform.position, destinationTransform.position, 1 * Time.deltaTime);
        centerTransform = destinationTransform;
    }

    private void HandleFreeLook()
    {
        if (Mouse.current?.rightButton.isPressed != true) return;

        Vector2 mouseDelta = Mouse.current.delta.ReadValue();

        currentYaw += mouseDelta.x * freeCamSens;
        currentPitch -= mouseDelta.y * freeCamSens;
        currentPitch = Mathf.Clamp(currentPitch, -89f, 89f);

        transform.rotation = Quaternion.Euler(currentPitch, currentYaw, 0f);
    }

    private void HandleFreeMovement()
    {
        Vector3 moveInput = Vector3.zero;
        var kb = Keyboard.current;

        if (kb.wKey.isPressed) moveInput += transform.forward;
        if (kb.sKey.isPressed) moveInput -= transform.forward;
        if (kb.aKey.isPressed) moveInput -= transform.right;
        if (kb.dKey.isPressed) moveInput += transform.right;
        if (kb.qKey.isPressed) moveInput -= transform.up;
        if (kb.eKey.isPressed) moveInput += transform.up;

        transform.position += moveInput.normalized * moveSpeed * Time.deltaTime;
    }
}
