using UnityEngine;
using UnityEngine.Rendering.UI;

public class PointSpawner : MonoBehaviour
{
    private GameObject handlerObject;
    private APIHandler handler;
    private APIResponse response;
    [SerializeField] private GameObject spherePrefab;

    void Start()
    {
        handlerObject = GameObject.Find("API");
        handler = handlerObject.GetComponent<APIHandler>();
        response = handler.data;
        PlotPoints(response);
    }

    void PlotPoints(APIResponse data)
    {
        foreach (MatchPoint point in data.points) 
        {
            SpawnMatchPoint(point);
        }
    }

    void SpawnMatchPoint(MatchPoint match)
    {
        Vector3 position = new Vector3(match.x, match.y, match.z);
        GameObject obj = Instantiate(spherePrefab, position, Quaternion.identity);
        if (match.win)
            obj.GetComponent<Renderer>().material.color = Color.green;
        else
            obj.GetComponent<Renderer>().material.color = Color.red;
    }
}
