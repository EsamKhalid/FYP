using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UIElements;

public class MainMenuController : MonoBehaviour
{
    [SerializeField] private UIDocument uiDocument;

    [SerializeField] private string inputSceneName = "InputScreen";

    void Awake()
    {
        var root = uiDocument.rootVisualElement;

        root.Q<Button>("play-btn") .clicked += () => SceneManager.LoadScene(inputSceneName);
        root.Q<Button>("about-btn").clicked += ShowAbout;
        root.Q<Button>("quit-btn") .clicked += QuitGame;
    }

    void ShowAbout()
    {
        Debug.Log("About clicked");
    }

    void QuitGame()
    {
#if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
#else
        Application.Quit();
#endif
    }
}
