using System;
using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using Newtonsoft.Json;


public class ClusterScript : MonoBehaviour
{
    public GameObject playerPrefab;
    public GameObject spherePrefab;
    public TMP_InputField nameField;
    public TMP_InputField tagField;
    public void OnSubmitButton()
    {
        nameField.text = "SpilltTea";
        tagField.text = "TEA";
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
            APIResponse data = JsonConvert.DeserializeObject<APIResponse>(request.downloadHandler.text);

            //handleResponse(data);
            Debug.Log(request.downloadHandler.text);
        }
        else
        {
            Debug.LogError(request.error);
        }
    }

    //void handleResponse(APIResponse data)
    //{
    //    foreach (MatchPoint match in data.points)
    //    {
    //        SpawnMatchPoints(match);
    //    }
    //}

    void SpawnMatchPoints(MatchPoint match)
    {
        Vector3 position = new Vector3(match.x, match.y, match.z);
        GameObject obj = Instantiate(spherePrefab, position, Quaternion.identity);
        if (match.win)
            obj.GetComponent<Renderer>().material.color = Color.green;
        else
            obj.GetComponent<Renderer>().material.color = Color.red;
    }
}

//[System.Serializable]
//public class MatchPoint
//{
//    public float x;
//    public float y;
//    public float z;
//    public bool win;
//}

//[System.Serializable]
//public class PlayerResponse
//{
//    public string puuid;
//    public MatchPoint[] points;
//}

