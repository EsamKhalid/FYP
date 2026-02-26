using UnityEngine;
using UnityEngine.SceneManagement;

public class Menus : MonoBehaviour
{
    [SerializeField] private string gameSceneName;

    public void play()
    {
        SceneManager.LoadScene(gameSceneName);
    }

    public void quit()
    {
        Application.Quit();
    }
}
