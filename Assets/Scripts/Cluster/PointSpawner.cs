using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.Rendering.UI;
using UnityEngine.SceneManagement;

public class PointSpawner : MonoBehaviour
{
    private GameObject handlerObject;
    private APIHandler handler;
    private APIResponse response;

    private GameObject[] pointObjects;
    private GameObject[] playerPointObjects;
    private UMAPPoint[] umap_points;
    private UMAPPoint[] playerPoints;

    [SerializeField] private GameObject cubePrefab;
    [SerializeField] GameObject cameraObject;

    [SerializeField] private TextMeshProUGUI rankLabel;

    private string[] ranks = { "IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER" };

    private float currentSpacing = 1f;

    private CameraScript cameraScript;
    private int currentPoint = 0;

    void Awake()
    {
        cameraScript = cameraObject.GetComponent<CameraScript>();
        
        handlerObject = GameObject.Find("API");
        handler = handlerObject.GetComponent<APIHandler>();
        response = handler.data;
        umap_points = response.points;
        playerPoints = response.playerPoints;

        pointObjects = new GameObject[umap_points.Length];
        playerPointObjects = new GameObject[playerPoints.Length];
        PlotPoints(umap_points);
        plotPlayerPoints(playerPoints);
        cameraScript.centerTransform = pointObjects[0].transform;
        FilterByRank("IRON");
    }

    void PlotPoints(UMAPPoint[] points)
    {
        for (int i = 0; i < points.Length; i++)
        {
            Vector3 position = new Vector3(points[i].x, points[i].y, points[i].z) * currentSpacing;
            pointObjects[i] = Instantiate(cubePrefab, position, Quaternion.identity);
            Renderer cubeRenderer = pointObjects[i].GetComponent<Renderer>();
            Color pointColour;
            switch (points[i].cluster)
            {
                case -1:
                    pointColour = Color.white;  
                    break;
                case 0:
                    pointColour = Color.red;
                    break;
                case 1:
                    pointColour = Color.blue;
                    break;
                case 2:
                    pointColour = Color.green;
                    break;
                case 3:
                    pointColour = Color.orange;
                    break;
                case 4:
                    pointColour = Color.turquoise;
                    break;
                default:
                    pointColour = Color.pink;
                    break;
            }
            //cubeRenderer.material.color = pointColour;
            cubeRenderer.material.color = Color.clear;
        }
    }

    void plotPlayerPoints(UMAPPoint[] playerPoints)
    {
        for (int i = 0; i < playerPoints.Length; i++)
        {
            Vector3 position = new Vector3(playerPoints[i].x, playerPoints[i].y, playerPoints[i].z) * currentSpacing;
            pointObjects[i] = Instantiate(cubePrefab, position, Quaternion.identity);
            Renderer cubeRenderer = pointObjects[i].GetComponent<Renderer>();
            cubeRenderer.material.color = Color.white;
        }
    }

    public void UpdateSpacing(float newSpacing)
    {
        currentSpacing = newSpacing;

        for (int i = 0; i < pointObjects.Length; i++)
        {
            if (pointObjects[i] != null)
            {
                Vector3 newPos = new Vector3(umap_points[i].x, umap_points[i].y, umap_points[i].z) * currentSpacing;
                pointObjects[i].transform.position = newPos;
            }
        }
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

    public void FilterByRank(string targetRank)
    {

        //bool showAll = (targetRank.ToUpper() == "ALL");

        for (int i = 0; i < pointObjects.Length; i++)
        {
            if (pointObjects[i] != null)
            {
                string rank = umap_points[i].current_rank;

                //bool shouldBeVisible = showAll || (rank.ToUpper() == targetRank.ToUpper());
                bool shouldBeVisible =  (rank.ToUpper() == targetRank.ToUpper());

                pointObjects[i].SetActive(shouldBeVisible);
            }
        }
    }

    public void OnRankSliderChanged(float value)
    {
        int index = Mathf.RoundToInt(value);

        if (index >= 0 && index < ranks.Length)
        {
            string selectedRank = ranks[index];

            if (rankLabel != null) rankLabel.text = selectedRank;

            FilterByRank(selectedRank);
        }
    }

    public void BackToInput()
    {
        GameObject.Destroy(handlerObject);
        SceneManager.LoadScene("InputScreen");
    }
}
