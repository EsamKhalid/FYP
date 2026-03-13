using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class plotPCA : MonoBehaviour
{

    [SerializeField] private GameObject spherePrefab;

    [SerializeField] private float scale = 1f;
    [SerializeField] private float pointSize = 1f;

    private PointList pointList;
    private GameObject[] pointObjects;

    private float previousScale;
    private float previousPointSize;

    void Awake()
    {
        StartCoroutine(GetPoints());
    }

    IEnumerator GetPoints()
    {
        UnityWebRequest request = UnityWebRequest.Get("http://127.0.0.1:8000/points");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            pointList = JsonUtility.FromJson<PointList>(request.downloadHandler.text);

            SpawnPoints();   // spawn once
            previousScale = scale;
        }
        else
        {
            Debug.LogError(request.error);
        }
    }

    void SpawnPoints()
    {
        pointObjects = new GameObject[pointList.points.Length];

        for (int i = 0; i < pointList.points.Length; i++)
        {
            Point p = pointList.points[i];

            Vector3 pos = new Vector3(p.x * scale, p.y * scale, p.z * scale);

            GameObject sphere = Instantiate(spherePrefab, pos, Quaternion.identity);
            pointObjects[i] = sphere;
        }
    }

    void Update()
    {
        if (scale != previousScale || pointSize != previousPointSize)
        {
            UpdateScale();
            previousScale = scale;
            previousPointSize = pointSize;
        }
    }

    void UpdateScale()
    {
        for (int i = 0; i < pointList.points.Length; i++)
        {
            Point p = pointList.points[i];

            Vector3 pos = new Vector3(p.x * scale, p.y * scale, p.z * scale);

            pointObjects[i].transform.position = pos;
            pointObjects[i].transform.localScale = new Vector3(pointSize, pointSize, pointSize);
        }
    }
}


[System.Serializable]
public class Point
{
    public float x;
    public float y;
    public float z;

    public int match_id;
    public int participant_id;
}

[System.Serializable]
public class PointList
{
    public Point[] points;
}