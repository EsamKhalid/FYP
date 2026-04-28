using JetBrains.Annotations;
using Newtonsoft.Json;
using System;
using System.Collections;
using System.Collections.Generic;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class APIHandler : MonoBehaviour
{
    public APIResponse data;

    private void Awake()
    {
        DontDestroyOnLoad(this.gameObject);
    }

    IEnumerator GetPoints(string lane, string name, string tag, System.Action onSuccess = null, System.Action<string> onError = null)
    { 
        // String concatenation between url and input values
        string url = "http://127.0.0.1:8000/getPlayer/" + name + "/" + tag + "/" + lane;

        // Sends web request to url
        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            // Assigns returned json values to data attribute
            data = JsonConvert.DeserializeObject<APIResponse>(request.downloadHandler.text);
            // If no errors
            if (data.success)
            {
                onSuccess?.Invoke();
                // Loads main visualisation scene
                SceneManager.LoadScene("Main");
            }
            else
            {
                onError?.Invoke(data.error ?? "unknown error");
            }
        }
        else
        {
            onError?.Invoke(request.error ?? "network error");
        }
    }

    public void SubmitFromUI(string name, string tag, string lane,
                             System.Action onSuccess = null,
                             System.Action<string> onError = null)
    {
        StartCoroutine(GetPoints(lane, name, tag, onSuccess, onError));
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
    public UMAPPoint[] playerPoints;
    public UMAPPoint[] points;
    public bool success;
    public string error;
}


