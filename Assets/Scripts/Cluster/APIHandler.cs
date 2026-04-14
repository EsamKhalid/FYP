using Newtonsoft.Json;
using System;
using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class APIHandler : MonoBehaviour
{
    [SerializeField] private TMP_InputField nameField;
    [SerializeField] private TMP_InputField tagField;
    [SerializeField] private TMP_InputField laneField;

    public APIResponse data;

    private void Awake()
    {
        DontDestroyOnLoad(this.gameObject);
    }

    public void OnSubmitButton()
    {
        string name = nameField.text;
        string tag = tagField.text;
        string lane = laneField.text;
        //StartCoroutine(GetPlayerData(name, tag));
        StartCoroutine(GetPoints(lane));
    }

    IEnumerator GetPlayerData(string name, string tag)
    {
        string url = "http://127.0.0.1:8000/clusterManager/" + name + "/" + tag;
        UnityWebRequest request = UnityWebRequest.Get(url);

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            data = JsonConvert.DeserializeObject<APIResponse>(request.downloadHandler.text);
            SceneManager.LoadScene("Main");
            //handleResponse(data);
            //Debug.Log(request.downloadHandler.text);
        }
        else
        {
            Debug.LogError(request.error);
        }
    }

    IEnumerator GetPoints(string lane)
    {
        string url = "http://127.0.0.1:8000/UMAPPoints/" + lane;
        UnityWebRequest request = UnityWebRequest.Get(url);

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            data = JsonConvert.DeserializeObject<APIResponse>(request.downloadHandler.text);
            SceneManager.LoadScene("Main");
        }
        else
        {
            Debug.LogError(request.error);
        }
    }
}

[System.Serializable]
public class UMAPPoint
{
    public string puuid, match_id, lane;
    public bool win;
    public float x, y, z;
    public int cluster;
    public string current_rank;
}

[System.Serializable]
public class APIResponse
{
    public UMAPPoint[] umapPoints;
}


