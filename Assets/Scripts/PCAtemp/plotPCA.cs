using Newtonsoft.Json;
using System;
using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using UnityEngine.UIElements;

public class plotPCA : MonoBehaviour
{

    [SerializeField] private GameObject spherePrefab;
    [SerializeField] private float scale;
    private PointList pointList;
    private GameObject[] pointObjects;
    void Start()
    {
        pointObjects = new GameObject[pointList.points.Length];
        Debug.Log(pointObjects);
        spawnPoints();
        
    }

    private void Awake()
    {
        StartCoroutine(GetPoints());
        
    }

    IEnumerator GetPoints()
    {
        UnityWebRequest request = UnityWebRequest.Get("http://127.0.0.1:8000/points");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            //PointList data = JsonUtility.FromJson<PointList>(request.downloadHandler.text);
            pointList = JsonUtility.FromJson<PointList>(request.downloadHandler.text);

            //foreach (Point p in data.points)
            //{
            //    SpawnPoint(p);
            //}
        }
        else
        {
            Debug.LogError(request.error);
        }
    }

    GameObject SpawnPoint(Point p, float scale)
    {
        Vector3 position = new Vector3(p.x * scale, p.y * scale, p.z * scale);

        GameObject sphere = Instantiate(spherePrefab, position, Quaternion.identity);
        return sphere;

    }

    void spawnPoints()
    {
        foreach(GameObject gameObject in pointObjects)
        {
            Destroy(gameObject);
        }
        
        int count = 0;

        foreach (Point p in pointList.points)
        {
            pointObjects[count] = SpawnPoint(p, scale);
            count++;
        }
    }

    private void Update()
    {
        spawnPoints();
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