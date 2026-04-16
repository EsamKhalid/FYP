using UnityEngine;

public class APISpawner : MonoBehaviour
{
    GameObject handlerObject;

    void Awake()
    {
        handlerObject = GameObject.Find("API");
        if (handlerObject == null) 
        {
            handlerObject = new GameObject("API");
            handlerObject.AddComponent<APIHandler>();
        }

    }
}
