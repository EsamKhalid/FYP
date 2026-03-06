using UnityEngine;
using UnityEngine.Rendering.UI;

public class PointSpawner : MonoBehaviour
{
    private GameObject handlerObject;
    private APIHandler handler;
    private APIResponse response;

    private GameObject[] pointObjects;

    [SerializeField] private GameObject spherePrefab;
    [SerializeField] GameObject cameraObject;

    private CameraScript cameraScript;
    private int currentPoint = 0;
    private int count = 0;

    void Awake()
    {
        cameraScript = cameraObject.GetComponent<CameraScript>();
        
        //MatchPoint[] points = new MatchPoint[10];

        pointObjects = new GameObject[10];

        //for (int i = 0; i < points.Length; i++)
        //{
        //    points[i] = new MatchPoint();
        //    points[i].x = Random.Range(0, 15f);
        //    points[i].y = Random.Range(0, 15f);
        //    points[i].z = Random.Range(0, 15f);
        //    points[i].win = Random.value < 0.5f;
        //    SpawnMatchPoint(points[i]);
        //}
        //cameraScript.centerTransform = pointObjects[0].transform;

        handlerObject = GameObject.Find("API");
        handler = handlerObject.GetComponent<APIHandler>();
        response = handler.data;
        MatchPoint[] points = response.points;
        pointObjects = new GameObject[points.Length];
        PlotPoints(points);
    }

    void PlotPoints(MatchPoint[] points)
    {
        foreach (MatchPoint point in points) 
        {
            SpawnMatchPoint(point);
        }
    }

    void SpawnMatchPoint(MatchPoint match)
    {
        Vector3 position = new Vector3(match.x, match.y, match.z);
        GameObject obj = Instantiate(spherePrefab, position, Quaternion.identity);
        pointObjects[count] = obj;
        if (match.win)
            obj.GetComponent<Renderer>().material.color = Color.green;
        else
            obj.GetComponent<Renderer>().material.color = Color.red;
        count += 1;
    }

    public void nextPoint()
    {
        if (currentPoint == pointObjects.Length - 1)
        {
            currentPoint = 0;
            cameraScript.transitionCamera(pointObjects[currentPoint].transform);
        }
        else
        {
            currentPoint += 1;
            cameraScript.transitionCamera(pointObjects[currentPoint].transform);
        }
            
    }

    public void previousPoint()
    {
        if(currentPoint == 0)
        {
            currentPoint = pointObjects.Length;
        }
        currentPoint -= 1;
        cameraScript.transitionCamera(pointObjects[currentPoint].transform);
        
    }
}
