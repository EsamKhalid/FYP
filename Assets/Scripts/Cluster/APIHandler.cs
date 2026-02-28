using System;
using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using Newtonsoft.Json;
using UnityEngine.SceneManagement;

public class APIHandler : MonoBehaviour
{
    [SerializeField] private TMP_InputField nameField;
    [SerializeField] private TMP_InputField tagField;

    public APIResponse data;

    private void Awake()
    {
        DontDestroyOnLoad(this.gameObject);
    }

    public void OnSubmitButton()
    {
        string name = nameField.text;
        string tag = tagField.text;
        StartCoroutine(GetPlayerData(name, tag));
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

    void handleResponse(APIResponse data)
    {

    }
}

[System.Serializable]
public class MatchPoint
{
    public float x;
    public float y;
    public float z;
    public bool win;
}

[System.Serializable]
public class APIResponse
{
    public string puuid;
    public MatchPoint[] points;
}
