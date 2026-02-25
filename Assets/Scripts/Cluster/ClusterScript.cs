using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;


public class ClusterScript : MonoBehaviour
{
    public GameObject playerPrefab;
    public TMP_InputField inputField;
    public void OnSubmitButton()
    {
        string riotID = inputField.text;
        StartCoroutine(GetPlayerData(riotID));
    }

    IEnumerator GetPlayerData(string riotID)
    {
        string url = "http://127.0.0.1:8000/player/" + riotID;
        UnityWebRequest request = UnityWebRequest.Get(url);

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            PlayerResponse data =
                JsonUtility.FromJson<PlayerResponse>(request.downloadHandler.text);

            SpawnPlayer(data);
        }
        else
        {
            Debug.LogError(request.error);
        }
    }

    void SpawnPlayer(PlayerResponse data)
    {
        Vector3 position = new Vector3(data.x, data.y, data.z);
        Instantiate(playerPrefab, position, Quaternion.identity);
    }
}

[System.Serializable]
public class PlayerResponse
{
    public float x;
    public float y;
    public float z;
    public int cluster;
}
