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
    private TMP_InputField nameField;
    //private TMP_InputField tagField;
    private TMP_Dropdown laneDropdown;

    private Button submitButton;

    private string[] laneList = {"TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY" };
    private int laneValue = 0;

    public APIResponse data;

    private void Awake()
    {
        nameField = GameObject.Find("nameInput").GetComponent<TMP_InputField>();
        //tagField = GameObject.Find("tagInput").GetComponent<TMP_InputField>();
        laneDropdown = GameObject.Find("LaneDropdown").GetComponent<TMP_Dropdown>();
        submitButton = GameObject.Find("SubmitButton").GetComponent<Button>();
        submitButton.onClick.AddListener(OnSubmitButton);
        Debug.Log(laneDropdown);

        DontDestroyOnLoad(this.gameObject);
        laneValue = laneDropdown.value;
        laneDropdown.onValueChanged.AddListener(delegate { OnDropdownValueChanged(laneDropdown); });
    }

    public void OnSubmitButton()
    {
        string[] input = nameField.text.Split('#');
        string name = input[0];
        string tag = input[1];
        string lane = laneList[laneValue];
        StartCoroutine(GetPoints(lane, name, tag));
    }

    private void OnDropdownValueChanged(TMP_Dropdown change)
    {

        laneValue = change.value;
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

    IEnumerator GetPoints(string lane, string name, string tag) 
    {
        Debug.Log(name + tag + lane);
        string url = "http://127.0.0.1:8000/getPlayer/" + name + "/" + tag + "/" + lane;
        //string url = "http://127.0.0.1:8000/getPlayer/SpilltTea/TEA/MIDDLE";
        UnityWebRequest request = UnityWebRequest.Get(url);

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            data = JsonConvert.DeserializeObject<APIResponse>(request.downloadHandler.text);
            Debug.Log(data.success);
            if (data.success == true)
            {
                SceneManager.LoadScene("Main");
            }
            else
            {
                Debug.LogError(data.error);
            }
            
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
    public UMAPPoint[] playerPoints;
    public UMAPPoint[] points;
    public bool success;
    public string error;
}


