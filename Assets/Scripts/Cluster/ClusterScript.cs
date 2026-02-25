using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;


public class ClusterScript : MonoBehaviour
{
    public GameObject playerPrefab;
    public TMP_InputField nameField;
    public TMP_InputField tagField;
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
            PlayerResponse data = JsonUtility.FromJson<PlayerResponse>(request.downloadHandler.text);

            handleResponse(data);
        }
        else
        {
            Debug.LogError(request.error);
        }
    }

    void handleResponse(PlayerResponse data)
    {
        Vector3 position = new Vector3(data.x, data.y, data.z);
        Instantiate(playerPrefab, position, Quaternion.identity);
        Debug.Log(data.puuid);
    }
}

[System.Serializable]
public class PlayerResponse
{
    public float x;
    public float y;
    public float z;
    public int cluster;
    public string puuid;
}
