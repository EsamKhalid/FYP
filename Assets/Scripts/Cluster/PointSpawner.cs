using UnityEngine;
using UnityEngine.Rendering.UI;

public class PointSpawner : MonoBehaviour
{
    private GameObject handlerObject;
    private APIHandler handler;
    private APIResponse response;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        handlerObject = GameObject.Find("API");
        handler = handlerObject.GetComponent<APIHandler>();
        response = handler.data;
        Debug.Log(response.puuid);
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
